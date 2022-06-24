import os, sys
from subprocess import check_output
from time import sleep
from pathlib import Path
# Class imports
#sys.path.insert(0, "/home/nathan.ormsby/automated_debugging/")
from stageout import Stageout



class Manager:
    """ Responsible for management of workflow """

    def __init__(self, rundir):
        self.rundir = rundir
        self.cleared = None

    def check_condor_q(self):
        """Checks output of condor_q by creating and reading a text file with its output.

        Assigns boolean to self.cleared that is True if the condor queue is cleared of jobs"""

        os.chdir(self.rundir)
        cleared = False
        cmd1 = "condor_q > condor.txt"
        cmd2 = "rm condor.txt"

        check_output(cmd1, shell=True)
        f = open("condor.txt", 'r')
        lines = f.readlines()
        for line in lines:
            if "Total for query:" and "0 jobs" in line:
                cleared = True

            if "Total for query:" in line:
                print(line)

        f.close()
        check_output(cmd2, shell=True)
        self.cleared = cleared

    def stop_and_start(self):
        """Automatically stops and restarts a run for you, simple brute force hammer approach, default sleep time set
        to 5 min """

        cmd1 = "{}/stop" .format(self.rundir)
        cmd2 = "{}/start" .format(self.rundir)

        print("Stopping run")
        check_output(cmd1, shell=True)

        sleep_time = 30
        print("Waiting {} seconds for jobs to clear out.".format(sleep_time))

        while not self.cleared:
            self.check_condor_q()
            if not self.cleared:
                print("Jobs are still clearing out. Waiting another {} seconds.".format(str(sleep_time)))
            sleep(sleep_time)

        print("Jobs are cleared, restarting run")
        check_output(cmd2, shell=True)
        print("Run has been successfully restarted!")

    def cache_rerun(self, s, c):
        """Starts new run using data from the old run.

        Performs two step cleaning of output.map file utilizing classes Stageout and Copy then passes it as an argument to submit the new workflow to the cluster. """

        # Perform stageout steps
        s.create_dir()
        s.dax_name_check()



