# vsix-to-codium

A tool to download and install VS Code extensions in Codium-based browsers eg Windsurf and Cursor.

## Installation

```bash
pip install vsix-to-codium
```

## Usage

```bash
# Install an extension
vsix-to-codium publisher.extension-name

# Example: Install Python extension
vsix-to-codium ms-python.python
```

## Features

- Downloads extensions from VS Code Marketplace
- Automatically installs extensions in Codium
- Supports specific version installation
- Caches downloaded extensions to avoid redundant downloads
- Cleans up downloaded files after installation

## Development

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/yourusername/vsix-to-codium.git
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
