# code-to-codium

A tool to download and install VS Code extensions in Codium-based browsers eg Windsurf and Cursor.

## Installation

```bash
pip install code-to-codium
```

## Usage

```bash
# Install an extension
code-to-codium publisher.extension-name

# Example: Install Python extension
code-to-codium ms-python.python
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
git clone https://github.com/CodeWithOz/code-to-codium.git
cd code-to-codium

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
