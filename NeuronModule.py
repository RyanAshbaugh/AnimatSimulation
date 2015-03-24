from SynapseModule import Synapse as Synapse
import NetworkModule
import math
import random
import array
import numpy as np

class Neuron(object):

    ##MAKE SURE TO EXAMINE DYNAMIC STATES WHEN MODIFYING!!
    def __init__(self, mPotential, X, Y, i):
        self.membranePotential = mPotential
        self.axons = []
        self.weights = []
        self.X = X
        self.Y = Y
        self.p_M = 1
        self.p_S = 1
        self.dv_S = 10
        self.dv_M = 10
        self.FIRED_VALUE = 30
        self.firing_color = "#000000"
        self.color = "#ffffff"

        self.index = i

        self.a = 0
        self.b = 0
        self.c = 0
        self.d = 0
        self.u = self.b*self.membranePotential
        self.p_E = 0
        self.p_I = 0
        self.dv_E = 0
        self.dv_I = 0
        self.dv_M = 0
        self.dv_S = 0

        self.inputs = 0
        #connection vars
        self.Lnum = 3
        self.Rnum = 4
        self.l = []
        self.r = []


    def setRL(self,r,l):
        self.r = r
        self.l = l

    def copyDynamicState(self):
        state = []
        state.append(np.float16(self.membranePotential))
        state.append(np.float16(self.a))
        state.append(np.float16(self.b))
        state.append(np.float16(self.c))
        state.append(np.float16(self.d))
        state.append(np.float16(self.u))
        state.append(np.float16(self.inputs))
        axonstate = array.array("h")
        #weightstate = array.array("h")
        #axonstate.extend(self.axons[:])
        #for i in range(0, len(self.weights)-1):
        #    weightstate.append(int(self.weights[i]*10**1))
        #state.append(axonstate)
        #state.append(weightstate)

        return state

    def loadDynamicState(self, state):
        self.membranePotential = float(state[0])
        self.a = float(state[1])
        self.b = float(state[2])
        self.c = float(state[3])
        self.d = float(state[4])
        self.u = float(state[5])
        self.inputs = float(state[6])
        #self.axons = state[7]
        #self.weights = []
        #for i in range(0, len(state[8])):
        #    self.weights.append(float(state[8][i])/(10.**1))


    #Used for GUI
    def isFiring(self):
        try:
            return self.membranePotential >= self.FIRED_VALUE
        except RuntimeWarning:
            print self.membranePotential
            return False

    #Only used by checkIfFired() which is not used
    def fire(self):
        self.u=self.u + self.d
        #self.membranePotential+=self.c
        self.membranePotential = self.c
        #for x in range(0,len(self.axons)):
        #    self.axons[x].fire()
        if isinstance(self, SensoryNeuron):
            a = []
            #print "SENSORY NEURON FIRED!!! with PSP " + str(self.dv_E) + " " + str(self.X) + ", " + str(self.Y)
        elif isinstance(self, MotorNeuron):
            a = []
            #print "MOTOR NEURON FIRED!!! " + str(self.X) + ", " + str(self.Y)

    #Only used by Synapse module which is not used
    def receivePSP(self, pspAmount):
        self.inputs+=pspAmount

    def update(self, dt):
        self.I = self.getDrive(dt) + self.inputs
        #print "I = " + str(self.I)
        #print("self.u = " + str(self.u))
        self.membranePotential += 0.5*(0.04*math.pow(self.membranePotential, 2) + 5*self.membranePotential + 140-self.u + self.I)
        self.membranePotential += 0.5*(0.04*math.pow(self.membranePotential, 2) + 5*self.membranePotential + 140-self.u + self.I)

        self.u=self.u+self.a*(self.b*self.membranePotential - self.u)

        self.inputs = 0

    def getDrive(self, dt):
        return 0

    def addAxon(self, synapse):
        self.axon.append(synapse)

    #NOT USED
    def tryConnection(self, postNeuronTuple):
        index, postNeuron = postNeuronTuple
        if isinstance(postNeuron, ExcitatoryNeuron):
            connected = random.random() - self.p_E < 0
            #connected = True
            if connected:
                self.axons.append(index)
                self.weights.append(self.dv_E)
        elif isinstance(postNeuron, InhibitoryNeuron):
            connected = random.random() - self.p_I <0
            #connected = True
            if connected:
                self.axons.append(index)
                self.weights.append(self.dv_I)
        elif isinstance(postNeuron, MotorNeuron):
            connected = random.random() - self.p_M < 0
            #connected = True
            if connected:
                self.axons.append(index)
                self.weights.append(self.dv_M)
        elif isinstance(postNeuron, SensoryNeuron):
            #connected = random.random() - self.p_S < 0
            connected = True
            if connected:
                self.axons.append(index)
                self.weights.append(self.dv_S)

    #Not used
    def checkIfFired(self):
        if self.membranePotential > self.FIRED_VALUE:
            self.fire()

    def hasFired(self):
        return self.membranePotential > self.FIRED_VALUE

    def getMembranePotential(self):
         return self.membranePotential

