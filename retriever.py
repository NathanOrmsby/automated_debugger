from subprocess import check_output
import os


class Retriever:
    """ Class with methods to retrieve and return files and executables from failed workflow """

    def __init__(self, rundir):
        self.rundir = rundir
        self.sublist = None
        self.outlist = None
        self.elist = None
        self.exset = None
        self.sub_sh = None
        self.debug = None

    def read_debug(self):
        """Read generated debug file and return list of file lines"""

        fpath = self.debug

        flines = []
        elines = []
        f = open(fpath, 'r')
        lines = f.readlines()
        for line in lines:
            flines.append(line.strip())
        f.close()
        return flines

    def list_files(self):
        """ Assigns values to self attributes sublist, outlist, elist, and exset used in later methods. """

        flines = self.read_debug()
        sublines = []
        outlines = []
        elines = []
        exlines = []
        for line in flines:
            if "submit" in line:
                sublines.append(line.strip())

            elif "executable" in line:
                exlines.append(line.strip())

            elif "output" in line:
                outlines.append(line.strip())

            elif "error" in line:
                elines.append(line.strip())

        exstring = ''.join(exlines)
        substring = ''.join(sublines)
        outstring = ''.join(outlines)
        estring = ''.join(elines)

        exlist = exstring.split("executable  : ")
        sublist = substring.split("submit file: ")
        outlist = outstring.split("output file: ")
        elist = estring.split("error file: ")

        # First element is blank
        exlist.pop(0)
        sublist.pop(0)
        outlist.pop(0)
        elist.pop(0)

        # We don't want repeated executables
        exset = set(exlist)

        self.sublist = sublist
        self.outlist = outlist
        self.elist = elist
        self.exset = exset

    def called_executables(self):
        """ Searches list of subfiles and assigns dictionary of sh files called by each submit file to self.sub_sh attribute."""

        sub_sh = {}

        for i in range(len(self.sublist)):
            fpath = "./submitdir/work/" + self.sublist[i]

            f = open(fpath, 'r')
            lines = f.readlines()

            for line in lines:
                if "executable = /" in line:
                    tmp = list(line)
                    sub_sh[self.sublist[i]] = ''.join(tmp[13:])

            self.sub_sh = sub_sh

    def display_flist(self, files):
        """ Displays list of files depending on input given"""

        if files == "sub":
            for f in self.sublist:
                print(f)
        elif files == "out":
            for f in self.outlist:
                print(f)
        elif files == "error":
            for f in self.elist:
                print(f)
        elif files == "exe":
            for f in self.exset:
                print(f)
        elif files == "sub_sh":
            for f, e in self.sub_sh:
                print(print("Subfile: {} \nExecutable: {}\n".format(f, e)))
