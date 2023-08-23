import threading as th
import socket as so
import tkinter as tk
from PIL import Image, ImageTk
import time
import numpy as np
import matplotlib as mpl

class Widget:
    __default_color = "blue"
    __default_background_color = "white"
    
    def __init__(self, widget, pwidth, pheight, px, py, adaptive=True, textvariable=None, updatable=True, reverse=False):
        self.widget = widget
        self.pwidth = pwidth
        self.pheight = pheight
        self.px = px
        self.py = py
        self.width = self.height = self.x = self.y = None
        self.adaptive = adaptive
        self.textvariable = textvariable
        self.updatable = updatable
        self.reverse = reverse
        
        self.components = []
        
        self.first_time = True
    
    def set_width(self, npixel):
        self.pwidth = None
        self.width = npixel
        
    def set_height(self, npixel):
        self.pheight = None
        self.height = npixel
        
    def set_x(self, npixel):
        self.px = None
        self.x = npixel
        
    def set_y(self, npixel):
        self.py = None
        self.y = npixel
        
    def __update(self, window_width, window_height):
        if self.pwidth != None:
            self.width = int(self.pwidth * window_width)
        
        if self.pheight != None:
            self.height = int(self.pheight * window_height)
        
        if self.px != None:
            self.x = int(self.px * window_width)

        if self.reverse:
            x = self.x - self.width
        else:
            x = self.x
            
        if self.py != None:
            self.y = int(self.py * window_height)
        
        self.widget.place(x=x, y=self.y, width=self.width, height=self.height)
        
    def update(self, window):
        if window.adaptive and self.adaptive:
            self.__update(window.root.winfo_width(), window.root.winfo_height())
        else:
            if self.first_time:
                self.first_time = False
                
                if window.minsizes == None:
                    self.__update(window.root.winfo_width(), window.root.winfo_height())
                else:
                    self.__update(window.minsizes[0], window.minsizes[1])

