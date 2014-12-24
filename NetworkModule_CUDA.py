__author__ = 'Steven'
'''
Network Module
Simulates brain, contains all neurons

all data flow operations work correctly, just needs lots of functionality added

'''
import os
from NeuronModule import InhibitoryNeuron
from NeuronModule import ExcitatoryNeuron
from NeuronModule import MotorNeuron
from NeuronModule import SensoryNeuron
#import numbapro

import numpy as np
import gnumpy as gp
import copy
import time
import random

#@guvectorize(['void(float32[:], float32[:], float32[:], float32[:], float32[:], float32[:], float32[:], float32[:], float32[:,:], int32[:])'], '(n),(n),(n),(n),(n),(n),(n),(n),(n,n)->(n)')

#@jit(argtypes=[float32[:],float32[:],float32[:],float32[:],float32[:],float32[:],float32[:],float32[:],float32[:,:]])
#@autojit
def run_network(v, recentlyFired, a, b, c, d, u, I, S):

    #self.fireTogetherCount *= self.fireTogetherCount_decay
    #self.recentlyFired[self.recentlyFired > 0] -= 1

    #Vectorized Izhikevich model: self.I matrix set through Animat.smell()
    m = len(v)

    for i in range(m):
        if v[i] >= 30:
            v[i] = c[i]
            u[i] += d[i]
        sum = 0
        for i2 in range(m):
            sum += S[i2,i]
        I[i] = I[i]+sum
        v[i]=v[i]+0.5*(0.04*(v[i]**2) + 5*v[i] + 140-u[i] + I[i])
        v[i]=v[i]+0.5*(0.04*(v[i]**2) + 5*v[i] + 140-u[i] + I[i])

        u[i]=u[i]+a[i]*(b[i]*v[i] - u[i])
    #return 1

# from numbapro import guvectorize, autojit, vectorize, jit
# @guvectorize(['void(float32[:], float32[:], float32[:], float32[:], float32[:], float32[:], float32[:], float32[:], float32[:,:], float32[:])'] , '(n),(n),(n),(n),(n),(n),(n),(n),(n,n)->()', target='gpu')
# #@vectorize(['void(float32, float32, float32, float32, float32, float32, float32, float32, float32)'], target='gpu')
# #@autojit(target='parallel')
# def run_network(v, recentlyFired, a, b, c, d, u, I, S, r):
#
#     #self.fireTogetherCount *= self.fireTogetherCount_decay
#     #self.recentlyFired[self.recentlyFired > 0] -= 1
#
#     #Vectorized Izhikevich model: self.I matrix set through Animat.smell()
#     m = v.shape[0]
#
#     for i in range(m):
#         if v[i] >= 30:
#             v[i] = c[i]
#             u[i] += d[i]
#         sum = 0.
#         #INCORRECT!
#         for i2 in range(m):
#             sum += S[i2,i]
#             #sum += 1
#         I[i] = I[i]+sum
#         v[i]=v[i]+0.5*(0.04*(v[i]**2) + 5*v[i] + 140-u[i] + I[i])
#         v[i]=v[i]+0.5*(0.04*(v[i]**2) + 5*v[i] + 140-u[i] + I[i])
#
#         u[i]=u[i]+a[i]*(b[i]*v[i] - u[i])
#     r=1



#    return 1
#
# run_network.max_blocksize = 32


    # fired = np.nonzero(v >= 30)[0]
    # recentlyFired[fired] = 20
    #
    # #self.fireTogetherCount[np.ix_((self.recentlyFired > 0) & (self.recentlyFired < 20), self.recentlyFired == 20)] += 1
    # #self.S[(self.fireTogetherCount > 3) & (np.abs(self.S) < 5)] += 1
    #
    # v[fired] = c[fired]
    # u[fired]= u[fired] + d[fired]
    #
    # I = I + np.sum(S[fired],axis=0)
    #
    # v=v+0.5*(0.04*(v**2) + 5*v + 140-u + I)
    # v=v+0.5*(0.04*(v**2) + 5*v + 140-u + I)
    #
    # u=u+a*(b*v - u)

#numba_run_net = vectorize('void(float32[:],float32[:],float32[:],float32[:],float32[:],float32[:],float32[:],float32[:],float32[:,:])')(run_network)


