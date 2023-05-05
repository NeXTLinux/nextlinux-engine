#!/bin/bash

# Requires findimports from pip
#pip install -y findimports

findimports nextlinux_engine nextlinux_manager twisted | grep -v "nextlinux\|:" | cut -f 1 -d '.' | sort | uniq  > imports
findimports test | grep -v "nextlinux\|:" | cut -f 1 -d '.' | sort | uniq  > test_imports
