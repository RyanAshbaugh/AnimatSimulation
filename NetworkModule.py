__author__ = 'Steven'
'''
Network Module
Simulates brain, contains all neurons

all data flow operations work correctly, just needs lots of functionality added


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
     def __init__(self,inhib,excit,aa,bb):
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
         self.inhibParams = inhib
         self.excitParams = excit
         self.imported = False

         self.kSynapseDecay = 0.7


         #Izhikevich Variables
         self.v = np.array([], dtype = np.float32)
         self.a = np.array([], dtype = np.float32)
         self.b = np.array([], dtype = np.float32)
         self.c = np.array([], dtype = np.float32)
         self.d = np.array([], dtype = np.float32)
         self.S = np.array([[]], dtype = np.float32)
         self.u=self.b*self.v;                 # Initial values of u at ceiling


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


         #Network connection variables
         self.Lnum = 3      #ligand number
         self.Rnum = 3      #receptor number
         self.ligands = []  #holder for ligands of each neuron
         self.receptors = [] #holder for receptors of each neuron
         self.aa = -1 if aa is None else aa
         self.bb = -1 if bb is None else bb


     def findLRGradient(self):
         pass

     def findFBGradient(self):
         pass

     def build_matrices(self):
         pass

     #maybe add to OO... then let the network rebuild..?
     def add_neuron(self, type, pos, sensitivity = 50000):
         if type == 'inhibitory':
             loc = self.numInhibitory
             self._neurons.insert(loc, InhibitoryNeuron(pos[0], pos[1], 0))
             self.inhibitoryNeurons = np.append(self.inhibitoryNeurons, loc)
             self.a = np.insert(self.a, loc, self.inhibParams[1]+0.08*0.5)   #inhibParams[1] = a
             self.b = np.insert(self.b, loc, self.inhibParams[2]-0.05*0.5)
             self.c = np.insert(self.c, loc, self.inhibParams[3])
             self.d = np.insert(self.d, loc, self.inhibParams[4])
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
             self.a = np.insert(self.a, loc, self.excitParams[1])
             self.b = np.insert(self.b, loc, self.excitParams[2])
             self.c = np.insert(self.c, loc, self.excitParams[3])
             self.d = np.insert(self.d, loc, self.excitParams[4])
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

         self.u=self.b*self.v;

     def generateNeurons(self):
         self.add_neuron("motor",(-1,0))
         self.add_neuron("motor",(1,0))
         for i in xrange(10):                                         #generate 10x10 grid of neurons from -.5 to .5
             for j in xrange(10):
                 xPos = -.45+(i*(0.1))
                 yPos = -.45+(j*(0.1))
                 if (i == 4 or i == 5) and (j == 4 or j== 5): self.add_neuron("hunger",(xPos,yPos))
                 else: self.add_neuron("excitatory",(xPos,yPos))
                 ## Below code to add inhib neurons
                 #if i == 2 or i == 7:                                  #in rows 3 and 8 of grid
                 #    if(j in xrange(2,7)):                             #for neurons 3-7
                 #        self.add_neuron("inhibitory",(xPos,yPos))     #make inhibitory
                 #    else:
                 #        self.add_neuron("excitatory",(xPos,yPos))
                 #else:
                 #    self.add_neuron("excitatory",(xPos,yPos))         #otherwise make excitatory
         for i in xrange(0,10):
             temp = np.pi*((1.0/22.0)+((float(i)+.5)/11.0))
             self.add_neuron("sensory_A",(np.cos(temp)-.01,np.sin(temp)-.01))
             self.add_neuron("sensory_B",(np.cos(temp)+.01,np.sin(temp)+.01))



     def connectNetwork(self):
         L = 3
         K = 5
         A = 2.0
         B = 10000.0
         if self.aa == -1:        #if -1 then means aa and bb not already defined
            aa = [[np.random.laplace()*.25 for x in xrange(K)] for x in xrange(L)] #create LxK arrays
            bb = [[np.random.laplace()*.25 for x in xrange(K)] for x in xrange(L)]
            for i in xrange(L):
                aa[i][0] = np.sum(np.abs(aa[i][1:]))
                bb[i][0] = np.sum(np.abs(bb[i][1:]))
         else:
             aa = self.aa        #makes line length shorter
             bb = self.bb
         #set up ligand and receptor lists for each neuron based on a and b
         for z,neuron in enumerate(self._neurons):
            x,y = neuron.X,neuron.Y
            r = [aa[i][0] + aa[i][1]*x + aa[i][2]*y + aa[i][3]*np.cos(np.pi*x) + aa[i][4]*np.cos(np.pi*y) for i in xrange(3)]
            l = [bb[i][0] + bb[i][1]*x + bb[i][2]*y + bb[i][3]*np.cos(np.pi*x) + bb[i][4]*np.cos(np.pi*y) for i in xrange(3)]
            neuron.setRL(r,l)
         #for every neuron in the "grid"
         for index1 in (np.hstack((self.excitatoryNeurons,self.inhibitoryNeurons,self.hungerNeurons))):
            #if edge neuron, connect to appropriate motor
            if (self._neurons[index1].X==-0.45): self.connectNeurons(index1,self.motorNeurons[0],10)
            if (self._neurons[index1].X==0.45): self.connectNeurons(index1,self.motorNeurons[1],10)
            #if top neuron, connect each sense_A neuron to it
            if (self._neurons[index1].Y==0.45):
                for sense in self.senseNeurons_A:
                    self.connectNeurons(sense,index1,10)
            #if bottom neuron, connect each sense_B neuron to it
            if (self._neurons[index1].Y== -0.45):
                for sense in self.senseNeurons_B:
                    self.connectNeurons(sense,index1,10)
            for index2 in (np.hstack((self.excitatoryNeurons,self.inhibitoryNeurons))):
                #str_ = 5
                if (index1 != index2):
                    if (index1 in self.inhibitoryNeurons): str_ = -15
                    n1 = self._neurons[index1]    #pull neuron objects to get r and l arrays
                    n2 = self._neurons[index2]
                    #exp( A* sum( r(j,i) .* l(k,i)) / (B + exp(A*sum(r(j,i) .* l(k,i))) )
                    #print np.exp(A*np.sum(np.multiply(n1.receptors,n2.ligands)))
                    #print B+np.exp(A*np.sum(np.multiply(n1.receptors,n2.ligands)))
                    p = np.exp(A*np.sum(np.multiply(n1.receptors,n2.ligands)))/(B+np.exp(A*np.sum(np.multiply(n1.receptors,n2.ligands))))
                    #print p
                    if(random.random() < p):
                        #print str(type(n1)) + " @(" + str(n1.X) + "," + str(n1.Y) + ") ---> " + str(type(n2)) +\
                        #      " @(" + str(n2.X) + "," + str(n2.Y) + ")"
                        self.connectNeurons(index1, index2, 10)
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

     def _compile_network(self):
         pass



#TRACK U--OLD!!
     def runNetwork(self,t,dt):
         if t == 0: self._compile_network()

         #self.fireTogetherCount *= self.fireTogetherCount_decay
         #self.recentlyFired[self.recentlyFired > 0] -= 1

         #Vectorized Izhikevich model: self.I matrix set through Animat.smell()
         self.fired = (self.v >= 30).nonzero()[0]
         self.recentlyFired[self.fired] = 20

         #self.fireTogetherCount[np.ix_((self.recentlyFired > 0) & (self.recentlyFired < 20), self.recentlyFired == 20)] += 1
         #self.S[(self.fireTogetherCount > 3) & (np.abs(self.S) < 5)] += 1

         self.v[self.fired] = self.c[self.fired]
         self.u[self.fired]= self.u[self.fired] + self.d[self.fired]

         newI = np.sum(self.S[self.fired],axis=0)
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

