using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using Microsoft.Win32;
using MsgSecure.Viewer.Commands;
using MsgSecure.Viewer.Services;
using MsgSecure.Viewer.Services.Models;

namespace MsgSecure.Viewer.ViewModels
{
    public class ShellViewModel : INotifyPropertyChanged
    {
        private readonly IMailcoreClient _mailcoreClient;
        private string _status = "Ready";
        private MailboxDto? _currentMailbox;

        public ShellViewModel(IMailcoreClient mailcoreClient)
        {
            _mailcoreClient = mailcoreClient;
            OpenCommand = new AsyncRelayCommand(_ => OpenAsync());
            Messages = new ObservableCollection<MessageDto>();
        }

        public ICommand OpenCommand { get; }

        public ObservableCollection<MessageDto> Messages { get; }

        public string Status
        {
            get => _status;
            private set
            {
                if (_status != value)
                {
                    _status = value;
                    OnPropertyChanged();
                }
            }
        }

        public MailboxDto? CurrentMailbox
        {
            get => _currentMailbox;
            private set
            {
                if (_currentMailbox != value)
                {
                    _currentMailbox = value;
                    OnPropertyChanged();
                }
            }
        }

        private async Task OpenAsync()
        {
            var dialog = new OpenFileDialog
            {
                Filter = "Mail sources (*.pst;*.ost;*.msg;*.eml)|*.pst;*.ost;*.msg;*.eml|All files (*.*)|*.*",
                Multiselect = false
            };
            bool? result = dialog.ShowDialog();
            if (result != true)
            {
                return;
            }
            string path = dialog.FileName;
            Status = $"Loading {path}...";
            try
            {
                var mailbox = await _mailcoreClient.LoadMailboxAsync(path);
                CurrentMailbox = mailbox;
                Application.Current.Dispatcher.Invoke(() =>
                {
                    Messages.Clear();
                    foreach (var folder in mailbox.Folders)
                    {
                        foreach (var message in folder.Messages)
                        {
                            Messages.Add(message);
                        }
                    }
                });
                Status = $"Loaded {Messages.Count} message(s)";
            }
            catch (Exception ex)
            {
                Status = "Error: " + ex.Message;
            }
        }

        public event PropertyChangedEventHandler? PropertyChanged;
        private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
            => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
