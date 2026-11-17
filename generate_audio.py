"""Create fully original, locally-generated sound loops for Ruheklang.
Nothing is downloaded, no third-party samples are included.
Requires numpy, scipy and ffmpeg to regenerate.
"""
import numpy as np
from scipy.signal import butter, sosfilt
import subprocess, os

SR=32000
DUR=42.0
BLEND=1.2
N=int((DUR+BLEND)*SR)
T=np.arange(N,dtype=np.float32)/SR
rng=np.random.default_rng(20261117)
ROOT=os.path.join(os.path.dirname(__file__), 'assets')

def rn(): return rng.standard_normal(N).astype(np.float32)
def filt(x,typ,cut,order=2):
    if typ=='bandpass': wn=[cut[0],cut[1]]
    else: wn=cut
    return sosfilt(butter(order,wn,btype=typ,fs=SR,output='sos'),x).astype(np.float32)
def norm(x,goal=0.19):
    x=np.nan_to_num(x); q=np.percentile(np.abs(x[::50]),99.7)
    if q>0: x=x*(goal/q)
    return x.astype(np.float32)
def pink():
    x=rn()
    return norm(0.40*filt(x,'lowpass',250,1)+0.42*filt(x,'lowpass',1650,1)+0.18*x,0.32)
def brown():
    return norm(filt(rn(),'lowpass',160,2),0.32)
def drift(period=8, amount=0.3):
    z=rng.standard_normal(max(3,int((DUR+BLEND)/period*4)+3))
    coarse=np.linspace(0,(DUR+BLEND),len(z))
    y=np.interp(T,coarse,z)
    return np.maximum(0.12,1+amount*filt(y.astype(np.float32),'lowpass',0.2,1))

def put_drops(x,rate=16,amp=0.03,duration=0.029,flo=550,fhi=2300,kind='water'):
    count=rng.poisson(rate*(DUR+BLEND))
    starts=rng.integers(int(SR*.5),N-int(.3*SR),size=count)
    for st in starts:
        length=int(SR*duration*rng.uniform(.55,1.5))
        tt=np.arange(length,dtype=np.float32)/SR
        fq=rng.uniform(flo,fhi)
        if kind=='water':
            hz=fq*(1+0.25*np.exp(-tt*44))
            signal=np.sin(2*np.pi*np.cumsum(hz)/SR)
            env=np.exp(-tt*rng.uniform(65,150))
        elif kind=='pop':
            signal=rng.standard_normal(length)
            env=np.exp(-tt*rng.uniform(110,350))
        else:
            signal=rng.standard_normal(length)
            env=np.exp(-tt*rng.uniform(65,160))
        end=min(N,st+length)
        x[st:end] += (signal*env)[:end-st]*amp*rng.uniform(.3,1.3)
    return x

def birds(x,rate=0.22,vol=0.035):
    count=max(1,int(rate*(DUR+BLEND)))
    starts=np.sort(rng.integers(SR,N-20000,size=count))
    for st in starts:
        d=rng.uniform(.13,.48)
        L=int(d*SR)
        tt=np.arange(L,dtype=np.float32)/SR
        f1=rng.uniform(1800,3200)
        freq=f1+(rng.choice([-1,1])*rng.uniform(300,900))*(tt/d) + 140*np.sin(2*np.pi*8*tt)
        phase=np.cumsum(freq)*2*np.pi/SR
        env=np.sin(np.pi*tt/d)**1.8
        signal=(np.sin(phase)+.19*np.sin(2*phase))*env*vol*rng.uniform(.6,1.1)
        x[st:st+L]+=signal
    return x

def crickets(x,rate=0.64,vol=.027):
    for st in np.sort(rng.integers(SR,N-25000,size=max(1,int(rate*(DUR+BLEND))))):
        d=rng.uniform(.28,.9); L=int(d*SR)
        tt=np.arange(L,dtype=np.float32)/SR
        freq=rng.uniform(3300,5400)
        pulse=(np.sin(2*np.pi*rng.uniform(21,37)*tt)>0.05).astype(np.float32)
        env=np.sin(np.pi*tt/d)**.6
        signal=vol*env*pulse*(np.sin(2*np.pi*freq*tt)+.2*np.sin(2*np.pi*freq*1.93*tt))
        x[st:st+L]+=signal
    return x

def thunder(x):
    for at in [9.0,28.5]:
        at+=rng.uniform(-2,2)
        st=int(at*SR); L=int(5.3*SR)
        if st+L>N:continue
        tt=np.arange(L,dtype=np.float32)/SR
        sn=rng.standard_normal(L).astype(np.float32)
        low=filt(sn,'lowpass',125,3)
        low=norm(low,.6)
        attack=1-np.exp(-tt*3.5)
        env=attack*np.exp(-tt*.75)
        rattle=(np.sin(2*np.pi*(30+tt*1.3)*tt)*.2 + low*.85)*env
        x[st:st+L]+=rattle*.55
    return x

