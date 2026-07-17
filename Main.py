import tkinter as tk
import tkinter.filedialog as filedialog
import struct, math
import TMFDS_Signal_Lib as signal
import gui
import tkinter.font as tkfont
try:
    import numpy as np
    hasnumpy = True
except:
    hasnumpy = False

root=tk.Tk()

#get settings file
try:
    x=0/0
    file = open('Settings.txt')
    settings = eval(file.read())
    file.close()
except: #make settings if no file
    settings = {'dictfp':'','defaultperiod':0.8066,'defaultcf':500,'font':'','fontsize':10}

#get font
fontname = settings['font']
font=gui.Get_Font(root,fontname)

#font.configure(size = 10)
root.option_add("*Font",font)

restart = True
while restart:
    restart = False
    app = gui.Window(root,settings,hasnumpy)
    root.mainloop()

    restart = app.restart

    file = open('Settings.txt','w')
    file.write(str(app.settings))
    file.close()
    
    del(app)
    if restart:
        print("Restarting...")
        root = tk.Tk()
        fontname = settings['font']
        font=gui.Get_Font(root,fontname)
        root.option_add("*Font",font)
    
    
    
