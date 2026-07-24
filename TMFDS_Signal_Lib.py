import struct, math
try:
    import numpy as np
    hasnumpy = True
except:
    hasnumpy = False


#use savesig(list_of_signals) to save signals to a list
#use readsig(filepath) to read the signals in a wav file
#use getdictionary(filepath) to load the games dictionary file (you have to find the file path yourself)
#with the dictionary, you can use translate() and untranslate() to read and make messages


#Function Definitions
#--------------------------------------------------------------------------#
def loadwav(filepath,printinfo=False):


    file = open(filepath,'rb')

    wav=bytearray(file.read())

    file.close()

    fileLength = struct.unpack('<I',wav[4:8])[0]
    formatLength = struct.unpack('<I',wav[16:20])[0]
    dataLength = struct.unpack('<I',wav[24+formatLength:28+formatLength])[0]
    formatType = struct.unpack('<H',wav[20:22])[0]
    channels = struct.unpack('<H',wav[22:24])[0]
    sampleRate = struct.unpack('<I',wav[24:28])[0]
    if printinfo:
        print(struct.unpack('<I',wav[28:32])[0])
        print(struct.unpack('<H',wav[32:34])[0],'\n')
    bitsPerSample = struct.unpack('<H',wav[34:36])[0]
    if printinfo:
        print("fileLength",fileLength)
        print("formatLength",formatLength)
        print("dataLength",dataLength)
        print("formatType",formatType)
        print("channels",channels)
        print("sampleRate",sampleRate)
        print("bitsPerSample",bitsPerSample)

    #if bitsPerSample
    Audio = np.zeros(int(dataLength/2),np.int16)#np.array(wav[28+formatLength:], np.int16)

    #(bitsPerSample/8)
    for i in range(int(dataLength/2)):
        Audio[i]=struct.unpack('<h',wav[i*2+28+formatLength:i*2+30+formatLength])[0]

    return Audio, sampleRate, dataLength, channels

def makeheader(datasize,samplerate=11025,channels=1,bitsPerSample=16):
    header=bytearray(44)
#RIFF chunk
    header[0:4]=b'RIFF' #identifier
    header[4:8]=struct.pack('<I',datasize+36) #total file size - 8 bytes
    header[8:12]=b'WAVE' #file format id