class Network:

     def __init__(self,params):

         gp.board_id_to_use = 1
         gp.track_memory_usage=True
         #some constants/tracking numbers
         self.FIRED_VALUE = 30
         self.DT = 1
         self.numExcitatory = 0
         self.numInhibitory = 0
         self.numMotor = 0
         self.numSensory = 0
         self.totalNum = 0
         self.inhibParams = params[3]  #3 b/c passed all parameters, not just network realted ones
         self.excitParams = params[4]

         self.benchmarks = [["Fired assignemnt (nonzero)"],["recentlyFired assignment"],["u calc"],["I calc (gp.sum"],
                            ["v calc"],["u calc"],["copyDynamicState: "]]
         self.memUsage = []

         self.imported = False

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

         #These will be dictionaries of Lists eventually for different types of sensory neurons!
         self.senseNeurons = np.array([], dtype=np.int_)
         self.senseNeuronLocations = np.array([],ndmin=2)
         self.sensitivity = np.array([], ndmin = 2)


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
             self.senseNeurons += 1

         if type == 'excitatory':
             loc = self.numExcitatory + self.numInhibitory
             self._neurons.insert(loc, ExcitatoryNeuron(pos[0], pos[1], 0))
             self.excitatoryNeurons = np.append(self.excitatoryNeurons, loc)
             self.a = np.insert(self.a, loc, self.excitParams[1])
             self.b = np.insert(self.b, loc, self.excitParams[2])
             self.c = np.insert(self.c, loc, self.excitParams[3]+15*0.5**2)
             self.d = np.insert(self.d, loc, self.excitParams[4]-6*0.5**2)
             self.v = np.insert(self.v, loc, -65)
             self.numExcitatory += 1

             self.motorNeurons += 1
             self.senseNeurons += 1

         if type == 'motor':
             loc = self.numExcitatory + self.numInhibitory + self.numMotor
             self._neurons.insert(loc, MotorNeuron(pos[0], pos[1], 0))
             self.motorNeurons = np.append(self.motorNeurons, loc)
             self.a = np.insert(self.a, loc, 0.02)
             self.b = np.insert(self.b, loc, 0.2)
             self.c = np.insert(self.c, loc, -65+15*0.5**2)
             self.d = np.insert(self.d, loc, 8-6*0.5**2)
             self.v = np.insert(self.v, loc, -65)
             self.numMotor += 1

             self.senseNeurons += 1

         if type == 'sensory':
             loc = self.numExcitatory + self.numInhibitory + self.numMotor + self.numSensory
             self._neurons.insert(loc, SensoryNeuron(pos[0], pos[1], 0))
             self.senseNeurons = np.append(self.senseNeurons, loc)
             if self.numSensory == 0: self.senseNeuronLocations = np.array([pos[0],pos[1]],ndmin=2)
             else: self.senseNeuronLocations = np.insert(self.senseNeuronLocations, self.numSensory, np.array((pos[0], pos[1])), axis = 0)
             self.a = np.insert(self.a, loc, 0.02)
             self.b = np.insert(self.b, loc, 0.2)
             self.c = np.insert(self.c, loc, -65+15*0.5**2)
             self.d = np.insert(self.d, loc, 8-6*0.5**2)
             self.v = np.insert(self.v, loc, -65)
             self.sensitivity = np.append(self.sensitivity, sensitivity)
             self.numSensory += 1

         #'Shadow' Variables
         if(self.totalNum == 0):
             self.fireTogetherCount = np.array([0], ndmin = 2, dtype = np.float32)
             self.S = np.array([0], ndmin = 2, dtype = np.float32)
             #self.justFired = np.array([0],ndmin=2)
             self.justFired = np.array([0], dtype = np.float32)

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

     def populateTestNetwork(self):
         n_e = self.excitParams[0]
         n_i = self.inhibParams[0]   #first element is total num

         #inhibitory neurons
         for x in range(0, n_i):
             #theta = random.random()*2.*np.pi
             #r = random.random()
             theta = 2*np.pi*random.random()
             u = random.random()+random.random()
             r = 2-u if u>1 else u
             self.add_neuron("inhibitory", (r*np.cos(theta), r*np.sin(theta)))

         #excitatory neurons
         for x in range(0, n_e):
             #theta = random.random()*2.*np.pi
             #r = random.random()
             theta = 2*np.pi*random.random()
             u = random.random()+random.random()
             r = 2-u if u>1 else u
             self.add_neuron("excitatory", (r*np.cos(theta), r*np.sin(theta)))

         #motor neurons
         self.add_neuron("motor", (-1, 0))
         self.add_neuron("motor", (1, 0))

         #sensory neurons
         self.add_neuron("sensory", (np.cos(7*np.pi/8.), np.sin(7*np.pi/8.)))
         self.add_neuron("sensory", (np.cos(1*np.pi/8.), np.sin(1*np.pi/8.)))
         self.add_neuron("sensory", (np.cos(6*np.pi/8.), np.sin(6*np.pi/8.)))
         self.add_neuron("sensory", (np.cos(2*np.pi/8.), np.sin(2*np.pi/8.)))
         self.add_neuron("sensory", (np.cos(5*np.pi/8.), np.sin(5*np.pi/8.)))
         self.add_neuron("sensory", (np.cos(3*np.pi/8.), np.sin(3*np.pi/8.)))

         self.add_neuron("sensory", (np.cos(7.5*np.pi/8.), np.sin(7.5*np.pi/8.)))
         self.add_neuron("sensory", (np.cos(1.5*np.pi/8.), np.sin(1.5*np.pi/8.)))
         self.add_neuron("sensory", (np.cos(6.5*np.pi/8.), np.sin(6.5*np.pi/8.)))
         self.add_neuron("sensory", (np.cos(2.5*np.pi/8.), np.sin(2.5*np.pi/8.)))
         #self.add_neuron("sensory", (np.cos(5.5*np.pi/8.), np.sin(5.5*np.pi/8.)))
         #self.add_neuron("sensory", (np.cos(3.5*np.pi/8.), np.sin(3.5*np.pi/8.)))

         self.add_neuron("sensory", (np.cos(7.25*np.pi/8.), np.sin(7.25*np.pi/8.)))
         self.add_neuron("sensory", (np.cos(1.25*np.pi/8.), np.sin(1.25*np.pi/8.)))
         self.add_neuron("sensory", (np.cos(6.25*np.pi/8.), np.sin(6.25*np.pi/8.)))
         self.add_neuron("sensory", (np.cos(2.25*np.pi/8.), np.sin(2.25*np.pi/8.)))
         #self.add_neuron("sensory", (np.cos(5.25*np.pi/8.), np.sin(5.25*np.pi/8.)))
         #self.add_neuron("sensory", (np.cos(3.25*np.pi/8.), np.sin(3.25*np.pi/8.)))

         #self.add_neuron("sensory", (0,0), 10000)


     def copyDynamicState(self):
         state = []
         sTime = time.clock()
         state.append(self.a)
         state.append(self.b)
         state.append(self.c)
         state.append(self.d)
         state.append(self.u)
         state.append(self.v)
         #state.append(self.S.copy())
         #state.append(self.I.copy())
         state.append(self.benchmarks)
         state.append(self.memUsage)
         eTime = time.clock()
         self.benchmarks[6].append(eTime-sTime)

         return state

     def loadDynamicState(self, state):
         self.a = state[0]
         self.b = state[1]
         self.c = state[2]
         self.d = state[3]
         self.u = state[4]
         self.v = state[5]
         self.benchmarks = state[6]
         self.memUsage = state[7]
         #self.I = state[6]
         #self.S = state[6]

     def connectTestNetwork(self):

         #self.connectNeurons(self.senseNeurons[0], self.motorNeurons[1])
         #self.connectNeurons(self.senseNeurons[1], self.motorNeurons[0])
         #self.connectNeurons(self.senseNeurons[2], self.motorNeurons[1])
         #self.connectNeurons(self.senseNeurons[3], self.motorNeurons[0])
         #self.connectNeurons(self.senseNeurons[4], self.motorNeurons[1])
         #self.connectNeurons(self.senseNeurons[5], self.motorNeurons[0])

         dis = 0
         while(dis < 2):
             dis += 0.05
             print("dis: " + str(dis))
             print("p: " + str(self.gaussian(dis, 0.3, 6.5)))

         for index1 in range(0, len(self._neurons)):
             for index2 in range(0, len(self._neurons)):
                 if(index1 != index2):
                     str_ = 5
                     p = (self.gaussian(self.get_dist(index1, index2), 0.2, 4.5))
                     if(index1 in self.senseNeurons): str_ = 40
                     if( index1 in self.excitatoryNeurons and index2 in self.motorNeurons): str_ = 30
                     if(index1 in self.inhibitoryNeurons and index2 in self.motorNeurons): str_ = -80
                     if(index1 in self.inhibitoryNeurons):
                         str_ = -15
                         p = self.gaussian(self.get_dist(index1, index2), 0.3, 6.5)
                     #if(index1 == self.senseNeurons[-1] and index2 in self.inhibitoryNeurons):
                     #    p = 10
                     #    str_ = 150
                     if(index2 in self.motorNeurons and (self._neurons[index2].X * self._neurons[index1].X < 0) and self._neurons[index1].Y > 0):
                         p = 0.5
                     if(random.random() < p): self.connectNeurons(index1, index2, str_)

     def connectNeurons(self, n1, n2, dV = 100):
         self.S[n1, n2] = dV

     def get_dist(self, i1, i2):
         n1 = self._neurons[i1]
         n2 = self._neurons[i2]
         return np.sqrt((n1.X-n2.X)**2 + (n1.Y-n2.Y)**2)

     def gaussian(self, x, mu, sig):
         return np.exp(-1 * (x - mu**2.) / 2 * sig**2.)


     def getAverageExcitatoryVoltage(self):
        self.sumVoltage = 0
        for x in range (0, len(self._neurons)):
            if isinstance(self._neurons[x], ExcitatoryNeuron):
                self.sumVoltage += self.neuron.getMembranePotential()
        return self.sumVoltage/len(self._neurons)

     def get_neurons_firing(self):
         return np.array([[]])
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
         #return
         self.v = gp.as_garray(self.v)
         self.a = gp.as_garray(self.a)
         self.b = gp.as_garray(self.b)
         self.c = gp.as_garray(self.c)
         self.d = gp.as_garray(self.d)
         self.u = gp.as_garray(self.u)
         self.S = gp.as_garray(self.S)
         self.I2 = copy.deepcopy(gp.as_garray(self.I))
         print('compiled')


     # def runNetwork(self, t, dt):
     #
     #     print(self.v.dtype)
     #     print(self.v)
     #     print(self.recentlyFired.dtype)
     #     print(self.recentlyFired)
     #     print(self.a.dtype)
     #     print(self.a)
     #     print(self.b.dtype)
     #     print(self.b)
     #     print(self.c.dtype)
     #     print(self.c)
     #     print(self.d.dtype)
     #     print(self.d)
     #     print(self.u.dtype)
     #     print(self.u)
     #     print(self.I.dtype)
     #     print(self.I)
     #     print(self.S.dtype)
     #     print(self.S)
     #
     #
     #     run_network(self.v, self.recentlyFired, self.a, self.b, self.c, self.d, self.u, self.I, self.S)


