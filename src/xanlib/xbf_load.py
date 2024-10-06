from struct import unpack, calcsize
from .scene import Scene, Node, VertexAnimationFrameDatum, VertexAnimation, KeyAnimationFrame, KeyAnimation, Face, Vertex, Vector3, Animation, AnimationRange, FXEvent
from .xbf_base import NodeFlags


def convert_signed_5bit(v):
    sign=-1 if (v%32)>15 else 1
    return sign*(v%16)

def convert_to_5bit_signed(v):
    #TODO: unit test
    v_clamped = max(-15, min(15, int(round(v))))
    if v_clamped < 0:
        return v_clamped + 32
    else:
        return v_clamped

def readInt(file):
        return unpack("<i", file.read(4))[0]

def readUInt(file):
        return unpack("<I", file.read(4))[0]

def readInt16(file):
    return unpack("<h", file.read(2))[0]

def readInt8(file):
    return unpack("<b", file.read(1))[0]

def readUInt8(file):
    return unpack("<B", file.read(1))[0]

def readUInt16(file):
    return unpack("<H", file.read(2))[0]

def readMatrix(file):
        return unpack("<16d", file.read(8*16))

def readByte(file):
    return unpack("<c", file.read(1))[0]

def readString(file):
    st=""
    while val:=file.read(1)[0]:
        st+=chr(val)
    return st


def findString(file, s):
    b=0
    while (next_byte:=file.read(1))!=b'':
        if next_byte[0]==ord(s[b]):
            b+=1
            if b>=len(s):
                return True
        else:
            b=0
    return False

def read_vertex(buffer):
    return Vertex(
        unpack("<3f", buffer.read(4 * 3)),
        unpack("<3f", buffer.read(4 * 3))
    )

class VertexAnimationVertex(VertexAnimationFrameDatum):

    @property
    def position(self):
        return Vector3(self.x, self.y, self.z)

    @property
    def normal(self):
        return Vector3(*(convert_signed_5bit((self.normal_packed >> shift) & 0x1F)
                                for shift in (0, 5, 10)))

    def as_vertex(self):
        return Vertex(self.position, self.normal)

    def from_vertex(self, vertex):
        """Warning: does not roundtrip"""
        #TODO: unit test

        self.x = vertex.position[0]
        self.y = vertex.position[1]
        self.z = vertex.position[2]
        self.normal_packed = sum((convert_to_5bit_signed(v) & 0x1F) << shift for v, shift in zip(vertex.normal, [0, 5, 10]))

    def as_flag(self):
        return bool((self.normal_packed >> 15) & 1)


def read_vertex_from_vertex_animation(buffer):
    format_string = '<3hH'
    byte_count_to_read = calcsize(format_string)
    bytes_read = buffer.read(byte_count_to_read)
    unpacked = unpack(format_string, bytes_read)
    return VertexAnimationVertex(*unpacked)

def read_face(buffer):
    return Face(
        unpack("<3i", buffer.read(4 * 3)),
        unpack("<1i", buffer.read(4 * 1))[0],
        unpack("<1i", buffer.read(4 * 1))[0],
        tuple(
            unpack("<2f", buffer.read(4 * 2))
            for i in range(3)
        )
    )
        
def read_vertex_animation(buffer):
    frameCount = readInt(buffer)
    count = readInt(buffer)
    actual = readInt(buffer)
    keyList = [readUInt(buffer) for i in range(actual)]
    if count < 0: #compressed
        scale = readUInt(buffer)
        base_count = readUInt(buffer)
        assert count == -base_count
        real_count = base_count//actual
        frames = [[read_vertex_from_vertex_animation(buffer) for j in range(real_count)] for i in range(actual)]
        if (scale & 0x80000000): #interpolated
            interpolationData = [readUInt(buffer) for i in range(frameCount)]
            
    return VertexAnimation(
        frameCount,
        count,
        actual,
        keyList,
        scale if count<0 else None,
        base_count if count<0 else None,
        real_count if count<0 else None,
        frames if count<0 else None,
        interpolationData if ((count<0) and (scale & 0x80000000)) else None
    )

def read_key_animation(buffer):
    frameCount = readInt(buffer)
    flags = readInt(buffer)
    if flags==-1:
        matrices = [
            unpack('<16f', buffer.read(4*16))
            for i in range(frameCount+1)
        ]
    elif flags==-2:
        matrices = [
            unpack('<12f', buffer.read(4*12))
            for i in range(frameCount+1)
        ]
    elif flags==-3:
        actual = readInt(buffer)
        extra_data = [readInt16(buffer) for i in range(frameCount+1)]
        matrices = [
            unpack('<12f', buffer.read(4 * 12))
            for i in range(actual)
        ]
    else:
        frames = []
        for i in range(flags):
            frame_id = readInt16(buffer)
            flag = readInt16(buffer)
            assert not (flag & 0b1000111111111111)

            if ((flag >> 12) & 0b001):
                rotation = unpack('<4f', buffer.read(4*4))
            else:
                rotation = None
            if ((flag >> 12) & 0b010):
                scale = unpack('<3f', buffer.read(4*3))
            else:
                scale = None
            if ((flag >> 12) & 0b100):
                translation = unpack('<3f', buffer.read(4*3))
            else:
                translation = None

            frames.append(KeyAnimationFrame(
                            frame_id,
                            flag,
                            rotation,
                            scale,
                            translation
                        ))
        
    return KeyAnimation(
        frameCount,
        flags,
        matrices if flags in (-1,-2,-3) else None,
        actual if flags==-3 else None,
        extra_data if flags==-3 else None,
        frames if flags not in (-1,-2,-3) else None
    )        

