#!/usr/bin/env python3
"""
Remove all BOM (Byte Order Mark) characters from the consolidated Python file
"""

# Read the file in binary mode to handle BOM characters properly
with open('DROX_AI_CONSOLIDATED.py', 'rb') as f:
    content = f.read()

# Remove BOM characters (U+FEFF)
bom_char = b'\xef\xbb\xbf'  # UTF-8 BOM bytes
content = content.replace(bom_char, b'')

# Write back without BOM
with open('DROX_AI_CONSOLIDATED_FIXED.py', 'wb') as f:
    f.write(content)

print("All BOM characters removed. Fixed file saved as DROX_AI_CONSOLIDATED_FIXED.py")
