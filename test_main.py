import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import subprocess
from main import download_extension, main

class TestExtensionManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary extensions directory if it doesn't exist
        os.makedirs("extensions", exist_ok=True)
    
    def tearDown(self):
        # Clean up any test files in extensions directory
        if os.path.exists("extensions/test.publisher.extension.vsix"):
            os.remove("extensions/test.publisher.extension.vsix")
    
    @patch('requests.get')
    def test_download_extension_success(self, mock_get):
        # Mock the response from requests.get
        mock_response = MagicMock()
        mock_response.content = b"mock extension content"
        mock_get.return_value = mock_response
        
        extension_id = "publisher.extension"
        expected_path = "./extensions/publisher.extension.vsix"
        
        # Use mock_open to avoid actually writing to disk
        with patch('builtins.open', mock_open()) as mock_file:
            result = download_extension(extension_id)
        
        # Verify the correct URL was called
        expected_url = "https://marketplace.visualstudio.com/_apis/public/gallery/publishers/publisher/vsextensions/extension/latest/vspackage"
        mock_get.assert_called_once()
        self.assertEqual(mock_get.call_args[0][0], expected_url)
        
        # Verify the file was "written"
        mock_file.assert_called_once_with(expected_path, "wb")
        mock_file().write.assert_called_once_with(b"mock extension content")
        
        self.assertEqual(result, expected_path)
    
    @patch('requests.get')
    def test_download_extension_network_error(self, mock_get):
        # Mock a network error
        mock_get.side_effect = Exception("Network error")
        
        with self.assertRaises(Exception):
            download_extension("test.publisher.extension")
    
    @patch('sys.argv', ['main.py'])  # No extension ID provided
    def test_main_no_args(self):
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)
    
    @patch('sys.argv', ['main.py', 'publisher.extension'])
    @patch('main.download_extension')
    @patch('subprocess.run')
    def test_main_success(self, mock_run, mock_download):
        # Mock successful download and installation
        mock_download.return_value = "./extensions/publisher.extension.vsix"
        mock_run.return_value.returncode = 0
        
        main()  # Should complete without raising any exceptions
        
        # Verify download_extension was called
        mock_download.assert_called_once_with('publisher.extension')
        
        # Verify subprocess.run was called with correct arguments
        mock_run.assert_called_once_with(
            ['windsurf', '--install-extension', './extensions/publisher.extension.vsix'],
            check=True
        )
    
    @patch('sys.argv', ['main.py', 'publisher.extension'])
    @patch('main.download_extension')
    @patch('subprocess.run')
    def test_main_installation_error(self, mock_run, mock_download):
        # Mock successful download but failed installation
        mock_download.return_value = "./extensions/publisher.extension.vsix"
        mock_run.side_effect = subprocess.CalledProcessError(1, 'cmd')
        
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)

if __name__ == '__main__':
    unittest.main()
