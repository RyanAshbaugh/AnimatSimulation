__author__ = 'Kurt Hauser'
import Tkinter as tk
import copy

###FOR MORE THAN TAB_WIDTH NEEDS CHANGING

class TabBox:

    def __init__(self, root, bounds, toolbar = False):
        self.bounds = bounds[:]
        self.root = root
        self.TABS_PER_ROW = 5
        self.TAB_WIDTH = int((float(self.bounds[2]-self.bounds[0]))/self.TABS_PER_ROW)
        self.TAB_HEIGHT = 20
        self.TAB_POS_X = 0
        self.TAB_POS_Y = 0
        self.TOOLBAR_HEIGHT = 2
        self.content_bounds = [bounds[0], bounds[1]+ self.TAB_HEIGHT, bounds[2], bounds[3]]
        self.toolbar_bounds = [bounds[0], bounds[3]-self.TOOLBAR_HEIGHT, bounds[2], bounds[3]]

        self.area_canvas = tk.Canvas(self.root, width=self.bounds[2]-self.bounds[0], height=self.bounds[3]-self.bounds[1])
        self.area_canvas.place(x=self.bounds[0], y=self.bounds[1])
        #print((1, 1, self.TAB_WIDTH, self.TAB_HEIGHT))
        #self.area_canvas.create_rectangle((1, 1, self.TAB_WIDTH, self.TAB_HEIGHT), fill="#00ff00", state="normal")
        self.graphs = []
        self.canvases = []
        self.toolbar_canvases = []
        self.type = "canvas"
        self.toolbar = toolbar
        self.tabs = []
        self.titles = []
        self.active = -1
        if self.toolbar: self.content_bounds = [bounds[0], bounds[1]+self.TAB_HEIGHT, bounds[2], bounds[3]-self.TOOLBAR_HEIGHT-10]

    def add_canvas(self, canvas, title):
        if self.toolbar:
            toolbar_canvas = tk.Canvas(self.root, width = self.toolbar_bounds[2]-self.toolbar_bounds[0], height = self.TOOLBAR_HEIGHT)
            toolbar_canvas.place(x=self.toolbar_bounds[0], y= self.toolbar_bounds[1])
            self.toolbar_canvases.append(toolbar_canvas)

        self.type = "canvas"
        self.canvases.append(canvas)
        canvas.place(x=self.content_bounds[0], y=self.content_bounds[1])
        canvas.config(width=(self.content_bounds[2]-self.content_bounds[0]), height=(self.content_bounds[3]-self.content_bounds[1]))
        tab =self.area_canvas.create_rectangle((self.TAB_POS_X, self.TAB_POS_Y, self.TAB_POS_X + self.TAB_WIDTH, self.TAB_POS_Y + self.TAB_HEIGHT), state="normal")
        titleint = self.area_canvas.create_text(self.TAB_POS_X + self.TAB_WIDTH/2, self.TAB_POS_Y + self.TAB_HEIGHT/2, text=title)
        self.tabs.append(tab)
        self.titles.append(titleint)
        number = len(self.canvases)-1
        self.area_canvas.tag_bind(tab, '<ButtonPress-1>', lambda x:self.setActive(number))
        self.area_canvas.tag_bind(titleint, '<ButtonPress-1>', lambda x:self.setActive(number))
        self.setActive(len(self.canvases) - 1)
        self.TAB_POS_X += self.TAB_WIDTH
        if (self.TAB_POS_X + self.TAB_WIDTH) > (self.bounds[2] - self.bounds[0]):
            print('too many tabs')
            self.TAB_POS_X = 0
            self.TAB_POS_Y += self.TAB_HEIGHT
            self.content_bounds[1] += self.TAB_HEIGHT
            print(self.TAB_POS_X, self.TAB_POS_Y)
            for canvas in self.canvases:
                canvas.change_plot_bounds(self.content_bounds)
                canvas.set_area_bounds(self.content_bounds)
        if self.toolbar: return self.toolbar_canvases[-1]

    def add(self, graph, title):
        self.type = "graph"
        self.graphs.append(graph)
        graph.change_plot_bounds(self.content_bounds)
        graph.set_area_bounds(self.content_bounds)
        #canvas.place(x=self.content_bounds[0], y=self.content_bounds[1])
        #canvas.config(width = self.content_bounds[2] - self.content_bounds[0], height = self.content_bounds[3] - self.content_bounds[1])
        tab =self.area_canvas.create_rectangle((self.TAB_POS_X, self.TAB_POS_Y, self.TAB_POS_X + self.TAB_WIDTH, self.TAB_POS_Y + self.TAB_HEIGHT), state="normal")
        titleint = self.area_canvas.create_text(self.TAB_POS_X + self.TAB_WIDTH/2, self.TAB_POS_Y + self.TAB_HEIGHT/2, text=title)
        self.tabs.append(tab)
        self.titles.append(titleint)
        number = len(self.graphs)-1
        self.area_canvas.tag_bind(tab, '<ButtonPress-1>', lambda x:self.setActive(number))
        self.area_canvas.tag_bind(titleint, '<ButtonPress-1>', lambda x:self.setActive(number))
        self.setActive(len(self.graphs) - 1)
        self.TAB_POS_X += self.TAB_WIDTH
        if (self.TAB_POS_X + self.TAB_WIDTH) > (self.bounds[2] - self.bounds[0]):
            print('too many tabs')
            self.TAB_POS_X = 0
            self.TAB_POS_Y += self.TAB_HEIGHT
            self.content_bounds[1] += self.TAB_HEIGHT
            print(self.TAB_POS_X, self.TAB_POS_Y)
            for graph in self.graphs:
                graph.change_plot_bounds(self.content_bounds)
                graph.set_area_bounds(self.content_bounds)
        #for index in range(0, len(self.graphs)-1):
            #graph.canvas.config(state="hidden")
        #print('here')
        #graph.canvas.config(state=tk.HIDDEN)

    def setActive(self, index):
        self.active = index
        if self.type == "canvas":
            tk.Misc.lift(self.canvases[self.active], aboveThis=None)
            self.canvases[self.active].focus_force()
            if self.toolbar: tk.Misc.lift(self.toolbar_canvases[self.active], aboveThis = None)
            for i in range(0, len(self.canvases)):
                if i == index: self.area_canvas.itemconfig(self.tabs[self.active], fill = "#ffffff")
                else:
            #        self.graphs[i].canvas.lower(self.graphs[self.active].canvas)
            #        self.graphs[self.active].canvas.lift(self.graphs[i].canvas)
                    self.area_canvas.itemconfig(self.tabs[i], fill = "#eeeeee")
        else:
            tk.Misc.lift(self.graphs[self.active].canvas, aboveThis=None)
            for i in range(0, len(self.graphs)):
                if i == index: self.area_canvas.itemconfig(self.tabs[self.active], fill = "#ffffff")
                else:
            #        self.graphs[i].canvas.lower(self.graphs[self.active].canvas)
            #        self.graphs[self.active].canvas.lift(self.graphs[i].canvas)
                    self.area_canvas.itemconfig(self.tabs[i], fill = "#eeeeee")


