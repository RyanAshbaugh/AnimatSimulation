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
    def __init__(self,(id,origin,aa,bb)):

        self.net = NetworkModule.Network(aa,bb)
        self.net.generateNeurons()
        self.net.connectNetwork()
        self.pos = np.array([origin[0], origin[1]])
        self.id = id
        self.direc = np.pi/2.0
        self.Eating = False
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
    def __init__(self,(id,origin,aa,bb),rad=1):
        Animat.__init__(self,(id,origin,aa,bb))
        self.radius = rad
        self.motors = np.array([[0],[0]])
        self.cMotionEnergy = 0.01 # convert motion into energy expended in calories / (mm/sec)
        self.kBasalEnergy = 0.01
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
        self.pos = state[3]
        self.direc = state[4]
        self.Eating = state[5]
        self.net.loadDynamicState(state[6])
        self.benchmark = state[7]
       
        
    def move(self, trac, t):
        #set each wheel
        self.motors[0],self.motors[1] = self.net.getMotorData()  #right now only ever 0 or 20
        trac = .001 #need to change that later
        if self.Eating:
            self.motors = np.array([[0],[0]])
            trac = 0       #causes no movement

        # rotate body depending on the difference (hopefully small) of two motors along direction of travel
        self.direc = self.direc + math.atan(trac*(self.motors[1]-self.motors[0])/self.radius)
        self.unwind() #the angle direc could exceed 2*pi and 'wind up'
        self.determineMotion(trac)
        self.Energy = self.Energy - self.cMotionEnergy * self.motors.sum(axis=0) - self.kBasalEnergy

    def smell(self, foods):
        smell_loc_A = []
        smell_str_A = []
        smell_loc_B = []
        smell_str_B = []
        for food in foods:
            if food.getType() == "A":
                smell_loc_A.append(food.getPos())
                smell_str_A.append(food.getSmell())
            if food.getType() == "B":
                smell_loc_B.append(food.getPos())
                smell_str_B.append(food.getSmell())

        dir = -(self.direc - math.pi/2)   #figure out the clockwise direction of the animat
        if(dir <= 0): dir += math.pi*2    #bound direction to [0, 2*pi]
        rotMat = np.array([[np.cos(dir), -np.sin(dir)], [np.sin(dir), np.cos(dir)]])  #construct the rotation matrix

        worldPos_A = np.dot(self.net.senseNeuronLocations_A, rotMat) + self.pos           #get the world position of the sense neurons based on the position and rotation of the Animat
        worldPos_B = np.dot(self.net.senseNeuronLocations_B, rotMat) + self.pos           #get the world position of the sense neurons based on the position and rotation of the Animat

        #built-in!
        total_smell_A = self.net.sensitivity_A * np.sum(self.gaussian(scipy.spatial.distance.cdist(worldPos_A, smell_loc_A ), 0, 3), axis=1)  #figures out the total smell strength based on the distances (gaussian distribution)
        total_smell_B = self.net.sensitivity_B * np.sum(self.gaussian(scipy.spatial.distance.cdist(worldPos_B, smell_loc_B ), 0, 3), axis=1)  #figures out the total smell strength based on the distances (gaussian distribution)

        self.net.I[self.net.senseNeurons_A] = np.minimum(total_smell_A,100)   #sense neuron drive based on smell
        self.net.I[self.net.senseNeurons_B] = np.minimum(total_smell_B,100)   #sense neuron drive based on smell



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
        possibleFoods = []
        for i,food in enumerate(foods):
            x1,y1 = self.pos
            x2,y2 = food.getPos()
            dist = np.sqrt(np.square(np.abs(x2-x1))+np.square(np.abs(y2-y1)))
            if((dist < 0.5) and (food.getAmount() > 0)):
                possibleFoods.append(i)

        #print(whichFoods.size)
        if len(possibleFoods) > 0:
            toEat = possibleFoods[0] #pick first food in list, change maybe to whichever is closer?
            self.Eating = 1
            self.Energy += foods[toEat].getCalories()
            foods[toEat].decrAmt()
        else:
            self.Eating = 0 #move if not near food
        #check if hungry
        if self.Energy <= self.hungerThreshold:
            self.net.I[self.net.hungerNeurons] = 105  #-65->30 = 95 + 10 = 105
        return foods

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