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
        self.animatParams = {1 : (None,None,None,None,None)}  #id, origin, x0, y0, sigma

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

    def setAnimParams(self,id,animId,origin):
        self.animatParams[id] = (animId,origin,None,None,None)

    def setOrigin(self,id,origin):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],origin,temp[2],temp[3],temp[4])

    def setX0(self,id,x0):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],x0,temp[3],temp[4])

    def setY0(self,id,y0):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],temp[2],y0,temp[4])

    def setSigma(self,id,sigma):
        temp = self.animatParams[id]
        self.animatParams[id] = (temp[0],temp[1],temp[2],temp[3],sigma)

    def getAnimParams(self,id):
        return self.animatParams[id]

    #confusing, id is id of animat in this simulation, returns the unique id given by evo driver
    def getID(self,id):
        return self.animatParams[id][0]

    def getOrigin(self,id):
        return self.animatParams[id][1]

    def getX0(self,id):
        return self.animatParams[id][2]

    def getY0(self,id):
        return self.animatParams[id][3]

    def getSigma(self,id):
        return self.animatParams[id][4]


