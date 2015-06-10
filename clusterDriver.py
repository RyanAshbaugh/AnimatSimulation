

__author__ = 'RJ'
import numpy as np
from SimulationEngine import SimulationEngine
import time
import pp
import clusterSimEngine
import SimParam
import random


class ClusterDriver(): # class to run single sims could eliminate this class ?

    def __init__(self,id,parameters,animatParams,writeInt,writeFiles=True,time=1000):
        self.writeInt = writeInt
        self.id = id
        self.simulations = []
        self.results = []
        self.animatParams = [animatParams]
        for i,param in enumerate(parameters):
            self.simulations.append(Simulation(self.id,i+1,param,self.animatParams,time,writeInterval=self.writeInt,writeFiles=writeFiles))

    def startNode(self):
        jobServer = pp.Server()
        jobs = []
        for sim in self.simulations:
            jobs.append(jobServer.submit(sim.startSimulation,args=(["Energy","FoodDist"],)))
        for job in jobs:
            self.results.append(job())
        print "finished"
        print "cluster stats"
        jobServer.print_stats()
        jobServer.destroy()

## Class for cluster Driver when running evolutionary algorithm
class EvoClusterDriver():

    def __init__(self,id,simParams,metrics):

        ## Other variables
        self.id = id       #used for generating animat ids
        self.sims = []     #holder for all simulation objects
        self.results = []  #holder for results of
        self.metrics = metrics   #list of metrics to track
        self.simParams = simParams  #list of simParam objects for each simulation
        self.initializeSims() # creates simulation objects

    def initializeSims(self): # creates simulation objects
        for i,sP in enumerate(self.simParams):
            self.sims.append(Simulation(self.id,i,sP,60000,writeInterval=25,evo=True))

    def startNode(self): # runs on a local node and sets up PP servers on each CPU
        print "Node " + str(self.id) + " starting"
        js = pp.Server()    # create local server for SMP execution; detects number of CPUs on node
        jobs = [js.submit(sim.startSimulation,args=(self.metrics,),modules=("clusterDriver","SimParam")) for sim in self.sims] #submit all jobs to server
        #NOTE in below, callback in Simulation object should fill results, not the function call
        for job in jobs: self.results.append(job())   #execute all jobs; stores results; could use call-back object; this
        js.wait() # until all jobs have finished ... see documentation
        print "Node " + str(self.id) + " finished"
        #js.print_stats()
        js.destroy()
        return self.results


