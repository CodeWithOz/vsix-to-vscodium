"""Tests for code-to-codium CLI."""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import subprocess
import json
import requests
from code_to_codium.cli import download_extension, main


class TestExtensionManager(unittest.TestCase):
    def setUp(self):
        # Create a temporary extensions directory if it doesn't exist
        os.makedirs("extensions", exist_ok=True)

    def tearDown(self):
        # Clean up any test files in extensions directory
        test_files = [
            "extensions/publisher.extension-1.0.0.vsix",
            "extensions/publisher.extension-2.0.0.vsix",
        ]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)

    @patch("requests.post")
    @patch("requests.get")
    def test_download_extension_success(self, mock_get, mock_post):
        # Mock the API query response
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {
            "results": [{"extensions": [{"versions": [{"version": "1.0.0"}]}]}]
        }
        mock_post.return_value = mock_post_response

        # Mock the download response
        mock_get_response = MagicMock()
        mock_get_response.content = b"mock extension content"
        mock_get.return_value = mock_get_response

        extension_id = "publisher.extension"
        expected_path = "./extensions/publisher.extension-1.0.0.vsix"

        # Use mock_open to avoid actually writing to disk
        with patch('builtins.open', mock_open()) as mock_file:
            result = download_extension(extension_id)

        # Verify API query
        mock_post.assert_called_once()
        self.assertEqual(
            mock_post.call_args[1]["json"]["filters"][0]["criteria"][0]["value"],
            extension_id,
        )

        # Verify download request
        mock_get.assert_called_once()
        expected_download_url = "https://publisher.gallery.vsassets.io/_apis/public/gallery/publisher/publisher/extension/extension/1.0.0/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage"
        self.assertEqual(mock_get.call_args[0][0], expected_download_url)

        # Verify file writing
        mock_file.assert_called_once_with(expected_path, "wb")
        mock_file().write.assert_called_once_with(b"mock extension content")

        self.assertEqual(result, expected_path)

    @patch("requests.post")
    @patch("requests.get")
    def test_download_specific_version(self, mock_get, mock_post):
        mock_post_response = MagicMock()
        mock_post.return_value = mock_post_response

        mock_get_response = MagicMock()
        mock_get_response.content = b"mock extension content"
        mock_get.return_value = mock_get_response

        extension_id = "publisher.extension"
        specific_version = "2.0.0"
        expected_path = f"./extensions/{extension_id}-{specific_version}.vsix"

        with patch("builtins.open", mock_open()) as mock_file:
            result = download_extension(extension_id, specific_version=specific_version)

        self.assertEqual(result, expected_path)
        expected_download_url = f"https://publisher.gallery.vsassets.io/_apis/public/gallery/publisher/publisher/extension/extension/{specific_version}/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage"
        self.assertEqual(mock_get.call_args[0][0], expected_download_url)

    @patch("os.path.exists")
    @patch("requests.post")
    def test_download_extension_cached(self, mock_post, mock_exists):
        # Mock the API query response for version check
        mock_post_response = MagicMock()
        mock_post_response.json.return_value = {
            "results": [{"extensions": [{"versions": [{"version": "1.0.0"}]}]}]
        }
        mock_post.return_value = mock_post_response

        # Mock that the file already exists
        mock_exists.return_value = True

        extension_id = "publisher.extension"
        expected_path = "./extensions/publisher.extension-1.0.0.vsix"

        # Should return the cached path without making any download requests
        with patch("requests.get") as mock_get:
            result = download_extension(extension_id)
            mock_get.assert_not_called()

        self.assertEqual(result, expected_path)

    @patch("requests.post")
    def test_download_extension_invalid_id(self, mock_post):
        with self.assertRaises(SystemExit) as cm:
            download_extension("invalid_id")
        self.assertEqual(cm.exception.code, 1)
        mock_post.assert_not_called()

    @patch("requests.post")
    def test_download_extension_api_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("API Error")

        with self.assertRaises(requests.exceptions.RequestException):
            download_extension("publisher.extension")

    def test_main_no_args(self):
        with self.assertRaises(SystemExit) as cm:
            main([])
        self.assertEqual(cm.exception.code, 1)

    @patch('code_to_codium.cli.download_extension')
    @patch('subprocess.run')
    @patch('os.remove')
    def test_main_success_with_cleanup(self, mock_remove, mock_run, mock_download):
        vsix_path = "./extensions/publisher.extension-1.0.0.vsix"
        mock_download.return_value = vsix_path
        mock_run.return_value.returncode = 0

        main(["publisher.extension"])

        mock_download.assert_called_once_with("publisher.extension")
        mock_run.assert_called_once_with(
            [
                "windsurf",
                "--install-extension",
                vsix_path,
            ],
            check=True,
        )
        # Verify cleanup
        mock_remove.assert_called_once_with(vsix_path)

    @patch('code_to_codium.cli.download_extension')
    @patch('subprocess.run')
    @patch('os.remove')
    def test_main_cleanup_error(self, mock_remove, mock_run, mock_download):
        vsix_path = "./extensions/publisher.extension-1.0.0.vsix"
        mock_download.return_value = vsix_path
        mock_run.return_value.returncode = 0
        mock_remove.side_effect = OSError("Permission denied")

        # Should complete successfully even if cleanup fails
        main(["publisher.extension"])

        mock_remove.assert_called_once_with(vsix_path)
        # Verify that the installation completed
        mock_run.assert_called_once_with(
            [
                "windsurf",
                "--install-extension",
                vsix_path,
            ],
            check=True,
        )
