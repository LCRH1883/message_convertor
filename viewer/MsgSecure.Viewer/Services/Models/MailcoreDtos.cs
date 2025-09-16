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
