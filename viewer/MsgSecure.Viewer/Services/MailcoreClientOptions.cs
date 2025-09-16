namespace MsgSecure.Viewer.Services
{
    public class MailcoreClientOptions
    {
        public string PythonExecutable { get; set; } = "python";
        public string ServerArguments { get; set; } = "-m mailcore.rpc_server";
        public string WorkingDirectory { get; set; } = ".";
    }
}
