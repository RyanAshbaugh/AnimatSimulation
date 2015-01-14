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
import _tkinter
import Tkinter as tk
from PIL import Image
from PIL import ImageTk
from Graph import Graph
import jsonpickle
import cPickle
import json
import msgpack
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import time
from TabBox import TabBox
from VideoBar import VideoBar
import tkFileDialog
import collections
import SimParam


class GUIDriver:

    def __init__(self,master,devWin,simParams):
        self.sP = simParams
        #some parameters
        self.paused = False                     #paused?
        self.simRunning = True
        self.lastTime = 0                       #the last time on the clock
        self.sim_msps = 0                       #how many simulated milliseconds pass per second: i.e., a value of 1000 means real-time
        self.dis_t = 1                          #the time being currently displayed by the GUI
        self.buff_t = 0                         #the time buffered by the Simulation Engine
        self.writeInterval = 25                 #determines the interval between writes (in ms)
        self.simHistory = {}                    #dictionary of time: dynamic world state
        self.tracked_data = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.OrderedDict()))
        self.TRACK_NEURAL_FIRINGS = "Neural Firings"
        self.TRACK_ENERGY = "Energy"
        self.TRACK_POS = "Position"
        self.TRACK_LFP = "LFP"
        self.tracked_types = []
        self.simEngine = SimulationEngine()     #constructs a Simulation Engine
        self.world = 0                          #placeholder for the World currently being displayed
        #self.parameters = params                #[AnimNum,foodNum,WorldSize]
        #self.AnimatParams = animParams          #[type,origin,cal,inhib,excit]
        self.devWin = devWin

        #some general-purpose colors
        self.colorWhite = "#ffffff"
        self.colorGrey = "#dddddd"
        self.colorBlack = "#000000"
        self.colorLightBlue = "#ADD8E6"
        self.colorBlue = "#0000ff"
        self.colorRed = "#ff0000"
        self.colorGreen = "#00ff00"

        #setting up Tk window
        self.root = master
        self.root.title("Animat Simulation")
        self.canvas = tk.Canvas(self.root, width=1280, height=720)
        self.canvas.pack()

        #set up file options
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
        editmenu = tk.Menu(self.menubar, tearoff=0)
        editmenu.add_cascade(label="Write Interval", menu=speedmenu)
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
        self.root.config(menu=self.menubar)
        viewMenu = tk.Menu(self.menubar, tearoff=0)
        viewMenu.add_command(label="Internal Variables",command=self.varViewer)
        viewMenu.add_command(label="Connection Viewer",command=self.connectionViewer)
        self.menubar.add_cascade(label="View",menu=viewMenu)

        #initialize the graphs and video control bar
        self.worldGraph = Graph(self.root, [100, 50, 500, 475], [-10, 10, -10, 10])
        self.worldGraph.title('World')
        self.worldGraph.xlabel('distance')
        self.neuron_graphs = {}
        self.neuron_box = TabBox(self.root, [600, 50, 1000, 475])
        self.videoBar = VideoBar(self.canvas, (100, 515, 500, 525), (0, 15000), self.timeClicked)

        #some images--will probably eventually go in respective classes (static state)
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
        title = tk.Label(self.root,text="Neural Network Legend",font="bold",relief="ridge",padx=5,pady=5)
        title.place(x=1050,y=100)
        inhib_t = tk.Label(self.root, text="Inhibitory Neuron: ")
        inhib_t.place(x=1050,y=150)
        inhib_c = self.canvas.create_oval(1175,150,1200,175, fill = "#b1b1ff")
        excit_t = tk.Label(self.root, text="Excitatory Neuron: ")
        excit_t.place(x=1050,y=200)
        excit_c = self.canvas.create_oval(1175,200,1200,225, fill = "#ffb1b1")
        motor_t = tk.Label(self.root, text="Motor Neuron: ")
        motor_t.place(x=1050,y=250)
        motor_c = self.canvas.create_oval(1175,250,1200,275, fill = "#ffffff")
        sense_t = tk.Label(self.root, text="Sensory Neuron: ")
        sense_t.place(x=1050,y=300)
        sense_c = self.canvas.create_oval(1175,300,1200,325, fill = "#b1ffb1")

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
        self.worldGraph.set_numBounds(self.simEngine.staticWorld.numBounds)
        self.makeStatMenu(3)
        self.root.after(0, self.refreshScreen)                  #adds task to refresh screen information
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
                self.worldGraph.plotImage(self.worldGraph.size_up(self.animatImage, (animat.radius*2,animat.radius*2), animat.direc-np.pi/2.), (animat.radius*2,animat.radius*2), (animat.pos[0], animat.pos[1]), animat.direc-np.pi/2.)
                #self.worldGraph.plotCircle((animat.radius*2,animat.radius*2), (animat.pos[0], animat.pos[1]), self.colorGrey)
                self.worldGraph.plotText(("Purisa", 6) , (animat.pos[0], animat.pos[1]), animat.id)
                if not (animat.id in self.neuron_graphs.iterkeys()):
                    neuronGraph = Graph(self.root, self.neuron_box.content_bounds, [-1.1, 1.1, -1.1, 1.1])
                    self.neuron_graphs[animat.id] = neuronGraph
                    self.neuron_box.add(neuronGraph, animat.id)

                neuronGraph = self.neuron_graphs[animat.id]
                neuronGraph.plotCircle((2, 2), (0, 0), self.colorWhite)
                neurons = animat.net.getNeurons()
                for neuron in neurons:
                    neuronGraph.plotCircle((.05, .05), (neuron.X, neuron.Y), neuron.firing_color if neuron.isFiring() else neuron.color)
                neuronGraph.draw(self.canvas)

            foodImage = self.worldGraph.size_up(self.foodImage, (1,1), 0)
            for food in self.world.foods:
                if food.amt > 0.0:
                    self.worldGraph.plotImage(foodImage, (1, 1), food.pos)
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
        listBox = tk.Listbox(win)
        for i in [n.index for n in self.world.animats[0].net.getNeurons()]: listBox.insert('end',i)
        viewButton = tk.Button(win,text="View",command= lambda: self.plotConnection(win,listBox.get('active')))
        excitT = "Excitatory Neurons: "+str(self.world.animats[0].net.excitatoryNeurons[0])+"->"+str(self.world.animats[0].net.excitatoryNeurons[-1])
        #inhibT = "Inhibitory Neurons: "+str(self.world.animats[0].net.inhibitoryNeurons[0])+"->"+str(self.world.animats[0].net.inhibitoryNeurons[-1])
        senseT = "Sensory Neurons: "+str(self.world.animats[0].net.senseNeurons[0])+"->"+str(self.world.animats[0].net.senseNeurons[-1])
        motorT = "Motor Neurons: "+str(self.world.animats[0].net.motorNeurons[0])+"->"+str(self.world.animats[0].net.motorNeurons[-1])
        hungerT = "Hunger Neurons: "+str(self.world.animats[0].net.hungerNeurons[0])+"->"+str(self.world.animats[0].net.hungerNeurons[-1])
        excitL = tk.Label(win,text=excitT)
        #inhibL = tk.Label(win,text=inhibT)
        senseL = tk.Label(win,text=senseT)
        motorL = tk.Label(win,text=motorT)
        hungerL = tk.Label(win,text=hungerT)
        excitL.place(x=100,y=300)
        #inhibL.place(x=100,y=400)
        senseL.place(x=100,y=325)
        motorL.place(x=100,y=350)
        hungerL.place(x=100,y=375)
        listBox.place(x=100,y=100)
        viewButton.place(x=300,y=100)



    def plotConnection(self,window,index):
        neuronGraph = Graph(window, self.neuron_box.content_bounds, [-1.1, 1.1, -1.1, 1.1])
        neuronGraph.plotCircle((2, 2), (0, 0), self.colorWhite)
        neurons = self.world.animats[0].net.getNeurons()
        connections = np.nonzero(self.world.animats[0].net.S[index])[0]
        print connections
        for neuron in neurons:
            if neuron.index == index:
                neuronGraph.plotCircle((.05, .05), (neuron.X, neuron.Y), '#3333FF')  #blue for target neuron
            elif neuron.index in connections:
                neuronGraph.plotCircle((.05, .05), (neuron.X, neuron.Y), '#000000')  #black for connecting neurons
            else:
                neuronGraph.plotCircle((.05, .05), (neuron.X, neuron.Y), neuron.color) #plot normal color
        neuronGraph.draw(self.canvas)


    def showDevWin(self):
        self.simEngine.stopSimulation()
        self.root.destroy()
        self.devWin.deiconify()

    def benchmark(self):
        for anim in self.world.animats:
            anim.calcBenchmark(self.buff_t,self.simEngine.getRunTime())
