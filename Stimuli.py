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
        return self.pos


##################### Food CLass ######################################################
                 ## Basic food object ##

class GoodFood(Stimulus):

    def __init__(self,loc,amount=10.0):
        Stimulus.__init__(self,startPos = loc)
        self.amt = amount
        self.smellStr = 5
        self.calories = 10
        self.image = "apple.png"

    def getAmount(self):
        return self.amt

    def getSmell(self):
        return (self.amt * self.smellStr)/10.0  #divide by 10 to scale down to appropriate levels for network

    def getCalories(self):
        return self.calories

    def decrAmt(self):
        self.amt -= 1.0

class BadFood(Stimulus):

    def __init__(self,loc,amount=10.0):
        Stimulus.__init__(self,startPos = loc)
        self.amt = amount
        self.smellStr = 1
        self.calories = 5
        self.image = "beer.png"

    def getAmount(self):
        return self.amt

    def getSmell(self):
        return (self.amt * self.smellStr)/10.0  #divide by 10 to scale down to appropriate levels for network

    def getCalories(self):
        return self.calories

    def decrAmt(self):
        self.amt -= 1.0




