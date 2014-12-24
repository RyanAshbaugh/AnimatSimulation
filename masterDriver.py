__author__ = 'RJ'

import clusterDriver as cd
import pp
import time
import spur
import sys
import os

import getopt
import EvoDriver
import logging
import SimParam

class MasterDriver():

    #Driver for Master Node
    def __init__(self):
        self.sP = SimParam.SimParam()

        logger = logging.getLogger('pp')
        logging.basicConfig(filename='log.txt')
        self.runTime = 1000
        self.writeInt = 100
        tsTime = time.clock()
        self.runEvo = False
        #self.cwd = os.getcwd() + '/'
        self.doWrite = True
        self.usr = "lucasrh"        #Username for SSH connections
        self.pw = "Grammercy1101grove" #Password for SSH connections
        self.nodeShells = []        #Holder for ssh shells for each node in cluster, tuple of (shell,process) objects
        self.nodeP2Ps = [("10.2.1." + str(i) + ":60000") for i in xrange(2,12)]     #P2P address for each node on cluste
        self.nodeNum = 2            #Number of nodes needed. 1 Animat per node
        self.simNum = 3             #Number of simulations to run in parallel on each node, different worlds
        self.settingsFile = -1      #Holder for settingsFile
        self.animParams = [["Wheel Animat",(1,0),10,[80,.02,.25,-65,2],[320,.02,.2,-65,8]] for i in xrange(self.nodeNum)]
        #run parseOptions after all user changable vars are initialized to avoid errors
        self.parseOptions()         #Change above values if specified by command line options
        self.sP.setWorld(1,15,20)
        #self.worldParams = [[1,15,20] for i in xrange(self.simNum)]
        #for running simulations without evolutionary algorithm
        print "Node addresses to connect to:"
        print self.nodeP2Ps[0:8]
        if not self.runEvo:
            self.nodeDrivers = [cd.ClusterDriver(i+1,self.worldParams,self.animParams[i],self.writeInt,writeFiles=self.doWrite,time=self.runTime) for i in xrange(self.nodeNum)]    #driver objects for each node
            #self.initializeNodes(self.nodeNum,self.nodeShells)
            self.jobServer = pp.Server(ncpus=0,ppservers=tuple(self.nodeP2Ps[0:8]))     #connect to each node
            self.jobList =[self.jobServer.submit(node.startNode,modules=("pp",)) for node in self.nodeDrivers]
            sTime = time.clock()
            for job in self.jobList:
                print "job about to execute"
                job()       #execute job
            eTime = time.clock()
            print "Run Time: " + str(eTime-sTime)
            print"masterDriver stats"
            self.jobServer.print_stats()
            self.jobServer.destroy()
        #for running simulation with evolutionary algorithm
        else:
            evo = EvoDriver.EvoDriver()

        teTime = time.clock()
        print "Total Run Time: " + str(teTime-tsTime)


        #for shell,process in self.nodeShells: process.send_signal("SIGTERM")     #terminate all ppservers



    ## Read in Options from Command Line ##
    ##    -h : Display help information
    ##    -a : How many different animats to run  (1 animat per node)
    ##    -w : How many worlds to run animat in (i.e. how many simulations on each node)
    ##    -u : Username for SSH session
    ##    -p : Password for SSH session
    ##    -f : File to read settings from
    ##    -e : Run with evolutionary algorithm
    ##    -p : Print true or false

    def parseOptions(self):
        #Check for arguments
        options = sys.argv[1:]     #all command line arguments
        try:
            opts,args = getopt.getopt(options,"eha:w:u:p:f:p:t:i:")
        except getopt.GetoptError:
            print "run -h to display help information"
        for opt, arg in opts:
            if opt == '-h': self.printHelp()
            elif opt == '-a':
                self.nodeNum = int(arg)
                self.animParams = [["Wheel Animat",(1,0),10,[80,.02,.25,-65,2],[320,.02,.2,-65,8]] for i in xrange(self.nodeNum)]
            elif opt == '-w': self.simNum = int(arg)
            elif opt == '-u': self.usr = arg
            elif opt == '-p': self.pw = arg
            elif opt == '-f': self.readSettings(arg)
            elif opt == '-e': self.runEvo = True
            elif opt == '-p': self.doWrite = bool(arg)
            elif opt == '-t': self.runTime = int(arg)
            elif opt == '-i': self.writeInt = int(arg)

    def inializeEvo(self):
        pass

    def readSettings(self,fileName):
        f = open(fileName, 'r')
        self.nodeNum = int(f.readline())
        self.simNum = int(f.readline())
        temp = []
        for i in xrange(self.simNum):
            animNum = int(f.readline())
            foodNum = int(f.readline())
            size = int(f.readline())
            temp.append([animNum,foodNum,size])
        self.worldParams = temp
        temp = []
        for i in xrange(self.nodeNum):
            type = f.readline()
            origin = f.readline().split()
            energy = int(f.readline())
            inhib = f.readline().split(' ')
            excit = f.readline().split(' ')
            inhib[0] = int(inhib[0])
            for i,val in inhib[1:]: inhib[i] = float(val)
            excit[0] = int(excit[0])
            for i,val in excit[1:]: excit[i] = float(val)
            temp.append([type,(int(origin[0]),int(origin[1])),energy,inhib,excit])
        self.animParams = temp

    def printHelp(self):
        print "\nUsage:"
        print "     masterDriver.py <command> [options]\n"
        print "\nCommands: "
        print "     COMMANDS NOT YET IMPLEMENTED\n"
        print "\nOptions: "
        print "     -a         Number of Animats to simulate. Each runs on its own node. "
        print "     -w         Number of worlds to run each Animat in."
        print "     -u         Username for dogwood cluster."
        print "     -p         Password for dogwood cluster."
        print "     -h         Displays help information."
        print "     -f         File to read settings from."
        print "     -e         Run with Evolutionary Algorithm."
        print "     -t         Number of simulated milliseconds."
        print "     -i         Write interval"

        sys.exit()

    def initializeNodes(self,num,nodes):
        print "Connecting to Nodes"
        #create shell for each connection
        shell, process = -1,-1        #holder for shell,process tuple
        for i in xrange(num):
            print i
            if i+1 < 10: hn = "dogwood0" + str(i+1)
            else: hn = "dogwood" + str(i+1)
            shell = spur.SshShell(hostname=hn,username=self.usr,password=self.pw)
                 #alias to switch to AnimatClusterSim directory
            process = shell.spawn(["python","ppserver.py"],cwd=self.cwd,store_pid=True)       #spawn does not, ppserver does not terminate
            nodes.append((shell,process))

mD = MasterDriver()