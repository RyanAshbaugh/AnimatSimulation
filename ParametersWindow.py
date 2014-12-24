__author__ = 'Steven'
import Tkinter as tk

class ParameterWindow():

    def __init__(self):
        self.root = tk.Tk()
        mainContainer = tk.Frame(self.root, width=1280, height=720)

        inum_label = tk.Label(self.root, text = "Number of Inhibitory Neurons")
        inum_entry = tk.Entry(self.root)
        enum_label = tk.Label(self.root, text = "Number of Excitatory Neurons")
        enum_entry = tk.Entry(self.root)
        snum_label = tk.Label(self.root, text = "Number of Sensory Neurons")
        snum_entry = tk.Entry(self.root)
        mnum_label = tk.Label(self.root, text = "Number of Motor Neurons")
        mnum_entry = tk.Entry(self.root)

        enum_label.place(x=5,y=5)
        enum_entry.place(x=235,y=5)
        inum_label.place(x=5,y=35)
        inum_entry.place(x=235,y=35)
        snum_label.place(x=5,y=65)
        snum_entry.place(x=235,y=65)
        mnum_label.place(x=5,y=95)
        mnum_entry.place(x=235,y=95)

        #enum_entry.pack()
        enum_entry.insert(0, "2")
        mainContainer.pack()



        self.root.mainloop()



#p = ParameterWindow()