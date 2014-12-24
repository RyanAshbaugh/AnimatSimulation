import numpy as np
import scipy.spatial
from scipy import *
import time

global t1
global t2

def tic():
    global t1
    t1 = time.clock()

def toc():
    global t2
    global t1
    t2 = time.clock()
    print(t2-t1)
    t1 = t2

a = np.array([1,])
print a
a = np.insert(a, 0, 100)
print a

points = np.array([[2,3],[5,0],[1,2]])
print(points)

smells = np.array([[5, 2], [6, 4],[7, 3], [8, 5]])
smellstrength = np.array([[0, 1, 2, 3]])
#smellstrength=1
print(smells)
#smell = np.array([[5],[2]])
#print(points-smells)
#tic()
#dists = np.linalg.norm(points-smells,axis=1)
#toc()
#print(dists)
print(np.sum(scipy.spatial.distance.cdist( points, smells )*smellstrength, axis=1))

points = np.array([[1,0],[2,0]])
print(points)
dir = np.pi/2
rotMat = np.array([[cos(dir), -sin(dir)], [sin(dir), cos(dir)]])
print(rotMat)
print(np.dot(points,rotMat))