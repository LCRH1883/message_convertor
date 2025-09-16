using System;
using System.Collections.Generic;

namespace MsgSecure.Viewer.Services.Models
{
    public class AttachmentDto
    {
        public string Id { get; set; } = string.Empty;
        public string Filename { get; set; } = string.Empty;
        public long? Size { get; set; }
        public string? Sha256 { get; set; }
        public string? ContentType { get; set; }
        public string? DataBase64 { get; set; }

        public bool HasData => !string.IsNullOrEmpty(DataBase64);

        public string SizeDisplay => Size.HasValue ? $"{Size.Value:N0} bytes" : string.Empty;

        public byte[]? GetDataBytes()
        {
            if (!HasData) return null;
            try
            {
                return Convert.FromBase64String(DataBase64!);
            }
            catch
            {
                return null;
            }
        }
    }

    public class MessageDto
    {
        public string Id { get; set; } = string.Empty;
        public string Source { get; set; } = string.Empty;
        public string? SourcePath { get; set; }
        public string Subject { get; set; } = string.Empty;
        public string Sender { get; set; } = string.Empty;
        public IList<string> To { get; set; } = new List<string>();
        public IList<string> Cc { get; set; } = new List<string>();
        public IList<string> Bcc { get; set; } = new List<string>();
        public DateTimeOffset? SentAt { get; set; }
        public string? BodyText { get; set; }
        public string? BodyHtml { get; set; }
        public IList<AttachmentDto> Attachments { get; set; } = new List<AttachmentDto>();

        public int AttachmentCount => Attachments?.Count ?? 0;
        public bool HasAttachments => AttachmentCount > 0;
    }

    public class FolderDto
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Path { get; set; } = string.Empty;
        public IList<MessageDto> Messages { get; set; } = new List<MessageDto>();
        public IList<FolderDto> Subfolders { get; set; } = new List<FolderDto>();
    }

    public class MailboxDto
    {
        public string SourcePath { get; set; } = string.Empty;
        public string DisplayName { get; set; } = string.Empty;
        public IList<FolderDto> Folders { get; set; } = new List<FolderDto>();
    }
}