def make(name):
    if name=='white':
        x=norm(filt(rn(),'highpass',35,1),.40)
    elif name=='pink':
        x=norm(pink(),.40)
    elif name=='brown':
        x=norm(brown()+.24*filt(rn(),'lowpass',650,1),.39)
    elif name=='rain':
        x=norm(.60*filt(rn(),'bandpass',(300,9700),1)+.21*pink()+.24*filt(rn(),'lowpass',1100,1),.29)
        x=put_drops(x,rate=39,amp=.047,duration=.024,flo=700,fhi=3100)
        x*=drift(7,.12)
    elif name=='hardrain':
        x=norm(.8*filt(rn(),'bandpass',(140,11000),1)+.6*filt(rn(),'lowpass',950,2)+.25*pink(),.31)
        x=put_drops(x,rate=68,amp=.077,duration=.033,flo=350,fhi=2300)
        x*=drift(6,.16)
    elif name=='thunder':
        x=norm(.66*filt(rn(),'bandpass',(270,10300),1)+.30*pink(),.23)
        x=put_drops(x,rate=45,amp=.049,duration=.031)
        x=thunder(x)
    elif name=='sea':
        wash=filt(rn(),'bandpass',(130,3800),1)
        foam=filt(rn(),'highpass',900,1)
        low=filt(rn(),'lowpass',170,2)
        swell=np.zeros_like(T)
        pos=-3.
        while pos<DUR+BLEND:
            d=rng.uniform(4.3,8.5)
            st=max(0,int(pos*SR)); en=min(N,int((pos+d)*SR))
            if en>st:
                tt=T[st:en]-pos
                shape=(np.sin(np.pi*np.clip(tt/d,0,1))**1.8)*(0.55+0.45*np.minimum(tt/d*2,1))
                swell[st:en]+=shape.astype(np.float32)
            pos+=d*rng.uniform(.86,1.1)
        x=norm(.16*low+(wash*.53+foam*.15)*(.25+swell*.9),.34)
    elif name=='stream':
        main=filt(rn(),'bandpass',(280,8500),1)
        low=filt(rn(),'lowpass',1050,1)
        x=norm(main*.48+low*.6,.29)*drift(2.2,.10)
        x=put_drops(x,rate=30,amp=.064,duration=.038,flo=500,fhi=2800)
    elif name=='wind':
        x=norm(.80*filt(rn(),'lowpass',730,2)+.22*filt(rn(),'bandpass',(650,3200),1),.34)
        x*=drift(9,.48)
    elif name=='forest':
        x=norm(.4*filt(rn(),'bandpass',(150,2200),1)+.32*filt(rn(),'highpass',500,1),.22)
        x*=drift(12,.18)
        x=birds(x,rate=.36,vol=.09)
    elif name=='fire':
        x=norm(.68*filt(rn(),'lowpass',490,2)+.19*filt(rn(),'bandpass',(520,4500),1),.24)
        x=put_drops(x,rate=15,amp=.12,duration=.024,kind='pop')
        x=put_drops(x,rate=5,amp=.09,duration=.09,kind='pop')
    elif name=='fan':
        hum=np.sin(2*np.pi*83*T)+.38*np.sin(2*np.pi*166*T)
        whir=norm(filt(rn(),'bandpass',(70,1600),1),.18)
        blades=1+.09*np.sin(2*np.pi*7*T)
        x=norm(.18*hum+whir*blades,.27)
    elif name=='night':
        x=norm(.4*filt(rn(),'lowpass',340,1)+.25*filt(rn(),'bandpass',(300,2100),1),.19)
        x=crickets(x,rate=1.7,vol=.06)
    else: raise ValueError(name)
    # Matched loop boundary: material after DUR smoothly crossfades with start.
    total=int(DUR*SR); overlap=int(BLEND*SR)
    y=x[:total].copy()
    fade=(np.sin(np.linspace(0,np.pi/2,overlap,dtype=np.float32))**2)
    y[:overlap]=(x[total:total+overlap]*(1-fade)+x[:overlap]*fade)
    # Dual-mono for reliability on iOS; a subtle natural stereo ambience via short shift.
    left=np.clip(y*.92,-.92,.92)
    right=np.clip(np.roll(y,int(.006*SR))*.91,-.92,.92)
    interleaved=np.stack([left,right],axis=-1)
    pcm=(interleaved*32767).astype('<i2')
    out=os.path.join(ROOT,name+'.mp3')
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','s16le','-ar',str(SR),'-ac','2','-i','pipe:0','-codec:a','libmp3lame','-q:a','6','-id3v2_version','3','-map_metadata','-1',out]
    proc=subprocess.run(cmd,input=pcm.tobytes(),capture_output=True)
    if proc.returncode:raise RuntimeError(proc.stderr.decode())
    print(name,round(os.path.getsize(out)/1024),'KB', flush=True)

for name in ['rain','hardrain','thunder','sea','stream','wind','forest','fire','night','brown','pink','white','fan']:
    make(name)
