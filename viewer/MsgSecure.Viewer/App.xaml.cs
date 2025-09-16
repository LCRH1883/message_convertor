using System;
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
            _host = Host.CreateDefaultBuilder()
                .ConfigureServices((context, services) =>
                {
                    services.Configure<MailcoreClientOptions>(options =>
                    {
                        options.PythonExecutable = "python"; // TODO: allow configuration
                        options.ServerArguments = "-m mailcore.rpc_server";
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