class InhibitoryNeuron(Neuron):

    def __init__(self, X, Y, i):
        Neuron.__init__(self,65, X,Y, i)
        self.a = 0.02 + 0.08 * 0.5
        self.b = 0.25 - 0.05 * 0.5
        self.c = -65
        self.d = 2
        self.u = self.b*self.membranePotential
        self.p_E = 0.5
        self.p_I = 0.5
        self.dv_E = -3.5
        self.dv_I = -3.5
        self.firing_color = "#0000ff"
        self.color = "#b1b1ff"

    def getDrive(self, dt):
        return 0


class ExcitatoryNeuron(Neuron):

    def __init__(self, X, Y, i):
        Neuron.__init__(self, 65, X, Y, i)
       # Neuron.__init__(self,network, 65, X,Y)
        self.a = 0.02
        self.b = 0.2
        self.c = -65 + 15 * math.pow(0.5, 2)
        self.d = 8 - 6 * math.pow(0.5, 2)
        self.u = self.b*self.membranePotential
        self.p_E = .1
        self.p_I = .5
        self.p_M = .1
        self.dv_E = 0.6
        self.dv_I = 2.7
        self.dv_M = .6
        self.firing_color = "#000000"
        self.color = "#ff0000"   #Red

    def getDrive(self, dt):
        return 0.2


class MotorNeuron(Neuron):

    def __init__(self, X, Y, i):
        Neuron.__init__(self, 65, X,Y, i)
        self.a = 0.02
        self.b = 0.2
        self.c = -65 + 15 * (0.5**2)
        self.d = 8 - 6 * (0.5**2)
        self.u = self.b*self.membranePotential
        self.p_E = .1
        self.p_I = .5
        self.dv_E = 0.6
        self.dv_I = 2.7
        self.firing_color = "#000000"
        self.color = "#808080"  #Grey

    def getDrive(self,dt):
        return 0


class SensoryNeuron_A(Neuron):

    def __init__(self, X, Y, i):
        Neuron.__init__(self,65, X, Y, i)
        self.a = 0.02
        self.b = 0.2
        self.c = -65 + 15 * math.pow(0.5, 2)
        self.d = 8 - 6 * math.pow(0.5, 2)
        self.u = self.b*self.membranePotential
        self.p_E = .1
        self.p_I = .5
        self.dv_E = 100
        self.dv_I = 2.7
        self.dv_M = 100
        self.drive = 0
        self.DRIVE_CONSTANT = 50000
        self.firing_color = "#000000"
        self.color = "#009900"     #Green

    def getDrive(self,dt):
        return self.drive

    def setDrive(self,drive):
        #print "S-NEURON AT: " + str(self.X) + ", " + str(self.Y)
        #print "DRIVE IS: " + str(drive)
        self.drive = drive*self.DRIVE_CONSTANT
        if self.drive > 200: self.drive = 200

class SensoryNeuron_B(Neuron):

    def __init__(self, X, Y, i):
        Neuron.__init__(self,65, X, Y, i)
        self.a = 0.02
        self.b = 0.2
        self.c = -65 + 15 * math.pow(0.5, 2)
        self.d = 8 - 6 * math.pow(0.5, 2)
        self.u = self.b*self.membranePotential
        self.p_E = .1
        self.p_I = .5
        self.dv_E = 100
        self.dv_I = 2.7
        self.dv_M = 100
        self.drive = 0
        self.DRIVE_CONSTANT = 50000
        self.firing_color = "#000000"
        self.color = "#0000FF"   #Blue

    def getDrive(self,dt):
        return self.drive

    def setDrive(self,drive):
        #print "S-NEURON AT: " + str(self.X) + ", " + str(self.Y)
        #print "DRIVE IS: " + str(drive)
        self.drive = drive*self.DRIVE_CONSTANT
        if self.drive > 200: self.drive = 200

class HungerNeuron(Neuron):
    def __init__(self, X, Y, i):
        Neuron.__init__(self, 65,X, Y, i)
        self.a = 0.02
        self.b = 0.2
        self.c = -65 + 15 * math.pow(0.5, 2)
        self.d = 8 - 6 * math.pow(0.5, 2)
        self.u = self.b*self.membranePotential
        self.p_E = .1
        self.p_I = .5
        self.dv_E = 100
        self.dv_I = 2.7
        self.dv_M = 100
        self.drive = 0
        self.DRIVE_CONSTANT = 50000
        self.firing_color = "#000000"
        self.color = "#660066"    #Purple