# -*- coding: utf-8 -*-
"""
Created on Tue Apr 22 18:46:58 2014

World Stimulus Module
--food,prey etc

Contains base Stimulus class and all derived classes
"""

##################### Stimuli Base Class ######################################################
                 ## Anything animat can interact with in world ##
class Stimulus():
    
    #constructor
    #**kwargs
    #  startPos : takes (x,y) coordinate for starting position
    #  potency : sets smell potency? not sure if this is needed yet, just putting here
    def __init__(self, startPos = (0,0), potency = 1):
        self.pos = [startPos[0], startPos[1]]
        self.scentPotency = potency
        
    def getPos(self):
        return self.pos
    
    #returns scent strength    
    def getScent(self):
        return self.scentPotency

##################### Food CLass ######################################################
                 ## Basic food object ##
    
class Food(Stimulus):
    
    #constructor
    #**kwargs
    #  loc : takes (x,y) coordinate for starting position
    #  smell : sets smell potency? not sure if this is needed yet, just putting here
    #  amount : initial "amount" of food
    def __init__(self, loc = (0,0), smell = 1.0, amount = 10.0):
        Stimulus.__init__(self,startPos = loc, potency = smell)
        self.amt = amount
        
        
    def getAmount(self):
        return self.amt