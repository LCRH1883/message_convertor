using System;
using System.Collections.ObjectModel;
using System.Collections.Specialized;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
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
        private MessageDto? _selectedMessage;
        private double _previewFontSize = 14;

        public ShellViewModel(IMailcoreClient mailcoreClient)
        {
            _mailcoreClient = mailcoreClient;
            OpenCommand = new AsyncRelayCommand(_ => OpenAsync());
            OpenAttachmentCommand = new AsyncRelayCommand(param => OpenAttachmentAsync(param as AttachmentDto));
            SaveAttachmentCommand = new AsyncRelayCommand(param => SaveAttachmentAsync(param as AttachmentDto));
            Messages = new ObservableCollection<MessageDto>();
            Attachments = new ObservableCollection<AttachmentDto>();
            Attachments.CollectionChanged += Attachments_CollectionChanged;
        }

        public ICommand OpenCommand { get; }
        public ICommand OpenAttachmentCommand { get; }
        public ICommand SaveAttachmentCommand { get; }

        public ObservableCollection<MessageDto> Messages { get; }
        public ObservableCollection<AttachmentDto> Attachments { get; }

        public bool HasAttachments => Attachments.Count > 0;

        public MessageDto? SelectedMessage
        {
            get => _selectedMessage;
            set
            {
                if (_selectedMessage != value)
                {
                    _selectedMessage = value;
                    OnPropertyChanged();
                    UpdateAttachments();
                }
            }
        }

        public double PreviewFontSize
        {
            get => _previewFontSize;
            set
            {
                if (Math.Abs(_previewFontSize - value) > double.Epsilon)
                {
                    _previewFontSize = value;
                    OnPropertyChanged();
                }
            }
        }

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
                    SelectedMessage = null;
                    Messages.Clear();
                    foreach (var folder in mailbox.Folders)
                    {
                        foreach (var message in folder.Messages)
                        {
                            Messages.Add(message);
                        }
                    }
                    SelectedMessage = Messages.FirstOrDefault();
                });
                Status = $"Loaded {Messages.Count} message(s)";
            }
            catch (Exception ex)
            {
                Status = "Error: " + ex.Message;
            }
        }

        private void Attachments_CollectionChanged(object? sender, NotifyCollectionChangedEventArgs e)
        {
            OnPropertyChanged(nameof(HasAttachments));
        }

        private void UpdateAttachments()
        {
            Attachments.Clear();
            if (SelectedMessage?.Attachments is not null)
            {
                foreach (var attachment in SelectedMessage.Attachments)
                {
                    Attachments.Add(attachment);
                }
            }
            OnPropertyChanged(nameof(HasAttachments));
        }

        private Task OpenAttachmentAsync(AttachmentDto? attachment)
        {
            if (attachment?.HasData != true) return Task.CompletedTask;
            var bytes = attachment.GetDataBytes();
            if (bytes is null) return Task.CompletedTask;
            var fileName = SanitizeFileName(attachment.Filename);
            var tempPath = Path.Combine(Path.GetTempPath(), $"{Guid.NewGuid()}_{fileName}");
            try
            {
                File.WriteAllBytes(tempPath, bytes);
                Process.Start(new ProcessStartInfo(tempPath) { UseShellExecute = true });
            }
            catch (Exception ex)
            {
                Status = "Error opening attachment: " + ex.Message;
            }
            return Task.CompletedTask;
        }

        private Task SaveAttachmentAsync(AttachmentDto? attachment)
        {
            if (attachment?.HasData != true) return Task.CompletedTask;
            var bytes = attachment.GetDataBytes();
            if (bytes is null) return Task.CompletedTask;
            var dialog = new SaveFileDialog
            {
                FileName = SanitizeFileName(attachment.Filename),
                Filter = "All files (*.*)|*.*"
            };
            if (dialog.ShowDialog() == true)
            {
                try
                {
                    File.WriteAllBytes(dialog.FileName, bytes);
                }
                catch (Exception ex)
                {
                    Status = "Error saving attachment: " + ex.Message;
                }
            }
            return Task.CompletedTask;
        }

        private static string SanitizeFileName(string? fileName)
        {
            var name = string.IsNullOrWhiteSpace(fileName) ? "attachment" : fileName;
            foreach (var invalid in Path.GetInvalidFileNameChars())
            {
                name = name.Replace(invalid, '_');
            }
            return name;
        }

        public event PropertyChangedEventHandler? PropertyChanged;
        private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
            => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
