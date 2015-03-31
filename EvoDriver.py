__author__ = 'RJ'
'''

Driver for use when using evolutionary algorithm
Differs from masterDriver because each animat is run in only one world when using evo alg,
so task distribution needs to handled differently, no need for cluster driver

'''
import clusterDriver as cd
import spur # SSH client
import pp
import os
import numpy as np
import random
import json # for saving objects ... may not be used
import SimParam
import operator
import math
import cPickle


class EvoDriver():

    def __init__(self, usr="usrname", pw="pw"):

        #Simulation Variables
        self.IDcntr = 1          #keeps track so each animat gets unique id number
        self.worlds = []         #list of world configurations
        self.aType = "Wheel Animat"
        self.origin = (0,0) # starting position 
        self.cal = 1 # to be changed - used in food
        # food locations for standard 'worlds'
        fLocs1 = [(1,0),(-1,0),(0,1),(0,-1),(0,2),(0,-2),(2,0),(-2,0),(4,0),(-4,0),(0,4),(0,-4),(0,7),(7,0),(-7,0)]
        fLocs2 = [(1,1),(2,2),(3,3),(4,4),(3,5),(2,6),(1,7),(0,8),(-2,6),(-4,4),(-6,2),(-8,0),(-5,0),(-2,-3),(-5,-5)]
        fLocs3 = [(-2,2),(-1,0),(1,0),(-1,0),(2,-2),(3,5),(-5,5),(-8,8),(10,10),(-10,10),(10,-10),(0,-1),(0,-2),(0,-3),(0,-4)]
        self.worlds.append([1,15,20,fLocs1]) #number of animats,number of foods, world size, food locations
        self.worlds.append([1,15,20,fLocs2])
        self.worlds.append([1,15,20,fLocs3])
       
        #EvoDriver Variables
        self.cycleNum = 2       #set how many generations to run in evolution
        self.reRankNum = 100      #how many new animats to run before reRanking
        self.nodeNum = 8         #how many nodes on cluster - for load-balancing - ADJUST for new hardware
        self.maxAnimats = 1000    #how large list of parameters should be
        self.newGenSize = 100    #how many new animats to generate each iteration of evo alg
        ## NOTE when adding metrics to toTrack, make sure they are included in Simulation.filterResults
        self.toTrack = ["Energy","FoodsEaten","FindsFood","NetworkDensity","FiringRate","TotalMove"]  #names of metrics to track - keys to dictionary
        self.nodeP2Ps = [("10.2.1." + str(i) + ":60000") for i in xrange(2,12)]     #Cluster-specific P2P (peer-to-peer) address for each node on cluster (now dogwood) ...NB must change this for other clusters
        self.js = pp.Server(ncpus=0,ppservers=tuple(self.nodeP2Ps[0:8])) # prevents PP from using nodes on job server 
        self.L = 3                #number of parameter pairs used for constructing network connection weights
        self.K = 5                # number of location parameters for each parameter
        self.animats = []         #list of simParams
        self.results = []         #all results returned from Simulation, used to rank Animats on performance
        self.genData = []         #holds max,min,mean,sd,scores of each generation
        self.resultsHistory = []  #holds metric results from each generation
        self.animatHistory = []   #holds animat parameter configuration from each generation

        ## Setup
        input = raw_input("Load data from file? (y/n): ")
        if input == "y":
            lastGenNum = self.loadGen()                         #load data from save file
            self.run(genNum=lastGenNum+1)
        else:
            print "Simulator Initializing\n"
            self.generateParams(self.animats,self.maxAnimats)   #fill list with initial random animats
            print "Initial Run\n"
            self.results = self.runSims(self.animats)           #run all randomly generated animats
            self.rankAnimats()                                  #sort animats based on results
            self.run()

        ## Terminate
        self.saveResults()                                      #prompts for user to save results or not
        self.js.destroy()

    #runs simulations for each generation
    def run(self,genNum=0):
        for g in xrange(genNum,self.cycleNum):
            print "Starting generation " + str(g+1) + " of " + str(self.cycleNum)
            babies = self.mutate(self.animats[-self.reRankNum:]) #take top ranked animats and mutate
            self.randomizeWorlds(self.animats)                   #make sure random worlds change each generation
            self.animats = self.animats + babies
            self.results = self.runSims(self.animats)            #run all animats
            self.resultsHistory.append(self.results)             #self.results changes as animats are sorted, so keep store for later analysis
            self.rankAnimats()                                   #reRank all animats
            self.animats = self.animats[-self.maxAnimats:]       #keep only <self.maxAnimats> number of animats
            self.animatHistory.append(self.animats)              #save animats
            self.saveGen(g)                                      #save in case of crash/connection break

        #Generates initial animat parameters
    def generateParams(self,list,size,x0=-1,y0=-1,sigma=-1):
        print "Generating Animats\n"
        for i in xrange(size):
            sP = SimParam.SimParam()
            for j,world in enumerate(self.worlds): sP.setWorld(j+1,world[0],world[1],world[2],world[3])
            sP.setWorld(4,1,15,20,[(random.random()*20 - 20.0/2., random.random()*20 - 20.0/2.) for i in xrange(15)])
            sP.setWorld(5,1,15,20,[(random.random()*20 - 20.0/2., random.random()*20 - 20.0/2.) for i in xrange(15)])
            sP.setAnimParams(1,self.IDcntr,self.origin)
            if x0 == -1:
                #Unif[a,b), b > a: (b-a)*random + a
                sP.setX0(1,[[np.random.random_sample()*3.01 - 1.5 for x in xrange(self.K)] for x in xrange(self.L)]) #hardcoded for only 1 animat per simulation
                sP.setY0(1,[[np.random.random_sample()*3.01 - 1.5 for x in xrange(self.K)] for x in xrange(self.L)]) #hardcoded for only 1 animat per simulation
                sP.setSigma(1,[[np.random.exponential() for x in xrange(self.K)] for x in xrange(self.L)])
            else:
                sP.setX0(1,x0) #hardcoded for only 1 animat per simulation
                sP.setY0(1,y0) #hardcoded for only 1 animat per simulation
                sP.setSigma(1,sigma)
            list.append(sP)
            self.IDcntr += 1

    # Sorts list of animats based on results from simulations
    def rankAnimats(self):
        print "Ranking Animats"
        genData = []
        scores = {}    #dictionary of scores with ids as keys
        #calculate score based on each metric
        for metric in self.toTrack:
            print metric
            #build list of all results for this metric
            results = [(id,result[metric]) for id,result in self.results]
            #use simulation results to calculate max,min,mean,std so that evo performance can be tracked
            maxResult = max(results, key= lambda x: x[1])[1]
            minResult = min(results, key= lambda x: x[1])[1]
            mean = np.mean(results,axis=0)[1]
            sd = np.std(results,axis=0)[1]
            for id,result in results:
                try:
                    if metric == "TotalMove": pass               #Total movement is recorded but not used to rank animats
                    elif (metric == "NetworkDensity") or (metric == "FiringRate"):
                        scores[id] += ((result-mean)/sd)*(-1.0)  #These metrics should dock points
                    else:
                        scores[id] += (result-mean)/sd           #score is sum of z scores for all metrics
                except KeyError:                                 #KeyError when score updated for first time, so catch and set
                    if (metric == "NetworkDensity") or (metric == "FiringRate"):
                        scores[id] = ((result-mean)/sd)*(-1.0)   #These metrics should dock points
                    else:
                        scores[id] = (result-mean)/sd            #score is sum of z scores for all metrics
            genData.append((metric,maxResult,minResult,mean,sd,scores))
        #sort animats based on scores
        self.animats = self.sortByScores(scores)
        self.genData.append(genData)



    #takes dictionary of scores and sorts animat list accordingly
    def sortByScores(self,scores):
        idOrder = sorted(scores.items(), key=operator.itemgetter(1)) #return ids of animats in sorted order
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
            newx0 = self.animats[r1].getX0(1)   #hardcoded for 1 animat per sim
            newy0 = self.animats[r2].getY0(1)   #hardcoded for 1 animat per sim
            newsigma = self.animats[r2].getSigma(1)
            self.generateParams(recomb,1,newx0,newy0,newsigma)
        return randMut+recomb

    #Generic version of initRun
    def runSims(self,animats):
        print "Running Simulations"
        results = []
        simsPerNode = len(animats)/self.nodeNum              #evenly distribute number of simulations on each node
        extra = len(animats) % self.nodeNum
        nodeDrivers = []
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

    #recomputes random world food location, so it isnt the same every generation
    def randomizeWorlds(self,animats):
        for sP in animats:
            sP.setWorld(4,1,15,20,[(random.random()*20 - 20.0/2., random.random()*20 - 20.0/2.) for i in xrange(15)])
            sP.setWorld(5,1,15,20,[(random.random()*20 - 20.0/2., random.random()*20 - 20.0/2.) for i in xrange(15)])

    def saveResults(self):
        print "Simulation Complete\n"
        #input = raw_input("Enter 1 to save or anything else to close: ")
        #if input == "1":
        fn = raw_input("Enter filename to save results: ")
        print "Saving top animat for use in GUI version"
        with open(fn+'_topAnimat.txt','w') as f:
            json.dump(self.animats[-1].getAnimParams(1),f)
        print "Saving evolutionary algorithm stats"
        #printScores = raw_input("Include scores in log file? (1 if yes): ")
        #fn = raw_input("Enter filename for evo log file: ")
        with open(fn+'_detailScores.txt','w') as f:
            f.write("Animat Generation Results\n\n")
            for i,gen in enumerate(self.genData):
                f.write("\n\nResults for Generation: " + str(i))
                for metric in gen:
                    f.write("\n>>Metric: " + str(metric[0]))
                    f.write("\n>>  Max Score: " + str(metric[1]))
                    f.write("\n>>  Min Score: " + str(metric[2]))
                    f.write("\n>>  Mean: " + str(metric[3]))
                    f.write("\n>>  Standard Deviation: " + str(metric[4]))
        with open(fn+'_simpleScores.txt','w') as f:
            f.write("Animat Generation Results - each grid is mean and SD of each metric in a generation\n\n")
            for i,gen in enumerate(self.genData):
                f.write("\n" + str(i))
                for metric in gen: f.write("\n" + str(metric[3]) + " " + str(metric[4]))
                f.write("\n")
        #save metric results
        with open(fn+'_metricResults.txt','w') as f:
            f.write("Animat Scores - each line is animat id and score in each metric, each grid represents a generation\n")
            for i,gen in enumerate(self.resultsHistory):
                f.write("\n"+str(i))
                for id,result in gen:
                    f.write("\n"+str(id)+" ")
                    for metric in self.toTrack:
                        f.write(("%.4f" % result[metric]))
                        f.write(" ")
                f.write("\n")
        with open(fn+'_animatParameters.txt','w') as f:
            f.write("Animat Parameters - each grid is single generation in following configuration:\n")
            f.write("aa and bb are " + str(self.L) + " x " + str(self.K) + "\n\n")
            f.write("\nGen\nid aa aa aa aa aa aa aa aa aa aa aa aa aa aa aa ")
            f.write("bb bb bb bb bb bb bb bb bb bb bb bb bb bb bb\n\n")
            for i,gen in enumerate(self.animatHistory):
                f.write("\n"+str(i+1)+"\n")
                for anim in gen:
                    id,aa,bb = anim.getID(1), anim.getAA(1), anim.getBB(1)   #1 is animat id inside SimParam
                    f.write(str(id)+" ")
                    for row in aa:
                        for val in row:
                            f.write(("%.4f" % val))
                            f.write(" ")
                    for row in bb:
                        for val in row:
                            f.write(("%.4f" % val))
                            f.write(" ")
                    f.write("\n")
                f.write("\n")



    # Used for saving basic generation data in order to recover simulation if error occurs or connection breaks
    def saveGen(self,genNum):
        with open('gen.txt','w') as f:
            cPickle.dump((genNum,self.animats,self.animatHistory,self.results,self.genData,self.resultsHistory),f)

    def loadGen(self):
        with open('gen.txt','r') as f:
             data =  cPickle.load(f)
        self.animats,self.animatHistory,self.results,self.genData,self.resultsHistory = data[1:]
        return data[0] #return gen number left off at





ed = EvoDriver()
