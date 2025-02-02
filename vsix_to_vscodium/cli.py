"""Command-line interface for vsix-to-vscodium."""

import sys
import subprocess
import requests
import os
import json
import argparse
from typing import Optional, List


def get_vscode_extensions() -> List[str]:
    """
    Get a list of installed VS Code extensions.

    Returns:
        List[str]: List of extension IDs in the format 'publisher.extension'

    Raises:
        subprocess.CalledProcessError: If code command fails
        FileNotFoundError: If VS Code is not installed
    """
    try:
        result = subprocess.run(
            ["code", "--list-extensions"], check=True, capture_output=True, text=True
        )
        return result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Error getting VS Code extensions: {e}")
        raise
    except FileNotFoundError:
        print(
            "VS Code command 'code' not found. Is VS Code installed and in your PATH?"
        )
        raise


def download_extension(
    extension_id: str, specific_version: Optional[str] = None, no_cache: bool = False
) -> str:
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
        "User-Agent": "VSCodium Extension Manager/1.0",
    }

    print(f"Querying Marketplace API for {extension_id}...")
    response = requests.post(api_url, headers=headers, json=payload)
    response.raise_for_status()

    try:
        extension_data = response.json()
        if specific_version:
            version = specific_version
        else:
            version = extension_data["results"][0]["extensions"][0]["versions"][0][
                "version"
            ]
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


def install_extension(vsix_path: str, ide_name: str) -> None:
    """
    Install a .vsix extension in the specified IDE.

    Args:
        vsix_path: Path to the .vsix file
        ide_name: Name of the IDE executable (e.g., 'windsurf')

    Raises:
        subprocess.CalledProcessError: If installation fails
    """
    try:
        print(f"Installing extension using {ide_name}...")
        subprocess.run([ide_name, "--install-extension", vsix_path], check=True)
        print("Extension installed successfully!")
    finally:
        # Clean up the .vsix file regardless of installation success
        try:
            os.remove(vsix_path)
            print(f"Cleaned up {vsix_path}")
        except OSError as e:
            print(f"Warning: Could not remove {vsix_path}: {e}")


def main(args: Optional[list[str]] = None) -> None:
    """
    Main entry point for the CLI.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])
    """
    parser = argparse.ArgumentParser(
        description="Download and install VS Code extensions in VSCodium-based IDEs"
    )
    parser.add_argument(
        "--ide",
        default="codium",
        help="Name of the VSCodium-based IDE executable (default: codium)",
    )
    parser.add_argument(
        "--transfer-all",
        action="store_true",
        help="Transfer all extensions from VS Code installation",
    )
    parser.add_argument(
        "extension_id",
        nargs="?",
        help="Extension ID in format publisher.extension-name",
    )

    args = parser.parse_args(args)

    if args.transfer_all:
        try:
            extensions = get_vscode_extensions()
            print(f"Found {len(extensions)} extensions installed in VS Code")
            for ext_id in extensions:
                try:
                    print(f"\nProcessing {ext_id}...")
                    vsix_path = download_extension(ext_id)
                    install_extension(vsix_path, args.ide)
                except (
                    requests.exceptions.RequestException,
                    subprocess.CalledProcessError,
                ) as e:
                    print(f"Failed to process {ext_id}: {e}")
                    print("Continuing with next extension...")
            print("\nFinished processing all extensions")
        except (subprocess.CalledProcessError, FileNotFoundError):
            sys.exit(1)
    else:
        if not args.extension_id:
            parser.print_help()
            print("\nPlease provide an extension ID or use --transfer-all")
            sys.exit(1)

        try:
            vsix_path = download_extension(args.extension_id)
            install_extension(vsix_path, args.ide)
        except requests.exceptions.RequestException as e:
            print(f"Failed to download extension: {e}")
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Failed to install extension: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