# #TRACK U--OLD!!
#      from numbapro import vectorize, float32
#      @vectorize([float32(float32, float32)],
#           target='parallel')
#      def runNetwork(self,t,dt):
#          if t == 0: self._compile_networ
     # def runNetwork(self, t, dt):
     #     a=np.float32(0)
     #     run_network(self.v, self.recentlyFired, self.a, self.b, self.c, self.d, self.u, self.I, self.S, a)

#TRACK U--OLD!!
     def runNetwork(self,t,dt):

         if t == 0: self._compile_network()
         self.I = self.I2
         #self.fireTogetherCount *= self.fireTogetherCount_decay
         #self.recentlyFired[self.recentlyFired > 0] -= 1

         #Vectorized Izhikevich model: self.I matrix set through Animat.smell()
         sTime = time.clock()
         self.fired = (self.v >= 30).nonzero()[0]
         eTime = time.clock()
         self.benchmarks[0].append(eTime-sTime)

         sTime = time.clock()
         self.recentlyFired[self.fired] = 20
         eTime = time.clock()
         self.benchmarks[1].append(eTime-sTime)

         #self.fireTogetherCount[np.ix_((self.recentlyFired > 0) & (self.recentlyFired < 20), self.recentlyFired == 20)] += 1
         #self.S[(self.fireTogetherCount > 3) & (np.abs(self.S) < 5)] += 1

         self.v[self.fired] = self.c[self.fired]

         sTime = time.clock()
         self.u[self.fired]= self.u[self.fired] + self.d[self.fired]
         eTime = time.clock()
         self.benchmarks[2].append(eTime-sTime)
         #print(self.S)

         sTime = time.clock()
         self.I = self.I + gp.sum(self.S[self.fired],axis=0)
         eTime = time.clock()
         self.benchmarks[3].append(eTime-sTime)


         sTime = time.clock()
         self.v=self.v+0.5*(0.04*(self.v**2) + 5*self.v + 140-self.u + self.I)
         eTime = time.clock()
         self.benchmarks[4].append(eTime-sTime)

         self.v=self.v+0.5*(0.04*(self.v**2) + 5*self.v + 140-self.u + self.I)

         sTime = time.clock()
         self.u=self.u+self.a*(self.b*self.v - self.u)
         eTime = time.clock()
         self.benchmarks[5].append(eTime-sTime)

         # if t % 100 == 0:
         #     gp.memory_in_use()
         #     gp.memory_allocators()
