import argparse
from subprocess import check_output
from time import sleep
import os, sys
from pathlib import Path
# Class imports
sys.path.insert(0, "/home/nathan.ormsby/automated_debugging/")
#print(sys.path)
from manager import Manager
from retriever import Retriever


""" Make sure you run the debug script and pipe it to a file called "debug.txt" that is in the same directory as this script"""

# e.g. ./debug > debug.txt

# This file will output a txt file with a list of sub files that have failed in the workflow.

# Argparser command line arguments
parser = argparse.ArgumentParser()

parser.add_argument("--rundir", help="(REQUIRED) path to run directory")
parser.add_argument("--debug_path", help="Path to debug file, required for usage of file listing options. To create, run the command debug command and pipe the output to a text file. e.g. './debug > debug.txt'")
parser.add_argument("--error_flist", help="List all error output files of failed submit files", action="store_true")
parser.add_argument("--out_flist", help="List all failed submit files output files", action="store_true")
parser.add_argument("--sub_flist", help="List all failed submit files", action="store_true")
parser.add_argument("--exec_list", help="List all referenced executables in failed submit files", action="store_true")
parser.add_argument("--sub_sh_list", help="Prints list of sub files along with executables they access", action="store_true")
parser.add_argument("--brute_force", help="Stops and restarts run after jobs clear out", action="store_true")
parser.add_argument("--cache_rerun", help="Starts a new run in different directory using cache file.", action="store_true")

args = parser.parse_args()


# Category: Simple debugging
# Declare class and write debug text file
r = Retriever(args.rundir)

# file listing methods
if args.sub_flist or args.out_flist or args.error_flist or args.exec_list or args.sub_sh_list:

    if args.debug_path is not None:
        r.debug = args.debug_path
    else:
        print("Debug path must be provided to use file listing options")
        sys.exit()

    r.read_debug()
    r.list_files()
    r.called_executables()
    if args.sub_flist:
        s = "sub"
    elif args.out_flist:
        s = "out"
    elif args.error_flist:
        s = "error"
    elif args.exec_list:
        s = "exe"
    elif args.sub_sh_list:
        s = "sub_sh"
    r.display_flist(s)


# managing workflow
m = Manager(args.rundir)

# stop and start
if args.brute_force:
    m.stop_and_start()

# restart from cache (in progress)
