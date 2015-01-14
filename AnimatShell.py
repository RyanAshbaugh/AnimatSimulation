# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 17:57:04 2014

@author: RJ

Base Class for Animat Object
"""

import numpy as np
#from numpy import *
import math as math
import scipy.spatial
import time
import NetworkModule
import SimParam



##################### Animat Base Class ######################################################
    ## Child Class for all Animat Types ##
class Animat():
    
    #constructor
    #**kwargs
    #  startPos : takes (x,y) coordinate for starting position
    def __init__(self,(id,type,origin,cal,inhib,excit,aa,bb)):

        self.net = NetworkModule.Network(inhib,excit,aa,bb)
        self.net.generateNeurons()
        #self.net.populateTestNetwork()
        self.net.connectNetwork()
        #self.net.connectTestNetwork()
        self.pos = np.array([origin[0], origin[1]])
        self.id = id
        self.direc = np.pi/2.0
        self.Eating = False #does not start eating
        self.Energy = 200
        self.hungerThreshold = .75 * self.Energy
        self.maxInputStrength = np.ones(self.net.totalNum)*200.
        #self.image = pygame.image.load("roomba.png").convert_alpha()
    
    #**kwarg defaulted to return current frame data, change if need other frames data(proabably for testing)
    #def getPosition(self):
        #current position will always be last coordinates stored, returns 2 tuple (xCoord,Ycoord)
    #    return self.pos
        
        
##################### Wheel Animat Class ######################################################
    ##Simplest Type of Animat, Conists of circular body with 2 "wheels" for movement##        
class WheelAnimat(Animat):
    
    #constructor **kwargs
    #  origin : takes (x,y) coordinate for starting position
    #  rad : sets the radius of the animat
    #  cal : sets amt of energy in an item of food
    def __init__(self,(id,type,origin,cal,inhib,excit,aa,bb),rad=1):
        Animat.__init__(self,(id,type,origin,cal,inhib,excit,aa,bb))
        self.radius = rad
        self.motors = np.array([[0],[0]])
        self.cMotionEnergy = 0.01 # convert motion into energy expended in calories / (mm/sec)
        self.kBasalEnergy = 0.01
        self.Calories = cal # how much energy in a unit amount of food
        self.benchmark = []

    def runNetwork(self, t, dt):
        sTime = time.clock()
        self.net.runNetwork(t, dt)
        eTime = time.clock()
        self.benchmark.append(eTime-sTime)


    def copyDynamicState(self):
        state = []
        state.append(self.cMotionEnergy)
        state.append(self.kBasalEnergy)
        state.append(self.Energy)
        state.append(self.Calories)
        state.append(self.pos.copy())
        state.append(self.direc)
        state.append(self.Eating)
        state.append(self.net.copyDynamicState())
        state.append(self.benchmark)
        return state


    def loadDynamicState(self,state):
        self.cMotionEnergy = state[0]
        self.kBasalEnergy = state[1]
        self.Energy = state[2]
        self.Calories = state[3]
        self.pos = state[4]
        self.direc = state[5]
        self.Eating = state[6]
        self.net.loadDynamicState(state[7])
        self.benchmark = state[8]
       
        
    def move(self, trac, t):
        #set each wheel
        self.motors[0],self.motors[1] = self.net.getMotorData()  #right now only ever 0 or 20
        trac = .001 #need to change that later
        if self.Eating:
            self.motors = np.array([[0],[0]])
            trac = 0       #causes no movement

        # rotate body depending on the difference (hopefully small) of two motors along direction of travel
        self.direc = self.direc + math.atan(trac*(self.motors[1]-self.motors[0])/self.radius)
        #self.unwind() #the angle direc could exceed 2*pi and 'wind up'
        self.determineMotion(trac)
        self.Energy = self.Energy - self.cMotionEnergy * self.motors.sum(axis=0) - self.kBasalEnergy

    def smell(self, smells):
        smell_type = smells[0]

        smell_loc = smells[1][0]        #smell locations
        smell_str = smells[1][1] / 10       #smell strengths, divide by 10 because smell based on amount should fix

        dir = -(self.direc - math.pi/2)   #figure out the clockwise direction of the animat
        if(dir <= 0): dir += math.pi*2    #bound direction to [0, 2*pi]

        rotMat = np.array([[np.cos(dir), -np.sin(dir)], [np.sin(dir), np.cos(dir)]])  #construct the rotation matrix
        worldPos = np.dot(self.net.senseNeuronLocations, rotMat) + self.pos           #get the world position of the sense neurons based on the position and rotation of the Animat

        #built-in!
        total_smell = self.net.sensitivity* np.sum(  self.gaussian(scipy.spatial.distance.cdist(worldPos, smell_loc ), 0, 3) *smell_str, axis=1)  #figures out the total smell strength based on the distances (gaussian distribution)

        self.net.I[self.net.senseNeurons] = np.minimum(total_smell,100)   #sense neuron drive based on smell



    def gaussian(self, x, mu, sig):
         return np.exp(-1 * (x - mu)**2. / 2 * sig**2.)

    # direction and traction determine motion
    def unwind(self):
        if self.direc > math.pi + .5:
            self.direc = self.direc - 2*math.pi
        if self.direc < -1*math.pi -.5:
            self.direc = self.direc + 2*math.pi
        
    # direction and traction determine motion
    def determineMotion(self,trac):
        self.posInc = trac * np.mean(self.motors) * np.array([np.cos(self.direc), np.sin(self.direc)])
        self.pos = self.pos + self.posInc
        
    # 'Eat' if at food    
    def eat(self, foods):
        type = foods[0]
        food_loc = foods[1][0]
        food_amt = foods[1][1]

        food_dist = scipy.spatial.distance.cdist(np.array([self.pos]), food_loc)
        whichFoods = np.logical_and(food_dist[0] < .5, food_amt > 0).nonzero()[0]

        #print(whichFoods.size)
        if whichFoods.size > 0:
            self.Eating = 1
            try:
                 self.Energy += self.Calories * food_amt[whichFoods]
            except ValueError:
                 print "Eat error"
                 print whichFoods
                 self.Energy += self.Calories * food_amt[whichFoods][0]
            food_amt[whichFoods] -= 1.0
        else:
            self.Eating = 0 #move if not near food
        #check if hungry
        if self.Energy <= self.hungerThreshold:
            self.net.I[self.net.hungerNeurons] = 105  #-65->30 = 95 + 10 = 105
        return food_amt



            
    def getStats(self):
        #stat list = Type,Energy,
        stats = ["Wheel Animat"]
        stats.append(str(self.Energy))
        stats.append(str(self.cMotionEnergy))
        stats.append(str(self.kBasalEnergy))
        #add function call to network to get neuron stats
        return stats

    def calcBenchmark(self,bufferedTime,runTime):
        log = open("Benchmarks.txt","w")
        log.write("Benchmark Log\n")
        neuronNums = self.net.getNeuronNums()
        log.write("Number of Sensory Neurons: " + str(neuronNums[0]) + "\n")
        log.write("Number of Excitatory Neurons: " + str(neuronNums[1]) + "\n")
        log.write("Number of Inhibitory Neurons: " + str(neuronNums[2]) + "\n")
        log.write("Number of Motor Neurons: " + str(neuronNums[3]) + "\n")
        #print self.benchmark
        log.write("Buffered Time: " + str(bufferedTime*.001) + "s" + " completed in " + str(runTime) + "s\n")
        avg = math.fsum(self.benchmark)/(float)(len(self.benchmark))
        log.write("\nAverage Run Time: " + str(avg))
        log.close()
        self.net.calcBenchmark()