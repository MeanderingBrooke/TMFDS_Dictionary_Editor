import tkinter as tk
import tkinter.filedialog as filedialog
import struct, math, time
import TMFDS_Signal_Lib as signal
from tkinter import ttk
import tkinter.font as tkfont
try:
    import numpy as np
except:
    pass
        

class Window(tk.Frame):
    def __init__(self,root,settings,hasnumpy=True):
        if not hasnumpy:
            print("Numpy not installed, signal save and load functions not enabled")
            print("Please install numpy :(")

        self.restart = False

        self.root = root
        root.title("TMFDS")
        self.settings=settings
        self.dict={}
        self.filepath = '' #current filepath

        #set up frame for buttons on the bottom of the screen
        self.btnframe = tk.Frame(root)
        self.btnframe.pack(fill = tk.X,side=tk.BOTTOM)

        self.loadbtn = tk.Button(self.btnframe,text="Load Signal",command=self.Open_Sig)
        self.savebtn = tk.Button(self.btnframe,text="Save Signal",command=self.Save_Sig)
        self.calcbtn = tk.Button(self.btnframe,text="Calculator",command=self.Open_Calculator)

        if hasnumpy:
            self.loadbtn.pack(fill = tk.BOTH,side=tk.LEFT)
            self.savebtn.pack(fill = tk.BOTH,side=tk.LEFT)
        self.calcbtn.pack(fill = tk.BOTH,side=tk.LEFT)

        tk.Button(self.btnframe,text="Save Dictionary",command=self.Save_Dict).pack(fill = tk.BOTH,side=tk.LEFT)


        #text box for input and output
        self.textbox = tk.Text(root, width = 10, height = 10, wrap = "none")
        
        self.textbox.pack(expand = True, fill = tk.BOTH,side=tk.LEFT)

        #set up dictionary 
        self.dictframe = tk.Frame(root)
        self.dictframe.pack(fill = tk.Y,side=tk.LEFT)

        self.dictlist=tk.StringVar()
        self.searchdict=tk.StringVar()

        search=tk.Entry(self.dictframe,textvariable=self.searchdict)
        search.pack()
        search.bind('<Return>', self.Search)
        
        self.dictitems = tk.Listbox(self.dictframe,listvariable=self.dictlist)
        #selectmode=tk.SINGLE,
        self.dictitems.bind('<Double-1>', self.Edit_Dict_Entry)
        self.dictitems.pack(expand = True,fill = tk.Y)#,side=tk.LEFT)
        
        self.editdictbtn = tk.Button(self.dictframe,text="Edit",command=self.Edit_Dict_Entry)
        self.editdictbtn.pack(fill=tk.X)

        tk.Button(self.dictframe,text="Add",command=self.Add_Dict_Entry).pack(fill=tk.X)
        #tk.Button(self.dictframe,text="Del",command=self.Del_Dict_Entry).pack(fill=tk.X)
    

        

        
        #set up menu
        self.menu = tk.Menu(root)
        self.root.config(menu=self.menu)
        
        self.file_menu=tk.Menu(self.menu)
        self.menu.add_cascade(label='File',menu=self.file_menu)
        if hasnumpy:
            self.file_menu.add_command(label='Load Signal',command=self.Open_Sig)
            self.file_menu.add_command(label='Save As',command=self.Save_Sig)
        self.file_menu.add_command(label='Save Dict',command=self.Save_Dict)
        self.settings_menu=tk.Menu(self.menu)
        self.menu.add_cascade(label='Settings',menu=self.settings_menu)
        self.settings_menu.add_command(label='Set Dictionary',command=self.Change_Dict)
        self.settings_menu.add_command(label='Change Font',command=self.Edit_Font)
        self.settings_menu.add_command(label='Default Format',command=self.Set_Global_Format)
        self.dict_menu=tk.Menu(self.menu)
        self.menu.add_cascade(label='Dictionary',menu=self.dict_menu)
        self.dict_menu.add_command(label='Add',command=self.Add_Dict_Entry)
        self.dict_menu.add_command(label='Sort',command=self.Sort_Dict)
        self.dict_menu.add_command(label='Refresh',command=self.Load_Dict)
        self.dict_menu.add_command(label='Delete',command=self.Del_Dict_Entry)



        #Variables for calculator
        self.calc1=tk.StringVar()
        self.calc2=tk.StringVar()
        self.unit1=tk.StringVar()
        self.unit2=tk.StringVar()
        self.unit_type=tk.StringVar()

        #load dictionary file
        self.Setup()


        #self.Open_Calculator()
        
    def Setup(self):
        if self.settings['dictfp'] == '':
            fp = filedialog.askopenfilename(title="Open Dictionary Save")
        else:
            fp = self.settings['dictfp']
        done = False
        while not done:
            done = True
            
            try:
                self.dict = signal.getdictionary(fp)
                self.settings['dictfp'] = fp
            except:
                done = False
                fp = filedialog.askopenfilename(title="Open Dictionary Save")


        self.Load_Dict()
            
    def Load_Dict(self):
        self.dictlist.set('')
        words = self.dict['wordDict']
        item = ''
        dictlist = []
        for i in range(len(words['keys'])):
            key = str(words['keys'][i])
            #print('x'*(5-len(key)))
            item = key + ' '*(max(5-len(key),1)) + words['values'][i]
            dictlist.append(item)
        self.dictlist.set(dictlist)

    def Sort_Dict(self):
        
        words = self.dict['wordDict']
        newkeys = words['keys'].copy()
        newkeys.sort()
        newkeys.reverse()
        newvalues = []
        for i in newkeys:
            index = words['keys'].index(i)
            newvalues.append(words['values'][index])
        self.dict['wordDict']['keys']=newkeys.copy()
        self.dict['wordDict']['values']=newvalues.copy()

        self.Load_Dict()

    def Change_Dict(self):
        fp = ''
        done = False
        while not done:
            done = True
            
            try: self.dict = signal.getdictionary(fp)
            except:
                done = False
                fp = filedialog.askopenfilename()
                if fp == '':
                    done = True
                print(fp,done)
        self.settings['dictfp'] = fp

    def Confirm_Button(self,root):
        btnframe = tk.Frame(root)
        button_pressed = tk.BooleanVar(value=False)
        tk.Button(btnframe,text="Ok",command = lambda: button_pressed.set(1)).pack(side=tk.LEFT)
        tk.Button(btnframe,text="Cancel",command = lambda: button_pressed.set(0)).pack(side=tk.LEFT)


        return btnframe,button_pressed

    def Formatting_Options(self,root,formatting,rowstart=2):
        beforeframe = tk.Frame(root)
        afterframe = tk.Frame(root)
        beforeframe.grid(row=rowstart, column=0)
        afterframe.grid(row=rowstart, column=1)
        
        before = tk.IntVar(value=formatting['formatMode']+1)
        after = tk.IntVar(value=formatting['formatModeAfter']+1)
        bkond = tk.BooleanVar(value=formatting['breakOnDouble'])
        desc = tk.StringVar(value=formatting['desc'])
        
        tk.Label(beforeframe, text = "Before").pack(anchor=tk.W)
        tk.Radiobutton(beforeframe, text="None", variable=before, value=1).pack(anchor=tk.W)
        tk.Radiobutton(beforeframe, text="Space", variable=before, value=2).pack(anchor=tk.W)
        tk.Radiobutton(beforeframe, text="New Line", variable=before, value=3).pack(anchor=tk.W)
        tk.Radiobutton(beforeframe, text="2 New Line", variable=before, value=4).pack(anchor=tk.W)

        tk.Label(afterframe, text = "After").pack(anchor=tk.W)
        tk.Radiobutton(afterframe, text="None", variable=after, value=1).pack(anchor=tk.W)
        tk.Radiobutton(afterframe, text="Space", variable=after, value=2).pack(anchor=tk.W)
        tk.Radiobutton(afterframe, text="New Line", variable=after, value=3).pack(anchor=tk.W)
        tk.Radiobutton(afterframe, text="2 New Line", variable=after, value=4).pack(anchor=tk.W)

        tk.Checkbutton(root, text="New Line on Double", variable=bkond).grid(row=rowstart+1,column=0,columnspan=2)

        tk.Entry(root,textvariable = desc).grid(row=rowstart+2,column=0,columnspan=2)

        return before,after,bkond,desc

    def Set_Global_Format(self,Event=None):
        formatwindow= tk.Toplevel(self.root)
        btnframe, button_pressed = self.Confirm_Button(formatwindow)

        formatting = self.settings['defaultformat']

        tk.Label(formatwindow,text="Set Default Format For New Words").grid(row=0,column=0)
        before,after,bkond,desc = self.Formatting_Options(formatwindow,formatting,1)
        btnframe.grid(row=4,column=0)

        formatwindow.wait_variable(button_pressed)
        formatwindow.destroy()
        
        
        #print(button_pressed.get())
        if button_pressed.get():
            formatting['formatMode']=before.get()-1
            formatting['formatModeAfter']=after.get()-1
            formatting['breakOnDouble']=bkond.get()
            formatting['desc']=desc.get()
            self.settings['defaultformat']=formatting.copy()
            print(formatting)
            print(self.settings['defaultformat'])
        
        

    def Edit_Dict_Entry(self,event=None): #unused is unused, makes event binding happy

        selected = self.dictitems.curselection()[0]
        #print(selected)
        editwindow = tk.Toplevel(self.root)

        tk.Label(editwindow, text = "Changes Not Saved To Disk").grid(row=0,column=0,columnspan=2)

        word = tk.StringVar(value=self.dict['wordDict']['values'][selected])

        tk.Entry(editwindow,textvariable = word).grid(row=1,column=0,columnspan=2)
        

        
        
        formatting = self.dict['descDict']['values'][selected]


        before,after,bkond,desc = self.Formatting_Options(editwindow,formatting,2)
        button_pressed = tk.BooleanVar(value=False)
        
        okbtn = tk.Button(editwindow,text='OK',command = lambda: button_pressed.set(1))
        cslbtn = tk.Button(editwindow,text='Cancel',command = lambda: button_pressed.set(0))

        okbtn.grid(row=5, column=0)
        cslbtn.grid(row=5, column=1)

        
        
        editwindow.wait_variable(button_pressed)
        editwindow.destroy()
        
        
        #print(button_pressed.get())
        if button_pressed.get():
            formatting['formatMode']=before.get()-1
            formatting['formatModeAfter']=after.get()-1
            formatting['breakOnDouble']=bkond.get()
            formatting['desc']=desc.get()
            self.dict['descDict']['values'][selected]=formatting
            self.dict['wordDict']['values'][selected]=word.get()
            
            key = str(self.dict['wordDict']['keys'][selected])
            item = key + ' '*(max(5-len(key),1)) + word.get()
            self.dictitems.delete(selected)
            self.dictitems.insert(selected,item)




            
    def Add_Dict_Entry(self,Event = None):
        addwindow = tk.Toplevel(self.root)

        entry = tk.StringVar(value = '')

        tk.Entry(addwindow,textvariable=entry).grid(row=0,column=0,columnspan=2)
        value = 0
                
        button_pressed = tk.BooleanVar(value=False)
        btnframe = tk.Frame(addwindow)
        btnframe.grid(row=5, column=0)

        formatting = self.settings['defaultformat'].copy()  #stupid fucking pointers, without the .copy() it will set the formatting to the same dict as the default format, meaning changes here will change the original too
                                                            #why the hell did they do that its just weird
