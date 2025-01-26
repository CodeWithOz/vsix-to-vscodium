"""Command-line interface for vsix-to-codium."""

import sys
import subprocess
import requests
import os
import json
from typing import Optional


def download_extension(extension_id: str, specific_version: Optional[str] = None, no_cache: bool = False) -> str:
    """
    Download a VS Code extension from the marketplace.

    Args:
        extension_id: The extension ID in format 'publisher.extension'
        specific_version: Specific version to download. Defaults to None (latest).
        no_cache: Force re-download even if file exists. Defaults to False.

    Returns:
        str: Path to the downloaded .vsix file

    Raises:
        SystemExit: If the extension ID is invalid
        requests.exceptions.RequestException: If there's an error downloading the extension
    """
    try:
        publisher, extension_name = extension_id.split(".", 1)
    except ValueError:
        print("Invalid extension ID format. Use 'publisher.extension'")
        sys.exit(1)

    # Query the marketplace API for extension metadata
    api_url = "https://marketplace.visualstudio.com/_apis/public/gallery/extensionquery"
    payload = {
        "filters": [{"criteria": [{"filterType": 7, "value": extension_id}]}],
        "flags": 914,
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json;api-version=3.0-preview.1",
        "User-Agent": "VSCode Extension Manager/1.0",
    }

    print("Querying Marketplace API...")
    response = requests.post(api_url, headers=headers, json=payload)
    response.raise_for_status()

    try:
        extension_data = response.json()
        if specific_version:
            version = specific_version
        else:
            version = extension_data["results"][0]["extensions"][0]["versions"][0]["version"]
    except (KeyError, IndexError) as e:
        print(f"Failed to get extension metadata: {e}")
        sys.exit(1)

    # Create extensions directory if it doesn't exist
    os.makedirs("extensions", exist_ok=True)
    file_path = f"./extensions/{extension_id}-{version}.vsix"

    # Check if file already exists
    if not no_cache and os.path.exists(file_path):
        print(f"File {file_path} already exists.")
        print("Use no_cache=True to force re-download.")
        return file_path

    # Download the extension
    download_url = f"https://{publisher}.gallery.vsassets.io/_apis/public/gallery/publisher/{publisher}/extension/{extension_name}/{version}/assetbyname/Microsoft.VisualStudio.Services.VSIXPackage"

    print(f"Downloading version {version}...")
    download_response = requests.get(download_url)
    download_response.raise_for_status()

    with open(file_path, "wb") as f:
        f.write(download_response.content)

    print("=" * 50)
    print(f"Successfully downloaded to: {file_path}")
    print("=" * 50)

    return file_path


def main(args: Optional[list[str]] = None) -> None:
    """
    Main entry point for the CLI.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])
    """
    if args is None:
        args = sys.argv[1:]

    if not args:
        print("Please provide the extension ID as an argument")
        print("Example: vsix-to-codium publisher.extension-name")
        sys.exit(1)

    extension_id = args[0]

    try:
        # Download the .vsix file
        print(f"Downloading extension: {extension_id}")
        vsix_path = download_extension(extension_id)
        print(f"Downloaded to: {vsix_path}")

        # Install the extension in VS Codium
        print("Installing extension...")
        subprocess.run(['windsurf', '--install-extension', vsix_path], check=True)
        print("Extension installed successfully!")

        # Clean up the .vsix file
        try:
            os.remove(vsix_path)
            print(f"Cleaned up {vsix_path}")
        except OSError as e:
            print(f"Warning: Could not remove {vsix_path}: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Failed to download extension: {e}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install extension: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
