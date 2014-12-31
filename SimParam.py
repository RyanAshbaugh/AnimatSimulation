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
        self.animatParams = {1 : (None,None,None,None,None,None,None,None)}  #id, type, origin, calories, inhib, excit, aa, bb

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

    def setAnimParams(self,simid,id,type,origin,cal,inhib,excit):
        self.animatParams[simid] = (id,type,origin,cal,inhib,excit,None,None)

    def setType(self,id,type):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],type,temp[2],temp[3],temp[4],temp[5],temp[6],temp[7])

    def setOrigin(self,id,origin):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],origin,temp[3],temp[4],temp[5],temp[6],temp[7])

    def setCalories(self,id,cal):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],temp[2],cal,temp[4],temp[5],temp[6],temp[7])

    def setInhib(self,id,inhib):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],temp[2],temp[3],inhib,temp[5],temp[6],temp[7])

    def setExcit(self,id,excit):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],temp[2],temp[3],temp[4],excit,temp[6],temp[7])

    def setAA(self,id,aa):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],temp[2],temp[3],temp[4],temp[5],aa,temp[7])

    def setBB(self,id,bb):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],temp[2],temp[3],temp[4],temp[5],temp[6],bb)

    def getAnimParams(self,id):
        return self.animatParams[id]

    #confusing, id is id of animat in this simulation, returns the unique id given by evo driver
    def getID(self,id):
        return self.animatParams[id][0]

    def getType(self,id):
        return self.animatParams[id][1]

    def getOrigin(self,id):
        return self.animatParams[id][2]

    def getCalories(self,id):
        return self.animatParams[id][3]

    def getInhib(self,id):
        return self.animatParams[id][4]

    def getExcit(self,id):
        return self.animatParams[id][5]

    def getAA(self,id):
        return self.animatParams[id][6]

    def getBB(self,id):
        return self.animatParams[id][7]


