using System;

namespace MsgSecure.Viewer.Services
{
    public class MailcoreClientOptions
    {
        public string PythonExecutable { get; set; } = @"D:\Repos\message_convertor\.venv\Scripts\python.exe";
        public string ServerArguments { get; set; } = "-m mailcore.rpc_server";
        public string WorkingDirectory { get; set; } = AppContext.BaseDirectory;
    }
}
