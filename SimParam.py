__author__ = 'RJ'

'''

Holder object for all parameters needed to run simulation

For ease of use, readability, simpler to manipulate

'''

class SimParam():

    def __init__(self):
        self.worldParams = (None,None,None)    #animNum,foodNum,worldSize
        ## Note should change calories to be a world param
        self.animatParams = {1 : (None,None,None,None,None,None,None,None)}  #id, type, origin, calories, inhib, excit, aa, bb

    #####  worldParam access methods  ######

    def setWorld(self,animNum,foodNum,worldSize):
        self.worldParams = (animNum,foodNum,worldSize)

    def setAnimNum(self,num):
        self.worldParams = (num,self.worldParams[1],self.worldParams[2])

    def setFoodNum(self,num):
        self.worldParams = (self.worldParams[0],num,self.worldParams[2])

    def setWorldSize(self,size):
        self.worldParams = (self.worldParams[0],self.worldParams[1],size)

    def getWorld(self):
        return self.worldParams

    def getAnimNum(self):
        return self.worldParams[0]

    def getFoodNum(self):
        return self.worldParams[1]

    def getWorldSize(self):
        return self.worldParams[2]


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


