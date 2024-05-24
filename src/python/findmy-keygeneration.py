"""
Example showing how to retrieve the primary key of your own AirTag, or any other FindMy-accessory.

This key can be used to retrieve the device's location for a single day.
"""
import json
import plistlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from findmy.keys import KeyType
from pprint import pprint

from findmy import FindMyAccessory

# Path to a .plist dumped from the Find My app.
PLIST_PATH = Path("decrypted.plist")

# == The variables below are auto-filled from the plist!! ==
with PLIST_PATH.open("rb") as f:
    device_data = plistlib.load(f)

pprint(device_data)

# PRIVATE master key. 28 (?) bytes.
MASTER_KEY = device_data["privateKey"]["key"]["data"][-28:]

# "Primary" shared secret. 32 bytes.
if 'sharedSecret' in device_data:
    SKN = device_data["sharedSecret"]["key"]["data"]
elif 'peerTrustSharedSecret' in device_data:
    SKN = device_data["peerTrustSharedSecret"]["key"]["data"]

# "Secondary" shared secret. 32 bytes.
# This doesn't apply in case of MacBook, but is used for AirTags and other accessories.
if 'secureLocationsSharedSecret' in device_data:
    SKS = device_data["secureLocationsSharedSecret"]["key"]["data"]
if 'secondarySharedSecret' in device_data:
    SKS = device_data["secondarySharedSecret"]["key"]["data"]
else:
    SKS = SKN


def main() -> None:
    paired_at = device_data["pairingDate"].replace(tzinfo=timezone.utc)
    airtag = FindMyAccessory(MASTER_KEY, SKN, SKS, paired_at)

    # Generate keys for 0.5 days ahead and 15 days behind
    previous_days = 15
    future_days = 0.5
    now = datetime.now(tz=timezone.utc) + timedelta(days=future_days)
    previous_days_ago = datetime.now(tz=timezone.utc) + timedelta(days=-previous_days)
    lookup_time = previous_days_ago.replace(
        minute=previous_days_ago.minute // 15 * 15,
        second=0,
        microsecond=0,
    ) + timedelta(minutes=15)

    mycsv = open('discovery-keys.csv', 'w')

    while lookup_time < now:
        keys = airtag.keys_at(lookup_time)
        for key in keys:
            if key.key_type == KeyType.PRIMARY:
                mycsv.write(f'{lookup_time};{key.adv_key_b64};{key.private_key_b64};{key.key_type};{key.hashed_adv_key_b64}\n')

        lookup_time += timedelta(minutes=15)

if __name__ == "__main__":
    main()