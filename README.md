# vsix-to-vscodium

A tool to download and install VS Code extensions in VSCodium-based IDEs.

## Installation

```bash
pip install vsix-to-vscodium
```

## Usage

### Install a single extension

```bash
# Basic usage (defaults to windsurf)
vsix-to-vscodium publisher.extension-name

# Specify a different IDE
vsix-to-vscodium --ide cursor publisher.extension-name

# Example: Install Python extension in Cursor
vsix-to-vscodium --ide cursor ms-python.python
```

### Transfer all VS Code extensions

If you're switching from VS Code to a VSCodium-based IDE, you can transfer all your installed extensions at once:

```bash
# Transfer all extensions (defaults to windsurf)
vsix-to-vscodium --transfer-all

# Transfer all extensions to a specific IDE
vsix-to-vscodium --transfer-all --ide cursor
```

## Features

- Downloads extensions from VS Code Marketplace
- Automatically installs extensions in VSCodium-based IDEs
- Supports multiple VSCodium-based IDEs (e.g., Windsurf, Cursor)
- Bulk transfer of all installed VS Code extensions
- Supports specific version installation
- Caches downloaded extensions to avoid redundant downloads
- Cleans up downloaded files after installation

## Caveats

- When searching for installed extensions in the Extensions view, you must prepend `@enabled` to your search term to see extensions installed via this tool:

  ![Extensions search showing @enabled requirement](https://github.com/CodeWithOz/vsix-to-vscodium/raw/main/docs/images/enabled-search.png)

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