def read_animation(buffer):
    name = readString(buffer)
    read_start = len(name)+1
    args = []
    for i in range(read_start,36):
        args.append(ord(readByte(buffer)))
    ranges = []
    while readInt(buffer)==1:
        ranges.append(AnimationRange(*[readInt(buffer) for i in range(5)]))
    # go back if there is no more animation range
    buffer.seek(buffer.tell()-4)
    return Animation(name, args, ranges)


# Effect events seems to be constituted mostly from a head part, an optionnal name and an optionnal tail part
def get_event_details(event_type, is_long):
    head_len = 0
    has_name1 = True
    has_name2 = False
    tail_len = 0
    
    event_name="Unknown "+str(event_type)
    if event_type==1:      
        event_name = "Hide"
    elif event_type==2:      
        event_name = "Unhide"
    elif event_type==3:      
        event_name = "Emitter On"
        if is_long:
            head_len = 13
    elif event_type==4:      
        event_name = "Emitter Off"
        if is_long:
            head_len = 13
    elif event_type==6:      
        event_name = "Texture Change"
        has_name2 = True
    elif event_type==7:
        event_name = "UV anim On"
        tail_len = 8
    elif event_type==8:
        event_name = "UV anim Off"
    elif event_type==9:      
        event_name = "Sound"
    elif event_type==10:      
        event_name = "Fire Weapon"
        head_len = 4
        has_name1 = False
    elif event_type==11:      
        event_name = "Speed Change"
        head_len = 8
        has_name1 = False
    elif event_type==12:      
        event_name = "Light On"
        tail_len = 116
        has_name1 = False
    elif event_type==13:      
        event_name = "Light Off"
        head_len = 4
        has_name1 = False

    return (event_name,head_len,tail_len,has_name1,has_name2)

def read_event(fd, event_frame):
    event_type=readInt(fd)

    if event_type>13:
        fd.seek(fd.tell()-4)
        return None
    
    unknown=readInt(fd)
    is_long=readInt(fd)

    (event_name,head_len,tail_len,has_name1,has_name2) = get_event_details(event_type, is_long==6)

    head_args=[]
    if head_len>0:
        for i in range(head_len):
            head_args.append(ord(readByte(fd)))
    
    name1=""
    if has_name1:
        name1=readString(fd)

    name2=""
    if has_name2:
        name2=readString(fd)

    tail_args=[]
    if tail_len>0:
        for i in range(tail_len):
            tail_args.append(ord(readByte(fd)))

    return FXEvent(event_type, event_name, unknown, is_long, head_args, name1, name2, tail_args, event_frame)
            
def read_node(buffer, parent=None):
    buffer_position = buffer.tell()
    try:
        vertexCount = readInt(buffer)
        if vertexCount == -1:
            return None
        node = Node()
        node.parent = parent
        node.flags = NodeFlags(readInt(buffer))
        faceCount = readInt(buffer)
        childCount = readInt(buffer)
        node.transform = readMatrix(buffer)
        nameLength = readInt(buffer)
        node.name = buffer.read(nameLength).decode()
        
        node.children = [read_node(buffer, node)   for i in range(childCount)]
        node.vertices = [read_vertex(buffer) for i in range(vertexCount)]
        node.faces    = [read_face(buffer)   for i in range(faceCount)]

        if NodeFlags.PRELIGHT in node.flags:
            node.rgb = [tuple(readUInt8(buffer) for i in range(3)) for j in range(vertexCount)]

        if NodeFlags.FACE_DATA in node.flags:
            node.faceData = [readInt(buffer) for i in range(faceCount)]

        if NodeFlags.VERTEX_ANIMATION in node.flags:
            node.vertex_animation = read_vertex_animation(buffer)

        if NodeFlags.KEY_ANIMATION in node.flags:
            node.key_animation = read_key_animation(buffer)
            
        return node
    except Exception:
        buffer.seek(buffer_position)
        raise

def load_xbf(filename):
    scene = Scene()
    scene.file = filename  
    with open(filename, 'rb') as f:
        scene.version = readInt(f)
        FXDataSize = readInt(f)
        
        # FX event and animation parsing
        before_FXData = f.tell()

        # FX header parsing
        unknown0 = f.read(24)
        anim_count = readInt(f)
        unknown1 = f.read(1)
        particle_count = readInt(f)
        event_byte_length = readInt(f) # not sure
        unknown2 = readInt(f) # seams to be 1
        frame_count = readInt(f)
        # TMP: frame_count is not there if we have particle data, so set it to zero for now
        if particle_count>0:
            frame_count=0
        unknown3 = readInt(f)
        
        # at start of event frames array
        event_count=0
        events = []
        for i in range(frame_count):
            event_count_this_frame = readInt(f)
            for j in range(event_count_this_frame):
                events.append(i)
            event_count += event_count_this_frame

        # find start of events
        # TMP: should not be needed if particles data were properly parsed
        if findString(f, "MASTER"):
            f.read(1) # zero ending the string

            # parse events
            event_counter = 0
            while event := read_event(f, events[event_counter] if events and event_counter < len(events) else None ):
                scene.events.append(event)
                event_counter+=1

            # parse animations
            for anim_index in range(anim_count):
                scene.animations.append(read_animation(f))
        
        # store all FXData separately
        f.seek(before_FXData)
        scene.FXData = f.read(FXDataSize)

        textureNameDataSize = readInt(f)
        scene.textureNameData = f.read(textureNameDataSize)
        while True:
            try:
                node = read_node(f)
                if node is None:
                    current_position = f.tell()
                    f.seek(0, 2)
                    assert current_position == f.tell(), 'Not at EOF'
                    return scene
                scene.nodes.append(node)
            except Exception as e:
                scene.error = e
                scene.unparsed = f.read()
                return scene
