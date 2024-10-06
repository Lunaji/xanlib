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
    #fw = open(os.path.join(wd,"animout4.txt"), "w")
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


def to_text_file(fn,ext):
    fd = open(os.path.join(wd,fn+ext), "rb")
    fw = open(os.path.join(wd,fn+".txt"), "w")
    fw.write(str(fd.read()))

def find_string(t,s):
    b=0
    for i in range(len(t)):
       v=t[i]
       if v==ord(s[b]):
            b+=1
            if b>=len(s):
                 return i-b+1
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

def read_name(fd):
    st=""
    while val:=fd.read(1)[0]:
        st+=chr(val)
    return st

# Effect events seems to be constituted mostly from a head part, an optionnal name and an optionnal post part
def get_event_details(event_type, is_long):
    head_len=0
    has_name = True
    has_second_name = False
    post_len=0
    
    event_name="Unknown "+str(event_type)
    if event_type==1:      
        event_name="Hide"
    elif event_type==2:      
        event_name="Unhide"
    elif event_type==3:      
        event_name="Emitter On"
        if is_long:
            head_len=13
    elif event_type==4:      
        event_name="Emitter Off"
        if is_long:
            head_len=13
    elif event_type==6:      
        event_name="Texture Change"
        has_second_name=True
    elif event_type==7:
        event_name="UV anim On"
        post_len=8
    elif event_type==8:
        event_name="UV anim Off"
    elif event_type==9:      
        event_name="Sound"
    elif event_type==10:      
        event_name="Fire Weapon"
        head_len=4
        has_name=False
    elif event_type==11:      
        event_name="Speed Change"
        head_len=8
        has_name=False
    elif event_type==12:      
        event_name="Light On"
        post_len=116
        has_name=False
    elif event_type==13:      
        event_name="Light Off"
        head_len=4
        has_name=False

    return (event_name,head_len,post_len,has_name,has_second_name)

def parse_events(pos, FXData, events):
    print("Effects:")
    found_count=0
    while pos<len(FXData):
        event_type=FXData[pos]
        is_long=FXData[pos+8]==6
        #print("         around:",FXData[pos-5:pos],FXData[pos:pos+5])

        if event_type>47:
            break
        pos+=4

        (event_name,head_len,post_len,has_name,has_second_name) = get_event_details(event_type, is_long)

        head_args=""
        if head_len>0:
            for i in range(pos,pos+head_len):
                head_args+=" "+str(FXData[i])
            pos+=head_len
        
        target_name=""
        if has_name:
            target_name=get_name(FXData, pos)
            pos+=len(target_name)+1

        second_name=""
        if has_second_name:
            second_name=get_name(FXData, pos)
            pos+=len(second_name)+1

        post_args=""
        if post_len>0:
            for i in range(pos,pos+post_len):
                post_args+=" "+str(FXData[i])
            pos+=post_len

        frame_number = ""
        if events:
            if found_count<len(events):
                frame_number = str(events[found_count]) + "\t"
            else:
                frame_number = "Error"
        
        #stringout = " - " + frame_number + event_name + "\t\t" + target_name + "\t" + second_name + head_args + post_args
        stringout = " - " + frame_number + event_name + "\t\t" + target_name + "\t" + second_name
        print(stringout)
        found_count+=1
    print("found events:",found_count)
    return pos


def read_events(fd, events):
    print("Effects:")
    found_count=0
    while True:
        event_type=readInt(fd)
        unknown=readInt(fd)
        is_long=readInt(fd)
        #print("         around:",FXData[pos-5:pos],FXData[pos:pos+5])

        if event_type>47:
            fd.seek(fd.tell()-12)
            break

        (event_name,head_len,post_len,has_name,has_second_name) = get_event_details(event_type, is_long==6)

        head_args=""
        if head_len>0:
            for i in range(head_len):
                head_args+=" "+str(fd.read(1)[0])
        
        target_name=""
        if has_name:
            target_name=read_name(fd)

        second_name=""
        if has_second_name:
            second_name=read_name(fd)

        post_args=""
        if post_len>0:
            for i in range(post_len):
                post_args+=" "+str(fd.read(1)[0])

        frame_number = ""
        if events:
            if found_count<len(events):
                frame_number = str(events[found_count]) + "\t"
            else:
                frame_number = "Error"
        
        #stringout = " - " + frame_number + event_name + "\t\t" + target_name + "\t" + second_name + head_args + post_args
        stringout = " - " + frame_number + event_name + "\t\t" + target_name + "\t" + second_name
        print(stringout)
        found_count+=1
    print("found events:",found_count)

