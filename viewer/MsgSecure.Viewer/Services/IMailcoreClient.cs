using System.Collections.Generic;
using System.Threading.Tasks;
using MsgSecure.Viewer.Services.Models;

namespace MsgSecure.Viewer.Services
{
    public interface IMailcoreClient
    {
        Task<bool> PingAsync();
        Task<MailboxDto> LoadMailboxAsync(string path);
        Task<MessageDto> LoadMessageAsync(string path);
        Task ExportTextAsync(IEnumerable<MessageDto> messages, string destination, string sourceLabel, bool includeAttachments);
        Task ExportJsonAsync(IEnumerable<MessageDto> messages, string destination, string sourceLabel, string? outputTextPath);
        Task ExportHashesAsync(IEnumerable<MessageDto> messages, string destination);
        Task ExportBundleAsync(IEnumerable<MessageDto> messages, ExportOptionsDto options);
    }
}
