import plistlib
from pathlib import Path

# Path to a .plist dumped from the Find My app.
PLIST_PATH = Path('namingrecord_decrypted.plist')

# == The variables below are auto-filled from the plist!! ==
with PLIST_PATH.open('rb') as f:
    naming_record = plistlib.load(f)

name = naming_record['name']

if 'emoji' in naming_record:
    emoji = naming_record['emoji']
    print(f'{emoji} {name}')
else:
    print(f'{name}')