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

#default settings if no file is found, or a key is missing from the file
defaultsettings = {'dictfp':'',
                   'defaultperiod':0.8066,
                   'defaultcf':500,
                   'font':'',
                   'fontsize':10,
                   'defaultformat':{'desc': 'none', 'formatMode': 0, 'formatModeAfter': 0, 'breakOnDouble': False}
                   }


#get settings file
try:
    file = open('Settings.txt')
    print("opened settings")
    settings = eval(file.read())
    print(settings)
    file.close()
except: #use default settings if unable to load file
    print("no settings file")
    settings = defaultsettings.copy()

#add any missing keys to the settings dict
for i in defaultsettings.keys():
    if not i in settings.keys(): print(f"Adding key '{i}' to settings") #print the added keys
    settings.setdefault(i,defaultsettings[i]) #does not change values if the key is already in the dict

#get font
fontname = settings['font']
font=gui.Get_Font(root,fontname)

#font.configure(size = 10)
root.option_add("*Font",font)

#loop to allow the program to restart
restart = True
while restart:
#default is not restarting
    restart = False
#gui window
    app = gui.Window(root,settings,hasnumpy)
    root.mainloop()

#save the gui restart option, is true if the program is supposed to restart upon closing
    restart = app.restart 

#save the settings to the file
    file = open('Settings.txt','w')
    file.write(str(app.settings))
    file.close()

#delete the gui object variable
    del(app)
#if the program is restarting, remake the window and get the font
    if restart:
        print("Restarting...")
        root = tk.Tk()
        fontname = settings['font']
        font=gui.Get_Font(root,fontname)
        root.option_add("*Font",font)
    

#end of program
