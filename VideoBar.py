__author__ = 'Steven'
import copy

class VideoBar:
    def __init__(self, canvas, graphBounds, timeBounds, onClick):
        self.canvas = canvas
        self.onClick = onClick

        self.numTicks = 6

        self.graphBounds = graphBounds
        self.timeBounds = timeBounds
        self.originaltimeBounds = copy.deepcopy(timeBounds)
        self.buff_t = 0
        self.curr_t = 0
        self.colorLightBlue = "#ADD8E6"
        self.colorBlue = "#0000ff"
        self.colorBlack = "#000000"
        self.colorWhite = "#ffffff"

        self.timeRect = self.canvas.create_rectangle(self.graphBounds, fill = self.colorWhite)
        self.bufferRect = self.canvas.create_rectangle(self.graphBounds, fill = self.colorLightBlue)
        self.canvas.tag_bind(self.bufferRect, '<ButtonPress-1>', self.onBufferClick)
        self.currentRect = self.canvas.create_rectangle(self.graphBounds, fill = self.colorBlue)
        self.canvas.tag_bind(self.currentRect, '<ButtonPress-1>', self.onBufferClick)
        self.t_text = self.canvas.create_text((0,0))

        self.textIDs = []
        self.t_i = 0
        self.lineIDs = []
        self.l_i = 0

        self.ticks = []
        self.createTicks()

    def onBufferClick(self, event):
        t = (float(event.x - self.graphBounds[0]) / float(self.graphBounds[2] - self.graphBounds[0])) * float(self.timeBounds[1]-self.timeBounds[0]) + self.timeBounds[0]
        self.onClick(int(t))

    def reset(self):
        self.timeBounds = copy.deepcopy(self.originaltimeBounds)
        self.createTicks()

    def getText(self):
        if self.t_i >= len(self.textIDs):
            self.textIDs.append(self.canvas.create_text(0, 0))
        ID = self.textIDs[self.t_i]
        self.canvas.itemconfig(ID, state = "normal")
        self.t_i += 1
        return ID

    def getLine(self):
        if self.l_i >= len(self.lineIDs):
            self.lineIDs.append(self.canvas.create_line(0, 0, 0, 0))
        ID = self.lineIDs[self.l_i]
        self.canvas.itemconfig(ID, state = "normal")
        self.l_i += 1
        return ID

    def cleanUp(self):
        for index in range(self.l_i, len(self.lineIDs)-1):
            self.canvas.itemconfig(self.lineIDs[index], state = "hidden")
        for index in range(self.t_i, len(self.textIDs)-1):
            self.canvas.itemconfig(self.textIDs[index], state = "hidden")
        self.l_i = 0
        self.t_i = 0

    def createTicks(self):
        self.ticks = []
        interval = (float(self.timeBounds[1] - self.timeBounds[0]))/(float(self.numTicks-1))
        self.ticks.append((int(self.timeBounds[0]), self.graphBounds[0]))
        for i in range(1, self.numTicks):
            t = float(self.timeBounds[0]) + float(i) * interval
            x = (((float(t - self.timeBounds[0]))/float(self.timeBounds[1] - self.timeBounds[0])) * (self.graphBounds[2] - self.graphBounds[0])) + self.graphBounds[0]
            self.ticks.append((self.format_time(int(t)), x))

    def update(self, curr_t, buff_t):
        self.buff_t = buff_t
        self.curr_t = curr_t
        if buff_t > self.timeBounds[1]:
            self.timeBounds = (0, self.timeBounds[1] * 2)
            self.createTicks()

    def format_time(self, t):
        min = 0
        ms = t % 1000
        sec = t / 1000
        if sec > 59:
            min = sec / 60
            sec = sec % 60
        return str('{0:2n}'.format(min)) + ":" + '{0:02n}'.format(sec) + ("." + '{0:03n}'.format(ms) if (ms != 0) else "")

    def draw(self):
        buff_pos = (float(self.buff_t)/float(self.timeBounds[1])) * (self.graphBounds[2] - self.graphBounds[0]) + self.graphBounds[0]
        dis_pos = (float(self.curr_t)/float(self.timeBounds[1])) * (self.graphBounds[2] - self.graphBounds[0]) + self.graphBounds[0]
        self.canvas.coords(self.bufferRect, (self.graphBounds[0], self.graphBounds[1], buff_pos, self.graphBounds[3]))
        self.canvas.coords(self.t_text, (dis_pos, self.graphBounds[1]-10))
        self.canvas.itemconfig(self.t_text, text = self.format_time(self.curr_t))
        self.canvas.coords(self.currentRect, (self.graphBounds[0], self.graphBounds[1], dis_pos, self.graphBounds[3]))
        for i in range(0, len(self.ticks)):
            tick_l, x = self.ticks[i]
            text = self.getText()
            line = self.getLine()
            y1 = self.graphBounds[3]
            y2 = self.graphBounds[3] - int(float(self.graphBounds[3] - self.graphBounds[1])/3.)
            self.canvas.coords(text, (x, self.graphBounds[3] + 10))
            self.canvas.itemconfig(text, text = str(tick_l))
            self.canvas.coords(line, (x, y1, x, y2))
            self.canvas.itemconfig(line, fill = self.colorBlack)


        self.cleanUp()

