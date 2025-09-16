using System;

namespace MsgSecure.Viewer.Services.Models
{
    public class ExportOptionsDto
    {
        public string TextPath { get; set; } = string.Empty;
        public bool IncludeAttachmentsInText { get; set; }
        public bool IncludeJson { get; set; }
        public string? JsonPath { get; set; }
        public bool IncludeHashes { get; set; }
        public string? HashesPath { get; set; }
        public string SourceLabel { get; set; } = string.Empty;
        public string Encoding { get; set; } = "utf-8";
    }
}
