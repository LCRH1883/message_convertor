using System.Windows;
using Microsoft.Win32;
using MsgSecure.Viewer.ViewModels;

namespace MsgSecure.Viewer.Dialogs
{
    public partial class ExportDialog : Window
    {
        public ExportDialog()
        {
            InitializeComponent();
        }

        private ExportOptionsViewModel Options => (ExportOptionsViewModel)DataContext;

        private void BrowseText_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new SaveFileDialog
            {
                Filter = "Text files (*.txt)|*.txt|All files (*.*)|*.*",
                FileName = Options.TextPath
            };
            if (dialog.ShowDialog(this) == true)
            {
                Options.TextPath = dialog.FileName;
            }
        }

        private void BrowseJson_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new SaveFileDialog
            {
                Filter = "JSON files (*.json)|*.json|All files (*.*)|*.*",
                FileName = Options.JsonPath ?? string.Empty
            };
            if (dialog.ShowDialog(this) == true)
            {
                Options.JsonPath = dialog.FileName;
            }
        }

        private void BrowseHashes_Click(object sender, RoutedEventArgs e)
        {
            var dialog = new SaveFileDialog
            {
                Filter = "CSV files (*.csv)|*.csv|All files (*.*)|*.*",
                FileName = Options.HashesPath ?? string.Empty
            };
            if (dialog.ShowDialog(this) == true)
            {
                Options.HashesPath = dialog.FileName;
            }
        }

        private void Ok_Click(object sender, RoutedEventArgs e)
        {
            if (!Options.Validate())
            {
                MessageBox.Show(this, "Please choose a text output file.", "Export Messages", MessageBoxButton.OK, MessageBoxImage.Warning);
                return;
            }
            DialogResult = true;
        }
    }
}
