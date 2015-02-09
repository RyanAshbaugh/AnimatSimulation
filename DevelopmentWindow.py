__author__ = 'RJ'

import Tkinter as tk
from Graph import Graph
from PIL import ImageTk
from PIL import Image
import numpy as np
from VideoBar import VideoBar
import GUIdriver
import ParametersWindow
import SimulationEngine
import cPickle
import tkFileDialog
import json
import SimParam
import random

class DevelopmentWindow():

    def __init__(self):
        self.worlds = []
        ## Set up worlds
        fLocs1 = [(2,0),(-2,0),(0,2),(0,-2),(0,3),(0,-3),(3,0),(-3,0),(4,0),(-4,0),(0,4),(0,-4),(0,7),(7,0),(-7,0)]
        fLocs2 = [(1,1),(2,2),(3,3),(4,4),(3,5),(2,6),(1,7),(0,8),(-2,6),(-4,4),(-6,2),(-8,0),(-5,0),(-2,-3),(-5,-5)]
        fLocs3 = [(-2,2),(-1,0),(1,0),(-1,0),(2,-2),(3,5),(-5,5),(-8,8),(10,10),(-10,10),(10,-10),(0,-1),(0,-2),(0,-3),(0,-4)]
        fLocs4 = [(random.random()*20 - 20.0/2., random.random()*20 - 20.0/2.) for i in xrange(20)]
        fLocs5 = [(random.random()*20 - 20.0/2., random.random()*20 - 20.0/2.) for i in xrange(20)]
        self.worlds.append([1,15,20,fLocs1])
        self.worlds.append([1,15,20,fLocs2])
        self.worlds.append([1,15,20,fLocs3])
        self.worlds.append([1,20,20,fLocs4])
        self.worlds.append([1,20,20,fLocs5])

        #parameters
        self.sP = SimParam.SimParam()
        self.sP.setWorld(1,self.worlds[0][0],self.worlds[0][1],self.worlds[0][2],self.worlds[0][3])   #change first index to change default world
        self.sP.setWorld(2,self.worlds[1][0],self.worlds[1][1],self.worlds[1][2],self.worlds[1][3])
        self.sP.setWorld(3,self.worlds[2][0],self.worlds[2][1],self.worlds[2][2],self.worlds[2][3])
        self.sP.setWorld(4,self.worlds[3][0],self.worlds[3][1],self.worlds[3][2],self.worlds[3][3])
        self.sP.setWorld(5,self.worlds[4][0],self.worlds[4][1],self.worlds[4][2],self.worlds[4][3])
        self.sP.setAnimParams(1,1,"Wheel Animat",(1,0),1,[80,.02,.25,-65,2],[320,.02,.2,-65,8])
        self.paused = True                     #paused?
        self.lastTime = 0
        self.sim_msps = 0
        self.dis_t = 1                         #the t being displayed
        self.buff_t = 0
        self.writeInterval = 100
        self.simHistory = {}                    #this will fill with produced worlds from the simulations
        self.simEngine = SimulationEngine.SimulationEngine()
        self.developmentHistory = {}
        self.layoutHist = 300                   #y value holder for new aniimat config button placement
        self.layoutList = []                    # holds config/delete animat buttons and labels for any animats other than default

        #intialize TK
        self.root = tk.Tk()
        self.root.title("Development Simulation")
        self.canvas = tk.Canvas(self.root, width=1080, height=720)
        self.canvas.pack()

        #some general-purpose colors
        self.colorWhite = "#ffffff"
        self.colorGrey = "#dddddd"
        self.colorBlack = "#000000"
        self.colorLightBlue = "#ADD8E6"
        self.colorBlue = "#0000ff"
        self.colorRed = "#ff0000"

        #file options
        self.file_opt = options = {}
        options['defaultextension'] = '.netsim'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt'), ('Simulation Files', '.netsim')]
        #options['initialdir'] = 'C:\\'
        options['initialfile'] = '.netsim'
        options['parent'] = self.root
        options['title'] = 'Save Simulation As...'

        #set up menu bar
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Start Simulation", command=self.startSimulation)
        filemenu.add_command(label="Save Current Development Simulation", command=self.saveCurrentSimulation)
        filemenu.add_command(label="Load Development from File", command=self.loadSimulationFromFile)
        filemenu.add_separator()
        filemenu.add_command(label="Load Results from Evolutionary Algorithm",command=self.loadEvo)
        filemenu.add_separator()
        filemenu.add_command(label="Exit",command=self.root.destroy)
        menubar.add_cascade(label="File", menu=filemenu)
        speedmenu = tk.Menu(menubar, tearoff=0)
        speedmenu.add_command(label="1ms", command=lambda:self.setWriteInterval(1))
        speedmenu.add_command(label="25ms", command=lambda:self.setWriteInterval(25))
        speedmenu.add_command(label="50ms", command=lambda:self.setWriteInterval(50))
        speedmenu.add_command(label="100ms", command=lambda:self.setWriteInterval(100))
        speedmenu.add_command(label="1s", command=lambda:self.setWriteInterval(1000))
        speedmenu.add_command(label="Do not write")
        speedmenu.invoke(3)   #default write interval is 100
        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label="Parameters",command = self.editParameters)
        editmenu.add_cascade(label="Write Interval", menu=speedmenu)
        menubar.add_cascade(label="Edit", menu=editmenu)
        self.root.config(menu=menubar)

        #Set up neuron graph and text log box and control bar
        self.neuronGraph = Graph(self.root, [75, 75, 475, 475], [-1.1, 1.1, -1.1, 1.1])
        self.neuronGraph.plotCircle((2, 2), (0, 0), self.colorWhite)
        self.neuronGraph.title("Development")
        self.neuronGraph.xlabel("XAXIS")
        self.neuronGraph.ylabel("YAXIS")
        self.neuronGraph.draw(self.canvas)

        #Set up World Parameter Options
        self.animNum_sv = tk.StringVar()
        self.animNum_sv.set(str(self.sP.getAnimNum(1)))
        self.foodNum_sv = tk.StringVar()
        self.foodNum_sv.set(str(self.sP.getFoodNum(1)))
        self.arenaSize_sv = tk.StringVar()
        self.arenaSize_sv.set(str(self.sP.getWorldSize(1)))
        title = tk.Label(self.root, text="Parameter Settings",font="bold",relief="ridge",padx=5,pady=5)
        title.place(x=600,y=75)
        # animNum_l = tk.Label(self.root, text="Number of Animats:")
        # animNum_l.place(x=600,y=125)
        # animNum_e = tk.Entry(self.root, textvariable=self.animNum_sv)
        # animNum_e.place(x=750,y=125)
        foodNum_l = tk.Label(self.root, text="Number of Foods:")
        foodNum_l.place(x=600,y=125)
        foodNum_e = tk.Entry(self.root, textvariable=self.foodNum_sv)
        foodNum_e.place(x=750,y=125)
        arenaSize_l = tk.Label(self.root, text="World Size: ")
        arenaSize_l.place(x=600,y=150)
        arenaSize_e = tk.Entry(self.root, textvariable=self.arenaSize_sv)
        arenaSize_e.place(x=750,y=150)
        #button for retreiving parameters
        self.setParamButton = tk.Button(self.root, text="Set Parameters", command=self.saveParameters)
        self.setParamButton.place(x=675,y=175)

        title2 = tk.Label(self.root, text="Animat Settings", font="bold", relief="ridge",padx=5,pady=5)
        title2.place(x=600,y=250)
        defaultAnim_l = tk.Label(self.root, text="* Animat 1: ", font="bold")
        defaultAnim_l.place(x=600,y=300)
        #Animat Buttons
        animConfigButton = tk.Button(self.root, text="Configure Animat", command=lambda: self.configAnimat(0))
        animConfigButton.place(x=700,y=300)
        newAnimButton = tk.Button(self.root, text="Add New Animat",bg='green', command=self.addAnimat)
        newAnimButton.place(x=750,y=250)

        self.videoBar = VideoBar(self.canvas, (100, 515, 500, 525), (0, 5000), self.timeClicked)

        #set up images
        playImage = ImageTk.PhotoImage(Image.open("play.png").resize((40, 40), Image.ANTIALIAS))
        pauseImage = ImageTk.PhotoImage(Image.open("pause.png").resize((40,40), Image.ANTIALIAS))
        stopImage = ImageTk.PhotoImage(Image.open("stop.png").resize((40,40), Image.ANTIALIAS))
        restartImage = ImageTk.PhotoImage(Image.open("restart.png").resize((40,40), Image.ANTIALIAS))
        step_fImage = ImageTk.PhotoImage(Image.open("step_f.png").resize((40,40), Image.ANTIALIAS))
        step_bImage = ImageTk.PhotoImage(Image.open("step_b.png").resize((40,40), Image.ANTIALIAS))

        #video control buttons
        self.playButton = tk.Button(self.root, command = self.play, image = playImage)
        self.playButton.place(x = 100,y=545)
        self.pauseButton = tk.Button(self.root, command = self.pause, image = pauseImage)
        self.pauseButton.place(x=155,y=545)
        self.stopButton = tk.Button(self.root, command = self.stop, image = stopImage)
        self.stopButton.place(x=210,y=545)
        self.restartButton = tk.Button(self.root, command = self.restart, image = restartImage)
        self.restartButton.place(x=265, y=545)
        self.step_bButton = tk.Button(self.root, command = self.step_b, image = step_bImage)
        self.step_bButton.place(x=320, y=545)
        self.step_fButton = tk.Button(self.root, command = self.step_f, image = step_fImage)
        self.step_fButton.place(x=375, y=545)

        #speed scale bar
        spdlabel = self.canvas.create_text(357, 615, text="Select Speed (ms/s)")
        self.speedScale = tk.Scale(self.root, from_=0, to=500, orient = "horizontal", length = 300)
        self.speedScale.place(x = 215, y = 625)
        self.root.after(0, self.refreshScreen)
        self.root.mainloop()

    def refreshScreen(self):
        #print(len(self.developmentHistory.keys()))
        if not self.paused:
            self.developmentHistory.update(self.simEngine.getNewDevelopments())
            t = sorted(self.developmentHistory.keys())[len(self.developmentHistory.keys())-1]
            network = self.developmentHistory[t]
            self.neuronGraph.plotCircle((2, 2), (0, 0), self.colorWhite)
            for neuron in network.getNeurons():
                self.neuronGraph.plotCircle((.05, .05), (neuron.X, neuron.Y), neuron.firing_color if neuron.isFiring() else neuron.color)
            self.neuronGraph.draw(self.canvas)

        self.root.after(1 if int(np.floor(1000/20)) < 1 else int(np.floor(1000/20)), self.refreshScreen)

    #Button Functions
    def play(self):
        self.simEngine.startNewDevelopmentSim()
        self.paused = False


    def pause(self):
        pass

    def stop(self):
        self.simEngine.stopSimulation()

    def restart(self):
        self.developmentHistory = {}
        self.simEngine.startNewDevelopmentSim()

    def step_b(self):
        pass

    def step_f(self):
        pass

    def timeClicked(self):
        pass

    def saveParameters(self):
        self.sP.setWorld((int)(self.animNum_sv.get()),self.foodNum_sv.get(),self.arenaSize_sv.get())
        #self.parameters[0] = (int)(self.animNum_sv.get())
        #self.parameters[1] = (int)(self.foodNum_sv.get())
        #self.parameters[2] = (int)(self.arenaSize_sv.get())
        saved = tk.Label(self.root, text="***SAVED***", font="bold",fg="red")
        saved.place(x=775,y=75)
        saved.after(2000,saved.destroy)

    def configAnimat(self,id):
        self.win = tk.Toplevel(height=600,width=700)
        self.win.title("Animat Configuration")
        title = tk.Label(self.win, text="Configure Animat", font="bold", relief="ridge",padx=5,pady=5)
        #set up entry variables
        self.type_sv = tk.StringVar()
        self.type_sv.set(str(self.sP.getType(id)))
        self.origin_sv = tk.StringVar()
        self.origin_sv.set(str(self.sP.getOrigin(id)))
        self.cal_sv = tk.StringVar()
        self.cal_sv.set(str(self.sP.getCalories(id)))
        self.inhibNum_sv = tk.StringVar()
        temp = self.sP.getInhib(id)
        self.inhibNum_sv.set(temp[0])
        self.inhibA_sv = tk.StringVar()
        self.inhibA_sv.set(temp[1])
        self.inhibB_sv = tk.StringVar()
        self.inhibB_sv.set(temp[2])
        self.inhibC_sv = tk.StringVar()
        self.inhibC_sv.set(temp[3])
        self.inhibD_sv = tk.StringVar()
        self.inhibD_sv.set(temp[4])
        temp = self.sP.getExcit(id)
        self.excitNum_sv = tk.StringVar()
        self.excitNum_sv.set(temp[0])
        self.excitA_sv = tk.StringVar()
        self.excitA_sv.set(temp[1])
        self.excitB_sv = tk.StringVar()
        self.excitB_sv.set(temp[2])
        self.excitC_sv = tk.StringVar()
        self.excitC_sv.set(temp[3])
        self.excitD_sv = tk.StringVar()
        self.excitD_sv.set(temp[4])

        #labels and entries
        type_l = tk.Label(self.win, text="Type: " ,font="bold")
        self.type_e = tk.Entry(self.win, textvariable=self.type_sv)
        origin_l = tk.Label(self.win, text="Origin: ", font="bold")
        self.origin_e = tk.Entry(self.win, textvariable=self.origin_sv)
        cal_l = tk.Label(self.win, text="Calories: ", font="bold")
        self.cal_e = tk.Entry(self.win, textvariable=self.cal_sv)
        inhibNum_l = tk.Label(self.win, text="Inhibitory Neurons:", font="bold")
        self.inhibNum_e = tk.Entry(self.win, textvariable=self.inhibNum_sv)
        inhibA_l = tk.Label(self.win, text="a:", font="bold")
        self.inhibA_e = tk.Entry(self.win, textvariable=self.inhibA_sv,width=4)
        inhibB_l = tk.Label(self.win, text="b:", font="bold")
        self.inhibB_e = tk.Entry(self.win, textvariable=self.inhibB_sv,width=4)
        inhibC_l = tk.Label(self.win, text="c:", font="bold")
        self.inhibC_e = tk.Entry(self.win, textvariable=self.inhibC_sv,width=4)
        inhibD_l = tk.Label(self.win, text="d:", font="bold")
        self.inhibD_e = tk.Entry(self.win, textvariable=self.inhibD_sv,width=4)
        excitNum_l = tk.Label(self.win, text="Excitatory Neurons:", font="bold")
        self.excitNum_e = tk.Entry(self.win, textvariable=self.excitNum_sv)
        excitA_l = tk.Label(self.win, text="a:", font="bold")
        self.excitA_e = tk.Entry(self.win, textvariable=self.excitA_sv,width=4)
        excitB_l = tk.Label(self.win, text="b:", font="bold")
        self.excitB_e = tk.Entry(self.win, textvariable=self.excitB_sv,width=4)
        excitC_l = tk.Label(self.win, text="c:", font="bold")
        self.excitC_e = tk.Entry(self.win, textvariable=self.excitC_sv,width=4)
        excitD_l = tk.Label(self.win, text="d:", font="bold")
        self.excitD_e = tk.Entry(self.win, textvariable=self.excitD_sv,width=4)

        #placements
        title.place(x=2,y=2)
        type_l.place(x=40,y=50)
        self.type_e.place(x=185,y=50)
        origin_l.place(x=40,y=75)
        self.origin_e.place(x=185,y=75)
        cal_l.place(x=40,y=100)
        self.cal_e.place(x=185,y=100)
        inhibNum_l.place(x=40,y=125)
        self.inhibNum_e.place(x=185,y=125)
        inhibA_l.place(x=260,y=125)
        self.inhibA_e.place(x=280,y=125)
        inhibB_l.place(x=310,y=125)
        self.inhibB_e.place(x=330,y=125)
        inhibC_l.place(x=360,y=125)
        self.inhibC_e.place(x=380,y=125)
        inhibD_l.place(x=410,y=125)
        self.inhibD_e.place(x=430,y=125)
        excitNum_l.place(x=40,y=150)
        self.excitNum_e.place(x=185,y=150)
        excitA_l.place(x=260,y=150)
        self.excitA_e.place(x=280,y=150)
        excitB_l.place(x=310,y=150)
        self.excitB_e.place(x=330,y=150)
        excitC_l.place(x=360,y=150)
        self.excitC_e.place(x=380,y=150)
        excitD_l.place(x=410,y=150)
        self.excitD_e.place(x=430,y=150)

        saveButton = tk.Button(self.win, text="Save Configuration", command=lambda:self.saveAnimat(id))
        saveButton.place(x=200,y=200)

    def saveAnimat(self,id):
        self.sP.setType(id,self.type_e.get())
        self.sP.setOrigin(id,(int(self.origin_e.get()[1]),int(self.origin_e.get()[4])))
        self.sP.setCalories(id,int(self.cal_e.get()))
        inhib = [int(self.inhibNum_e.get()),float(self.inhibA_e.get()),float(self.inhibB_e.get()),
                 float(self.inhibC_e.get()),float(self.inhibD_e.get())]
        excit = [int(self.excitNum_e.get()),float(self.excitA_e.get()),float(self.excitB_e.get()),
                 float(self.excitC_e.get()),float(self.excitD_e.get())]
        self.sP.setInhib(id,inhib)
        self.sP.setExcit(id,excit)
        self.win.destroy()

    def addAnimat(self):
        self.sP.setAnimNum(1,self.sP.getAnimNum(1)+1)
        #self.parameters[0] += 1      #increase animatNum by 1
        self.layoutHist += 50        #shift current y value down
        #id = self.sP.getAnimNum() - 1  #-1 beacause index = id-1
        self.sP.setAnimParams(self.sP.getAnimNum(),"Wheel Animat",(1,0),10,[80,.02,.25,-65,2],[320,.02,.2,-65,8])
        newLabel = tk.Label(self.root, text=("* Animat: " + str(self.sP.getAnimNum())), font="bold")
        newConfigButton = tk.Button(self.root, text="Configure Animat", command=lambda: self.configAnimat(id))
        newDeleteButton = tk.Button(self.root, text="Remove Animat", command=lambda: self.deleteAnimat(id))
        self.layoutList.append([newLabel,newConfigButton,newDeleteButton])
        newLabel.place(x=600,y=self.layoutHist)
        newConfigButton.place(x=700,y=self.layoutHist)
        newDeleteButton.place(x=825,y=self.layoutHist)
        newConfigButton.invoke()

    ##NEED TO ADAPT TO simParam  FIGURE OUT WORLD ANIM ID IMPLEMENTATION FIRST
    def deleteAnimat(self,id):
        pass
        # del self.animatParams[id]
        # self.layoutHist -= 50
        # self.parameters[0] -= 1
        # label,config,delete = self.layoutList[id-1]
        # label.destroy()
        # config.destroy()
        # delete.destroy()
        # del self.layoutList[id-1]

    #Menu Bar Functions
    def startSimulation(self):
        self.simWin = tk.Toplevel(self.root)
        self.root.withdraw()
        self.simEngine.stopSimulation()
        self.gui = GUIdriver.GUIDriver(self.simWin,self.root,self.sP)

    #NEED TO IMPLEMENT AFTER
    def loadEvo(self):
        #pass
        fn = tkFileDialog.askopenfilename()
        with open(fn,'r') as f:
            evoParams =  json.load(f)
        print evoParams
        self.sP.setAnimParams(1,1,evoParams[1],evoParams[2],evoParams[3],evoParams[4],evoParams[5])
        self.sP.setAA(1,evoParams[6])
        self.sP.setBB(1,evoParams[7])
        self.simWin = tk.Toplevel(self.root)
        self.root.withdraw()
        self.simEngine.stopSimulation()
        self.gui = GUIdriver.GUIDriver(self.simWin,self.root,self.sP)

    def editParameters(self):
        paramWin = ParametersWindow.ParameterWindow()

    def saveCurrentSimulation(self):
        self.simEngine.stopSimulation()
        f = tkFileDialog.asksaveasfile(mode='w', **self.file_opt)
        cPickle.dump((self.simEngine.staticWorld, self.simHistory), f)
        if not f is None: f.close()

    def loadSimulationFromFile(self):
        f = tkFileDialog.askopenfile(mode='r', **self.file_opt)
        if f is None: return
        self.simEngine.loadSimulationFromFile(f)
        self.simHistory = {}
        self.dis_t = 0
        self.buff_t = 0
        self.videoBar.reset()
        self.paused = True

    def setWriteInterval(self,t):
        self.simEngine.setWriteInterval(t)


devWin = DevelopmentWindow()