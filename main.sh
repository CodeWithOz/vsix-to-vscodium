#!/bin/bash

# Get the extension ID from the command line argument
extension_id=$1

# Download the .vsix file using offvsix
offvsix $extension_id

# Install the extension in VS Codium
windsurf --install-extension ./extensions/$extension_id.vsix