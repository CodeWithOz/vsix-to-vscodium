#!/usr/bin/env python3
import sys
import subprocess
import requests
import os

def download_extension(extension_id):
    # VS Code Marketplace API URL
    base_url = "https://marketplace.visualstudio.com/_apis/public/gallery/publishers"
    
    # Parse publisher and extension name from the extension ID
    publisher, extension_name = extension_id.split(".", 1)
    
    # Create the download URL
    download_url = f"{base_url}/{publisher}/vsextensions/{extension_name}/latest/vspackage"
    
    # Create extensions directory if it doesn't exist
    os.makedirs("extensions", exist_ok=True)
    
    # Download the extension
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/octet-stream"
    }
    response = requests.get(download_url, headers=headers)
    response.raise_for_status()
    
    # Save the extension
    vsix_path = f"./extensions/{extension_id}.vsix"
    with open(vsix_path, "wb") as f:
        f.write(response.content)
    
    return vsix_path

def main():
    # Get the extension ID from command line argument
    if len(sys.argv) != 2:
        print("Please provide the extension ID as an argument")
        print("Example: ./main.py publisher.extension-name")
        sys.exit(1)
    
    extension_id = sys.argv[1]
    
    try:
        # Download the .vsix file
        print(f"Downloading extension: {extension_id}")
        vsix_path = download_extension(extension_id)
        print(f"Downloaded to: {vsix_path}")
        
        # Install the extension in VS Codium
        print("Installing extension...")
        subprocess.run(['windsurf', '--install-extension', vsix_path], check=True)
        print("Extension installed successfully!")
        
    except requests.exceptions.RequestException as e:
        print(f"Failed to download extension: {e}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install extension: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
