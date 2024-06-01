#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
BAUUID_RECORD_PATH=~/Library/com.apple.icloud.searchpartyd/

baUUIDarr=(
    # <baUUID1>
    # <baUUID2>
    # ...
)

echo baUUIDarr=$baUUIDarr

# if no values, get baUUIDs by searching BAUUID_RECORD_PATH for '{UUID}.record' files
if [[ -z $baUUIDarr ]]; then
    echo "No values in baUUIDarr. Finding all baUUIDs from $BAUUID_RECORD_PATH"
    # baUUIDarr=`find $BAUUID_RECORD_PATH -iname "*-*-*-*-*.record" | awk -F'/' '{print $NF}' | awk -F'.record' '{print $1}'`

    baUUIDarr=(
        $( find $BAUUID_RECORD_PATH -iname "*-*-*-*-*.record" | awk -F'/' '{print $NF}' | awk -F'.record' '{print $1}' )
    )

    echo baUUIDarr=$baUUIDarr
fi


for i in "${baUUIDarr[@]}"; do
    export baUUID=$i
    echo baUUID=$baUUID

    # remove old files
    rm decrypted.plist namingrecord_decrypted.plist discovery-keys.csv location_history.json

    # get HEXKEY from BeaconStore
    # "-g  Display the password for the item found"
    # "-w  Display only the password on stdout"
    export HEXKEY=`security find-generic-password -l "BeaconStore" -g -w`
    echo HEXKEY=$HEXKEY

    # find record filepath
    # normally stored in RECORD_FILEPATH=$BAUUID_RECORD_PATH/<SharedBeacons, OwnedBeacons>/<baUUID>.record
    export RECORD_FILEPATH=`find $BAUUID_RECORD_PATH -iname "$baUUID.record"`
    echo RECORD_FILEPATH=$RECORD_FILEPATH

    export NAMINGRECORD_FILEPATH=`find $BAUUID_RECORD_PATH/BeaconNamingRecord/$baUUID -iname "*-*-*-*-*.record"`
    echo NAMINGRECORD_FILEPATH=$NAMINGRECORD_FILEPATH

    # decrypt. produces decrypted.plist and namingrecord_decrypted.plist
    chmod +x $SCRIPT_DIR/src/swift/findmy-decryptor.swift
    $SCRIPT_DIR/src/swift/findmy-decryptor.swift || { echo "ERROR: findmy-decryptor.swift failed"; continue; }

    # get device name from namingrecord_decrypted.plist and set in DEVICE_NAME
    unset DEVICE_NAME
    export DEVICE_NAME=`python3 $SCRIPT_DIR/src/python/findmy-plistnamingrecord-to-name.py`
    echo DEVICE_NAME=$DEVICE_NAME

    # generate keys. takes decrypted.plist, produces discovery-keys.csv
    python3 $SCRIPT_DIR/src/python/findmy-keygeneration.py || { echo "ERROR: findmy-keygeneration.py failed"; continue; }

    # start anisette docker container
    docker run -d --restart always --name anisette-v3 -p 6969:6969 dadoum/anisette-v3-server

    # get historical locations. takes discovery-keys.csv, produces location_history.json
    # will require icloud login, produces byproduct file account.json
    python3 $SCRIPT_DIR/src/python/findmy-historicallocations.py || { echo "ERROR: findmy-historicallocations.py failed"; continue; }

    # plots location history and opens map with default browser
    python3 $SCRIPT_DIR/src/python/findmy-plotlocationhistory.py || { echo "ERROR: findmy-plotlocationhistory.py failed"; continue; }

done
