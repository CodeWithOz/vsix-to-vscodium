"""Tests for vsix-to-vscodium CLI."""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import subprocess
import requests
import json
import sys
import os

from vsix_to_vscodium.cli import (
    download_extension,
    main,
    get_vscode_extensions,
    install_extension,
)


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

    def test_get_vscode_extensions_success(self):
        """Test successful retrieval of VS Code extensions."""
        mock_output = "publisher1.ext1\npublisher2.ext2\npublisher3.ext3"
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.stdout = mock_output
            extensions = get_vscode_extensions()

            self.assertEqual(
                extensions, ["publisher1.ext1", "publisher2.ext2", "publisher3.ext3"]
            )
            mock_run.assert_called_once_with(
                ["code", "--list-extensions"],
                check=True,
                capture_output=True,
                text=True,
            )

    def test_get_vscode_extensions_not_found(self):
        """Test when VS Code is not installed."""
        with patch("subprocess.run", side_effect=FileNotFoundError()):
            with self.assertRaises(FileNotFoundError):
                get_vscode_extensions()

    def test_get_vscode_extensions_command_error(self):
        """Test when VS Code command fails."""
        with patch(
            "subprocess.run", side_effect=subprocess.CalledProcessError(1, "code")
        ):
            with self.assertRaises(subprocess.CalledProcessError):
                get_vscode_extensions()

    def test_install_extension_success(self):
        """Test successful extension installation."""
        vsix_path = "./extensions/test.vsix"
        ide_name = "test-ide"

        with patch("subprocess.run") as mock_run, patch("os.remove") as mock_remove:
            install_extension(vsix_path, ide_name)

            mock_run.assert_called_once_with(
                ["test-ide", "--install-extension", vsix_path], check=True
            )
            mock_remove.assert_called_once_with(vsix_path)

    def test_install_extension_cleanup_error(self):
        """Test when cleanup fails but installation succeeds."""
        vsix_path = "./extensions/test.vsix"
        ide_name = "test-ide"

        with patch("subprocess.run") as mock_run, patch(
            "os.remove", side_effect=OSError("Permission denied")
        ):
            install_extension(vsix_path, ide_name)

            mock_run.assert_called_once()  # Installation should still happen
            # Function should complete without raising an exception

    def test_install_extension_installation_error(self):
        """Test when installation fails."""
        vsix_path = "./extensions/test.vsix"
        ide_name = "test-ide"

        with patch(
            "subprocess.run", side_effect=subprocess.CalledProcessError(1, "test-ide")
        ), patch("os.remove") as mock_remove:
            with self.assertRaises(subprocess.CalledProcessError):
                install_extension(vsix_path, ide_name)

            # Verify cleanup happens even when installation fails
            mock_remove.assert_called_once_with(vsix_path)

    @patch("vsix_to_vscodium.cli.get_vscode_extensions")
    @patch("vsix_to_vscodium.cli.download_extension")
    @patch("vsix_to_vscodium.cli.install_extension")
    def test_main_transfer_all_success(
        self, mock_install, mock_download, mock_get_extensions
    ):
        """Test successful transfer of all extensions."""
        mock_get_extensions.return_value = ["pub1.ext1", "pub2.ext2"]
        mock_download.side_effect = [
            "./extensions/pub1.ext1.vsix",
            "./extensions/pub2.ext2.vsix",
        ]

        main(["--transfer-all"])

        self.assertEqual(mock_get_extensions.call_count, 1)
        self.assertEqual(mock_download.call_count, 2)
        self.assertEqual(mock_install.call_count, 2)

        # Verify calls were made with correct arguments
        mock_download.assert_any_call("pub1.ext1")
        mock_download.assert_any_call("pub2.ext2")
        mock_install.assert_any_call("./extensions/pub1.ext1.vsix", "codium")
        mock_install.assert_any_call("./extensions/pub2.ext2.vsix", "codium")

    @patch("vsix_to_vscodium.cli.get_vscode_extensions")
    @patch("vsix_to_vscodium.cli.download_extension")
    @patch("vsix_to_vscodium.cli.install_extension")
    def test_main_transfer_all_custom_ide(
        self, mock_install, mock_download, mock_get_extensions
    ):
        """Test transferring all extensions to a custom IDE."""
        mock_get_extensions.return_value = ["pub1.ext1"]
        mock_download.return_value = "./extensions/pub1.ext1.vsix"

        main(["--transfer-all", "--ide", "windsurf"])

        mock_install.assert_called_once_with("./extensions/pub1.ext1.vsix", "windsurf")

    @patch("vsix_to_vscodium.cli.get_vscode_extensions")
    @patch("vsix_to_vscodium.cli.download_extension")
    @patch("vsix_to_vscodium.cli.install_extension")
    def test_main_transfer_all_partial_failure(
        self, mock_install, mock_download, mock_get_extensions
    ):
        """Test when some extensions fail to transfer."""
        mock_get_extensions.return_value = ["pub1.ext1", "pub2.ext2"]
        mock_download.side_effect = [
            "./extensions/pub1.ext1.vsix",
            requests.exceptions.RequestException("API Error"),
        ]

        main(["--transfer-all"])

        # Should still try to install the successful download
        mock_install.assert_called_once_with("./extensions/pub1.ext1.vsix", "codium")

    def test_main_single_extension_custom_ide(self):
        """Test installing single extension with custom IDE."""
        with patch("vsix_to_vscodium.cli.download_extension") as mock_download, patch(
            "vsix_to_vscodium.cli.install_extension"
        ) as mock_install:
            mock_download.return_value = "./extensions/test.vsix"

            main(["--ide", "windsurf", "publisher.extension"])

            mock_download.assert_called_once_with("publisher.extension")
            mock_install.assert_called_once_with("./extensions/test.vsix", "windsurf")

    def test_main_no_args_shows_help(self):
        """Test that running without args shows help."""
        with patch("sys.stdout"), patch("sys.stderr"):
            with self.assertRaises(SystemExit):
                main([])

    @patch('vsix_to_vscodium.cli.download_extension')
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
                "codium",
                "--install-extension",
                vsix_path,
            ],
            check=True,
        )
        # Verify cleanup
        mock_remove.assert_called_once_with(vsix_path)

    @patch('vsix_to_vscodium.cli.download_extension')
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
                "codium",
                "--install-extension",
                vsix_path,
            ],
            check=True,
        )

    @patch("vsix_to_vscodium.cli.download_extension")
    @patch("subprocess.run")
    @patch("os.remove")
    def test_main_installation_error(self, mock_remove, mock_run, mock_download):
        """Test that installation errors are handled correctly."""
        vsix_path = "./extensions/publisher.extension-1.0.0.vsix"
        mock_download.return_value = vsix_path
        mock_run.side_effect = subprocess.CalledProcessError(1, "codium")

        with self.assertRaises(SystemExit) as cm:
            main(["publisher.extension"])

        self.assertEqual(cm.exception.code, 1)
        # Verify cleanup happens even when installation fails
        mock_remove.assert_called_once_with(vsix_path)
