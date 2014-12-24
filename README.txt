LAST EDIT: 11/12/2014


****** AnimatClusterSimulation ReadME ********************

 Prior to running for first time
 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  -To install pp type: pip install --user pp --allow-external --allow-unverified
  -To upgrade numpy (dogwood has outdated version) type: pip install --user --upgrade numpy


 To Run
 ~~~~~~~~~~~~~~~~~
  First start ppservers on nodes:

	user@dogwood00 AnimatClusterSim$ python startServers.py

  Let run untill done running simulations then enter 'q' to close servers.
  **Note, you must enter 'r' to restart all the servers if any changes are made to the source code, i.e. redefine     metrics


  Now run masterDriver.py

  user@dogwood00$ python masterDriver.py <Command> [options]
	Commands:
		Not currently implemented, perhaps presets for high-res record vs quick-run
	Options:
		-h : Display this help message
                -a : How many different animats to run  (1 animat per node)
                -w : How many worlds to run animat in (i.e. how many simulations on each node)
                -u : Username for SSH session
                -p : Password for SSH session
                -f : File to read settings from
                -e : Run with evolutionary algorithm
                -p : Print true or false
                -t : Number of simulated milliseconds
                -i : Write interval

