#!/usr/bin/env bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

rm decrypted.plist discovery-keys.csv location_history.json

baUUIDarr=(
    <baUUID1>
    <baUUID2>
    ...
)


for i in "${baUUIDarr[@]}"
do

    export baUUID=$i
    echo baUUID=$baUUID

    # get HEXKEY
    export HEXKEY=`security find-generic-password -l "BeaconStore" | grep gena | awk -F' ' '{print $1}' | awk -F'=0x' '{print $NF}'`
    echo HEXKEY=$HEXKEY

    # find record filepath
    # normally stored in RECORD_FILEPATH=~/Library/com.apple.icloud.searchpartyd/<SharedBeacons, OwnedBeacons>/<baUUID>.record
    export RECORD_FILEPATH=`find ~/Library/com.apple.icloud.searchpartyd/ -iname "$baUUID.record"`
    echo RECORD_FILEPATH=$RECORD_FILEPATH

    # decrypt. produces decrypted.plist
    chmod +x $SCRIPT_DIR/src/swift/findmy-decryptor.swift
    $SCRIPT_DIR/src/swift/findmy-decryptor.swift || (echo "findmy-decryptor.swift failed"; return 1)

    # generate keys. takes decrypted.plist, produces discovery-keys.csv
    python3 $SCRIPT_DIR/src/python/findmy-keygeneration.py || (echo "findmy-keygeneration.py failed"; return 1)

    # start anisette docker container
    docker run -d --restart always --name anisette-v3 -p 6969:6969 dadoum/anisette-v3-server

    # get historical locations. takes discovery-keys.csv, produces location_history.json
    # will require icloud login, produces byproduct file account.json
    python3 $SCRIPT_DIR/src/python/findmy-historicallocations.py || (echo "findmy-historicallocations.py failed"; return 1)

    # plots location history and opens map with default browser
    python3 $SCRIPT_DIR/src/python/findmy-plotlocationhistory.py || (echo "findmy-plotlocationhistory.py failed"; return 1)

done