# Simulation object
class Simulation():

    def __init__(self,clusterId,simId,simParam,runTime,writeInterval=25,evo=False,writeFiles=True): # runTime in virtual millisec
        self.writeFiles = writeFiles
        self.evo = evo # may not be used much
        self.simEngine = clusterSimEngine.clusterSimEngine()
        self.sP = simParam
        self.runTime = runTime                  # how many "cycles" simEngine will run (time = ms?)
        self.writeInterval = writeInterval      # how often simEngine will save state to buffer
        self.logFile = 0                        # logfile for state data
        self.lastLogged = -1                    # keeps track of last state written to file
        self.simHistory = []
        self.id = simId # simulation ID
        self.clusterId = clusterId # ID of node this set of sims is running on


    def startSimulation(self,metrics):
        if (not self.evo) : self.printStartupInfo() # for debugging 
        results = []
        for id in xrange(1,self.sP.getWorldNum()+1): # running several simulated worlds for this animat
            self.sP.worldToRun = id
            #set up simEngine
            self.simEngine.setWriteInterval(self.writeInterval)
            #print "Sim " + str(self.id) + " starting"
            completed = self.simEngine.initializeEngine(self.sP,self.runTime) # initialize & run; pass world info and animat info to simEngine
            self.simHistory = self.simEngine.getResults() 
            results.append(self.filterResults(metrics)) # can change which metrics are selected ... may be simplified?

        return [self.sP.getID(1),self.avgResults(results)] # match ID of animat parameters with results


    def avgResults(self,results): # average results from each world
        newR = {} # dictionary to store results
        for result in results:
            for metric,val in result.iteritems():
                try: newR[metric] = newR[metric] + val
                except KeyError: newR[metric] = val # to set first entry
        for metric,val in newR.iteritems():newR[metric] = newR[metric]/float(len(results))
        return newR

    #results are scores out of 1000
    def filterResults(self,metrics): # calls computation of metrics
        temp = {}        #dictionary of results
        if "Energy" in metrics: temp["Energy"] = self.getNrg()
        if "FindsFood" in metrics: temp["FindsFood"] = self.findsFood()
        if "TotalMove" in metrics: temp["TotalMove"] = self.totalMove()
        if "FoodsEaten" in metrics: temp["FoodsEaten"] = self.foodsEaten()
        if "NetworkDensity" in metrics: temp["NetworkDensity"] = self.networkDensity()
        if "FiringRate" in metrics: temp["FiringRate"] = self.firingRate()
        return temp

    #returns number of foods eaten by animat
    def foodsEaten(self):
        return len(self.simHistory[-1][1].getFood()) - len(np.nonzero(self.simHistory[-1][1].getFood())[0])

    #returns list of tuples of (time,energy)
    def getNrg(self):
        nrgs = [s.getEnergy() for t,s in self.simHistory]
        return np.average(nrgs)   #returns average energy of animat

    #calculates how often animat moves toward food
    #score incr/decr by distance traveled to food/away from food
    def findsFood(self):
        score = 0.0
        initNrg = self.simHistory[0][1].getEnergy()       #get initial energy from first state
        prevDist = self.minFoodDist(self.simHistory[0][1])#find initial distance
        for t,s in self.simHistory[1:]: # coordinates of motion
            if s.getEnergy() < (.5*initNrg):
                newDist = self.minFoodDist(s)
                if newDist < prevDist: score += np.abs(prevDist-newDist)
                else: score -= np.abs(prevDist-newDist)
                prevDist = newDist
        return score

    #finds distance to closest food
    def minFoodDist(self,s):
        foodLocs = self.simEngine.getFoodLocs()              #get food locations
        pos = s.getPos()
        dists = []
        x1,y1 = pos
        for loc in foodLocs:
            x2,y2 = loc
            dists.append(np.sqrt(np.square(x2-x1)+np.square(y2-y1)))
        return np.min(dists)

    #returns average movement
    def totalMove(self):
        prevDist = self.simHistory[0][1].getPos()
        dists = []
        for t,s in self.simHistory[1:]:
            x1,y1 = prevDist
            x2,y2 = s.getPos()
            dists.append(np.sqrt(np.square(x2-x1)+np.square(y2-y1)))
            prevDist = x2,y2
        return np.sum(dists)

    #returns number of connections for non predefined connections (no sense,motor neuron connections)
    def networkDensity(self):
        connectionNum = np.nonzero(self.simHistory[0][1].getS())[0].size  #get overall connection num
        #HACK should be able to pull number of each type of neuron, not hardcoded
        connectionNum -= 120   #100 connections for sensory neurons, 20 for motor neurons
        return connectionNum

    #returns avg firing rate per second
    def firingRate(self):
        sps = 1000/self.writeInterval  #find number of states saved per second of simulated time
        time = self.runTime/1000       #get total number of seconds
        fps = []                       #holds total number of firings in each second
        cntr = 0
        for sec in xrange(time):
            numFirings = 0
            for state in xrange(sps):
                state = self.simHistory[cntr][1]                     #pull state
                numFirings += (state.getV() >= 30).nonzero()[0].size #find number of neurons fired
                cntr += 1
            fps.append(numFirings)
        return np.average(fps)



    def printStartupInfo(self):
        print "Animat Cluster Simulation started\n"
        print "Simulation Length: " + str(float(self.runTime)/60000.0) + " simulated minutes\n"
        print "Write Interval: " + str(float(self.writeInterval)/1000.0) + " simulated seconds\n"