class Window:
    __default_title = "Pyscreener2"
    __default_icon = "/home/racteur/githubs/me/pyscreener2/default_icon.ico"
    __default_sizes = (800, 600, 100, 100)
    
    def __init__(self, root=None, parent=None, title=None, icon=None, properties=None, background_color=None, minsizes=None, maxsizes=None, adaptive=True):
        if root == None:
            self.root = tk.Tk()
        else:
            self.root = root

        self.root.configure(bg=background_color)
            
        self.parent = parent
            
        self.windows = []
        self.widgets = []
        
        if title == None or type(title) != str:
            title = Window.__default_title

        self.root.title(title)
        
        if icon == None or type(icon) != str:
            icon = Window.__default_icon
        
        self.icon = ImageTk.PhotoImage(Image.open(icon))
        self.root.wm_iconphoto(True, self.icon)
            
        if properties == None or type(properties) != list:
            self.properties = Window.__default_sizes
        else:
            self.properties = properties

        self.minsizes = minsizes

        if minsizes != None:
            self.root.minsize(minsizes[0], minsizes[1])
        
        self.maxsizes = maxsizes
        
        if maxsizes != None:
            self.root.maxsize(maxsizes[0], maxsizes[1])
            
        self.width, self.height, self.x, self.y = self.properties
        self.first_width = self.width
        self.first_height = self.height
        self.root.geometry("{0}x{1}+{2}+{3}".format(self.width, self.height, self.x, self.y))
            
        self.adaptive = adaptive
            
        def f(event):
            if self.properties[0] != self.root.winfo_width() or self.properties[1] != self.root.winfo_height():
                self.update()
                
        self.root.bind("<Configure>", f)
        
        self.update()
        
    __default_label_text = "__label__"
    def label(self, pwidth, pheight, px, py, adaptive=True, reverse=False, color="black", background_color="white", justify=tk.CENTER, font="arial"):
        v = tk.StringVar()
        w = Widget(tk.Label(self.root, textvariable=v, fg=color, bg=background_color, justify=justify, font=font), pwidth, pheight, px, py, adaptive=adaptive, textvariable=v, reverse=reverse)
        v.set(Window.__default_label_text)
        self.widgets.append(w)
        return w
    
    __default_entry_text = "__entry__"
    def entry(self, pwidth, pheight, px, py, adaptive=True, reverse=False, color="black", background_color="white", justify=tk.CENTER, font="arial"):
        v = tk.StringVar()
        v.set(Window.__default_entry_text)
        w = Widget(tk.Entry(self.root, textvariable=v, fg=color, bg=background_color, justify=justify, font=font), pwidth, pheight, px, py, adaptive=adaptive, textvariable=v, reverse=reverse)
        self.widgets.append(w)
        return w
    
    __default_button_text = "__button__"
    def button(self, pwidth, pheight, px, py, adaptive=True, reverse=False, command=lambda: 0, text=None, color="black", background_color="white", justify=tk.CENTER, font="arial"):
        if text == None:
            text = Window.__default_button_text
            
        w = Widget(tk.Button(self.root, text=text, command=command, fg=color, bg=background_color, justify=justify, font=font), pwidth, pheight, px, py, adaptive=adaptive, textvariable=v, reverse=reverse)
        self.widgets.append(w)
        return w

    def menu(self, pwidth, pheight, px, py, adaptive=True, description={}):
        m = Widget(tk.Menu(self.root), pwidth, pheight, px, py, adaptive, updatable=False)
        self.root.config(menu=m.widget)
        self.widgets.append(m)
        
        keys = description.keys()
        n = len(keys)
        pwidth2 = pwidth / n
        
        for key in keys:
            menu = tk.Menu(m.widget)
            m.components.append(menu)
            m.widget.add_cascade(label=str(key), menu=menu)
            
            for key2 in description[key]:
                menu.add_command(label=str(key2), command=description[key][key2])
                
        return m
        
    def text(self, pwidth, pheight, px, py, adaptive=True, reverse=False, color="black", background_color="white", font="arial", state=tk.NORMAL, relief=None, xscrollcommand=None, yscrollcommand=None):
        t = Widget(tk.Text(self.root, fg=color, bg=background_color, font=font, state=state, relief=relief, xscrollcommand=xscrollcommand, yscrollcommand=yscrollcommand), pwidth, pheight, px, py, adaptive=adaptive, reverse=reverse)
        self.widgets.append(t)
        return t
    
    def scrollbar(self, pwidth, pheight, px, py, adaptive=True, reverse=False, color="white", command=None):
        s = Widget(tk.Scrollbar(self.root, bg=color, command=command), pwidth, pheight, px, py, adaptive=adaptive, reverse=reverse)
        self.widgets.append(s)
        return s
        
    def widget(self, widget, pwidth, pheight, px, py, adaptive=True):
        w = Widget(widget, pwidth, pheight, px, py, adaptive)
        self.widgets.append(w)
        return w
    
    def window(self, title=None, icon=None, properties=None, background_color=None):
        w = Window(tk.Toplevel(), title=title, icon=icon, properties=properties, background_color=background_color)
        self.windows.append(w)
        return w
        
    def update(self):
        for widget in self.widgets:
            if widget.updatable:
                widget.update(self)

        self.root.update()

        self.properties = [self.root.winfo_width(), self.root.winfo_height(), self.root.winfo_rootx(), self.root.winfo_rooty()]
        self.width, self.height, self.x, self.y = self.properties

    def run(self):
        self.update()
        self.root.mainloop()
        
if __name__ == "__main__":
    w = Window(properties=[400, 400, 100, 100], minsizes=[300, 300], adaptive=True)
    
    # label = w.label(0.5, 0.2, 0.25, 0.2)
    # label.textvariable.set("Click on button :")
    # label.widget.config(justify=tk.LEFT)
    
    def f():
        properties = w.properties
        properties[2] += 400
        under_window = w.window(title=str(w.root.title()), properties=properties)
        button = under_window.button(0.5, 0.2, 0.25, 0.5, text="Try", command=f)
        under_window.update()
        
        menu = w.menu(0.9, 0.1, 0, 0, description={
            "file": {
                "new": (lambda: print("new file")),
                "open": (lambda: print("open file")),
                "about": (lambda: print("about files"))
            },
            "settings": {
                "parameters": (lambda: print("change something")),
                "help": (lambda: print("get help"))
            },
            "help": {
                "help": (lambda: print("get help"))
            }
        })
        
    # button = w.button(0.5, 0.2, 0.25, 0.5, text="####", color="yellow", background_color="red", command=f, adaptive=False)
    
    scrollbar = w.scrollbar(0.1, 1, 1, 0, color="blue", reverse=True)
    
    text = w.text(0.8, 0.8, 0.1, 0.1, color="blue", background_color="white", yscrollcommand=scrollbar.widget.set)
    
    scrollbar.widget.config(command=text.widget.yview)
    scrollbar.set_width(40)
    
    w.run()