import os
import math
import sys
import struct

def readInt(file):
	return struct.unpack("<i", file.read(4))[0]

def readUInt(file):
	return struct.unpack("<I", file.read(4))[0]

def readInt16(file):
    return struct.unpack("<h", file.read(2))[0]

def readInt8(file):
    return struct.unpack("<b", file.read(1))[0]

def readUInt8(file):
    return struct.unpack("<B", file.read(1))[0]

def readUInt16(file):
    return struct.unpack("<H", file.read(2))[0]

def readMatrix(file):
	return struct.unpack("<16d", file.read(8*16))

def readByte(file):
    return struct.unpack("<c", file.read(1))[0]

wd=os.path.dirname(os.path.realpath(__file__))

def is_ascii(s):
    #return s < 128
    return s >=32 and s <= 122

def load_file(fn):
    fd = open(os.path.join(wd,fn), "rb")
    fw = open(os.path.join(wd,"animout3.txt"), "w")
    version = readInt(fd)
    FXDataSize = readInt(fd)
    FXData = fd.read(FXDataSize)
    fw.write(str(FXData))
    counter = 0
    curstr = ""
    cuts=[]
    durs=[]
    for i in range(len(FXData)):
        val = FXData[i]
        if is_ascii(val):
            curstr+=chr(val)
            counter+=1
        else:
             if counter>1:
                cuts.append(i-counter)
                durs.append(counter)
                #print(i-counter,counter,curstr)
             curstr=""
             counter=0
    for i in range(len(cuts)):
         pos = cuts[i]
         dur = durs[i]
         next= cuts[i+1] if i<len(cuts)-1 else len(FXData)
         curstr = FXData[pos:next]
         outstr=str(i)+"("+str(next-pos)+"): "
         for i in range(len(curstr)):
            val=curstr[i]
            if is_ascii(val) and i<dur:
                outstr+=chr(val)
            else:
                outstr+=" "+str(val)
         print(outstr)
         print(curstr)

def find_string(t,s):
    b=0
    for i in range(len(t)):
       v=t[i]
       if v==ord(s[b]):
            b+=1
            if b>=len(s):
                 return i-b
       else:
            b=0
    return -1

def get_name(s, i):
    st=""
    while i<len(s):
        if s[i]==0:
            return st
        st+=chr(s[i])
        i+=1
    return ""

def parse_events(pos, FXData):
    print("Effects:")
    while pos<len(FXData):
        event_type=FXData[pos]

        if event_type>47:
            break
        pos+=4

        # Effect events seems to be constituted mostly from a head part, an optionnal name and an optionnal post part
        head_len=8
        has_name = True
        post_len=0
        
        event_name="Unknown "+str(event_type)
        if event_type==1:      
            event_name="Hide"
        elif event_type==2:      
            event_name="Unhide"
        elif event_type==3:      
            event_name="Emitter On"
            head_len=21
        elif event_type==4:      
            event_name="Emitter Off"
            head_len=21
        elif event_type==7:
            event_name="UV anim On"
            post_len=8
        elif event_type==8:
            event_name="UV anim Off"
        elif event_type==9:      
            event_name="Sound"
        elif event_type==10:      
            event_name="Fire Weapon"
            head_len=12
            has_name=False

        head_args=""
        if head_len>0:
            for i in range(pos,pos+head_len):
                head_args+=" "+str(FXData[i])
            pos+=head_len
        
        target_name=""
        if has_name:
            target_name=get_name(FXData, pos)
            pos+=len(target_name)+1

        post_args=""
        if post_len>0:
            for i in range(pos,pos+post_len):
                post_args+=" "+str(FXData[i])
            pos+=post_len

        stringout = event_name + ": " + target_name + head_args + post_args
        print(stringout)
    return pos

def parse_anim(pos, FXData):
    print("Animations:")
    while pos<len(FXData)-60:
        anim_name=get_name(FXData, pos)
        args=""
        deuxcentquatre=0
        for i in range(pos+len(anim_name)+1,pos+60):
            if FXData[i]==204:
                deuxcentquatre+=1
            else:
                if deuxcentquatre>0:
                    args+=" 204("+str(deuxcentquatre)+")" if deuxcentquatre>1 else " 204"
                    deuxcentquatre=0
                args+=" "+str(FXData[i])
            
        stringout = anim_name + args
        print(stringout)
        pos+=60
    return pos

def parse_xbf(fn):
    fd = open(os.path.join(wd,fn), "rb")
    version = readInt(fd)
    FXDataSize = readInt(fd)
    FXData = fd.read(FXDataSize)
    mastpos = find_string(FXData, "MASTER")
    if mastpos<0:
         return
    pos=mastpos+8
    # Effects events:
    pos=parse_events(pos, FXData)
    # animations:
    pos=parse_anim(pos, FXData)

def parse_fx(fn):
    fd = open(os.path.join(wd,fn), "rb")
    FXData = fd.read()
    mastpos = find_string(FXData, "MASTER")
    if mastpos<0:
         return
    pos=mastpos+8
    # Effects events:
    #pos=parse_events(pos, FXData)
    
    # animations:
    pos=4
    pos=parse_anim(pos, FXData)
    
# info:
# - replay count (4B?) -20
# - at the end: start anim (4B) -8 end anim (4B) -4

#parse_xbf("IN_Medical_H0.Xbf")
parse_xbf("AT_Sniper_H0.XBF")
#parse_xbf("AT_MGT_H0_base.xbf")
#parse_xbf("IN_SurfaceWorm_H0.xbf")
#parse_fx("testing_fx.FX")