#-------------------------------------------------------------------------------
        word = tk.StringVar(value='')

        tk.Entry(addwindow,textvariable = word).grid(row=1,column=0,columnspan=2)

        before,after,bkond,desc=self.Formatting_Options(addwindow,formatting,2)
#-------------------------------------------------------------------------------
        tk.Button(btnframe,text="Ok",command = lambda: button_pressed.set(1)).pack(side=tk.LEFT)
        tk.Button(btnframe,text="Cancel",command = lambda: button_pressed.set(0)).pack(side=tk.LEFT)

        wait = True
        while wait:            
            addwindow.wait_variable(button_pressed)

            if not button_pressed.get():
                break

            try:
                value = int(entry.get())
                wait = False
            except:
                print("Enter a valid integer!")
                
            if value >= 0:
                wait = True
                print("Enter a valid integer!")

            if wait == False and value in self.dict['wordDict']['keys']:
                wait = True
                print(f"{value} is already in dictionary")

            if not wait:
                self.dict['wordDict']['keys'].append(value)
                if word.get() == '':
                    word.set(f"@{value}UNDEF")
                self.dict['wordDict']['values'].append(word.get())

                formatting['desc']=desc.get()
                formatting['formatMode']=before.get()-1
                formatting['formatModeAfter']=after.get()-1
                formatting['breakOnDouble']=bkond.get()
                
                self.dict['descDict']['values'].append(formatting)
                self.dict['descDict']['keys'].append(value)
 
                key = str(value)
                item = key + ' '*(max(5-len(key),1)) + word.get()
                self.dictitems.insert(tk.END,item)
                print("added to dict")
                
        addwindow.destroy()

    def Del_Dict_Entry(self):
        selections = list(self.dictitems.curselection())
        
        selections.sort()
        selections.reverse()
        for selected in selections:
            print(f"{self.dict['wordDict']['keys'][selected]}, {self.dict['wordDict']['values'][selected]}")
        for selected in selections:
            print(f"deleting {self.dict['wordDict']['keys'][selected]}, {self.dict['wordDict']['values'][selected]}")
            del(self.dict['wordDict']['values'][selected])
            del(self.dict['wordDict']['keys'][selected])
            del(self.dict['descDict']['values'][selected])
            del(self.dict['descDict']['keys'][selected])
            self.dictitems.delete(selected)
        #self.Load_Dict()
        
        
    def Save_Dict(self):
        fp = self.settings['dictfp']
        if r"Applesinmypants" in fp:
            print("DO NOT SAVE TO ORIGINAL FILE,\nIT CAN AND WILL FUCK IT UP")
            print("If you are not saving to original file and are still getting this message,")
            print("move the file out of the Applesinmypants folder")
            print("or make sure that there is nothing named Applesinmypants in the file path")
            print("Sorry for the hacky fix, I just didn't want anyone fucking their save data")
            fp=filedialog.asksaveasfilename(title="Save Dictionary")
        
        if fp != '':
            dictionary = self.dict
            for i in range(len(dictionary['wordDict']['values'])):
                word = dictionary['wordDict']['values'][i]
                dictionary['wordDict']['values'][i] = word.replace("'",'`')

            for i in range(len(dictionary['descDict']['values'])):
                desc = dictionary['descDict']['values'][i]['desc']
                dictionary['descDict']['values'][i]['desc'] = desc.replace("'",'`')
            dictionary = str(dictionary)
            dictionary = dictionary.replace(": True",": true")
            dictionary = dictionary.replace(": False",": false")
            dictionary = dictionary.replace("'",'"')
            dictionary = dictionary.replace("`","`")
            file = open(fp,'w')
            file.write(dictionary)
            file.close()
            print(f"Saved dict to {fp}")
            
    def Search(self,Event=None):
        value=self.searchdict.get()
        isint=True
        key=0
        try: key=int(value)
        except: isint=False
        index=-1
        if isint and key in self.dict['wordDict']['keys']:
            index=self.dict['wordDict']['keys'].index(key)
        elif value.upper() in self.dict['wordDict']['values']:
            index=self.dict['wordDict']['values'].index(value.upper())
        else:
            for i in range(len(self.dict['wordDict']['values'])):
                if value.upper() in self.dict['wordDict']['values'][i]:
                    index=i
        if index > -1:
            self.dictitems.see(index)
            #self.dictitems.activate(index)
            self.dictitems.selection_clear(0,tk.END)
            self.dictitems.select_set(index)
    
    def Open_Sig(self):
        fp=filedialog.askopenfilename(filetypes = [("WAV","*.wav")])
        if fp != '':
            self.textbox.delete('1.0','end')
            period,centerfreq = self.Get_Sig_Params()
            offsets=signal.readsig(fp,centerfreq,period)
            translation, unknowns = signal.translate(offsets,self.dict)
            print(translation)
            self.textbox.insert('1.0',translation)
    


    def Save_Sig(self):
        text = self.textbox.get('1.0', 'end')
        sig,compilefailed,_ = signal.untranslate(text,self.dict)
        if compilefailed:
            print("failed to parse text")
            return
        fp=filedialog.asksaveasfilename(filetypes = [("WAV","*.wav")],defaultextension = '.wav')
        
        period,centerfreq = self.Get_Sig_Params()
        
        if fp != '':
            signal.savesig(sig,fp,centerfreq,period,11025)
            print(sig)
        

    def Get_Sig_Params(self):
        periodstr = tk.StringVar()
        cfstr = tk.StringVar() #center frequency
        srstr = tk.StringVar() #samplerate
        options = tk.Toplevel(self.root)

        tk.Label(options, text="Period").grid(row=0, column=0)
        tk.Label(options, text="Center Frequency").grid(row=1, column=0)

        period_entry = tk.Entry(options,textvariable = periodstr)
        cf_entry = tk.Entry(options,textvariable = cfstr)

        period_entry.grid(row=0, column=1)
        cf_entry.grid(row=1, column=1)

        periodstr.set(str(self.settings['defaultperiod']))
        cfstr.set(str(self.settings['defaultcf']))

        button_pressed = tk.StringVar()
        
        okbtn = tk.Button(options,text='OK',command = lambda: button_pressed.set("button pressed"))#, command=function)#options.destroy)
        
        okbtn.grid(row=2, column=0)
        
        okbtn.wait_variable(button_pressed)
        period = float(periodstr.get())
        centerfreq = float(cfstr.get())
        options.destroy()
        print("done")
        return period, centerfreq
        

    def Edit_Settings(self):
        pass


    def Edit_Font(self):
        fontwindow = tk.Toplevel(self.root)
        sysfonts = list(tkfont.families(self.root))
        sysfonts.sort()
        fontlist = tk.StringVar(value = sysfonts)
        size=tk.StringVar(value = str(self.settings["fontsize"]))

        button_pressed = tk.BooleanVar(value=False)
        btnframe = tk.Frame(fontwindow)
        tk.Button(btnframe,text="Ok",command = lambda: button_pressed.set(1)).pack(side=tk.LEFT)
        tk.Button(btnframe,text="Cancel",command = lambda: button_pressed.set(0)).pack(side=tk.LEFT)
        fontsel = tk.Listbox(fontwindow,selectmode=tk.SINGLE,listvariable=fontlist)

        fontsel.pack(fill=tk.Y,expand=True)
        tk.Spinbox(fontwindow,from_=1,to=40,textvariable=size).pack()#Entry(fontwindow,textvariable=size).pack()
        btnframe.pack(anchor = tk.S)
        fontwindow.wait_variable(button_pressed)
        selection = fontsel.curselection()
        fontwindow.destroy()
        size = int(size.get())

        
        if button_pressed.get() and len(selection) :
            font = sysfonts[selection[0]]
            self.settings["font"] = font
            self.restart = True
            
        if button_pressed.get() and self.settings["fontsize"]!=size:
            self.settings["fontsize"]=size
            self.restart = True
            
        if self.restart:
            self.root.destroy()
        
        

    def Open_Calculator(self):
        calculator  = tk.Toplevel(self.root)#,title="Unit Conversion")
        self.calc1.set('0')
        self.calc2.set('0')
        units = list(signal.UNITS.keys()) + ["Base Conversion"]
        
        unitselect = ttk.Combobox(calculator,values=units,state="readonly",textvariable = self.unit_type)
        unitselect.grid(row=0,column=0)
        unitselect.bind("<<ComboboxSelected>>", self.Select_Unit_Type)
        
        tk.Entry(calculator,textvariable = self.calc1).grid(row=1,column=0)#,columnspan=2)
        tk.Entry(calculator,textvariable = self.calc2).grid(row=1,column=1)

        tk.Button(calculator,text="Convert",command=self.Calc_To).grid(row=3,column=0)#,columnspan=2)
        tk.Button(calculator,text="Convert",command=self.Calc_From).grid(row=3,column=1)

        self.unit1=ttk.Combobox(calculator,state="readonly")
        self.unit2=ttk.Combobox(calculator,state="readonly")
        self.unit1.grid(row=2,column=0)
        self.unit2.grid(row=2,column=1)
        
        

    def Select_Unit_Type(self,event):
        unit_type = self.unit_type.get()
        if unit_type in signal.UNITS.keys():            
            units = self.Unit_Translate(list(signal.UNITS[unit_type].keys()))
            self.unit1['values']=units
            self.unit2['values']=units
        else:
            self.unit1['values']=['Base 10']
            self.unit2['values']=['Base 8']
        self.unit1.current(0)
        self.unit2.current(0)

    def Calc_From(self):
        unit_type = self.unit_type.get()

        unit1 = self.unit1.get()
        unit2 = self.unit2.get()
        
        unit1 = self.unit1['values'].index(unit1)
        unit2 = self.unit2['values'].index(unit2)

        
        
        value = float(self.calc1.get())
        if not unit_type in signal.UNITS.keys(): #base 8 conversion handler
            out = signal.octf(value,includeo=False)
            self.calc2.set(str(out))
            return
        unit1 = list(signal.UNITS[unit_type].keys())[unit1]
        unit2 = list(signal.UNITS[unit_type].keys())[unit2]
        
        out = signal.convertunits(unit_type,unit1,unit2,value)
        self.calc2.set(str(out))

        
    def Calc_To(self):
        unit_type = self.unit_type.get()
        
        unit1 = self.unit1.get()
        unit2 = self.unit2.get()

        unit1 = self.unit1['values'].index(unit1)
        unit2 = self.unit2['values'].index(unit2)

        
        
        if not unit_type in signal.UNITS.keys(): #base 8 conversion handler
            num=self.calc2.get()
            if not ('8' in num or '9' in num):
                out = signal.octf2float(num)
                self.calc1.set(str(out))
            return
        
        unit1 = list(signal.UNITS[unit_type].keys())[unit1]
        unit2 = list(signal.UNITS[unit_type].keys())[unit2]
        
        value = float(self.calc2.get())
        out = signal.convertunits(unit_type,unit2,unit1,value)
        self.calc1.set(str(out))

    def Unit_Translate(self,unit_list):
        out = []
        for i in unit_list:
            isnum=False
            v=i.split()
            #print('v',v)
            try:
                int(v[0])
                isnum=True
            except:out.append(i)
            if isnum:
                unitname = ''
                for n in v:
                    #print('n',n)
                    unitname += signal.translate([int(n)],self.dict)[0]
                    #print(unitname,n)
                out.append(unitname)
        return out



def Get_Font(root,fontname,fontsize=12):
    if fontname in tkfont.families():
        font=tkfont.Font(root=root,font=(fontname,fontsize))
        print(f"Using font {fontname}")
    else:
        font=tkfont.nametofont('TkFixedFont')

        print("Using default font")
    #root.option_add("*Font",font)
    return font
 


