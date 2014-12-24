__author__ = 'RJ'

import spur
import os
import logging

cwd = os.getcwd() + '/'
usr = "lucasrh"
pw = "Grammercy1101grove"

flag = True

while flag:

    print "Starting Servers\n"
    nodes = []
    for i in xrange(11):
        if i+1 < 10: hn = "dogwood0" + str(i+1)
        else: hn = "dogwood" + str(i+1)
        shell = spur.SshShell(hostname=hn,username=usr,password=pw)
        #alias to switch to AnimatClusterSim directory
        process = shell.spawn(["python","ppserver.py"],cwd=cwd,store_pid=True)       #spawn does not, ppserver does not terminate
        nodes.append((shell,process))
        print hn + " connected"

    input = raw_input("\nEnter r to refresh ppservers or q to quit to close all servers: ")

    if input == "r":
        print "Closing servers\n"
        for shell,process in nodes:
            try:
                process.send_signal("SIGTERM")     #terminate all ppservers
            except spur.results.RunProcessError:
                print 'error'
        print "Cleaning up\n"
        for shell,process in nodes:
            try:
                shell.run(["killall","python"])    #just to be sure
            except spur.results.RunProcessError:
                print 'error'
        print "Servers Restarting\n"

    elif input == "q":
        print "Terminating Servers\n"
        for shell,process in nodes:
            try:
                process.send_signal("SIGTERM")     #terminate all ppservers
            except spur.results.RunProcessError:
                pass
        print "Cleaning up\n"
        for shell,process in nodes:
            try:
                shell.run(["killall","python"])    #just to be sure
            except spur.results.RunProcessError:
                pass
        print "Complete!\n"
        flag = False