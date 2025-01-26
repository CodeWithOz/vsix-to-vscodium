# vsix-to-codium

A tool to download and install VS Code extensions in Codium-based IDEs.

## Installation

```bash
pip install vsix-to-codium
```

## Usage

### Install a single extension

```bash
# Basic usage (defaults to windsurf)
vsix-to-codium publisher.extension-name

# Specify a different IDE
vsix-to-codium --ide cursor publisher.extension-name

# Example: Install Python extension in Cursor
vsix-to-codium --ide cursor ms-python.python
```

### Transfer all VS Code extensions

If you're switching from VS Code to a Codium-based IDE, you can transfer all your installed extensions at once:

```bash
# Transfer all extensions (defaults to windsurf)
vsix-to-codium --transfer-all

# Transfer all extensions to a specific IDE
vsix-to-codium --transfer-all --ide cursor
```

## Features

- Downloads extensions from VS Code Marketplace
- Automatically installs extensions in Codium-based IDEs
- Supports multiple Codium-based IDEs (e.g., Windsurf, Cursor)
- Bulk transfer of all installed VS Code extensions
- Supports specific version installation
- Caches downloaded extensions to avoid redundant downloads
- Cleans up downloaded files after installation

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/CodeWithOz/vsix-to-codium.git
cd vsix-to-codium

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
