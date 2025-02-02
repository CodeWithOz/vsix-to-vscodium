# vsix-to-vscodium

A tool to download and install VS Code extensions in VSCodium-based IDEs.

## Why does this package exist?

This package was born out of the creator's experience trying out the [Windsurf IDE](https://codeium.com/windsurf). After discovering that many important extensions were missing, he learned that Windsurf, like other VSCodium-based IDEs, uses a different extensions marketplace due to [Microsoft's licensing restrictions](https://github.com/VSCodium/vscodium/blob/master/docs/index.md#extensions-marketplace).

Rather than manually downloading and installing each extension, he decided to try out Windsurf's AI features by building a package that could copy over VS Code extensions with a single command. That package is `vsix-to-vscodium`.

## Installation

```bash
pip install vsix-to-vscodium
```

## Usage

### Install a single extension

```bash
# Basic usage (defaults to VSCodium)
vsix-to-vscodium publisher.extension-name

# Specify a different IDE
vsix-to-vscodium --ide windsurf publisher.extension-name

# Example: Install Python extension in Windsurf
vsix-to-vscodium --ide windsurf ms-python.python
```

### Transfer all VS Code extensions

If you're switching from VS Code to a VSCodium-based IDE, you can transfer all your installed extensions at once:

```bash
# Transfer all extensions (defaults to VSCodium)
vsix-to-vscodium --transfer-all

# Transfer all extensions to a specific IDE
vsix-to-vscodium --transfer-all --ide windsurf
```

## Features

- Downloads extensions from VS Code Marketplace
- Automatically installs extensions in VSCodium-based IDEs
- Supports multiple VSCodium-based IDEs (e.g., Windsurf)
- Bulk transfer of all installed VS Code extensions
- Supports specific version installation
- Caches downloaded extensions to avoid redundant downloads
- Cleans up downloaded files after installation

## Caveats

- When searching for installed extensions in the Extensions view, you must prepend `@enabled` to your search term to see extensions installed via this tool:

  ![Extensions search showing @enabled requirement](https://github.com/CodeWithOz/vsix-to-vscodium/raw/main/docs/images/enabled-search.png)

## Next Steps/Improvements

- Show failed installs in final message when installation is complete, especially when installing multiple extensions
- Allow updates of extensions that have newer versions of what's installed
- Allow selecting extensions for install instead of just installing everything in VS Code
  - Some extensions actually don't make sense to copy, e.g., GitHub Copilot when running Windsurf
- Don't install disabled extensions
  - Perhaps add a flag that allows user to specify that disabled extensions should also be installed
- Use open-vsx extensions directly when extensions are already available there

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/CodeWithOz/vsix-to-vscodium.git
cd vsix-to-vscodium

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install development dependencies
pip install flit
flit install -s --deps develop
```

Run tests:

```bash
pytest
```

## License

MIT
