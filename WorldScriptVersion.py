# -*- coding: utf-8 -*-
"""
Created on Sun Feb 16 21:33:58 2014

Main Simulation Driver File
Doubles as simulation driver and simulated "World"

contains all objects in simulated world
as well as controls flow of operations of simulation

"""

import socket
import os
import time
import NetworkModule
import GUICommunicator
import numpy as np
import AnimatShell
import Stimuli

print "Simulation Server starting. .. ..."


#dt is current "time" in miliseconds, dx is gradient grid size
def updateDel(s,delS,dt,dx=0.1):
    for i in range(0,len(s)):
        for j in range(0,len(s)):
            #try/catch blocks allow spaces outside of grid to be used in equation
            #not the most elegent solution, but works nonetheless
            try:
                a = s[i+1][j]
            except IndexError:
                a = 0.0
            try:
                b = s[i-1][j]
            except IndexError:
                b = 0.0
            try:
                c =s[i][j+1]
            except IndexError:
                c = 0.0
            try:
                d = s[i][j-1]
            except IndexError:
                d = 0.0
            delS[i][j] = ((a+b+c+d) - 4.0*s[i][j]) / (dx*dx)

#updates smell gradient
def updateSmells(s,delS,dt,foods,a=0.0001):
    updateDel(s,delS,dt)
    for i in range(0,len(s)):
        for j in range(0,len(s)):
            s[i][j] = s[i][j] + a*delS[i][j]*dt
    for i in range(0,len(foods)):
        x,y = foods[i].getPos()
        smellGrid[x][y] = foods[i].getScent() * foods[i].getAmount()

##################### Create Virtual World #############################

# Parameters
arenaSize = (20,20) #20 by 20 because GUI world x/yCoords={-10,-9..9,10}
#foodNum = 3
foodNum = 1

# Set up virtual world objects
#brain = NetworkModule.Network(testing = True) #testing=true causes constructor to skip auto-neuron config
brain = NetworkModule.Network()
#creature = AnimatShell.DumbWheelAnimat(brain)
creature = AnimatShell.WheelAnimat(brain)
#creature = AnimatShell.WheelAnimat(NetworkModule.Network(<network config data>))  #possibly how it should ultimately be so that network is only accesable by animat
foods = []
for x in range(0,foodNum):
    foods.append(Stimuli.Food(loc = (x + 1,0))) #food defaulted amt = 1 and scentPotency = 1

# Initialize Smell Grids
smellGrid = np.zeros(arenaSize,dtype = 'g') # 'g' = long double, no overflow unless caused by memory
delSmell = np.zeros(arenaSize,dtype = 'g')
for i in range(0,foodNum):
    x,y = foods[i].getPos()
    smellGrid[x][y] = foods[i].getScent()
# intialize smell gradient across grid
for x in range(100):
    updateSmells(smellGrid,delSmell,float(x)*0.001,foods)
#print delSmell

# Initialize world terrain
# more code to be added
tractionGrid = .1 #will eventually be a 2d array for storing traction

#serviceBroker will handle all communication with GUI
serviceBroker = GUICommunicator.GUICommunicator()

#--------------HACK for dumb animat---------------#
brain.hackInData()
#---------------------------------------------------#

#send all data to GUI necessary to initialize GUI objects
def sendParameters():
    neuronNum = brain.getTotalNeuronNum() #HACK should call animat for brain size ultimately
    #first request will always be parameter data
    print serviceBroker.waitForRequest()
    serviceBroker.sendTuple((neuronNum,1,foodNum))  #(<total neuron number>,<number of animats>,<number of foods>)
    print brain.getTotalNeuronNum()
    #GUIdriver then will always request for each neuron location for plotting
    for x in range(0,neuronNum):
        print serviceBroker.waitForRequest()
        print (brain.neurons[x].X, brain.neurons[x].Y)
        serviceBroker.sendTuple((x, brain.neurons[x].X, brain.neurons[x].Y)) #HACK directly accesing network just for testing purposes
    #GUIdriver then will always request for food, untill more stimuli are added
    sendFoodData()
    #serviceBroker.waitForRequest()
    #serviceBroker.sendTuple(<food data tuple>) #will be stored in world.py

def sendFoodData():
    for q in range(0,len(foods)):
        print q
        print serviceBroker.waitForRequest()
        x,y = foods[q].getPos()
        a = foods[q].getAmount()
        print x,y,a
        serviceBroker.sendTuple((x,y,a))

def determineSmellStrength(pos):
    smellStr = 0
    for food in foods:
        smellStr += (food.getAmount()) / (getDist(food.getPos(), pos)**3)
    #print("smellStr " + str(smellStr))
    return smellStr
    #return smellGrid[pos[0]][pos[1]]

def getDist(x1, x2):
    return np.sqrt( (x1[0] - x2[0])**2 + (x1[1] - x2[1])**2)

def determineTraction(pos):
    #uses position to look up in traction grid and return appropriate traction
    #needs to be implemented
    pass


######################### Main Simulation Loo p############################
ctrl = True
while ctrl:

    #Establish the connection
    serviceBroker.waitForConnection() #script pauses here until connection is made
    try:
        sendParameters()
        advance = raw_input("Press Enter to Start Simulation")
        #this loop will eventually run for an unpredetermined time


        #for t in range(0,len(brain.hackedPosHistory)):
        t = 0
        dt = 1
        while True:
            #print "Time: " + str(t)
            currentLocation = creature.getPosition()
            #updateSmells(smellGrid,delSmell,t,foods)
            smells = [];
            for data in creature.getSenseNeuronLocations():
                n, x, y = data
                position = [x,y]
                #print "POSITION == " + str(position)
                smell = (n, determineSmellStrength(position))
                #print "SMELL == " + str(smell)
                smells.append(smell)
            creature.runNetwork(dt, smells)
            #smells = determineSmellStrength(currentLocation)
            traction = determineTraction(currentLocation) #does nothing right now
            #creature.hackMove(traction,smells,t)    #HACK for dumb animat
            creature.move(traction,smells,t)  #what should be implemented
            movData = creature.getMovementData(t)    #always returns current frames data
            #request for panel 1 data, tuple of (x,y,direc)
            serviceBroker.waitForRequest()
            serviceBroker.sendTuple(movData)
            #request for panel 2 data, all firings in one tuple
            serviceBroker.waitForRequest()
            serviceBroker.sendTuple(brain.getHackedFirings(t)) #HACK for dumb animat
            #serviceBroker.sendTuple(brain.getFirings(t))
            #advance = raw_input("") #used for stepping through frame by frame
            t = t + dt
        serviceBroker.closeConnection()
        print "closed"

    except IOError:
        #Send responseclient disconnected
        print "Error - Client has closed Connection"
        #Close client socket
        serviceBroker.closeConnection()
        ctrl = False

serviceBroker.closeServer()
