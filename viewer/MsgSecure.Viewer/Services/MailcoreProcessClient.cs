using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Options;
using MsgSecure.Viewer.Services.Models;

namespace MsgSecure.Viewer.Services
{
    public class MailcoreProcessClient : IMailcoreClient, IDisposable
    {
        private readonly MailcoreClientOptions _options;
        private readonly SemaphoreSlim _mutex = new(1, 1);
        private Process? _process;
        private StreamWriter? _writer;
        private StreamReader? _reader;
        private readonly StringBuilder _stderrBuffer = new();
        private int _nextId = 1;
        private bool _disposed;

        public MailcoreProcessClient(IOptions<MailcoreClientOptions> options)
        {
            _options = options.Value;
        }

        public async Task<bool> PingAsync()
        {
            var response = await SendRequestAsync("ping", new object());
            return response?.GetValue<string>() == "pong";
        }

        public async Task<MailboxDto> LoadMailboxAsync(string path)
        {
            var response = await SendRequestAsync("load_mailbox", new { path });
            return response!.Deserialize<MailboxDto>() ?? new MailboxDto();
        }

        public async Task<MessageDto> LoadMessageAsync(string path)
        {
            var response = await SendRequestAsync("load_message", new { path });
            return response!.Deserialize<MessageDto>() ?? new MessageDto();
        }

        public Task ExportTextAsync(IEnumerable<MessageDto> messages, string destination, string sourceLabel, bool includeAttachments)
        {
            var payload = new
            {
                messages,
                dest = destination,
                source = sourceLabel,
                show_attachments = includeAttachments
            };
            return SendRequestAsync("export_text", payload);
        }

        public Task ExportJsonAsync(IEnumerable<MessageDto> messages, string destination, string sourceLabel, string? outputTextPath)
        {
            var payload = new
            {
                messages,
                dest = destination,
                source = sourceLabel,
                output_text = outputTextPath
            };
            return SendRequestAsync("export_json", payload);
        }

        public Task ExportHashesAsync(IEnumerable<MessageDto> messages, string destination)
        {
            var payload = new { messages, dest = destination };
            return SendRequestAsync("export_hashes", payload);
        }

        private async Task<JsonNode?> SendRequestAsync(string method, object parameters)
        {
            await _mutex.WaitAsync().ConfigureAwait(false);
            try
            {
                EnsureProcess();
                if (_writer is null || _reader is null)
                {
                    throw new InvalidOperationException("RPC process not started");
                }

                int id = _nextId++;
                var request = new JsonObject
                {
                    ["jsonrpc"] = "2.0",
                    ["id"] = id,
                    ["method"] = method,
                    ["params"] = JsonSerializer.Deserialize<JsonNode>(JsonSerializer.Serialize(parameters))
                };
                string line = request.ToJsonString();
                await _writer.WriteLineAsync(line).ConfigureAwait(false);
                await _writer.FlushAsync().ConfigureAwait(false);

                while (true)
                {
                    string? responseLine = await _reader.ReadLineAsync().ConfigureAwait(false);
                    if (responseLine is null)
                    {
                        var stderr = _stderrBuffer.ToString().Trim();
                        throw new IOException(string.IsNullOrEmpty(stderr)
                            ? "RPC server terminated unexpectedly"
                            : $"RPC server terminated unexpectedly: {stderr}");
                    }
                    var envelope = JsonNode.Parse(responseLine)!.AsObject();
                    if (envelope["id"]?.GetValue<int>() != id)
                    {
                        continue;
                    }
                    if (envelope.TryGetPropertyValue("error", out var errorNode))
                    {
                        throw new InvalidOperationException(errorNode?["message"]?.GetValue<string>() ?? "RPC error");
                    }
                    return envelope["result"];
                }
            }
            finally
            {
                _mutex.Release();
            }
        }

        private void EnsureProcess()
        {
            if (_process is { HasExited: false })
            {
                return;
            }

            _process?.Dispose();
            _stderrBuffer.Clear();

            var startInfo = new ProcessStartInfo
            {
                FileName = _options.PythonExecutable,
                Arguments = _options.ServerArguments,
                WorkingDirectory = _options.WorkingDirectory,
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            startInfo.Environment["PYTHONPATH"] = _options.WorkingDirectory;

            _process = Process.Start(startInfo) ?? throw new InvalidOperationException("Failed to start mailcore RPC server");
            _writer = _process.StandardInput;
            _reader = _process.StandardOutput;
            _process.ErrorDataReceived += (_, e) =>
            {
                if (!string.IsNullOrEmpty(e.Data))
                {
                    _stderrBuffer.AppendLine(e.Data);
                }
            };
            _process.BeginErrorReadLine();
        }

        public void Dispose()
        {
            if (_disposed) return;
            _disposed = true;
            try
            {
                if (_process is { HasExited: false })
                {
                    _writer?.WriteLine("{\"jsonrpc\":\"2.0\",\"id\":0,\"method\":\"shutdown\"}");
                    _writer?.Flush();
                    _process.WaitForExit(1000);
                }
            }
            catch
            {
            }
            finally
            {
                try
                {
                    _process?.CancelErrorRead();
                }
                catch
                {
                }
                _writer?.Dispose();
                _reader?.Dispose();
                _process?.Dispose();
                _mutex.Dispose();
            }
        }
    }
}
