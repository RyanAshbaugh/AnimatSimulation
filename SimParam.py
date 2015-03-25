__author__ = 'RJ'

'''

Holder object for all parameters needed to run simulation

For ease of use, readability, simpler to manipulate

'''

class SimParam():

    def __init__(self):
        #general usage vars
        self.worldParams = {1 : (None,None,None,None)}    #animNum,foodNum,worldSize,foodLocs
        ## Note should change calories to be a food/world param
        self.animatParams = {1 : (None,None,None,None)}  #id, origin, aa, bb

        #vars for evoDriver usage
        self.worldToRun = 1     #used so World.py knows which world param to extract and use
    #####  worldParam access methods  ######

    def setWorld(self,id,animNum,foodNum,worldSize,foodLocs):
        self.worldParams[id] = (animNum,foodNum,worldSize,foodLocs)

    def setAnimNum(self,id,num):
        self.worldParams[id] = (num,self.worldParams[1],self.worldParams[2],self.worldParams[3])

    def setFoodNum(self,id,num):
        self.worldParams[id] = (self.worldParams[0],num,self.worldParams[2],self.worldParams[3])

    def setWorldSize(self,id,size):
        self.worldParams[id] = (self.worldParams[0],self.worldParams[1],size,self.worldParams[3])

    def setFoodLocs(self,id,locs):
        self.worldParams[id] = (self.worldParams[0],self.worldParams[1],self.worldParams[2],locs)


    def getWorldNum(self):
        return len(self.worldParams)

    def getWorld(self,id):
        return self.worldParams[id]

    def getAnimNum(self,id):
        return self.worldParams[id][0]

    def getFoodNum(self,id):
        return self.worldParams[id][1]

    def getWorldSize(self,id):
        return self.worldParams[id][2]

    def getFoodLocs(self,id):
        return self.worldParams[id][3]


    #####  animatParam access methods  ######

    def setAnimParams(self,simid,id,origin):
        self.animatParams[simid] = (id,origin,None,None)

    def setOrigin(self,id,origin):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],origin,temp[2],temp[3])

    def setAA(self,id,aa):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],aa,temp[3])

    def setBB(self,id,bb):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],temp[2],bb)

    def getAnimParams(self,id):
        return self.animatParams[id]

    #confusing, id is id of animat in this simulation, returns the unique id given by evo driver
    def getID(self,id):
        return self.animatParams[id][0]

    def getOrigin(self,id):
        return self.animatParams[id][1]

    def getAA(self,id):
        return self.animatParams[id][2]

    def getBB(self,id):
        return self.animatParams[id][3]


