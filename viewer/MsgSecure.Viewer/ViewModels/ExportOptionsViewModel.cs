using System;
using System.ComponentModel;
using System.IO;
using System.Runtime.CompilerServices;
using MsgSecure.Viewer.Services.Models;

namespace MsgSecure.Viewer.ViewModels
{
    public class ExportOptionsViewModel : INotifyPropertyChanged
    {
        private string _textPath = string.Empty;
        private bool _includeAttachments;
        private bool _includeJson;
        private string? _jsonPath;
        private bool _includeHashes;
        private string? _hashesPath;
        private bool _exportSelectedOnly;
        private bool _canExportSelected;
        private string _encoding = "utf-8";

        private bool _jsonPathManuallyEdited;
        private bool _hashPathManuallyEdited;

        public event PropertyChangedEventHandler? PropertyChanged;

        public string TextPath
        {
            get => _textPath;
            set
            {
                if (_textPath != value)
                {
                    _textPath = value;
                    OnPropertyChanged();
                    UpdateDerivedPaths();
                }
            }
        }

        public bool IncludeAttachmentsInText
        {
            get => _includeAttachments;
            set
            {
                if (_includeAttachments != value)
                {
                    _includeAttachments = value;
                    OnPropertyChanged();
                }
            }
        }

        public bool IncludeJson
        {
            get => _includeJson;
            set
            {
                if (_includeJson != value)
                {
                    _includeJson = value;
                    OnPropertyChanged();
                    UpdateDerivedPaths();
                }
            }
        }

        public string? JsonPath
        {
            get => _jsonPath;
            set
            {
                if (_jsonPath != value)
                {
                    _jsonPath = value;
                    _jsonPathManuallyEdited = true;
                    OnPropertyChanged();
                }
            }
        }

        public bool IncludeHashes
        {
            get => _includeHashes;
            set
            {
                if (_includeHashes != value)
                {
                    _includeHashes = value;
                    OnPropertyChanged();
                    UpdateDerivedPaths();
                }
            }
        }

        public string? HashesPath
        {
            get => _hashesPath;
            set
            {
                if (_hashesPath != value)
                {
                    _hashesPath = value;
                    _hashPathManuallyEdited = true;
                    OnPropertyChanged();
                }
            }
        }

        public bool ExportSelectedOnly
        {
            get => _exportSelectedOnly;
            set
            {
                if (_exportSelectedOnly != value)
                {
                    _exportSelectedOnly = value;
                    OnPropertyChanged();
                }
            }
        }

        public bool CanExportSelected
        {
            get => _canExportSelected;
            set
            {
                if (_canExportSelected != value)
                {
                    _canExportSelected = value;
                    OnPropertyChanged();
                }
            }
        }

        public string Encoding
        {
            get => _encoding;
            set
            {
                if (_encoding != value)
                {
                    _encoding = value;
                    OnPropertyChanged();
                }
            }
        }

        public ExportOptionsDto ToDto(string sourceLabel)
        {
            return new ExportOptionsDto
            {
                TextPath = TextPath,
                IncludeAttachmentsInText = IncludeAttachmentsInText,
                IncludeJson = IncludeJson && !string.IsNullOrWhiteSpace(JsonPath),
                JsonPath = IncludeJson ? JsonPath : null,
                IncludeHashes = IncludeHashes && !string.IsNullOrWhiteSpace(HashesPath),
                HashesPath = IncludeHashes ? HashesPath : null,
                SourceLabel = sourceLabel,
                Encoding = Encoding
            };
        }

        public bool Validate() => !string.IsNullOrWhiteSpace(TextPath);

        private void UpdateDerivedPaths()
        {
            if (string.IsNullOrWhiteSpace(TextPath))
            {
                return;
            }
            try
            {
                if (IncludeJson && !_jsonPathManuallyEdited)
                {
                    JsonPath = Path.ChangeExtension(TextPath, ".json");
                    _jsonPathManuallyEdited = false;
                }
                if (IncludeHashes && !_hashPathManuallyEdited)
                {
                    var basePath = Path.ChangeExtension(TextPath, null) ?? TextPath;
                    HashesPath = basePath + "_hashes.csv";
                    _hashPathManuallyEdited = false;
                }
            }
            catch
            {
                // ignore invalid paths while typing
            }
        }

        private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
            => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
