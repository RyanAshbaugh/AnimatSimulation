#from NeuronModule import Neuron

class Synapse():
	
	def __init__(self,postNeuron,PSP):
		self.postNeuron = postNeuron
		self.PSP = PSP
	
	def fire(self):
		self.postNeuron.receivePSP(self.PSP)