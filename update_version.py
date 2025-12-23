"""
Script to update version.py with current build date
Called automatically by build.bat
"""
from datetime import datetime

VERSION = "1.0.2"
BUILD_DATE = datetime.now().strftime("%Y-%m-%d %H:%M")

version_content = f'''"""
Version information for Run8 Industry Tool
This file is automatically updated during the build process
"""

VERSION = "{VERSION}"
BUILD_DATE = "{BUILD_DATE}"
'''

with open('version.py', 'w', encoding='utf-8') as f:
    f.write(version_content)

print(f"Updated version.py: Version {VERSION}, Build Date {BUILD_DATE}")
