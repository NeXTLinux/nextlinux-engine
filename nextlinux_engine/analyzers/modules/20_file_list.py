#!/usr/bin/env python3

import json
import os
import stat
import sys

import nextlinux_engine.analyzers.utils

analyzer_name = "file_list"

try:
    config = nextlinux_engine.analyzers.utils.init_analyzer_cmdline(
        sys.argv, analyzer_name
    )
except Exception as err:
    print(str(err))
    sys.exit(1)

imgname = config["imgid"]
imgid = config["imgid_full"]
outputdir = config["dirs"]["outputdir"]
unpackdir = config["dirs"]["unpackdir"]

meta = nextlinux_engine.analyzers.utils.get_distro_from_squashtar(
    os.path.join(unpackdir, "squashed.tar"), unpackdir=unpackdir
)
distrodict = nextlinux_engine.analyzers.utils.get_distro_flavor(
    meta["DISTRO"], meta["DISTROVERS"], likedistro=meta["LIKEDISTRO"]
)

simplefiles = {}
outfiles = {}

try:
    allfiles = {}
    fmap = {}
    if os.path.exists(unpackdir + "/nextlinux_allfiles.json"):
        with open(unpackdir + "/nextlinux_allfiles.json", "r") as FH:
            allfiles = json.loads(FH.read())
    else:
        fmap, allfiles = nextlinux_engine.analyzers.utils.get_files_from_squashtar(
            os.path.join(unpackdir, "squashed.tar")
        )
        with open(unpackdir + "/nextlinux_allfiles.json", "w") as OFH:
            OFH.write(json.dumps(allfiles))

    # fileinfo
    for name in list(allfiles.keys()):
        outfiles[name] = json.dumps(allfiles[name])
        simplefiles[name] = oct(stat.S_IMODE(allfiles[name]["mode"]))

except Exception as err:
    import traceback

    traceback.print_exc()
    raise err

if simplefiles:
    ofile = os.path.join(outputdir, "files.all")
    nextlinux_engine.analyzers.utils.write_kvfile_fromdict(ofile, simplefiles)

if outfiles:
    ofile = os.path.join(outputdir, "files.allinfo")
    nextlinux_engine.analyzers.utils.write_kvfile_fromdict(ofile, outfiles)

sys.exit(0)
