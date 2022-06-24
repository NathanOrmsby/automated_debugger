import os, sys
from subprocess import check_output


class Stageout:
    """ Part of the two stage process of cleaning the output.map file. Used in the cache_rerun method of the manager
    class."""

    def __init__(self, rundir, new_path=False):
        self.rundir = rundir
        self.path = new_path
        self.daxes = False
        self.map = None

    def create_dir(self):
        """ Creates new run directory given new path. If new path not given, adds _cache_rerun to rundir and
        puts in parent directory.

        Copies over the output.map file from the rundir """

        if self.path:
            os.mkdir(self.path)
        else:
            name = str(self.rundir.split("/")[-1]) + "_cache_rerun"
            ppath = '/'.join(self.rundir.split("/")[:-1])
            self.path = "{}/{}" .format(ppath, name)
            os.mkdir(self.path)

        cmd = "cd {} && cp {}/output.map .".format(self.path, self.rundir)
        check_output(cmd, shell=True)
        self.map = "{}/output.map" .format(self.path)

    def dax_name_check(self):
        """ Retrieves names of dax files in workflow. Built to handle case of multiple daxes.

        Checks if any directories in local-site-scratch/work match the dax names. If not, remove the daxes.

        If case where no dax names match, then set self.no_dax to True. (look in work dir for files)"""

        l = os.listdir(self.rundir)
        subdirs = [f for f in l if os.path.isdir("{}/{}" .format(self.rundir, f))]

        multiple = False
        for i in subdirs:
            if i == "daxes":
                multiple = True
        if multiple:
            dax_files = [f for f in os.listdir("{}/daxes" .format(self.rundir)) if ".dax" in f]
        else:
            dax_files = [f for f in os.listdir(self.rundir) if ".dax" in f]

        # Remove .dax from dax_files
        names = [''.join(i[:-4]) for i in dax_files]
        wdirs = os.listdir(self.rundir + "/local-site-scratch/work")

        daxes = []
        for i in names:
            for j in wdirs:
                if i == j:
                    daxes.append(i)

        if len(daxes) > 1:
            self.daxes = daxes
        else:
            print("No working directories matching dax names in local-site-scratch.")
            print("Will need to just check the work dir")

    def edit_map(self):
        """ Uses information from dax_name_check to search working directories for files. If the files in the working
        directories are in the output.map file, that means we need to edit the output.map file to point toward the
        working directory instead of whatever empty path it is currently pointing to.

        Files in working directory are incomplete jobs, the path in output.map points to where the job would deposit
        if it completed. If restarting from cache, it is important to fix the paths of incomplete jobs"""

        wdir = "{}/local-site-scratch/work".format(self.rundir)

        # No working directories. Just loop through wdir
        if not self.daxes:
            f = open(self.map, 'r')
            lines = f.readlines()
            print("Line length: {}" .format(len(lines)))
            f.close()

            for i in range(len(lines)):
                cols = lines[i].strip().split(" ")
                fpath = "{}/{}".format(wdir, cols[0])
                if os.path.exists(fpath):
                    cols[1] = "{}/{}".format(wdir, cols[0])
                    lines[i] = ' '.join(cols) + '\n'

        else:
            # 1 or more working directories. Loop through all of them and edit relevant lines for each dir.

            f = open(self.map, 'r')
            lines = f.readlines()
            f.close()

            for dax in self.daxes:
                fpath = "{}/{}".format(wdir, dax)

                for i in range(len(lines)):
                    cols = lines[i].strip().split(" ")
                    if os.path.exists("{}/{}".format(fpath, cols[0])):
                        cols[1] = "{}/{}".format(fpath, cols[0])
                        lines[i] = ' '.join(cols) + "\n"

        # Write changes to output.map
        print("after editing. Line length: {}" .format(len(lines)))
        f = open("{}/stageout_test.map".format(self.path), 'w')
        for line in lines:
            f.write(line)
        f.close()

    def checker(self):
        """ Checks filesize of paths in edited map file. Removes paths that lead to empty files.

        Writes new file with only desired lines, fastest approach. """

        infile = "{}/stageout_test.map".format(self.path)
        outfile = "{}/cleaning_test.map".format(self.path)

        ind = []
        with open(infile, 'r') as f_in:
            with open(outfile, 'w') as f_out:
                for line in f_in:
                    cols = line.strip().split(' ')
                    if not os.path.getsize(cols[1]) == 0:
                        f_out.write(' '.join(cols[:-1]))
                    else:
                        ind.append(line)
                f_out.close()
            f_in.close()

        f = open("{}/files_with_no_size.txt".format(self.path), 'w')
        for i in ind:
            f.write(i + '\n')
        f.close()
