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
    def __init__(self, startPos = (0,0)):
        self.pos = startPos

    def getPos(self):
        return [self.pos[0],self.pos[1]]


##################### Food CLass ######################################################
                 ## Basic food object ##

class Food_A(Stimulus):

    def __init__(self,loc,amount=10.0):
        Stimulus.__init__(self,startPos = loc)
        self.type = "A"
        self.amt = amount
        self.smellStr = 1
        self.calories = 10
        self.image = "apple_bunch.png"

    def getType(self):
        return self.type

    def getAmount(self):
        return self.amt

    def getSmell(self):
        return (self.amt * self.smellStr)/10.0  #divide by 10 to scale down to appropriate levels for network

    def getCalories(self):
        return self.calories

    def decrAmt(self):
        self.amt -= 1.0

class Food_B(Stimulus):

    def __init__(self,loc,amount=10.0):
        Stimulus.__init__(self,startPos = loc)
        self.type = "B"
        self.amt = amount
        self.smellStr = 1
        self.calories = 5
        self.image = "apple.png"

    def getType(self):
        return self.type

    def getAmount(self):
        return self.amt

    def getSmell(self):
        return (self.amt * self.smellStr)/10.0  #divide by 10 to scale down to appropriate levels for network

    def getCalories(self):
        return self.calories

    def decrAmt(self):
        self.amt -= 1.0




