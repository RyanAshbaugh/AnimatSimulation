__author__ = 'RJ'

"""
Main driver file for evolutionary algorithm (cluster version)

Essentially revamped startServers.py to execute evo alg as well as ssh connections in order to easily kill rouge
python processes if things break

"""

__author__ = 'RJ'

import spur
import os
import EvoDriver
import logging

class EvolutionaryAlgorithm:

    def __init__(self):
        self.cwd = os.getcwd() + '/'
        self.usr = "lucasrh"
        self.pw = "Grammercy1101grove"
        self.hosts = ["dogwood0"+str(i+1) if i+1 < 10 else "dogwood"+str(i) for i in xrange(11)]
        self.nodes = []

        self.startServers()
        try:
            EvoDriver.EvoDriver()
        except Exception as e:
            print "Error encountered in EvoDriver.py"
            print e.strerror()
        self.closeServers()

    def startServers(self):
        print "Starting Servers\n"
        for hn in self.hosts:
            shell = spur.SshShell(hostname=hn,username=self.usr,password=self.pw)
            process = shell.spawn(["python","ppserver.py"],cwd=self.cwd,store_pid=True)#store pid in order to close later
            self.nodes.append((shell,process))
            print hn + " connected"

    def closeServers(self):
        print "Terminating Servers\n"
        for shell,process in self.nodes:
            try:
                process.send_signal("SIGTERM")     #terminate process
            except spur.results.RunProcessError:
                pass                               #means ppserver self terminated for some reason
        self.cleanUp()                             #kill any remaining python processes
        for shell,process in self.nodes: shell.run(["logout"]) #close ssh session
        print "Complete!\n"

    def cleanUp(self):
        print "Cleaning up\n"
        for shell,process in self.nodes:
            try:
                shell.run(["killall","python"])    #kill any rouge python processes
            except spur.results.RunProcessError:
                pass                               #means that no processes were killed
