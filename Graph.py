__author__ = 'Steven'
import ImageTk
import Image
import numpy as np
import Queue
import Tkinter as tk
from PIL import Image
from PIL import ImageTk

class Graph:

    def __init__(self, root, graphBounds = [0,0,0,0], numBounds = [0,0,0,0]):
        self.root = root
        self.graphBounds = graphBounds[:]
        self.graph_cBounds = graphBounds[:]
        self.numBounds = numBounds
        self.area_bounds = graphBounds[:]

        self.area_canvas = tk.Canvas(self.root, width=graphBounds[2]-graphBounds[0], height=graphBounds[3]-graphBounds[1])
        self.area_canvas.place(x=graphBounds[0], y=graphBounds[1])
        self.canvas = tk.Canvas(self.root, width=graphBounds[2]-graphBounds[0], height=graphBounds[3]-graphBounds[1])
        self.canvas.place(x=graphBounds[0], y=graphBounds[1])

        self.graphBounds[2] -= self.graphBounds[0]
        self.graphBounds[3] -= self.graphBounds[1]
        self.graphBounds[0] = 0
        self.graphBounds[1] = 0
        #self.canvas.pack()
        self.colorWhite = "#ffffff"
        self.colorGrey = "#dddddd"
        self.colorBlack = "#000000"
        self.unitWidth = (self.graphBounds[2]-self.graphBounds[0]) / ( self.numBounds[1] - self.numBounds[0] )
        self.unitHeight = (self.graphBounds[3]-self.graphBounds[1]) / ( self.numBounds[3] - self.numBounds[2] )
        self.xticks = []
        self.yticks = []
        self._title = self.area_canvas.create_text((0,0), state="hidden")
        self._xlabel = self.area_canvas.create_text((0,0), state = "hidden")
        self._ylabel = self.area_canvas.create_text((0,0), state = "hidden")
        self.title_text = ""
        self.has_title = False
        self.has_xlabel = False
        self.has_ylabel = False
        self.TITLE_SPACE = 30
        self.LABEL_SPACE = 20

        self.outAxesX = False
        self.outAxesY = False

        self.x_n = 10
        self.y_n = 10

        self.circleIDs = []
        self.c_i = 0
        self.imageIDs = []
        self.i_i = 0
        self.lineIDs = []
        self.l_i = 0
        self.rectangleIDs = []
        self.r_i = 0
        self.textIDs = []
        self.t_i = 0

        self.main_rectangle = self.canvas.create_rectangle((0,0),(0,0))
        self.canvas.tag_bind(self.main_rectangle, '<ButtonPress-1>', self.zoomIn)
        self.canvas.tag_bind(self.main_rectangle, '<ButtonPress-3>', self.zoomOut)
        self.canvas.bind('<ButtonPress-1>', self.zoomIn)
        self.canvas.bind('<ButtonPress-3>', self.zoomOut)
        self.canvas.config(bg=self.colorWhite, borderwidth = 1, highlightbackground=self.colorBlack)
        self.images = []
        self.imageIndex = 0
        self.circles = []
        self.circleIndex = 0
        self.lines = []
        self.lineIndex = 0
        self.rectangles = []
        self.rectangleIndex = 0
        self.texts = []
        self.textIndex = 0

    def zoomIn(self, event):
        x1, x2, y1, y2 = self.numBounds
        self.numBounds = (x1/1.2, x2/1.2, y1/1.2, y2/1.2)
        self.unitWidth = (self.graphBounds[2]-self.graphBounds[0]) / ( self.numBounds[1] - self.numBounds[0] )
        self.unitHeight = (self.graphBounds[3]-self.graphBounds[1]) / ( self.numBounds[3] - self.numBounds[2] )

    def zoomOut(self, event):
        x1, x2, y1, y2 = self.numBounds
        self.numBounds = (x1*1.2, x2*1.2, y1*1.2, y2*1.2)
        self.unitWidth = (self.graphBounds[2]-self.graphBounds[0]) / ( self.numBounds[1] - self.numBounds[0] )
        self.unitHeight = (self.graphBounds[3]-self.graphBounds[1]) / ( self.numBounds[3] - self.numBounds[2] )

    def transformCoordinates(self, coords):
        x = float(coords[0])
        y = float(coords[1])
        nbx1 = self.numBounds[0]
        nbx2 = self.numBounds[1]
        nby1 = self.numBounds[2]
        nby2 = self.numBounds[3]
        nx = x - nbx1
        ny = nby2 - y
        #ny = y + nby1
        xprop = nx/(nbx2-nbx1)
        yprop = ny/(nby2-nby1)
        retX = int(round(xprop * (self.graphBounds[2]-self.graphBounds[0])) + self.graphBounds[0])
        retY = int(round(yprop * (self.graphBounds[3]-self.graphBounds[1])) + self.graphBounds[1])
        return (retX, retY)

    def title(self, title):
        self.area_canvas.coords(self._title, int(float(self.graph_cBounds[2] - self.graph_cBounds[0])/2.), self.TITLE_SPACE/3)
        self.area_canvas.itemconfig(self._title, text = title, state = "normal", font = "Arial 14")
        self.has_title = True

        bounds = self.graph_cBounds[:]
        bounds[1] += self.TITLE_SPACE
        self.change_plot_bounds(bounds)
        return

    def set_area_bounds(self, bounds):
        self.area_bounds = bounds[:]
        graphBounds = bounds
        self.area_canvas.config(width=graphBounds[2]-graphBounds[0], height=graphBounds[3]-graphBounds[1], bg = "#ff0000")
        self.area_canvas.place(x=graphBounds[0], y=graphBounds[1])

    def change_plot_bounds(self,bounds):
        ydif = (self.graph_cBounds[3] - self.graph_cBounds[1]) - (bounds[3] - bounds[1])
        xdif = (self.graph_cBounds[2] - self.graph_cBounds[0]) - (bounds[2] - bounds[0])
        self.graphBounds[3] -= ydif
        self.graphBounds[2] -= xdif
        self.graph_cBounds = bounds[:]
        self.canvas.config(width=self.graphBounds[2]-self.graphBounds[0], height=self.graphBounds[3]-self.graphBounds[1])
        self.canvas.place(x=self.graph_cBounds[0], y=self.graph_cBounds[1])
        self.unitWidth = (self.graphBounds[2]-self.graphBounds[0]) / ( self.numBounds[1] - self.numBounds[0] )
        self.unitHeight = (self.graphBounds[3]-self.graphBounds[1]) / ( self.numBounds[3] - self.numBounds[2] )


    def xlabel(self, label):
        self.area_canvas.itemconfig(self._xlabel, text = label, state = "normal", font = "Arial 8")

        self.has_xlabel = True

        bounds = self.graph_cBounds[:]
        bounds[3] -= self.LABEL_SPACE
        print(bounds)
        self.change_plot_bounds(bounds)
        self.area_canvas.coords(self._xlabel, int(float(self.graph_cBounds[2] - self.graph_cBounds[0])/2.), (self.graph_cBounds[3] - self.area_bounds[1]) + self.LABEL_SPACE*2/3)
        return

        #self.graphBounds[1] += self.TITLE_SPACE
        graphBounds = [self.graphBounds[0] + self.area_bounds[0], self.graphBounds[1]+self.area_bounds[1], self.graphBounds[2] + self.area_bounds[0], self.graphBounds[3] + self.area_bounds[1]]
        graphBounds = self.graph_cBounds
        graphBounds[3] -= self.LABEL_SPACE
        #self.graphBounds[3] -= self.TITLE_SPACE
        self.graphBounds[3] -= self.LABEL_SPACE
        self.canvas.config(width=graphBounds[2]-graphBounds[0], height=graphBounds[3]-graphBounds[1])
        self.canvas.place(x=self.graph_cBounds[0], y=self.graph_cBounds[1])
        self.graph_cBounds = graphBounds
        self.area_canvas.coords(self._xlabel, int(float(self.graph_cBounds[2] - self.graph_cBounds[0])/2.), (self.graph_cBounds[3] - self.area_bounds[1]) + self.LABEL_SPACE*2/3)
        self.unitWidth = (self.graphBounds[2]-self.graphBounds[0]) / ( self.numBounds[1] - self.numBounds[0] )
        self.unitHeight = (self.graphBounds[3]-self.graphBounds[1]) / ( self.numBounds[3] - self.numBounds[2] )

    def ylabel(self, label):
        return
        self.area_canvas.itemconfig(self._ylabel, text = label, state = "normal", font = "Arial 8")
        self.has_ylabel = True
        #self.graphBounds[1] += self.TITLE_SPACE
        graphBounds = [self.graphBounds[0] + self.area_bounds[0], self.graphBounds[1]+self.area_bounds[1], self.graphBounds[2] + self.area_bounds[0], self.graphBounds[3] + self.area_bounds[1]]
        graphBounds = self.graph_cBounds
        graphBounds[2] -= self.LABEL_SPACE
        #self.graphBounds[3] -= self.TITLE_SPACE
        self.graphBounds[2] -= self.LABEL_SPACE
        self.canvas.config(width=graphBounds[2]-graphBounds[0], height=graphBounds[3]-graphBounds[1])
        self.canvas.place(x=self.graph_cBounds[0], y=self.graph_cBounds[1])
        self.graph_cBounds = graphBounds
        print(self.graph_cBounds)
        print(int(float(self.graph_cBounds[2] - self.graph_cBounds[0])/2.), (self.graph_cBounds[3] - self.area_bounds[1]) + self.LABEL_SPACE/3)
        self.area_canvas.coords(self._ylabel, int(float(self.graph_cBounds[2] - self.graph_cBounds[0])/2.), (self.graph_cBounds[3] - self.area_bounds[1]) + self.LABEL_SPACE*2/3)
        self.area_canvas.coords(self._ylabel, (self.graph_cBounds[2] - self.area_bounds[0]) + self.LABEL_SPACE*2/3, int(float(self.graph_cBounds[3] - self.graph_cBounds[1])/2. + self.graph_cBounds[1]-self.area_bounds[1]))
        self.unitWidth = (self.graphBounds[2]-self.graphBounds[0]) / ( self.numBounds[1] - self.numBounds[0] )
        self.unitHeight = (self.graphBounds[3]-self.graphBounds[1]) / ( self.numBounds[3] - self.numBounds[2] )

    def inBounds(self, coords):
        x = coords[0]
        y = coords[1]
        ret = False
        if(float(x) < float(self.numBounds[1]) and float(x) > float(self.numBounds[0])): ret = True
        return ret and (float(y) < float(self.numBounds[3]) and float(y) > float(self.numBounds[2]))

    def size_up(self, image, size, angle):
        w = size[0] * self.unitWidth
        h = size[1] * self.unitHeight
        return ImageTk.PhotoImage(image.resize((int(w), int(h)), Image.NEAREST).rotate(np.degrees(angle)))

    def plotImage(self, img, size, coords, angle = 0):
        w = size[0] * self.unitWidth
        h = size[1] * self.unitHeight
        #img = ImageTk.PhotoImage(image.resize((int(w), int(h)), Image.NEAREST).rotate(np.degrees(angle)))
        #img = image.rotate(np.degrees(angle))
        if(self.imageIndex > len(self.images)-1):
            self.images.append((img, coords, (w, h)))
        else: self.images[self.imageIndex] = (img, coords, (w, h))
        self.imageIndex += 1

    def plotCircle(self, size, coords, color):
        w = float(size[0])
        h = float(size[1])
        p1 = (float(coords[0]) - w/2., float(coords[1]) + h/2.)
        p2 = (float(coords[0]) + w/2., float(coords[1]) - h/2.)
        if(self.circleIndex > len(self.circles)-1):
            self.circles.append((p1, p2, color))
        else: self.circles[self.circleIndex] = (p1, p2, color)
        self.circleIndex += 1

    def plotLine(self, width, p1, p2, color):
        if(self.lineIndex > len(self.lines)-1):
            self.lines.append((width, p1, p2, color))
        else: self.lines[self.lineIndex] = (width, p1, p2, color)
        self.lineIndex += 1

    def plotText(self, font, coords, text, color = "#000000"):
        if(self.textIndex > len(self.texts)-1):
            self.texts.append((font, coords, text, color))
        else: self.texts[self.textIndex] = (font, coords, text, color)
        self.textIndex += 1

    def getLine(self):
        if self.l_i >= len(self.lineIDs):
            self.lineIDs.append(self.canvas.create_line(0, 0, 0, 0))
        ID = self.lineIDs[self.l_i]
        self.canvas.itemconfig(ID, state = "normal")
        self.canvas.tag_bind(ID, '<ButtonPress-1>', self.zoomIn)
        self.canvas.tag_bind(ID, '<ButtonPress-3>', self.zoomOut)
        self.l_i += 1
        return ID


    def getImage(self):
        if self.i_i >= len(self.imageIDs):
            self.imageIDs.append(self.canvas.create_image(0, 0))
        ID = self.imageIDs[self.i_i]
        self.canvas.tag_bind(ID, '<ButtonPress-1>', self.zoomIn)
        self.canvas.tag_bind(ID, '<ButtonPress-3>', self.zoomOut)
        self.i_i += 1
        return ID

    def getCircle(self):
        if self.c_i >= len(self.circleIDs):
            self.circleIDs.append(self.canvas.create_oval(0, 0, 0, 0))
        ID = self.circleIDs[self.c_i]
        self.canvas.itemconfig(ID, state = "normal")
        self.canvas.tag_bind(ID, '<ButtonPress-1>', self.zoomIn)
        self.canvas.tag_bind(ID, '<ButtonPress-3>', self.zoomOut)
        self.c_i += 1
        return ID

    def getText(self):
        if self.t_i >= len(self.textIDs):
            self.textIDs.append(self.canvas.create_text(0, 0))
        ID = self.textIDs[self.t_i]
        self.canvas.itemconfig(ID, state = "normal")
        self.canvas.tag_bind(ID, '<ButtonPress-1>', self.zoomIn)
        self.canvas.tag_bind(ID, '<ButtonPress-3>', self.zoomOut)
        self.t_i += 1
        return ID

    def getRectangle(self):
        if self.r_i >= len(self.rectangleIDs):
            self.rectangleIDs.append(self.canvas.create_rectangle(0, 0, 0, 0))
        ID = self.rectangleIDs[self.r_i]
        self.canvas.itemconfig(ID, state = "normal")
        self.canvas.tag_bind(ID, '<ButtonPress-1>', self.zoomIn)
        self.canvas.tag_bind(ID, '<ButtonPress-3>', self.zoomOut)
        self.r_i += 1
        return ID

    def plot(self, xvals, yvals, xrange = [], yrange = [], style = '-', color = "#000000"):
        if len(xvals) == 0: return
        if yrange == []:
            ymax = max(yvals)
            ymin = min(yvals)
        else:
            ymax = yrange[1]
            ymin = yrange[0]
        if xrange == []:
            xmax = max(xvals)
            xmin = min(xvals)
        else:
            xmax = xrange[1]
            xmin = xrange[0]
        self.numBounds = [xmin, xmax, ymin, ymax]
        self.unitWidth = (self.graphBounds[2]-self.graphBounds[0]) / ( self.numBounds[1] - self.numBounds[0] )
        self.unitHeight = (self.graphBounds[3]-self.graphBounds[1]) / ( self.numBounds[3] - self.numBounds[2] )
        if style == '-':
            for index in range(0, len(xvals)-1):
                self.plotLine(1, (xvals[index], yvals[index]), (xvals[index+1], yvals[index+1]), color)
        elif style == '.':
            for index in range(0, len(xvals)-1):
                self.plotLine(1, (xvals[index], yvals[index]), (xvals[index]+1, yvals[index]), color)

    def drawAxes(self):
        if(0 < self.numBounds[1] and 0 > self.numBounds[0]):
            x1, y1 = self.transformCoordinates((0, self.numBounds[2]))
            x2, y2 = self.transformCoordinates((0, self.numBounds[3]))
            line = self.getLine()
            self.canvas.coords(line, (x1, y1, x2, y2))
            self.canvas.itemconfig(line, fill = self.colorBlack, width = 1)
            self.outAxesX = False
        else: self.outAxesX = True
        if(0 < self.numBounds[3] and 0 > self.numBounds[2]):
            x1, y1 = self.transformCoordinates((self.numBounds[0], 0))
            x2, y2 = self.transformCoordinates((self.numBounds[1], 0))
            line = self.getLine()
            self.canvas.coords(line, (x1, y1, x2, y2))
            self.canvas.itemconfig(line, fill = self.colorBlack, width = 1)
            self.outAxesY = False
        else: self.outAxesY = True

    def drawLabels(self):
        pass

    def drawTicks(self):
        self.tick_width = 2
        xinterval = (float(self.numBounds[1])-float(self.numBounds[0]))/self.x_n
        yinterval = (float(self.numBounds[3])-float(self.numBounds[2]))/self.y_n
        xtick = float(self.numBounds[0])
        ytick = float(self.numBounds[2])
        self.xticks = []
        self.yticks = []
        count = 0
        while(count <= self.x_n):
            self.xticks.append(str(xtick))
            line = self.getLine()
            label = self.getText()
            coords = self.transformCoordinates((xtick, 0))
            if self.outAxesY: coords = (coords[0],self.graphBounds[0]+2)
            self.canvas.coords(line, (coords[0], coords[1]-self.tick_width, coords[0], coords[1]+self.tick_width))
            self.canvas.coords(label, (coords[0], coords[1]+self.tick_width+10))
            self.canvas.itemconfig(line, fill = self.colorBlack, width = 1)
            if(np.abs(xtick) > 0.0000000001): self.canvas.itemconfig(label, text=str('{0:.2f}'.format(xtick)), font = ("Purisa", 6), fill = self.colorBlack)
            xtick += xinterval
            self.textIndex += 1
            count += 1
        count = 0
        while(count <= self.y_n):
            self.yticks.append(str(ytick))
            line = self.getLine()
            label = self.getText()
            coords = self.transformCoordinates((0, ytick))
            if self.outAxesY: coords = (self.graphBounds[0]+2, coords[1])
            self.canvas.coords(line, (coords[0]-self.tick_width, coords[1], coords[0]+self.tick_width, coords[1]))
            self.canvas.coords(label, (coords[0]-self.tick_width-15, coords[1]))
            self.canvas.itemconfig(line, fill = self.colorBlack, width = 1)
            #print(ytick)
            if(np.abs(ytick) > 0.0000001): self.canvas.itemconfig(label, text=str('{0:.2f}'.format(ytick)), font = ("Purisa", 6), fill = self.colorBlack)
            ytick += yinterval
            self.textIndex += 1
            count += 1



    def cleanUp(self):
        for index in range(self.l_i, len(self.lineIDs)):
            self.canvas.itemconfig(self.lineIDs[index], state = tk.HIDDEN)
        for index in range(self.c_i, len(self.circleIDs)):
            self.canvas.itemconfig(self.circleIDs[index], state = tk.HIDDEN)
        for index in range(self.i_i, len(self.imageIDs)):
            self.canvas.itemconfig(self.imageIDs[index], state = tk.HIDDEN)
        for index in range(self.r_i, len(self.rectangleIDs)):
            self.canvas.itemconfig(self.rectangleIDs[index], state = tk.HIDDEN)
        for index in range(self.t_i, len(self.textIDs)):
            self.canvas.itemconfig(self.textIDs[index], state = tk.HIDDEN)
        self.l_i = 0
        self.i_i = 0
        self.c_i = 0
        self.r_i = 0
        self.t_i = 0
        self.imageIndex = 0
        self.circleIndex = 0
        self.lineIndex = 0
        self.textIndex = 0
        self.rectangleIndex = 0

    def set_numBounds(self, numb):
        self.numBounds = numb[:]
        self.unitWidth = (self.graphBounds[2]-self.graphBounds[0]) / ( self.numBounds[1] - self.numBounds[0] )
        self.unitHeight = (self.graphBounds[3]-self.graphBounds[1]) / ( self.numBounds[3] - self.numBounds[2] )

    def draw(self, canvas):

        rect = self.main_rectangle

        for index in range(0, self.imageIndex):
            image = self.images[index]
            im = self.getImage()
            w, h = image[2]
            coords = self.transformCoordinates(image[1])
            self.canvas.coords(im, (coords[0]-(w/2), coords[1]))
            #self.canvas.coords(im, coords)
            self.canvas.itemconfig(im, image = image[0], state = "normal")

        for index in range(0, self.circleIndex):
            circle = self.circles[index]
            p1, p2, color = circle
            p1 = self.transformCoordinates(p1)
            p2 = self.transformCoordinates(p2)
            circleID = self.getCircle()
            self.canvas.coords(circleID, p1[0], p1[1], p2[0], p2[1])
            self.canvas.itemconfig(circleID, outline = "black", fill = color, width = 2)

        for index in range(0, self.lineIndex):
            line = self.lines[index]
            width, p1, p2, color = line
            p1 = self.transformCoordinates(p1)
            p2 = self.transformCoordinates(p2)
            lineID = self.getLine()
            self.canvas.coords(lineID, (p1[0], p1[1], p2[0], p2[1]))
            self.canvas.itemconfig(lineID, fill = color, width = 1, state = "normal")

        for index in range(0, self.textIndex):
            text = self.texts[index]
            font, coords, text, color = text
            coords = self.transformCoordinates(coords)
            textID = self.getText()
            self.canvas.coords(textID, coords)
            self.canvas.itemconfig(textID, font = font, fill = color, text = text)

        self.drawAxes()
        self.drawTicks()

        self.cleanUp()
        self.canvas.config(state="disabled")