def parse_anim(pos, FXData):
    print("Animations:")
    found_count=0
    while pos<len(FXData)-60:
        anim_name=get_name(FXData, pos)
        args=""
        deuxcentquatre=0
        for i in range(pos+len(anim_name)+1,pos+36):
            if FXData[i]==204:
                deuxcentquatre+=1
            else:
                if deuxcentquatre>0:
                    args+=" 204("+str(deuxcentquatre)+")" if deuxcentquatre>1 else " 204"
                    deuxcentquatre=0
                args+=" "+str(FXData[i])
        found_count+=1
        pos=pos+36
        print(" - " + anim_name)
        while FXData[pos]==1:
            # todo: read as int instead of individual byte
            repeat=FXData[pos+4]
            frame_start=FXData[pos+16]
            frame_end=FXData[pos+20]
            #stringout = " - " + anim_name + "\t\t" + str(frame_start) + "\t" + str(frame_end) + "\t" + args
            stringout = "\t" + str(frame_start) + "\t" + str(frame_end) + "\t(" + str(repeat) + ")"
            print(stringout)
            pos+=24
    print("found animation:",found_count)
    return pos


def read_anim(counter,fd):
    print("Animations:")
    for anim_index in range(counter):
        anim_name=read_name(fd)
        args=""
        deuxcentquatre=0
        for i in range(len(anim_name)+1,36):
            value=fd.read(1)[0]
            if value==204:
                deuxcentquatre+=1
            else:
                if deuxcentquatre>0:
                    args+=" 204("+str(deuxcentquatre)+")" if deuxcentquatre>1 else " 204"
                    deuxcentquatre=0
                args+=" "+str(value)
        print(" - " + anim_name + "\t\t" + args)
        while readInt(fd)==1:
            # todo: read as int instead of individual byte
            repeat=readInt(fd)
            unkown1=readInt(fd)
            unkown2=readInt(fd)
            frame_start=readInt(fd)
            frame_end=readInt(fd)
            #stringout = " - " + anim_name + "\t\t" + str(frame_start) + "\t" + str(frame_end) + "\t" + args
            stringout = "\t" + str(frame_start) + "\t" + str(frame_end) + "\t(" + str(repeat) + ")"
            print(stringout)
        fd.seek(fd.tell()-4)
    
def parse_xbf(fn):
    fd = open(os.path.join(wd,fn), "rb")
    version = readInt(fd)
    FXDataSize = readInt(fd)
    FXHeaderPosition = fd.tell()

    unknown0 = fd.read(24)
    anim_count = readInt(fd)
    unknown1 = fd.read(1)
    particle_count = readInt(fd)
    print("Particles:",particle_count)
    event_byte_length = readInt(fd) # not sure
    unknown2 = readInt(fd) # seams to be 1
    frame_count = readInt(fd)
    # TMP: avoid reading frame_count if we have particle data for now
    if particle_count>0:
        frame_count=0
    unknown3 = readInt(fd)

    # at start of event frames array
    event_count=0
    events = []
    for i in range(frame_count):
        event_count_this_frame = readInt(fd)
        for j in range(event_count_this_frame):
            events.append(i)
        event_count += event_count_this_frame

    print("event count:", event_count)
    print(events)

    fxdata_start = fd.tell()
    Startoffset = fxdata_start-FXHeaderPosition
    FXData = fd.read(FXDataSize-Startoffset)
    mastpos = find_string(FXData, "MASTER")
    if mastpos<0:
         return
    pos=mastpos+7
    #master=get_name(FXData, pos) # read "master"
    #pos+=len(master)+1
    fd.seek(fxdata_start + pos)

    # Effects events:
    pos=read_events(fd, events)

    # animations:
    print("Animation count:",anim_count)
    read_anim(anim_count, fd)

def parse_fx(fn):
    fd = open(os.path.join(wd,fn), "rb")
    animcount = readInt(fd)
    FXData = fd.read()
    mastpos = find_string(FXData, "MASTER")
    if mastpos<0:
         return
    pos=mastpos+7
    # Effects events:
    pos=parse_events(pos, FXData)
    
    # animations:
    print("Animation count:",animcount)
    pos=4
    pos=parse_anim(pos, FXData)
    
# info:
# - replay count (4B?) -20
# - at the end: start anim (4B) -8 end anim (4B) -4

#parse_xbf("IN_Medical_mod2.Xbf")
#parse_xbf("AT_Sniper_H0.XBF")
parse_xbf("AT_MGT_H0_base.xbf")
#parse_xbf("IN_SurfaceWorm_H0.xbf")
#parse_xbf("HK_Deathhand_H0.xbf")
#parse_fx("testing_fx.FX")
#parse_fx("deathhand.FX")
#to_text_file("AT_MGT_H0_base",".xbf")