#
#      #TRACK U--VECTORIZED!!!!
#      def runNetwork(self, dt, t):
#
#          #self.fireTogetherCount *= self.fireTogetherCount_decay
#          #self.recentlyFired[self.recentlyFired > 0] -= 1
#
#          #Vectorized Izhikevich model: self.I matrix set through Animat.smell()
# #         self.fired = (self.v >= 30).nonzero()[0]
# #         self.fired = np.zeros(self.v.shape)
# #         print(self.fired)
# #          print(self.v.dtype)
# #          print(self.v)
#
#          from numbapro import guvectorize, autojit, vectorize, jit
#          self.imported = True
#
#          temp = 30 * np.ones(self.v.shape, dtype = np.float32)
#          print('starting')
#          fast_greq = vectorize(['int32(float32, float32)'], target='gpu')(greq)
#          print('done')
#          self.fired = fast_greq(self.v, temp)
# #         print(self.fired)
# #         self.recentlyFired[self.fired] = 20
#
#          #self.fireTogetherCount[np.ix_((self.recentlyFired > 0) & (self.recentlyFired < 20), self.recentlyFired == 20)] += 1
#          #self.S[(self.fireTogetherCount > 3) & (np.abs(self.S) < 5)] += 1
#
#          self.v[self.fired] = self.c[self.fired]
#          self.u[self.fired]= self.u[self.fired] + self.d[self.fired]
#
#          self.I = self.I + np.sum(self.S[self.fired],axis=0)
#
#          self.v=self.v+0.5*(0.04*(self.v**2) + 5*self.v + 140-self.u + self.I)
#          self.v=self.v+0.5*(0.04*(self.v**2) + 5*self.v + 140-self.u + self.I)
#
#          self.u=self.u+self.a*(self.b*self.v - self.u)



     #uses voltages of firing motorNeurons to return new motor data
     def getMotorData(self,m1,m2):

         newM1 = 0 if(self.v[self.motorNeurons[0]] <= 30) else 30
         newM2 = 0 if(self.v[self.motorNeurons[1]] <= 30) else 30

         return newM1,newM2

     def getTotalNeuronNum(self):
         return self.totalNum

     def getNeuronNums(self):
         return [self.numSensory,self.numExcitatory,self.numInhibitory,self.numMotor]

     def calcBenchmark(self):
        log = open("Network_Benchmarks.txt","w")
        log.write("runNetwork Benchmark Log\n")
        log.write("\n")
        log.write(self.benchmarks[0][0] + ": " + str(self.getAvg(self.benchmarks[0][1:])) + "\n")
        log.write(self.benchmarks[1][0] + ": " + str(self.getAvg(self.benchmarks[1][1:])) + "\n")
        log.write(self.benchmarks[2][0] + ": " + str(self.getAvg(self.benchmarks[2][1:])) + "\n")
        log.write(self.benchmarks[3][0] + ": " + str(self.getAvg(self.benchmarks[3][1:])) + "\n")
        log.write(self.benchmarks[4][0] + ": " + str(self.getAvg(self.benchmarks[4][1:])) + "\n")
        log.write(self.benchmarks[5][0] + ": " + str(self.getAvg(self.benchmarks[5][1:])) + "\n")
        log.write(self.benchmarks[6][0] + ": " + str(self.getAvg(self.benchmarks[6][1:])) + "\n")
        log.write("\n" + (stat+"\n") for stat in self.memUsage)
        log.close()

     def getAvg(self,a):
         avg = 0.0
         for num in a:
             avg += num
         return avg/(float)(len(a))

# @guvectorize(['void(float32[:], int32[:], float32[:])'], '(n),()->(n)', target='gpu')
# def fast_greq(arr, val, out):
#     for index in range(arr.shape[0]):
#         if arr[index] >= val[0]:
#             out[index] = 1
#         else: out[index] = 0

# @vectorize(['int32(float32, float32)'], target='parallel')
# #@autojit(target='gpu')
# def fast_greq(a, b):
#      return (a - b) > 0
# #fast_greq.max_blocksize = 32

def greq(a,b):
    return (a-b) > 0

#@vectorize(['int32'])
#
# @guvectorize(['void(float32[:], float32[:], float32[:])'], '(n),(m)->()')
# def fast_greq(arr, val, out):
#     #out = []
#     for index in range(arr.shape[0]):
#         if arr[index] >= val[0]:
#             out.append(index)

