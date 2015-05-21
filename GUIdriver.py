# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 21:05:31 2014

Animat Simulator GUI
Displays simulated world as well as neural network of the animat in the simulation

"""

import numpy as np
from SimulationEngine import SimulationEngine
try:
   import cPickle as pickle
except:
   import pickle
import Tkinter as tk
from PIL import Image
from PIL import ImageTk
from Graph import Graph # Steven wrote this to wrap Tk functions for ease of use
import cPickle
import matplotlib # only used for summary statistics graphs
matplotlib.use('TkAgg') # we use Tk back end
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import time
from TabBox import TabBox # SH wrote this
from VideoBar import VideoBar # SH wrote this for multiple animats to switch neuron graphs
import tkFileDialog
import collections
import SimParam
import NeuronModule


class GUIDriver:

    def __init__(self,master,devWin,simParams):
        self.sP = simParams
        #some parameters
        self.paused = False                     # whether simulation playback is paused
        self.simRunning = True                  # whether simulation is running - so buffering to GUI
        self.lastTime = 0                       # the last time on the clock
        self.sim_msps = 0                       # how many simulated milliseconds pass per second in display: i.e., a value of 1000 means real-time - useful for animat moving, but too fast to see neural activity
        self.dis_t = 1                          #the time being currently displayed by the GUI
        self.buff_t = 0                         #the time buffered by the Simulation Engine
        self.writeInterval = 25                 # sets the interval between write states (in simulated ms); 
        self.simHistory = {}                    # dictionary of time: dynamic world state
        self.tracked_data = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.OrderedDict())) # not clear what this is; SH
        self.TRACK_NEURAL_FIRINGS = "Neural Firings"
        self.TRACK_ENERGY = "Energy"
        self.TRACK_POS = "Position"
        self.TRACK_LFP = "LFP" # probably should give this another name
        self.tracked_types = []
        self.simEngine = SimulationEngine()     #constructs a Simulation Engine
        self.world = 0                          #placeholder for the World currently being displayed
        
        
        self.devWin = devWin              # development window is parent; use this to set up parameters

        #some general-purpose colors
        self.colorWhite = "#ffffff"
        self.colorGrey = "#dddddd"
        self.colorBlack = "#000000"
        self.colorLightBlue = "#ADD8E6"
        self.colorBlue = "#0000ff"
        self.colorRed = "#ff0000"
        self.colorGreen = "#00ff00"

        #setting up Tk window
        self.root = master          # window passed in
        self.root.title("Animat Simulation")
        self.canvas = tk.Canvas(self.root, width=1280, height=720)
        self.canvas.pack()

        #set up file options to save simulations
        self.file_opt = options = {}
        options['defaultextension'] = '.sim'
        options['filetypes'] = [('all files', '.*'), ('text files', '.txt'), ('Simulation Files', '.sim')]
        #options['initialdir'] = 'C:\\'
        options['initialfile'] = '.sim'
        options['parent'] = self.root
        options['title'] = 'Save Simulation As...'

        #set up menu bar
        self.menubar = tk.Menu(self.root)
        filemenu = tk.Menu(self.menubar, tearoff=0)
        filemenu.add_command(label="Save Current Simulation", command=self.saveCurrentSimulation)
        filemenu.add_command(label="Load Simulation from File", command=self.loadSimulationFromFile)
        filemenu.add_command(label="Calculate Benchmark", command=self.benchmark)
        filemenu.add_separator()
        filemenu.add_command(label="Exit",command=self.quit)
        self.menubar.add_cascade(label="File", menu=filemenu)
        speedmenu = tk.Menu(self.menubar, tearoff=0)
        speedCheckVar = tk.IntVar()
        speedmenu.add_radiobutton(label="1ms", variable = speedCheckVar, command=lambda:self.setWriteInterval(1))
        speedmenu.add_radiobutton(label="25ms", variable = speedCheckVar, command=lambda:self.setWriteInterval(25))
        speedmenu.add_radiobutton(label="50ms", variable = speedCheckVar, command=lambda:self.setWriteInterval(50))
        speedmenu.add_radiobutton(label="100ms", variable = speedCheckVar, command=lambda:self.setWriteInterval(100))
        speedmenu.add_radiobutton(label="1s", variable = speedCheckVar, command=lambda:self.setWriteInterval(1000))
        speedmenu.add_radiobutton(label="Do not write", variable = speedCheckVar)
        speedmenu.invoke(1)   #default write interval is 100
        worldmenu = tk.Menu(self.menubar, tearoff=0)
        worldVar = tk.IntVar()    #not used just required
        worldmenu.add_radiobutton(label="World 1", variable = worldVar, command=lambda:self.setWorldNum(1))
        worldmenu.add_radiobutton(label="World 2", variable = worldVar, command=lambda:self.setWorldNum(2))
        worldmenu.add_radiobutton(label="World 3", variable = worldVar, command=lambda:self.setWorldNum(3))
        worldmenu.add_radiobutton(label="World 4", variable = worldVar, command=lambda:self.setWorldNum(4))
        worldmenu.add_radiobutton(label="World 5", variable = worldVar, command=lambda:self.setWorldNum(5))
        speedmenu.invoke(self.sP.worldToRun-1)   #default write interval is 25
        editmenu = tk.Menu(self.menubar, tearoff=0)
        editmenu.add_cascade(label="Write Interval", menu=speedmenu)
        editmenu.add_cascade(label="World to Run", menu=worldmenu)
        editmenu.add_command(label="Parameters", command=self.showDevWin)
        self.menubar.add_cascade(label="Edit", menu=editmenu)
        trackmenu = tk.Menu(self.menubar, tearoff=0)
        trackmenu.add_checkbutton(label="Neural Firings", command = lambda:self.track(self.TRACK_NEURAL_FIRINGS))
        trackmenu.add_checkbutton(label="Energy", command = lambda:self.track(self.TRACK_ENERGY))
        trackmenu.add_checkbutton(label="Position", command = lambda:self.track(self.TRACK_POS))
        trackmenu.add_checkbutton(label="LFP", command = lambda:self.track(self.TRACK_LFP))
        trackmenu.invoke(0)
        trackmenu.invoke(1)
        trackmenu.invoke(2)
        trackmenu.invoke(3)
        self.menubar.add_cascade(label="Track", menu = trackmenu)
        viewMenu = tk.Menu(self.menubar, tearoff=0)
        viewMenu.add_command(label="Internal Variables",command=self.varViewer)
        viewMenu.add_command(label="Connection Viewer",command=self.connectionViewer)
        self.menubar.add_cascade(label="View",menu=viewMenu)
        debugMenu = tk.Menu(self.menubar, tearoff=0)
        debugMenu.add_command(label="Print S",command = self.printS)
        debugMenu.add_command(label="Print RL",command = self.printRL)
        self.menubar.add_cascade(label="Debug",menu=debugMenu)
        self.root.config(menu=self.menubar)

        #initialize the graphs and video control bar
        self.worldGraph = Graph(self.root, [100, 50, 500, 475], [-10, 10, -10, 10])
        self.worldGraph.title('World')
        self.worldGraph.xlabel('distance')
        self.neuron_graphs = {}
        self.neuron_box = TabBox(self.root, [600, 50, 1000, 475])
        self.videoBar = VideoBar(self.canvas, (100, 515, 500, 525), (0, 15000), self.timeClicked)

        #some images--will probably eventually go in respective classes (static state) - can remove 
        self.animatImage = Image.open("roomba.png")
        self.aImage = ImageTk.PhotoImage(self.animatImage)
        self.foodImage = Image.open("beer.png")
        self.fImage = ImageTk.PhotoImage(self.foodImage)
        playImage = ImageTk.PhotoImage(Image.open("play.png").resize((40, 40), Image.ANTIALIAS))
        pauseImage = ImageTk.PhotoImage(Image.open("pause.png").resize((40,40), Image.ANTIALIAS))
        stopImage = ImageTk.PhotoImage(Image.open("stop.png").resize((40,40), Image.ANTIALIAS))
        restartImage = ImageTk.PhotoImage(Image.open("restart.png").resize((40,40), Image.ANTIALIAS))
        step_fImage = ImageTk.PhotoImage(Image.open("step_f.png").resize((40,40), Image.ANTIALIAS))
        step_bImage = ImageTk.PhotoImage(Image.open("step_b.png").resize((40,40), Image.ANTIALIAS))
        continueImage = ImageTk.PhotoImage(Image.open("continue.png").resize((40,40), Image.ANTIALIAS))

        #video control buttons
        self.playButton = tk.Button(self.root, command = self.play, image = playImage, relief='sunken')
        self.playButton.place(x = 100,y=545)
        self.pauseButton = tk.Button(self.root, command = self.pause, image = pauseImage, relief='raised')
        self.pauseButton.place(x=155,y=545)
        # self.stopButton = tk.Button(self.root, command = self.stop, image = stopImage)
        # self.stopButton.place(x=320, y=545)
        self.restartButton = tk.Button(self.root, command = self.restart, text="Start New Simulation")
        self.restartButton.place(x=320, y=575)
        self.step_bButton = tk.Button(self.root, command = self.step_b, image = step_bImage)
        self.step_bButton.place(x=210,y=545)
        self.step_fButton = tk.Button(self.root, command = self.step_f, image = step_fImage)
        self.step_fButton.place(x=265, y=545)
        # self.continueButton = tk.Button(self.root, command = self.continue_, image = continueImage)
        # self.continueButton.place(x=430, y=545)
        self.simCtrlButton = tk.Button(self.root, command=self.simCtrl, text="Stop Simulation",bg='red')
        self.simCtrlButton.place(x=320,y=545)

         # Buttons using images
        # self.playButton = tk.Button(self.root, command = self.play, text="Play", relief='sunken')
        # self.playButton.place(x = 100,y=545)
        # self.pauseButton = tk.Button(self.root, command = self.pause, text="Pause", relief='raised')
        # self.pauseButton.place(x=155,y=545)
        # # self.stopButton = tk.Button(self.root, command = self.stop, image = stopImage)
        # # self.stopButton.place(x=320, y=545)
        # self.restartButton = tk.Button(self.root, command = self.restart, text="Start New Simulation")
        # self.restartButton.place(x=320, y=575)
        # self.step_bButton = tk.Button(self.root, command = self.step_b, text = "Step <-")
        # self.step_bButton.place(x=210,y=545)
        # self.step_fButton = tk.Button(self.root, command = self.step_f, text = "Step ->")
        # self.step_fButton.place(x=265, y=545)
        # # self.continueButton = tk.Button(self.root, command = self.continue_, image = continueImage)
        # # self.continueButton.place(x=430, y=545)
        # self.simCtrlButton = tk.Button(self.root, command=self.simCtrl, text="Stop Simulation",bg='red')
        # self.simCtrlButton.place(x=320,y=545)

        #speed lock buttons
        self.speedButtons = tk.IntVar()
        rb1 = tk.Radiobutton(self.root, text="Real-Time", variable=self.speedButtons, value=1, command = self.realTime)
        rb1.place(x = 100, y = 600)
        rb2 = tk.Radiobutton(self.root, text="Synced", variable=self.speedButtons, value=2, command = self.synced)
        rb3 = tk.Radiobutton(self.root, text="Select:", variable=self.speedButtons, value=3, command = self.chooseSpeed)
        rb2.place(x = 100, y = 630)
        rb3.place(x = 100, y = 660)

        spdlabel = self.canvas.create_text(357, 635, text="Select Speed (ms/s)")
        self.speedScale = tk.Scale(self.root, from_=0, to=500, orient = "horizontal", length = 300)
        self.speedScale.place(x = 215, y = 645)

        rb3.invoke() #needs to be called after speed scale is created

        #Create legend for neuron map
        tk.Label(self.root,text="Neural Network Legend",font="bold",relief="ridge",padx=5,pady=5).place(x=1050,y=100)
        #inhib_t = tk.Label(self.root, text="Inhibitory Neuron: ")
        #inhib_t.place(x=1050,y=150)
        #inhib_c = self.canvas.create_oval(1175,150,1200,175, fill = "#b1b1ff")
        tk.Label(self.root, text="Excitatory Neuron: ").place(x=1050,y=150)
        self.canvas.create_oval(1200,150,1225,175, fill = NeuronModule.ExcitatoryNeuron(0,0,0).color)
        tk.Label(self.root, text="Hunger Neuron: ").place(x=1050,y=200)
        self.canvas.create_oval(1200,200,1225,225, fill = NeuronModule.HungerNeuron(0,0,0).color)
        tk.Label(self.root, text="Motor Neuron: ").place(x=1050,y=250)
        self.canvas.create_oval(1200,250,1225,275, fill = NeuronModule.MotorNeuron(0,0,0).color)
        tk.Label(self.root, text="Sensory Neuron A: ").place(x=1050,y=300)
        self.canvas.create_oval(1200,300,1225,325, fill = NeuronModule.SensoryNeuron_A(0,0,0).color)
        tk.Label(self.root, text="Sensory Neuron B: ").place(x=1050,y=350)
        self.canvas.create_oval(1200,350,1225,375, fill = NeuronModule.SensoryNeuron_B(0,0,0).color)

        #pack up the Frame and run
        mainContainer = tk.Frame(self.root)
        mainContainer.pack()
        self.run()              #runs a simulation, for now
        self.root.mainloop()    #starts the Tkinter event loop

    #called to start a new simulation
    def run(self):

        self.simEngine.startNewSim(self.sP)                            #starts a new simulation
        self.world = self.simEngine.staticWorld
        self.simEngine.setWriteInterval(self.writeInterval)     #sets the write interval of the simulator
        self.worldGraph.set_numBounds(self.simEngine.staticWorld.numBounds) # bounds of box animat is contained
        self.makeStatMenu(3)
        self.root.after(0, self.refreshScreen)                  #adds task to refresh screen information - starts animation
        self.lastTime = time.clock()                            #clocks the start of the simulation
        #self.makeStatMenu(3)                                    #right now hardcoded to 3 food items

    #main GUI refresh method
    def refreshScreen(self):


        # 1. The program needs to get the new states produced by the Simulation Engine since the last screen refresh.

        static, states = self.simEngine.getNewStates()          #the Simulation Engine passes back new states and the static world
        self.simHistory.update(states)                          #updates the GUI's simulation history with the new states


        # 2. The program needs to figure out what time to display based on the selected speed and what has been recorded.

        systime = time.clock()                                  #gets the system time
        elapsed_time = systime - self.lastTime                  #calculates the elapsed time from the last time the loop was run
        self.lastTime = systime                                 #records new system time for the next loop
        if not self.paused and self.dis_t <= self.buff_t:           #advances the displayed time, as long as it's not ahead of the simulation and is not paused
                self.dis_t += self.calculate_dis_dt(elapsed_time)
        dis_t_int = int(np.floor(self.dis_t/self.writeInterval) * self.writeInterval)    #finds the displayed time based on the write interval: I.E., requests closest written time to the time that should be displayed


        # 3. If able to find the displayed time in recorded simulation history, the program needs to store and display the corresponding World graphically

        if dis_t_int in self.simHistory.keys():


            # 3.a. loads ands stores the World

            static.loadDynamicState(self.simHistory[dis_t_int]) #loads the dynamic state at the displayed time into the static World object
            self.world = static                                 #sets this loaded world as the GUI's world for other menus, etc


            # 3.b. displays the World on two Graph objects and draws them

            #plot the world: the Animat and food, for now
            for animat in self.world.animats:
                self.worldGraph.plotCircle((animat.radius*2,animat.radius*2), (animat.pos[0], animat.pos[1]), self.colorGrey)
                headPos = animat.pos[0]+(animat.radius)*np.cos(animat.direc), animat.pos[1]+(animat.radius)*np.sin(animat.direc)
                self.worldGraph.plotCircle((.2,.2), headPos, self.colorBlack)
                self.worldGraph.plotText(("Purisa", 6) , (animat.pos[0], animat.pos[1]), animat.id)
                if not (animat.id in self.neuron_graphs.iterkeys()):
                    neuronGraph = Graph(self.root, self.neuron_box.content_bounds, [-1.3, 1.3, -1.3, 1.3])
                    self.neuron_graphs[animat.id] = neuronGraph
                    self.neuron_box.add(neuronGraph, animat.id)

                neuronGraph = self.neuron_graphs[animat.id]
                neuronGraph.plotCircle((2, 2), (0, 0), self.colorWhite)
                neurons = animat.net.getNeurons()
                for neuron in neurons:
                    neuronGraph.plotCircle((.05, .05), (neuron.X, neuron.Y), neuron.firing_color if neuron.isFiring() else neuron.color)
                neuronGraph.draw(self.canvas)


            for food in self.world.foods:
                #foodImage = self.worldGraph.size_up(Image.open(food.image), (1,1), 0)
                if food.amt > 0.0:
                    self.worldGraph.plotCircle((1,1), food.getPos(), self.colorGreen)
                    self.worldGraph.plotText(("Purisa", 6) , (food.getPos()[0], food.getPos()[1]), food.getType())
                #self.worldGraph.plotCircle((1,1), food.pos, self.colorGreen)
            self.worldGraph.draw(self.canvas)

        for type in self.tracked_types:
            if type == self.TRACK_ENERGY:
                for t in sorted(states.keys()):
                    static.loadDynamicState(states[t])
                    for animat in static.animats:
                        self.tracked_data[animat.id][type][t] = animat.Energy
            elif type == self.TRACK_NEURAL_FIRINGS:
                for t in sorted(states.keys()):
                    static.loadDynamicState(states[t])
                    for animat in static.animats:
                        self.tracked_data[animat.id][type][t] = animat.net.get_neurons_firing()
            elif type == self.TRACK_POS:
                for t in sorted(states.keys()):
                    static.loadDynamicState(states[t])
                    for animat in static.animats:
                        self.tracked_data[animat.id][type][t] = animat.pos
            elif type == self.TRACK_LFP:
                continue
                for t in sorted(states.keys()):
                    static.loadDynamicState(states[t])
                    for animat in static.animats:
                        self.tracked_data[animat.id][type][t] = np.mean(animat.net.v.as_numpy_array()[animat.net.excitatoryNeurons])


        # 4. Regardless of displaying a World, the program needs to make sure that the display time is reasonable and update the video control bar

        self.buff_t = sorted(self.simHistory.keys())[len(self.simHistory.keys())-1]  #set the buffered time to the latest time in history
        if (self.dis_t > self.buff_t): self.dis_t = self.buff_t                      #sets the display time to the buffered time, if ahead
        if  (self.dis_t < 0): self.dis_t = 0                                         #sets the display time to 0, if below 0
        self.videoBar.update(dis_t_int, self.buff_t)                                 #updates the video bar with the displayed time and the buffered time
        self.videoBar.draw()


        # 5. Reschedule another refresh!
        self.root.after(1 if int(np.floor(1000/10)) < 1 else int(np.floor(1000/10)), self.refreshScreen)  #tells Tkinter to refresh the display again in 1/20 seconds


    #calculate the simulated time interval based on how many simulated ms per real-time seconds are supposed to be displayed
    def calculate_dis_dt(self, elapsedTime):
        if self.sim_msps == "synced":
            return self.buff_t - self.dis_t
        if self.sim_msps == "real-time":
            return int(round(elapsedTime * 1000))
        self.sim_msps = self.speedScale.get()
        if self.sim_msps == 0: return 1
        return int(round(float(self.sim_msps) * elapsedTime))

    def play(self):
        self.paused = False
        self.playButton.config(relief='sunken')
        self.pauseButton.config(relief='raised')

    def pause(self):
        self.paused = True
        self.playButton.config(relief='raised')
        self.pauseButton.config(relief='sunken')

    def timeClicked(self, t):
        self.dis_t = t

    def simCtrl(self):
        if self.simRunning:
            self.simEngine.stopSimulation()
            self.simCtrlButton.config(text="Resume Simulation",bg='green')
            self.simRunning = False
        else:
            self.continue_()
            self.simCtrlButton.config(text="Stop Simulation",bg='red')
            self.simRunning = True

    def stop(self):
        self.simEngine.stopSimulation()

    def step_f(self):
        self.dis_t += self.writeInterval

    def step_b(self):
        self.dis_t -= self.writeInterval

    def realTime(self):
        self.sim_msps = "real-time"

    def synced(self):
        self.sim_msps = "synced"

    def chooseSpeed(self):
        self.sim_msps = self.speedScale.get()

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

##MODIFY THISS!!
    def restart(self):
        self.dis_t = 0
        self.buff_t = 0
        self.paused = False
        self.simHistory = {}
        self.simEngine.startNewSim(self.sP)
        self.tracked_data = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.OrderedDict()))
        self.lastTime = time.clock()
        self.videoBar.reset()
        self.simCtrlButton.config(text="Stop Simulation",bg='red')
        self.simRunning = True
        self.playButton.config(relief='sunken')
        self.pauseButton.config(relief='raised')

    def setWriteInterval(self, interval):
        self.writeInterval = interval
        self.simEngine.setWriteInterval(interval)

    def continue_(self):
        if len(self.simHistory) == 0 or self.simEngine.is_running(): return
        self.simEngine.continueSim(self.simHistory[self.buff_t], self.buff_t)

    def track(self, to_track):
        if to_track in self.tracked_types: return
        else:
            self.tracked_types.append(to_track)

    def quit(self):
        self.simEngine.stopSimulation()
        self.root.destroy()
        self.devWin.destroy()

    def makeStatMenu(self,foodNum):
        statMenu = tk.Menu(self.menubar,tearoff=0)
        animatMenu = tk.Menu(statMenu,tearoff=0)
        if self.world != 0:
            index = 0
            for animat in self.world.animats:
                index += 1
                animatMenu.add_command(label=("Animat " + str(index)), command=lambda:self.animatStatWindow(animat))

        statMenu.add_cascade(label="Animats",menu=animatMenu)
        stimMenu = tk.Menu(statMenu,tearoff=0)
        foodMenu = tk.Menu(stimMenu,tearoff=0)
        for i in range(0,foodNum):
            foodMenu.add_command(label=("Food "+str(i+1)),command=self.foodStatWindow)
        stimMenu.add_cascade(label="Food",menu=foodMenu)
        statMenu.add_cascade(label="Stimuli",menu=stimMenu)

        self.menubar.add_cascade(label="Statistics",menu=statMenu)

    def animatStatWindow(self, anim):
        stats = anim.getStats()
        win = tk.Toplevel(height=600,width=700)
        #title and icon
        win.title("Animat Stats")
#        icon = tk.Label(win,image=self.aImage,relief="ridge")
#        icon.place(x=20,y=20)
        #stat list
        title = tk.Label(win,text="Stats for Animat: " + str(anim.id),font="bold",relief="ridge",padx=5,pady=5)
        type_l = tk.Label(win,text=("Type: "))
        type_t = tk.Text(win,height=1,width=30,bg="grey")
        type_t.insert(tk.END,str(anim.__class__))
        nrg_l = tk.Label(win,text=("Energy: "))
        nrg_t = tk.Text(win,height=1,width=30,bg="grey")
        nrg_t.insert(tk.END,str(anim.Energy))
        title2 = tk.Label(win,text="Internals",font="bold",relief="ridge",padx=5,pady=5)
        cme_l = tk.Label(win,text=("cMotionEnergy: "))
        cme_t = tk.Text(win,height=1,width=30,bg="grey")
        cme_t.insert(tk.END,str(anim.cMotionEnergy))
        kbe_l = tk.Label(win,text=("kBasalEnergy: "))
        kbe_t = tk.Text(win,height=1,width=30,bg="grey")
        kbe_t.insert(tk.END,str(anim.kBasalEnergy))

        tab_box = TabBox(win, [20, 250, 620, 550], toolbar=True)
        count = 1
        for type in self.tracked_types:
            f = Figure(figsize=(5,4), dpi=50)
            a = f.add_subplot(111)
            t = self.tracked_data[anim.id][type].keys()
            s = self.tracked_data[anim.id][type].values()
            if type == self.TRACK_NEURAL_FIRINGS:
                t = []
                s = []
                for ti in self.tracked_data[anim.id][type].keys():
                    for si in self.tracked_data[anim.id][type][ti][0]:
                        t.append(ti)
                        s.append(si)
            if type == self.TRACK_POS:
                t = []
                s = []
                for ti in self.tracked_data[anim.id][type].keys():
                    t.append(self.tracked_data[anim.id][type][ti][0])
                    s.append(self.tracked_data[anim.id][type][ti][1])
            if type == self.TRACK_NEURAL_FIRINGS:
                a.plot(t,s,'.k')
            else: a.plot(t,s,'-k')
            canvas = FigureCanvasTkAgg(f, master=win)
            tbcan = tab_box.add_canvas(canvas.get_tk_widget(), type)
            NavigationToolbar2TkAgg(canvas, tbcan)

        #placements
        title.place(x=300,y=20)
        type_l.place(x=300,y=60)
        type_t.place(x=390,y=60)
        nrg_l.place(x=300,y=90)
        nrg_t.place(x=390,y=90)
        title2.place(x=300,y=130)
        cme_l.place(x=300,y=170)
        cme_t.place(x=390,y=170)
        kbe_l.place(x=300,y=200)
        kbe_t.place(x=390,y=200)

    ## NEEDS IMPLEMENTATION
    def foodStatWindow(self):
        win = tk.Toplevel(height=600,width=700)
        #title and icon
        win.title("Food Stats")
        icon = tk.Label(win,image=self.fImage,relief="ridge")
        icon.place(x=20,y=20)
        #stat list
        title = tk.Label(win,text="Stats for Food 1",font="bold",relief="ridge",padx=5,pady=5)
        #placements
        title.place(x=300,y=20)

    def varViewer(self,time):
        win = tk.Toplevel(height=800,width=1100)
        win.title("Internal Variable Viewer")

        tBox = tk.Frame(win,height=500,width=700)
        h = len(self.simHistory[0].getS())     #get S because has highest number of rows
        w = len(self.simHistory[0].getA()) * 2 #get A because has highest number of columns
        vScroll = tk.Scrollbar(tBox,orient="vertical")
        hScroll = tk.Scrollbar(tBox,orient="horizontal")
        disBox = tk.Text(tBox,xscrollcommand=hScroll.set,yscrollcommand=vScroll.set)
        state = self.simHistory[time]
        #disBox.insert("INSERT",)


        #placements
        tBox.place(x=100,y=100)
        vScroll.pack(side="right",fill="y")
        hScroll.pack(side="bottom",fill="x")
        disBox.pack()

    def connectionViewer(self):
        win = tk.Toplevel(height=800,width=1100)
        win.title("Network Connection Viewer")
        fig = Figure(figsize=(10,10))
        ax = fig.add_subplot(111,xlim=(-1.5, 1.5),ylim=(-1.5, 1.5))
        netCircle = plt.Circle((0,0), radius = 1, fill = False )
        ax.add_artist(netCircle)
        neurons = self.world.animats[0].net.getNeurons()
        locs = {}                        # used for storing neurons in index : location,color
        for neuron in neurons:
            ax.add_artist(plt.Circle((neuron.X,neuron.Y),radius=.025,facecolor=neuron.color,edgecolor='black'))
            locs[neuron.index] = (neuron.X,neuron.Y,neuron.color)
        for i,connectsFrom in enumerate(self.world.animats[0].net.S):
            startLoc = locs[i][0],locs[i][1]+.025
            color = locs[i][2]
            for connectsTo in np.nonzero(connectsFrom)[0]:
                endLoc = locs[connectsTo][0],locs[connectsTo][1]-.025
                weight = connectsFrom[connectsTo]
                ax.annotate("",xy=endLoc,xytext=startLoc,size=5,
                            arrowprops=dict(arrowstyle="->", color=color))
        #ax.annotate("",xy=(-1,0),xytext=(1,0),arrowprops=dict(arrowstyle="simple",connectionstyle="arc3,rad=0.3",alpha=0.3))
        ax.add_artist(plt.Circle((1,1.35),radius=.025,facecolor=NeuronModule.ExcitatoryNeuron(0,0,0).color,edgecolor='black'))
        ax.add_artist(plt.Text(1.04,1.33,"Excitatory",size='small'))
        ax.add_artist(plt.Circle((1,1.25),radius=.025,facecolor=NeuronModule.SensoryNeuron_A(0,0,0).color,edgecolor='black'))
        ax.add_artist(plt.Text(1.04,1.23,"Sensory A",size='small'))
        ax.add_artist(plt.Circle((1,1.15),radius=.025,facecolor=NeuronModule.SensoryNeuron_B(0,0,0).color,edgecolor='black'))
        ax.add_artist(plt.Text(1.04,1.13,"Sensory B",size='small'))
        ax.add_artist(plt.Circle((1,1.05),radius=.025,facecolor=NeuronModule.MotorNeuron(0,0,0).color,edgecolor='black'))
        ax.add_artist(plt.Text(1.04,1.03,"Motor",size='small'))
        ax.add_artist(plt.Circle((1,0.95),radius=.025,facecolor=NeuronModule.HungerNeuron(0,0,0).color,edgecolor='black'))
        ax.add_artist(plt.Text(1.04,0.93,"Hunger",size='small'))

        ##Show plot
        canvas = FigureCanvasTkAgg(fig,master=win)
        canvas.show()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        NavigationToolbar2TkAgg(canvas,win)


    #Used for debug, prints value of S to terminal
    def printS(self):
        S = self.world.animats[0].net.S
        print "S: \n"
        print "Excitatory Neurons"
        for i in self.world.animats[0].net.excitatoryNeurons:
            print S[i]
        print "Sensory A Neurons"
        for i in self.world.animats[0].net.senseNeurons_A:
            print S[i]
        print "Sensory B Neurons"
        for i in self.world.animats[0].net.senseNeurons_B:
            print S[i]
        print "Motor Neurons"
        for i in self.world.animats[0].net.motorNeurons:
            print S[i]
        print "Hunger Neurons"
        for i in self.world.animats[0].net.hungerNeurons:
            print S[i]

    def printRL(self):
        neurons = self.world.animats[0].net.getNeurons()
        print "Excitatory Neurons"
        for i in self.world.animats[0].net.excitatoryNeurons:
            print "R", neurons[i].r, "L", neurons[i].l
        print "Sensory A Neurons"
        for i in self.world.animats[0].net.senseNeurons_A:
            print "R", neurons[i].r, "L", neurons[i].l
        print "Sensory B Neurons"
        for i in self.world.animats[0].net.senseNeurons_B:
            print "R", neurons[i].r, "L", neurons[i].l
        print "Motor Neurons"
        for i in self.world.animats[0].net.motorNeurons:
            print "R", neurons[i].r, "L", neurons[i].l
        print "Hunger Neurons"
        for i in self.world.animats[0].net.hungerNeurons:
            print "R", neurons[i].r, "L", neurons[i].l


    def setWorldNum(self,num):
        self.sP.worldToRun = num

    def showDevWin(self):
        self.simEngine.stopSimulation()
        self.root.destroy()
        self.devWin.deiconify()

    def benchmark(self):
        for anim in self.world.animats:
            anim.calcBenchmark(self.buff_t,self.simEngine.getRunTime())
