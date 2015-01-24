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
    
class Food(Stimulus):
    
    #constructor
    #**kwargs
    #  loc : takes (x,y) coordinate for starting position
    #  smell : sets smell potency? not sure if this is needed yet, just putting here
    #  amount : initial "amount" of food
    def __init__(self, loc = (0,0), smell = 1.0, amount = 10.0, cal = 1):
        Stimulus.__init__(self,startPos = loc)
        self.amt = amount
        self.smellStr = smell
        self.calories = cal

    def getAmount(self):
        return self.amt

    def getSmell(self):
        return (self.amt * self.smellStr)/10.0  #divide by 10 to scale down to appropriate levels for network

    def getCalories(self):
        return self.calories

    def decrAmt(self):
        self.amt -= 1.0




