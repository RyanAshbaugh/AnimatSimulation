
__author__ = 'RJ'
"""

Simulation Engine for running on cluster
Does not use threads
Does not copy objects to send back to driver, only stores states in list form

"""
import time
import World
import pp
import SimParam

class clusterSimEngine():

    def __init__(self):
        self.stateList = []        # list for storing states (time,state)
        self.timeStep = 1          # time
        self.clockStart = -1       # real world clock time, used to benchmark
        self.writeInterval = 500   # store every 500 "cycles" = 500 simulated ms
        self.world = 0             # place holder for world variable
        self.foodLocs = 0


    def initializeEngine(self,simParam,simLength):
        self.clockStart = time.clock()
        self.world = World.World(simParam)
        self.foodLocs = self.world.getFoodLocs()
        self.stateList.append((0,self.world.copyDynamicState()))     #store initial world state
        for t in xrange(1,simLength+1):
            self.simulate(t)
        return True


    def simulate(self,t):
        self.world.update(t,self.timeStep)
        if (t%self.writeInterval == 0):
            self.stateList.append((t,self.world.copyDynamicState()))

    def getFoodLocs(self):
        return self.foodLocs

    def setWriteInterval(self,interval):
        self.writeInterval = interval

    def getResults(self):
        return self.stateList