
'''
Network Module
Simulates brain, contains all neurons




'''

from NeuronModule import InhibitoryNeuron
from NeuronModule import ExcitatoryNeuron
from NeuronModule import MotorNeuron
from NeuronModule import SensoryNeuron_A
from NeuronModule import SensoryNeuron_B
from NeuronModule import HungerNeuron
import math
import numpy as np
import random
import SimParam

class Network:

    #kwargs used for evo driver
     def __init__(self,x0,y0,sigma):
         #some constants/tracking numbers
         self.FIRED_VALUE = 30
         self.DT = 1
         self.numExcitatory = 0
         self.numInhibitory = 0
         self.numMotor = 0
         self.numSensory_A = 0
         self.numSensory_B = 0
         self.numHunger = 0
         self.totalNum = 0
         self.voltIncr = 15.0     #S matrix contains connection weights too small to be used as voltage,
         self.kSynapseDecay = 0.7
         self.x0 = x0
         self.y0 = y0
         self.sigma = sigma


         #Izhikevich Variables
         self.v = np.array([], dtype = np.float32)
         self.a = np.array([], dtype = np.float32)
         self.b = np.array([], dtype = np.float32)
         self.c = np.array([], dtype = np.float32)
         self.d = np.array([], dtype = np.float32)
         self.S = np.array([[]], dtype = np.float32)
         self.u=self.b*self.v                 # Initial values of u at ceiling


         #'Shadow' Variables
         self.fireTogetherCount = np.array([], ndmin = 2, dtype = np.float)
         self.firingCount = np.array([])
         self.recentlyFired = np.array([], dtype = np.float32)
         self.justFired = np.array([], dtype = np.int_, ndmin = 2)

         #'Shadow' Variable assistants
         #self.fireTogetherWindow = np.array([])
         self.firingCount_decay = 0.01
         self.fireTogetherCount_decay = 0.98

         #other neuron mappings
         self._neurons = []
         self.inhibitoryNeurons = np.array([], dtype=np.int_)
         self.excitatoryNeurons = np.array([], dtype=np.int_)
         self.motorNeurons = np.array([], dtype=np.int_)
         self.hungerNeurons = np.array([],dtype=np.int_)

         #These will be dictionaries of Lists eventually for different types of sensory neurons!
         self.senseNeurons_A = np.array([], dtype=np.int_)
         self.senseNeuronLocations_A = np.array([],ndmin=2)
         self.sensitivity_A = np.array([], ndmin = 2)
         self.senseNeurons_B = np.array([], dtype=np.int_)
         self.senseNeuronLocations_B = np.array([],ndmin=2)
         self.sensitivity_B = np.array([], ndmin = 2)


     #maybe add to OO... then let the network rebuild..?
     def add_neuron(self, type, pos, sensitivity = 50000):
         if type == 'inhibitory':
             loc = self.numInhibitory
             self._neurons.insert(loc, InhibitoryNeuron(pos[0], pos[1], 0))
             self.inhibitoryNeurons = np.append(self.inhibitoryNeurons, loc)
             self.a = np.insert(self.a, loc, 0.02)
             self.b = np.insert(self.b, loc, 0.2)
             self.c = np.insert(self.c, loc, -65)
             self.d = np.insert(self.d, loc, 8)
             self.v = np.insert(self.v, loc, -65)
             self.numInhibitory += 1

             self.excitatoryNeurons += 1
             self.motorNeurons += 1
             self.senseNeurons_A += 1
             self.senseNeurons_B += 1
             self.hungerNeurons += 1

         if type == 'excitatory':
             loc = self.numExcitatory + self.numInhibitory
             self._neurons.insert(loc, ExcitatoryNeuron(pos[0], pos[1], 0))
             self.excitatoryNeurons = np.append(self.excitatoryNeurons, loc)
             self.a = np.insert(self.a, loc,0.02)
             self.b = np.insert(self.b, loc, 0.2)
             self.c = np.insert(self.c, loc, -65)
             self.d = np.insert(self.d, loc, 8)
             self.v = np.insert(self.v, loc, -65)
             self.numExcitatory += 1

             self.motorNeurons += 1
             self.senseNeurons_A += 1
             self.senseNeurons_B += 1
             self.hungerNeurons += 1

         if type == 'motor':
             loc = self.numExcitatory + self.numInhibitory + self.numMotor
             self._neurons.insert(loc, MotorNeuron(pos[0], pos[1], 0))
             self.motorNeurons = np.append(self.motorNeurons, loc)
             self.a = np.insert(self.a, loc, 0.02)
             self.b = np.insert(self.b, loc, 0.2)
             self.c = np.insert(self.c, loc, -65)
             self.d = np.insert(self.d, loc, 8)
             self.v = np.insert(self.v, loc, -65)
             self.numMotor += 1

             self.senseNeurons_A += 1
             self.senseNeurons_B += 1
             self.hungerNeurons += 1

         if type == 'sensory_A':
             loc = self.numExcitatory + self.numInhibitory + self.numMotor + self.numSensory_A
             self._neurons.insert(loc, SensoryNeuron_A(pos[0], pos[1], 0))
             self.senseNeurons_A = np.append(self.senseNeurons_A, loc)
             if self.numSensory_A == 0: self.senseNeuronLocations_A = np.array([pos[0],pos[1]],ndmin=2)
             else: self.senseNeuronLocations_A = np.insert(self.senseNeuronLocations_A, self.numSensory_A, np.array((pos[0], pos[1])), axis = 0)
             self.a = np.insert(self.a, loc, 0.02)
             self.b = np.insert(self.b, loc, 0.2)
             self.c = np.insert(self.c, loc, -65)
             self.d = np.insert(self.d, loc, 8)
             self.v = np.insert(self.v, loc, -65)
             self.sensitivity_A = np.append(self.sensitivity_A, sensitivity)
             self.numSensory_A += 1

             self.senseNeurons_B += 1
             self.hungerNeurons += 1

         if type == 'sensory_B':
             loc = self.numExcitatory + self.numInhibitory + self.numMotor + self.numSensory_A + self.numSensory_B
             self._neurons.insert(loc, SensoryNeuron_B(pos[0], pos[1], 0))
             self.senseNeurons_B = np.append(self.senseNeurons_B, loc)
             if self.numSensory_B == 0: self.senseNeuronLocations_B = np.array([pos[0],pos[1]],ndmin=2)
             else: self.senseNeuronLocations_B = np.insert(self.senseNeuronLocations_B, self.numSensory_B, np.array((pos[0], pos[1])), axis = 0)
             self.a = np.insert(self.a, loc, 0.02)
             self.b = np.insert(self.b, loc, 0.2)
             self.c = np.insert(self.c, loc, -65)
             self.d = np.insert(self.d, loc, 8)
             self.v = np.insert(self.v, loc, -65)
             self.sensitivity_B = np.append(self.sensitivity_B, sensitivity)
             self.numSensory_B += 1

             self.hungerNeurons += 1

         if type == 'hunger':
             loc = self.numExcitatory + self.numInhibitory + self.numMotor + self.numSensory_A + self.numSensory_B + self.numHunger
             self._neurons.insert(loc, HungerNeuron(pos[0], pos[1], 0))
             self.hungerNeurons = np.append(self.hungerNeurons, loc)
             self.a = np.insert(self.a, loc, 0.02)
             self.b = np.insert(self.b, loc, 0.2)
             self.c = np.insert(self.c, loc, -65)
             self.d = np.insert(self.d, loc, 8)
             self.v = np.insert(self.v, loc, -65)
             self.numHunger += 1

         #'Shadow' Variables
         if(self.totalNum == 0):
             self.fireTogetherCount = np.array([0], ndmin = 2, dtype = np.float32)
             self.S = np.array([0], ndmin = 2, dtype = np.float32)
             #self.justFired = np.array([0],ndmin=2)
             self.justFired = np.array([0], dtype = np.float32)
         ## NEEDS FIXING FOR HOW LOC IS DEFINED
         else:
             self.fireTogetherCount = np.insert(self.fireTogetherCount, loc, 0, axis = 0)
             self.fireTogetherCount = np.insert(self.fireTogetherCount, loc, 0, axis = 1)

             self.S = np.insert(self.S, loc, np.float32(0), axis=0)
             self.S = np.insert(self.S, loc, np.float32(0), axis=1)

             self.justFired = np.insert(self.justFired, loc, np.array([0]), axis = 0)

         self.firingCount = np.insert(self.firingCount, loc, 0)
         self.recentlyFired = np.insert(self.recentlyFired, loc, np.float32(0))

         self.totalNum += 1


         #'Shadow' Variable assistants
         #self.fireTogetherWindow = np.insert(self.fireTogetherWindow, loc, 1)
         #self.firingCount_decay = np.array([])
         #self.fireTogetherCount_decay = np.array([])

         self.u=self.b*self.v

     def generateNeurons(self):
         #Generate neurons around the circle
         for i in xrange(40):
             loc = (np.cos(2*np.pi*(i+0.5)/40),np.sin(2*np.pi*(i+0.5)/40))
             if i < 20:
                 if i % 2 == 0:
                     self.add_neuron("sensory_A",loc)
                 else:
                     self.add_neuron("sensory_B",loc)
             else:
                 self.add_neuron("excitatory",loc)
         #Generate hunger and motor neurons
         self.add_neuron("hunger",(0,0))
         self.add_neuron("motor",(-1.2,0))
         self.add_neuron("motor",(1.2,0))

     def connectNetwork(self):
         #Parameters
         L = 3
         K = 6
         A = 2.0
         B = 20.0
         C = 1.0
         D = 1.0

         #Set up connection variable
         #set up ligand and receptor lists for each neuron in circle based on aa and bb
         for index in np.hstack((self.excitatoryNeurons,self.senseNeurons_A,self.senseNeurons_B)):
            x, y = self._neurons[index].X, self._neurons[index].Y
            rr,ll = [],[]
            for i in xrange(5):
                rVal = self.sigma[0][i] - np.sqrt( np.square(x - self.x0[0][i]) + np.square(y - self.y0[0][i]))
                lVal = self.sigma[1][i] - np.sqrt( np.square(x - self.x0[1][i]) + np.square(y - self.y0[1][i]))
                if rVal < 0.0: rVal = 0.0
                if lVal < 0.0: lVal = 0.0
                rr.append(rVal)
                ll.append(lVal)
            self._neurons[index].setRL(rr,ll)

         #Set up ligand and receptor lists for each motor neuron and hunger neuron
         for index in self.hungerNeurons:
            x, y = self._neurons[index].X, self._neurons[index].Y
            rr,ll = [],[]
            for i in xrange(5):
                rVal = self.sigma[0][i] - np.sqrt( np.square(x - self.x0[0][i]) + np.square(y - self.y0[0][i]))
                lVal = self.sigma[1][i] - np.sqrt( np.square(x - self.x0[1][i]) + np.square(y - self.y0[1][i]))
                if rVal < 0: rVal = 0
                if lVal < 0: lVal = 0
                rr.append(rVal)
                ll.append(lVal)
            rr[2] = 1
            self._neurons[index].setRL(rr,ll)

         index = self.motorNeurons[0]            #left motor neuron
         x, y = self._neurons[index].X, self._neurons[index].Y
         rr,ll = [],[]
         for i in xrange(5):
            rVal = self.sigma[0][i] - np.sqrt( np.square(x - self.x0[0][i]) + np.square(y - self.y0[0][i]))
            lVal = self.sigma[1][i] - np.sqrt( np.square(x - self.x0[1][i]) + np.square(y - self.y0[1][i]))
            if rVal < 0: rVal = 0
            if lVal < 0: lVal = 0
            rr.append(rVal)
            ll.append(lVal)
         ll[3] = 1
         self._neurons[index].setRL(rr,ll)

         index = self.motorNeurons[1]             #right motor neuron
         x, y = self._neurons[index].X, self._neurons[index].Y
         rr,ll = [],[]
         for i in xrange(5):
            rVal = self.sigma[0][i] - np.sqrt( np.square(x - self.x0[0][i]) + np.square(y - self.y0[0][i]))
            lVal = self.sigma[1][i] - np.sqrt( np.square(x - self.x0[1][i]) + np.square(y - self.y0[1][i]))
            if rVal < 0: rVal = 0
            if lVal < 0: lVal = 0
            rr.append(rVal)
            ll.append(lVal)
         ll[3] = 1
         self._neurons[index].setRL(rr,ll)

         #Set up connection weights
         neuronIndices = np.hstack((self.excitatoryNeurons,self.senseNeurons_A,self.senseNeurons_B,self.hungerNeurons,self.motorNeurons))
         for n1 in neuronIndices:
             for n2 in neuronIndices:
                 W = np.sum( np.multiply(self._neurons[n1].r, self._neurons[n2].l))
                 connectionWeight = np.exp(A* W) / (B + np.exp(A*W))
                 if connectionWeight <= 1.0/20.0: connectionWeight = 0
                 self.connectNeurons(n1,n2,connectionWeight)

         #Create I
         self.I = 2*np.ones( (self.totalNum), dtype = np.float32 )



     def copyDynamicState(self):
         state = []
         state.append(self.a.copy())
         state.append(self.b.copy())
         state.append(self.c.copy())
         state.append(self.d.copy())
         state.append(self.u.copy())
         state.append(self.v.copy())
         state.append(self.S.copy())
         try:
             state.append(self.I.copy())
         except AttributeError:
             pass #means its first frame and I has not been set yet
         return state

     def loadDynamicState(self, state):
         self.a = state[0]
         self.b = state[1]
         self.c = state[2]
         self.d = state[3]
         self.u = state[4]
         self.v = state[5]
         self.S = state[6]
         try:
            self.I = state[7]
         except IndexError:
             pass #not set yet


     def connectNeurons(self, n1, n2, dV = 100):
         self.S[n1, n2] = dV

     def get_dist(self, i1, i2):
         n1 = self._neurons[i1]
         n2 = self._neurons[i2]
         return np.sqrt((n1.X-n2.X)**2 + (n1.Y-n2.Y)**2)

    #NOT USED
     def getAverageExcitatoryVoltage(self):
        self.sumVoltage = 0
        for x in range (0, len(self._neurons)):
            if isinstance(self._neurons[x], ExcitatoryNeuron):
                self.sumVoltage += self.neuron.getMembranePotential()
        return self.sumVoltage/len(self._neurons)

     def get_neurons_firing(self):
         return (self.v >= self.FIRED_VALUE).nonzero()

     def getNeurons(self):

         #populates neuron objects with vectorized data so that upper levels can use them in an OO manner
         for i in range(0, len(self._neurons)):
             self._neurons[i].index = i
             self._neurons[i].a = self.a[i]
             self._neurons[i].b = self.b[i]
             self._neurons[i].membranePotential = self.v[i]
             self._neurons[i].c = self.c[i]
             self._neurons[i].d = self.d[i]
             self._neurons[i].u = self.u[i]

         return self._neurons


     def runNetwork(self,t,dt):
         #self.fireTogetherCount *= self.fireTogetherCount_decay
         #self.recentlyFired[self.recentlyFired > 0] -= 1

         self.fired = (self.v >= 30).nonzero()[0]
         self.recentlyFired[self.fired] = 20

         #self.fireTogetherCount[np.ix_((self.recentlyFired > 0) & (self.recentlyFired < 20), self.recentlyFired == 20)] += 1
         #self.S[(self.fireTogetherCount > 3) & (np.abs(self.S) < 5)] += 1

         self.v[self.fired] = self.c[self.fired]
         self.u[self.fired]= self.u[self.fired] + self.d[self.fired]

         newI = np.sum(self.S[self.fired],axis=0) * self.voltIncr
         self.I = self.kSynapseDecay*self.I + newI

         self.v=self.v+0.5*(0.04*(self.v**2) + 5*self.v + 140-self.u + self.I)
         self.v=self.v+0.5*(0.04*(self.v**2) + 5*self.v + 140-self.u + self.I)

         self.u=self.u+self.a*(self.b*self.v - self.u)


     #uses voltages of firing motorNeurons to return new motor data
     def getMotorData(self):

         newM1 = 0 if(self.v[self.motorNeurons[0]] <= 30) else (self.v[self.motorNeurons[0]])/30 + 30
         newM2 = 0 if(self.v[self.motorNeurons[1]] <= 30) else (self.v[self.motorNeurons[0]])/30 + 30
         return newM1,newM2

     def getTotalNeuronNum(self):
         return self.totalNum

