using System;
using System.IO;
using System.Windows;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using MsgSecure.Viewer.Services;
using MsgSecure.Viewer.ViewModels;

namespace MsgSecure.Viewer
{
    public partial class App : Application
    {
        private IHost? _host;

        public App()
        {
            Startup += OnStartup;
            Exit += OnExit;
        }

        private void OnStartup(object sender, StartupEventArgs e)
        {
            try
            {
                _host = Host.CreateDefaultBuilder()
                    .ConfigureServices((context, services) =>
                    {
                        services.Configure<MailcoreClientOptions>(options =>
                        {
                            var repoRoot = Path.GetFullPath(Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", ".."));
                            if (!Directory.Exists(Path.Combine(repoRoot, "mailcore")))
                            {
                                repoRoot = AppContext.BaseDirectory;
                            }
                            var pythonPath = Path.Combine(repoRoot, ".venv", "Scripts", "python.exe");
                            options.PythonExecutable = File.Exists(pythonPath) ? pythonPath : options.PythonExecutable;
                            options.ServerArguments = "-m mailcore.rpc_server";
                            options.WorkingDirectory = repoRoot;
                        });
                        services.AddSingleton<IMailcoreClient, MailcoreProcessClient>();
                        services.AddSingleton<ShellViewModel>();
                    })
                    .Build();

                _host.Start();

                var window = new MainWindow
                {
                    DataContext = _host.Services.GetRequiredService<ShellViewModel>()
                };
                window.Show();
            }
            catch (Exception ex)
            {
                MessageBox.Show(ex.ToString(), "MsgSecure Viewer Startup Error", MessageBoxButton.OK, MessageBoxImage.Error);
                Shutdown();
            }
        }

        private async void OnExit(object sender, ExitEventArgs e)
        {
            if (_host is not null)
            {
                await _host.StopAsync(TimeSpan.FromSeconds(2));
                _host.Dispose();
            }
        }
    }
}