#chunk describing data format
    header[12:16]=b'fmt ' #format block id
    header[16:20]=struct.pack('<I',16) #chunk size - 8 bytes (16)
    header[20:22]=struct.pack('<H',1) #audio format, 1 for PCM integer
    header[22:24]=struct.pack('<H',channels) #number of channels
    header[24:28]=struct.pack('<I',samplerate) #sample rate
    header[28:32]=struct.pack('<I',samplerate*(channels*bitsPerSample//8)) #bytes per second
    header[32:34]=struct.pack('<H',channels*bitsPerSample//8) #bytes per block
    header[34:36]=struct.pack('<H',bitsPerSample) #bits per sample
#data block
    header[36:40]=b'data' #identifier
    header[40:44]=struct.pack('<I',datasize) #data size
    return header
    
def makebody(Audio):
    data = bytearray()
    for i in Audio:
        data+=struct.pack('<h',int(i))
    return data

def makewav(Audio,sampleRate=11025,formatType=1,channels=1,bitsPerSample=16):
    data = makebody(Audio)
    header = makeheader(len(data),sampleRate)
    return header+data

def tosig(words,samplerate=11025,centerfreq=500,period=0.8066):
    freqinc = 1/period #frequency increment
    offset = 0
    rad = 0
    prevnum = 0
    samplesperperiod = period * samplerate
    deround = 0
    phase = 0
    #print(samplesperperiod)
    seg = np.array([])
    signal = np.array([],dtype=np.int16)
    for i in range(len(words)): #itterate through words
        offset = freqinc * words[i]
        
        rad = freqtosmpl(offset+centerfreq,samplerate)

        phase = (int(samplesperperiod+deround)*(i+1))*(prevnum/rad-1)+phase*(prevnum/rad)
        
        seg = np.sin(
              ((np.arange(int(samplesperperiod+deround))+phase)
              *2*math.pi)*rad)*32000
        #print(offset,rad)
        signal=np.append(signal,np.int16(seg))
        prevnum=rad
        deround+=samplesperperiod%1
        deround = deround % 1
    return signal

def savesig(words,filepath='signal.wav',centerfreq=500,period=0.8066,samplerate=11025):
    signal = tosig(words,samplerate,centerfreq,period)
    wav = makewav(signal,samplerate)
    file = open(filepath,mode='wb')
    file.write(wav)
    file.close()
    print(f"File saved as {filepath}")
    
def freqtosmpl(frequency,samplerate): #frequency to samples
    return frequency/samplerate

def readsig(filepath,centerfreq=500,period=0.8066):
    data, sampleRate, dataLength, channels = loadwav(filepath)
    signalcount = (len(data)/sampleRate)/period
    print(signalcount)

    datalen=len(data)

    #periodarray = getperiod(indexes)
    #avgprd=[]
    samplesperperiod = period * sampleRate
    targetindex = samplesperperiod
    previndex = 0
    #plot(periodarray)
    #print(period)
    #datalen=len(periodarray)
    fftout=[]
    for i in range(round(signalcount)):
        #print(previndex,targetindex)
        segment = data[min(int(previndex),datalen-1):min(int(targetindex),datalen-1)]
        #sumperiods = np.sum(signalperiods)
        #numperiods = np.sum(signalperiods>0)
        fftout.append(
            np.absolute(np.fft.fft(segment))
            #np.fft.rfft(segment)
            )
        previndex = targetindex
        targetindex += samplesperperiod
    #plot(avgprd)
    #plot(fftout[0])
    offsets = []
    index = 0
    for i in fftout:
        index = (np.argmax(i[0:len(i)//2]))
        freq = np.fft.fftfreq(len(i),1/sampleRate)[index]
        offsets.append((freq-centerfreq)*period)
    offsets = np.int16(
        np.round(np.array(offsets))
        )
    return offsets

def getdictionary(filepath):  #dictionary file should be in \Applesinmypants\The Message From Deep Space
    file=open(filepath)       #on windows it was in C:\Users\<user>\AppData\LocalLow\Applesinmypants\The Message From Deep Space
    dictdef = file.read()     #the file name should be something like DICTIONARY-1.save
    file.close()
    true=True                 #python wants True and False to be capitalized
    false=False               #defining lowercase true/false variables keep it happy
    dictionary = eval(dictdef)#eval evaluates a string as code
    return dictionary         #return result

def splitword(word,validwords):
    prev = len(word)
    segment = ''
    words = []
    for i in range(-1,-len(word)-1,-1):
        
        segment=word[i:prev]
        print(segment)
        if segment in validwords:
            words.append(segment)
            prev = i
        elif segment.isdigit():
            words.append(segment)
            prev = i
    return words

def olduntranslate(text,dictionary): #uses the dictionary saved by The Message From Deep Space, get it using getdictionary
    if type(text)==list:
        wordlist = text
    else:
        wordlist = text.split()
    words = dictionary['wordDict']

    out=[]
    prev = 0
    for word in wordlist:
        if word in words['values']:
            out.append(words['keys'][words['values'].index(word)])
        elif word.isdigit():
            out.append(int(word))
        else:
            out += untranslate(splitword(word,words['values']),dictionary)
            
    return out

def untranslate(text,dictionary,debug=False):
    words = dictionary['wordDict']
    start = 0
    failedfrom = -1
    
    sigs=[]
    while start < len(text):
        while start < len(text) and text[start].isspace():
            start += 1
        compilefailed = True
        for i in range(len(text),start-1,-1):
            segment = text[start:i]
            #print(segment)
            if segment in words['values']:
                sigs.append(words['keys'][words['values'].index(segment)])
                start = i
                compilefailed = False
                break
            elif len(segment) == 1 and segment.isdigit():
                sigs.append(int(segment))
                start = i
                compilefailed = False
                break
        if compilefailed:
            if start >= len(text):
                compilefailed = False
                break
            failedfrom = start
            print(f"compile failed from {start}:\n{text[start::]}")
            break
        
    return sigs, compilefailed,failedfrom
            
    #for i in range(1,len(words)+1):
        
        

def translate(sigs,dictionary,formated = True): #uses the dictionary saved by The Message From Deep Space, get it using getdictionary
    words = dictionary['wordDict']
    formating = dictionary['descDict']
    formatModes=['',' ','\n','\n\n']
    defaultform = {'desc': 'none', 'formatMode': 0, 'formatModeAfter': 0, 'breakOnDouble': False}
    out=''
    prev = 0
    translation = ''
    before = ''
    after = ''
    unknowns = []
    for i in sigs:
        if i in words['keys']:
            translation=words['values'][words['keys'].index(i)]
            Format = formating['values'][formating['keys'].index(i)]
        elif i >= 0:
            translation = str(i)
            Format = defaultform
        else:
            unknowns.append(i)
            translation = f'@{i}UNDEF'
            Format = defaultform
        
        if not formated: #if formating option is off, add a space after every word
            Format = {'desc': 'none', 'formatMode': 0, 'formatModeAfter': 1, 'breakOnDouble': False}

        before = formatModes[Format['formatMode']]
        after = formatModes[Format['formatModeAfter']]
        if Format['breakOnDouble'] and prev == i:
            after += '\n'
        out+=before + translation + after
        prev = i
    out = out.replace('  ',' ').replace('\n ','\n') #remove double spaces and spaces after a newline
    return out, unknowns

def octf(num,p=32,includeo=True): #print a float in octal
    i=int(num)
    f=num-i
    out=oct(i)+'.'
    for j in range(p):
        f*=8
        out+=oct(int(f))[2::]
        f-=int(f)
    if includeo:
        return '0'+out.strip('0')
    else:
        out = out.strip('0o')
        if out[0] == '.': out = '0' + out
        if out[-1] == '.': out += '0'
        return out

def octf2float(octal): #converts an octal string to a float
    if not '.' in octal:
        octal += '.'
    octal = octal.strip('0o')
    #if '.' in octal:
    dec = octal.index('.')
    #else:
    #    dec = len(octal) - 1
        
    num=int(octal.replace('.',''),base=8)
    num/=8**(len(octal)-dec-1)
    return num

def convertunits(unit_type,from_unit,to_unit,value,units={}):
    global UNITS
    if not units:
        units = UNITS[unit_type]
    result = value * units[from_unit]/units[to_unit]
    return result

#small function i made for myself, might make more useful in the future
def makeconfetti(n):
    v=[]
    for i in range(n):
        x=random.randint(-8,8)
        y=random.randint(-8,8)
        z=random.randint(-8,8)
        s=random.randint(1,16)/8
        c=random.randint(0,48)
        v.append((x,y,z,s,c))
    vis='VISUAL('
    for i in v:
        a=str(i)
        vis+="VERTEX"+a[1:-1]+','
    vis = vis[0:-1] + ')'
    vis = vis.replace('-','~')
    return vis
#need to add improve in the future, currently not very useful 
def mkvis(x,y,z,s,c):
    #v.append((x,y,z,a,c))
    vis='VISUAL('
    for i in range(len(x)):
        #print(i,end=', ')
        v=(float(x[i]),float(y[i]),float(z[i]),float(s[i]),int(c[i]))
        a=str(v)
        vis+="VERTEX"+a[1:-1]+','
    vis = vis[0:-1] + ')'
    vis = vis.replace('-','~')
    return vis
#------------------------------------------------------------------------------#
#End Functions

#Unit Constants
#Time Units, in Seconds
TIMEUNITS = {"Second":1,"Minute":60,"Hour":3600,"Day":86400,"Year":31556736,
             "-69":0.8066,"-71":812159.8938,"-70":2845876.7708}
#Mass Units, in Kg
MASSUNITS = {"Kilogram":1,"Gram":0.001,"Earth Mass":5.972e+24,"Solar Mass":1.989e+30,"Lb":0.453592,
             "-75":14.37218841684362,"-76":5.154011678907833e+25}
#Length Units, in Meters
LENGTHUNITS = {"Meter":1,"cm":0.01,"Km":1000,"AU":1.496e+11,"Light Second":299792458,"Light Year":9460730472580800,"ft":0.3048,
               "-72":241812597,"-73":1.826}
#Velocity Units, in Meters/Second
VELOCITYUNITS = {"m/s":1,"Km/hr":0.2777777777777778,"c":299792458,
                 "-73 -69 -8":2.263823456484007}
#All Units
UNITS = {"Time":TIMEUNITS,"Mass":MASSUNITS,"Length":LENGTHUNITS,"Velocity":VELOCITYUNITS}
