
#AnimatSimulation

AnimatSimulation simulates simple, virtual animals (animats) behavior using a neural network based on the Izhikevich neuron model. 
There are 2 components to the simulation.

1. **Evolutionary Algorithm**

   This is used for running simulations in parallel on a cluster to evolve animats. An intitial generation of animats are created, run through multiple simulations then ranked. New animats are then created based on the top scoring animats, then all animats run again. This repeats for a set number of cycles, or generations, evolving the animat. When completed, the option is given to save the top scoring Animat to run in the visual simulation, and also a log file detailing results of each generation is saved.

2.  **Visual Simulation**

   This is used to visualize simulations. An animat created by the Evolutionary Algorithm can be loaded and run, random animats can be created and run, or a user-defined animat may be created and run. Various statistics can be tracked and visualized while simulation is running such as energy levels, neuron firings, animat position, etc. 
 


## Dependencies 

####Evolutionary Algorithm

>* [Spur](https://pypi.python.org/pypi/spur) - Used for SSH connections in cluster
>* [Numpy](http://www.numpy.org/) - Scientific functions (also needed for visual simulation)
>* [ParallelPython](http://www.parallelpython.com/) - Used for cluster/SMP execution and management

####Visual Simulation

>* [matplotlib](http://matplotlib.org/) - Used for displaying data
>* [Tkinter](https://wiki.python.org/moin/TkInter) - Backend library for GUI
>* [PIL](http://www.pythonware.com/products/pil/) - Used for image processing

## To Run

####Evolutionary Algorithm
1. Copy all contents of AnimatSimulation onto master node of cluster.
2. Run startServers.py to start ParallelPython servers on all nodes in cluster. 
>$ python startServers.py   

3. Once all servers have been initialized, in a new terminal window, run EvoDriver.py
>$ python EvoDriver.py

4. When completed, the option to save top animat will be presented, as well as desired filenames for log files. Log files and animat data will be saved to current directory.


####Visual Simulation
1. Copy all contents of AnimatSimulation to desired location.
2. Run DevelopmentWindow.
>$ python DevelopmentWindow.py

3. Choose animat to run
    + To load animat produced from Evolutionary Algorithm, choose *File* --> *Load Results from Evolutionary Algorithm*
    + To run custom animat, choose *Edit* --> *Parameters* 
    + To run with default don't choose anything
4. To start the simulation choose *File* --> *Start Simulation*
5. Once simulation is running, you can always makes changes to animats by choosing *Edit* --> *Parameters*. To start a new simulation choose *File* --> *Start New Simulation*.

Simulations can be saved for replay by choosing *File* --> *Save Simulation*. Replaying a saved simulation can be done in the same manner.


