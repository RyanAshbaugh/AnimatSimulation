__author__ = 'Steven'
import threading
from World import World
import Queue
import copy
import cPickle
import random
import numpy as np
import time
import SimParam

class SimulationEngine:

    def __init__(self):

        self.worldBuffer = Queue.Queue()         #holds produced Worlds
        self.developmentBuffer = Queue.Queue()   #holds produced Networks

        self.dt = 1
        self.isRunning = False                   #is the simulation engine running?
        self.thread_exit = False                 #should the simulation stop?
        self.lock = threading.Lock()             #lock to manage above variables

        self.writeInterval = 1                   #default write interval of 1ms
        self.interval_lock = threading.Lock()    #lock to manage write interval

        world = 0                                 #placeholder World, should be fixed!
        self.staticWorld = copy.deepcopy(world)   #placeholder Static World

        self.runTime = -1                         #real time sim has been running
        self.runTimeS = -1

    #begins a new simulation
    def startNewSim(self,simParam):
        self.stopSimulation()
        with self.lock:
            self.thread_exit = False
            self.isRunning = True
        self.worldBuffer = Queue.Queue()
        world = World(simParam)                                       #starts the world
        self.staticWorld = copy.deepcopy(world)               #static copy to merge and send to GUI
        self.worldBuffer.put((0,world.copyDynamicState()))    #puts dynamic state in the first spot
        self.simThread = threading.Thread(target=self.simulate, args=(world, 0, 1))   #runs the thread
        self.runTimeS = time.clock()
        self.simThread.start()


    #the thread for World simulations
    def simulate(self, world, t, dt):

        exit = False
        while not exit:

            world.update(t,self.dt)  #advances world one time step
            t = t + dt               #advances simulated time one time step

            with self.interval_lock: #sets the write interval
                interval = self.writeInterval

            if(t%interval == 0):     #stores the world, if needed
                state = world.copyDynamicState()  #do this in a separate statement so it doesn't block the buffer
                self.worldBuffer.put((t, state))  #tuple of time, dynamic state

            #sees if the simulation should exit
            with self.lock:
                exit = self.thread_exit

        #tells the Simulation Engine that it is finished.
        with self.lock:
            self.isRunning = False



    #stops the thread in a safe manner.
    def stopSimulation(self):
        stopTime = time.clock()
        self.runTime += stopTime-self.runTimeS
        if self.isRunning == False: return
        while 1:
            with self.lock:
                self.thread_exit = True
                if self.isRunning == False:
                    self.simThread.join()
                    return

    #loads a simulation from a file into the Simulation Engine
    def loadSimulationFromFile(self, f):
        self.stopSimulation()
        contents = cPickle.load(f)
        self.staticWorld = contents[0]
        self.worldBuffer = Queue.Queue()
        for key in contents[1].iterkeys():
            self.worldBuffer.put((key, contents[1][key]))
        f.close()

    #continues Simulation from a given Dynamic State--should be reconfigured to take any world
    def continueSim(self, worldState, t):
        self.stopSimulation()

        with self.lock:
            self.thread_exit = False
            self.isRunning = True

        self.worldBuffer = Queue.Queue()
        world = self.staticWorld
        world.loadDynamicState(worldState)

        self.staticWorld = copy.deepcopy(world)                #static copy to merge and send to GUI
        self.worldBuffer.put((t,world.copyDynamicState()))    #puts dynamic state in the first spot
        self.simThread = threading.Thread(target=self.simulate, args=(world, t, 1))   #runs the thread
        self.runTimeS = time.clock()     #restart new run time
        self.simThread.start()

    #do not use this right now!
    #def getCurrentWorld(self):
    #    self.staticWorld.loadDynamicState(self.worldBuffer.get()[1])
    #    return self.staticWorld

    #is the engine running?
    def is_running(self):
        with self.lock:
            return self.isRunning

    #changes the write interval
    def setWriteInterval(self, dt):
        with self.interval_lock:
            self.writeInterval = dt

    #returns any states that have not yet been collected
    def getNewStates(self):
        retDict = {}
        max = self.worldBuffer.qsize()
        for x in range(0, max):
            worldData = self.worldBuffer.get()
            retDict[worldData[0]] = worldData[1]
        return (self.staticWorld, retDict)

    #begins a new simulation
    def startNewDevelopmentSim(self):
        self.stopSimulation()
        with self.lock:
            self.thread_exit = False
            self.isRunning = True
        self.developmentBuffer = Queue.Queue()
        network = NetworkModule.Network()
        network_copy = copy.deepcopy(network)
        self.developmentBuffer.put((0,network_copy))    #puts dynamic state in the first spot
        self.simThread = threading.Thread(target=self.developmentSimulation, args=(network,))   #runs the thread
        self.simThread.start()

    def getNewDevelopments(self):
        retDict = {}
        max = self.developmentBuffer.qsize()
        for x in range(0, max):
            developmentData = self.developmentBuffer.get()
            retDict[developmentData[0]] = developmentData[1]
        return retDict

    #WHENEVER USING RANGE!!
    #the thread for Development simulations
    def developmentSimulation(self, network):
        t = 0
        dist = 0.4
        r = 0.7
        old_n = []
        new_n = []
        dir = 0
        exit = False
        network.add_neuron("excitatory", (0, 0))
        while not exit:
            with self.lock:
                exit = self.thread_exit
            t = t + 1
            if random.random() < 0.25: type = "inhibitory"
            else: type = "excitatory"
            #theta = random.random()*2.*np.pi
            #r = random.random()
            neurons = network.getNeurons()
            new_n = []
            for i in range(len(old_n), len(neurons)):
                new_n.append(neurons[i])
            old_n = neurons[:]
            type = "excitatory"

            for neuron in new_n:
                #if random.random() < 0.25: type = "inhibitory"
                #else: type = "excitatory"
                network.add_neuron(type, (neuron.X + np.cos(dir)*r**(t-1)*dist, neuron.Y + np.sin(dir)*r**(t-1)*dist))
                #if random.random() < 0.25: type = "inhibitory"
                #else: type = "excitatory"
                network.add_neuron(type, (neuron.X - np.cos(dir)*r**(t-1)*dist, neuron.Y - np.sin(dir)*r**(t-1)*dist))
                ret = copy.deepcopy((t, network))
                self.developmentBuffer.put(ret)

            if(dir == 0): dir = np.pi/2.
            else: dir = 0
            print(len(neurons))
            if(len(neurons) >= 1000):
                with self.lock:
                    exit = True

            #network.add_neuron(type, (np.cos(theta) * r, np.sin(theta) * r))
            ret = copy.deepcopy((t, network))
            self.developmentBuffer.put(ret)

        with self.lock:
            self.isRunning = False

    def getRunTime(self):
        return self.runTime


