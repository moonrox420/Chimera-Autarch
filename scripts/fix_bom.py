#!/usr/bin/env python3
"""
Fix BOM (Byte Order Mark) character in consolidated Python file
"""

with open('DROX_AI_CONSOLIDATED.py', 'r', encoding='utf-8-sig') as f:
    content = f.read()

with open('DROX_AI_CONSOLIDATED_FIXED.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("BOM character removed. Fixed file saved as DROX_AI_CONSOLIDATED_FIXED.py")
