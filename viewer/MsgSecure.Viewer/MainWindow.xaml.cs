using System.ComponentModel;
using System.Net;
using System.Text;
using System.Text.RegularExpressions;
using System.Windows;
using MsgSecure.Viewer.Services.Models;
using MsgSecure.Viewer.ViewModels;

namespace MsgSecure.Viewer
{
    public partial class MainWindow : Window
    {
        private static readonly Regex HtmlRegex = new("<\\s*html", RegexOptions.IgnoreCase | RegexOptions.Compiled);
        private static readonly Regex HeadRegex = new("<\\s*head[^>]*>", RegexOptions.IgnoreCase | RegexOptions.Compiled);
        private static readonly Regex HtmlFragmentRegex = new("</?[a-z][a-z0-9-]*(\\s+[^<>]*)?>", RegexOptions.IgnoreCase | RegexOptions.Compiled);

        private ShellViewModel? _viewModel;

        public MainWindow()
        {
            InitializeComponent();
            Loaded += OnLoaded;
            Unloaded += OnUnloaded;
        }

        private void OnLoaded(object sender, RoutedEventArgs e)
        {
            _viewModel = DataContext as ShellViewModel;
            if (_viewModel is not null)
            {
                _viewModel.PropertyChanged += OnViewModelPropertyChanged;
                UpdatePreview();
            }
        }

        private void OnUnloaded(object sender, RoutedEventArgs e)
        {
            if (_viewModel is not null)
            {
                _viewModel.PropertyChanged -= OnViewModelPropertyChanged;
            }
        }

        private void OnViewModelPropertyChanged(object? sender, PropertyChangedEventArgs e)
        {
            if (e.PropertyName == nameof(ShellViewModel.SelectedMessage) ||
                e.PropertyName == nameof(ShellViewModel.PreviewFontSize))
            {
                Dispatcher.Invoke(UpdatePreview);
            }
        }

        private void UpdatePreview()
        {
            string html = BuildPreviewHtml(_viewModel?.SelectedMessage);
            PreviewBrowser.NavigateToString(html);
        }

        private string BuildPreviewHtml(MessageDto? message)
        {
            double fontSize = _viewModel?.PreviewFontSize ?? 14;
            var headBuilder = new StringBuilder();
            headBuilder.Append("<meta charset=\"utf-8\"/>");
            headBuilder.Append("<style>");
            headBuilder.Append("body { font-family: 'Segoe UI', 'Malgun Gothic', 'Segoe UI Emoji', 'Noto Sans CJK KR', sans-serif; margin: 12px; }");
            headBuilder.Append($"body {{ font-size: {fontSize}px; }}");
            headBuilder.Append(".plain { white-space: pre-wrap; }");
            headBuilder.Append("</style>");
            string headContent = headBuilder.ToString();

            if (message is null)
            {
                return $"<html><head>{headContent}</head><body><i>Select a message to preview.</i></body></html>";
            }

            string? bodyHtml = message.BodyHtml;
            string? bodyText = message.BodyText;

            if (!string.IsNullOrWhiteSpace(bodyHtml))
            {
                return EnsureHtmlWithHead(bodyHtml, headContent);
            }

            if (!string.IsNullOrWhiteSpace(bodyText) && LooksLikeHtml(bodyText))
            {
                return EnsureHtmlWithHead(bodyText, headContent);
            }

            if (!string.IsNullOrWhiteSpace(bodyText))
            {
                var decoded = WebUtility.HtmlDecode(bodyText);
                var safe = WebUtility.HtmlEncode(decoded);
                safe = safe.Replace("\r\n", "<br/>").Replace("\n", "<br/>");
                return $"<html><head>{headContent}</head><body><div class='plain'>{safe}</div></body></html>";
            }

            return $"<html><head>{headContent}</head><body><i>(No content)</i></body></html>";
        }

        private static bool LooksLikeHtml(string text)
        {
            if (string.IsNullOrWhiteSpace(text)) return false;
            if (HtmlRegex.IsMatch(text)) return true;
            return HtmlFragmentRegex.IsMatch(text);
        }

        private static string EnsureHtmlWithHead(string content, string headContent)
        {
            if (string.IsNullOrWhiteSpace(content))
            {
                return $"<html><head>{headContent}</head><body></body></html>";
            }

            if (!HtmlRegex.IsMatch(content))
            {
                return $"<html><head>{headContent}</head><body>{content}</body></html>";
            }

            if (HeadRegex.IsMatch(content))
            {
                return HeadRegex.Replace(content, match => match.Value + headContent, 1);
            }

            return HtmlRegex.Replace(content, match => match.Value + "<head>" + headContent + "</head>", 1);
        }
        private void MenuExit_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Shutdown();
        }

        private void MenuAbout_Click(object sender, RoutedEventArgs e)
        {
            MessageBox.Show("MsgSecure Viewer\r\n\r\nPreview build with attachment support.", "About MsgSecure Viewer", MessageBoxButton.OK, MessageBoxImage.Information);
        }

    }
}
