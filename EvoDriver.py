__author__ = 'RJ'
'''

Driver for use when using evolutionary algorithm
Differs from masterDriver because each animat is run in only one world when using evo alg,
so task distribution needs to handled differently, no need for cluster driver

'''
import clusterDriver as cd
import spur
import pp
import os
import numpy as np
import random
import json
import SimParam
import operator
import math

class EvoDriver():

    def __init__(self, usr="lucasrh", pw="Grammercy1101grove"):
        ## Variable Declaration
        #Simulation Variables
        self.IDcntr = 1          #keeps track so each animat gets unique id number
        self.aNum = 1            #number of animats in each simulation
        self.fNum = 15           #number of food items in each simulation
        self.wSize = 20          #size of world of simulation
        self.aType = "Wheel Animat"
        self.origin = (1,0)
        self.cal = 10
        self.inhib = [80,.02,.25,-65,2]
        self.excit = [320,.02,.2,-65,8]
        #self.izekVars = [80,.02,.25,-65,2,320,.02,.2,-65,8]    #parameters for izekevich parameters

        self.cycleNum = 10       #how many cycles on main loop
        self.reRankNum = 100      #how many new animats to run before reRanking
        self.nodeNum = 8         #how many nodes on cluster
        self.maxAnimats = 1000    #how large list of parameters should be
        self.newGenSize = 100    #how many new animats to generate each iteration of evo alg
        self.toTrack = ["FindsFood","AvgMove"]         #list of metrics to track
        self.animats = []         #list of simParams
        self.results = []         #all results returned from Simulation, used to rank Animats on performance
        self.nodeP2Ps = [("10.2.1." + str(i) + ":60000") for i in xrange(2,12)]     #P2P address for each node on cluste
        self.js = pp.Server(ncpus=0,ppservers=tuple(self.nodeP2Ps[0:8]))
        self.L = 3                #used for network connection probability
        self.K = 5                #used for network connectino probability
        self.genData = []

        ## Setup
        print "Simulator Initializing\n"
        self.generateParams(self.animats,self.maxAnimats)             #fill list with initial random animats
        print "Initial Run\n"
        self.results = self.runSims(self.animats)              #run all randomly generated animats
        self.rankAnimats()                            #sort animats based on results

        ## Main Loop
        for g in xrange(self.cycleNum):
            print "Starting generation " + str(g+1) + " of " + str(self.cycleNum)
            #since animat list is only reRanked every x amount of times, run top x animats in parallel
            babies = self.mutate(self.animats[-self.reRankNum:]) #take top ranked animats and mutate
            self.animats = self.animats + babies
            self.results = self.runSims(self.animats)                                 #run simulations on top animats
            self.rankAnimats()                                   #reRank all animats
            self.animats = self.animats[-self.maxAnimats:]       #keep only <self.maxAnimats> number of animats

        self.saveResults()                                       #prompts for user to save results or not
        self.js.destroy()


        #Generates initial animat parameters
    def generateParams(self,list,size,aa=-1,bb=-1):
        print "Generating Animats\n"
        for i in xrange(size):
            sP = SimParam.SimParam()
            sP.setWorld(self.aNum,self.fNum,self.wSize)
            sP.setAnimParams(1,self.IDcntr,self.aType,self.origin,self.cal,self.inhib,self.excit)
            if aa == -1:
                aa = [[np.random.laplace()*.25 for x in xrange(self.K)] for x in xrange(self.L)] #create LxK arrays
                bb = [[np.random.laplace()*.25 for x in xrange(self.K)] for x in xrange(self.L)]
                for x in xrange(self.L):
                    aa[x][0] = np.sum(np.abs(aa[x][1:]))
                    bb[x][0] = np.sum(np.abs(bb[x][1:]))
                sP.setAA(1,aa) #hardcoded for only 1 animat per simulation
                sP.setBB(1,bb) #hardcoded for only 1 animat per simulation
            else:
                sP.setAA(1,aa)
                sP.setBB(1,bb)
            list.append(sP)
            self.IDcntr += 1



    # This will take the list of animats, and sort them based on performance metrics
    def rankAnimats(self):
        print "Ranking Animats"
        genData = []
        scores = {}    #dictionary of scores with ids as keys
        for result in self.results:
            #print result
            scores[result[0]] = 0
        #calculate score based on each metric
        for metric in self.toTrack:
            print metric
            #find distribution of results
            maxScore = max(self.results, key=lambda x: x[1][metric])[1][metric]
            minScore = min(self.results, key=lambda x: x[1][metric])[1][metric]
            for result in self.results:
                #to give equal weight, scores calculated based on dist of each metric result
                try:
                    #avgMove needs dist of results to score, cannot be done solely in simulation object, unlike others
                    if metric == "AvgMove":
                        print "int if avgMove"
                        medScore = (maxScore - minScore)/2.0
                        #compare to med score since dont want to move too little or too much
                        score = medScore/result[1][metric]
                        if math.isinf(score): score = 0         #moves too much or too little so 0
                        #print "avgMove score" ,score
                        scores[result[0]] += score
                    else:
                        print "in else"
                        scores[result[0]] += (result[1][metric])
                        #print "else score", (result[1][metric])
                except ZeroDivisionError:
                    pass #max is zero so will not affect score
                except RuntimeWarning:
                    pass #sometimes above error thrown as warning instead
            mean = np.mean(scores.items(),axis=0)[1]
            std = np.std(scores.items(),axis=0)[1]
            genData.append((metric,maxScore,minScore,mean,std,scores))

        #sort based on scores
        self.animats = self.sortByScores(scores)
        self.genData.append(genData)



    #takes dictionary of scores and sorts animat list accordingly
    def sortByScores(self,scores):
        idOrder = sorted(scores.items(), key=operator.itemgetter(1)) #return ids of animats in sorted order
        print idOrder
        newAnim = []
        for id in idOrder:
            for sP in self.animats:
                if sP.getID(1) == id[0]:
                    newAnim.append(sP)
                    self.animats.remove(sP)
                    break
        return newAnim


    #takes in list of animats, then returns list of mutated animats
    def mutate(self,animats):
        print "Mutating"
        #Random mutation for first 50
        randMut = []
        self.generateParams(randMut,self.newGenSize/2)
        #Random recombination for last 50
        #Combines aa,bb
        recomb = []
        for i in xrange(self.newGenSize/2):
            r1 = random.randint(0,len(animats)-1)
            r2 = random.randint(0,len(animats)-1)
            newaa = self.animats[r1].getAA(1)   #hardcoded for 1 animat per sim
            newbb = self.animats[r2].getBB(1)   #hardcoded for 1 animat per sim
            self.generateParams(recomb,1,aa=newaa,bb=newbb)
        return randMut+recomb

    #Generic version of initRun
    def runSims(self,animats):
        print "Running Simulations"
        results = []
        simsPerNode = len(animats)/self.nodeNum              #evenly distribute number of simulations on each node
        extra = len(animats) % self.nodeNum
        nodeDrivers = []
        #animList = self.getAnimList(animats)
        for i in xrange(self.nodeNum):                          #need to create driver loaded with animats for each node
            temp = animats[i*simsPerNode:(i+1)*simsPerNode]#extract animats to run on current driver
            nodeDrivers.append(cd.EvoClusterDriver(i+1,temp,self.toTrack))
        if not(extra == 0):
            temp = animats[-extra:]                        #extract remaining animats
            nodeDrivers.append(cd.EvoClusterDriver(self.nodeNum+1,temp,self.toTrack))
        #js = pp.Server(ncpus=0,ppservers=tuple(self.nodeP2Ps[0:8]),restart=True)  #connect to each node
        jobs = [self.js.submit(node.startNode,modules=("clusterDriver","pp","SimParam")) for node in nodeDrivers] #send each driver to node
        for job in jobs:   #execute each job
            results += job()            #function output not saved, because callback should fill self.results
        self.js.wait()

        return results
        #return results
        #for nd in nodeDrivers: self.results += nd.getResults()    #get results and store
        #js.wait()
        #js.destroy()

    def saveResults(self):
        print "Simulation Complete\n"
        input = raw_input("Enter 1 to save or anything else to close: ")
        if input == "1":
            fn = raw_input("Enter filename for animat data to run in GUI: ")
            print "Saving top animat for use in GUI version"
            with open(fn+'.txt','w') as f:
                json.dump(self.animats[-1].getAnimParams(1),f)
            print "Saving evolutionary algorithm stats"
            printScores = raw_input("Include scores in log file? (1 if yes): ")
            fn = raw_input("Enter filename for evo log file: ")
            with open(fn+'_detail.txt','w') as f:
                f.write("Animat Generation Results\n\n")
                for i,gen in enumerate(self.genData):
                    f.write("\n\nResults for Generation: " + str(i))
                    for metric in gen:
                        f.write("\n>>Metric: " + str(metric[0]))
                        f.write("\n>>  Max Score: " + str(metric[1]))
                        f.write("\n>>  Min Score: " + str(metric[2]))
                        f.write("\n>>  Mean: " + str(metric[3]))
                        f.write("\n>>  Standard Deviation: " + str(metric[4]))
                        if printScores == '1':
                            f.write("\n>>  Scores after ranking this metric:\n" + str(metric[5]))
            with open(fn+'_simple.txt','w') as f:
                f.write("Animat Generation Results - each grid is mean and SD of each metric in a generation\n\n")
                for i,gen in enumerate(self.genData):
                    f.write("\n" + str(i))
                    for metric in gen: f.write("\n" + str(metric[3]) + " " + str(metric[4]))
                    f.write("\n")






class evoAnimat():

    def __init__(self,aa,bb,iv,id):
        self.aa = aa
        self.bb = bb
        self.izekVars = iv
        self.id = id
        self.score = 0
        self.results = []





