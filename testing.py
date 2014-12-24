__author__ = 'Steven'
import numpy
import threading

from numbapro import vectorize

def coderun():
    print("hi")
    print(sum(numpy.array([3,5], dtype = numpy.int_), numpy.int_(3)))



@vectorize(['int_(int_, int_)'],
 target='parallel')
def sum(a, b):
 return (a - b) > 0

#print(sum(numpy.array([3,5], dtype = numpy.int_), numpy.array([3,5], dtype = numpy.int_)))
t = threading.Thread(target=coderun, name="hi")
t.daemon=True
t.start()
while(1):
    pass