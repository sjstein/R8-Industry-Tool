import struct

version = '1.10'
last_update = '19-Sep-2024'
fname = 'AISpecialLocations.r8'

BYTLEN = 1
FLTLEN = 4
INTLEN = 4
SHTLEN = 2
UTFLEN = 2  # Length of UTF-16 char
SP_REC_PAD_LEN = 30  # Total of constant-length fields in SpawnPoint record


def encode_run8string(in_string):
    b_temp_string = bytearray()
    for k in range(0, len(in_string)):
        b_temp_string += (ord(in_string[k]).to_bytes()[0] >> 4).to_bytes()
        b_temp_string += ((ord(in_string[k]).to_bytes()[0] & 0x0F) << 4).to_bytes()
    return b_temp_string


class SpawnPoint:
    '''
    Size in bytes of SpawnPoint attributes:
        unk1            : 4
        name_len        : 4
        enc_name        : (2*name_len)
        type            : 1
        route_prefix    : 4
        track_id        : 4
        dir             : 1
        unk2            : 1
        unk3            : 2
        unk4            : 4
        time            : 2
        unk5            : 2
        skip            : 1
    '''

    def __init__(self, mem_map, mem_offset):
        ptr = mem_offset
        self.unk1 = mem_map[ptr:ptr + INTLEN]
        ptr += INTLEN
        self.name_len = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little')
        ptr += INTLEN
        self.enc_name = bytes(mem_map[ptr:ptr + self.name_len])  # name in encoded (4-bit rotated) format
        ptr += self.name_len
        self.type = int.from_bytes(mem_map[ptr:ptr + BYTLEN], 'little')
        ptr += BYTLEN
        self.route_prefix = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little')
        ptr += INTLEN
        self.track_id = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little')
        ptr += INTLEN
        self.dir = int.from_bytes(mem_map[ptr:ptr + BYTLEN], 'little')
        ptr += BYTLEN
        self.unk2 = mem_map[ptr:ptr + BYTLEN]
        ptr += BYTLEN
        self.unk3 = mem_map[ptr:ptr + SHTLEN]
        ptr += SHTLEN
        self.unk4 = mem_map[ptr:ptr + INTLEN]
        ptr += INTLEN
        self.time = int.from_bytes(mem_map[ptr:ptr + SHTLEN], 'little')  # Time value (Run8 caps to 1440 mins (one day))
        ptr += SHTLEN
        self.unk5 = mem_map[ptr:ptr + SHTLEN]
        ptr += SHTLEN
        self.skip = int.from_bytes(mem_map[ptr:ptr + BYTLEN], 'little')  # "Skip AutoTrain" checkbox
        ptr += BYTLEN
        self.name = ''
        # Decode characters of name via left-rotating 2 bytes (UTF-16) by 4 bits
        # This routine takes two consecutive bytes and decodes them to a single character byte (UTF-8)
        for n in range(mem_offset + 8, mem_offset + 8 + self.name_len, 2):
            self.name += chr(mem_map[n] << 4 | mem_map[n + 1] >> 4)

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def dumpAttrs(self):
        return [self.name_len, self.name, self.type, self.route_prefix, self.track_id, self.time, self.dir,
                self.skip, self.unk1, self.unk2, self.unk3, self.unk4, self.unk5]

    def dumpHeader(self):
        return ['NameLen', 'Name', 'Type', 'Route', 'Track', 'Time', 'Dir',
                'Skip', 'Unk_1', 'Unk_2', 'Unk_3', 'Unk_4', 'Unk_5']

    def rename(self, new_name):
        # rename the spawn point. Recalculate the length and re-encode the string
        self.name = new_name
        self.enc_name = encode_run8string(new_name)
        self.name_len = len(self.enc_name)

    def printAttrs(self):
        print(f'Name    : {self.name}')
        print(f'Type    : {self.type}')
        print(f'Time    : {self.time}')
        print(f'Dir     : {self.dir}')
        print(f'Skip?   : {self.skip}')
        print(f'Route ID: {self.route_prefix}')
        print(f'Trk ID  : {self.track_id}')
        print(f'Unk 1   : {self.unk1}')
        print(f'Unk 2   : {bytes(self.unk2).hex()}')
        print(f'Unk 3   : {bytes(self.unk3).hex()}')
        print(f'Unk 4 * : {bytes(self.unk4).hex()}')
        print(f'Unk 5   : {bytes(self.unk5).hex()}')


class SpawnFile:
    def __init__(self):
        self.unk1 = bytes(INTLEN)  # Unknown 4 bytes
        self.num_rec = 0  # Number of spawn points defined in the file
        self.spawn_points = list()  # Spawn records

    def to_bytes(self):
        # Return a bytearray of this object
        barray = bytearray()
        barray += self.unk1
        barray += self.num_rec.to_bytes(INTLEN, 'little')
        for spawn_point in self.spawn_points:
            barray += spawn_point.unk1
            barray += spawn_point.name_len.to_bytes(INTLEN, 'little')
            # Unpack name
            for j in range(0, spawn_point.name_len):
                barray += spawn_point.enc_name[j].to_bytes(BYTLEN, 'little')
            barray += spawn_point.type.to_bytes(BYTLEN, 'little')
            barray += spawn_point.route_prefix.to_bytes(INTLEN, 'little')
            barray += spawn_point.track_id.to_bytes(INTLEN, 'little')
            barray += spawn_point.dir.to_bytes(BYTLEN, 'little')
            barray += spawn_point.unk2
            barray += spawn_point.unk3
            barray += spawn_point.unk4
            barray += spawn_point.time.to_bytes(SHTLEN, 'little')
            barray += spawn_point.unk5
            barray += spawn_point.skip.to_bytes(BYTLEN, 'little')
        return barray


class Milepost:
    '''
    Size in bytes of Milepost attributes:
        unk1            : 4
        unk2            : 4
        name_len        : 4
        enc_name        : (2*name_len)
        tile_x          : 4
        tile_z          : 4
        cam_x           : 4
        cam_y           : 4
        cam_z           : 4
    '''

    def __init__(self, mem_map, mem_offset):
        ptr = mem_offset
        self.unk1 = mem_map[ptr:ptr + INTLEN]
        ptr += INTLEN
        self.unk2 = mem_map[ptr:ptr + INTLEN]
        ptr += INTLEN
        self.name_len = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.enc_name = bytes(mem_map[ptr:ptr + self.name_len])  # name in encoded (4-bit rotated) format
        ptr += self.name_len
        self.tile_x = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.tile_z = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        temp_int = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        self.cam_x = struct.unpack('f', temp_int.to_bytes(INTLEN, 'little', signed=True))[0]
        ptr += FLTLEN
        temp_int = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        self.cam_y = struct.unpack('f', temp_int.to_bytes(INTLEN, 'little', signed=True))[0]
        ptr += FLTLEN
        temp_int = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        self.cam_z = struct.unpack('f', temp_int.to_bytes(INTLEN, 'little', signed=True))[0]
        ptr += FLTLEN
        self.name = ''
        # Decode characters of name via left-rotating 2 bytes (UTF-16) by 4 bits
        # This routine takes two consecutive bytes and decodes them to a single character byte (UTF-8)
        for n in range(mem_offset + 12, mem_offset + 12 + self.name_len, 2):
            self.name += chr(mem_map[n] << 4 | mem_map[n + 1] >> 4)

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def dumpAttrs(self):
        return [self.name_len, self.name, self.unk1, self.unk2, self.tile_x, self.tile_z, self.cam_x,
                self.cam_y, self.cam_z]

    def dumpHeader(self):
        return ['NameLen', 'Name', 'unk1', 'unk2', 'tile_x', 'tile_z', 'cam_x',
                'cam_y', 'cam_z']

    def rename(self, new_name):
        # rename the point. Recalculate the length and re-encode the string
        self.name = new_name
        self.enc_name = encode_run8string(new_name)
        self.name_len = len(self.enc_name)

    def printAttrs(self):
        print(f'Name    : {self.name}')
        print(f'Unk1    : {self.unk1}')
        print(f'Unk2    : {self.unk2}')
        print(f'Tile_X  : {self.tile_x}')
        print(f'Tile_Z  : {self.tile_z}')
        print(f'Cam_X   : {self.cam_x}')
        print(f'Cam_Y   : {self.cam_y}')
        print(f'Cam_Z   : {self.cam_z}')


class MilepostFile:
    def __init__(self):
        self.unk1 = bytes(INTLEN)  # Unknown 4 bytes
        self.num_rec = 0  # Number of mileposts defined in the file
        self.mileposts = list()  # Spawn records

    def to_bytes(self):
        # Return a bytearray of this object
        barray = bytearray()
        barray += self.unk1
        barray += self.num_rec.to_bytes(INTLEN, 'little')
        for milepost in self.mileposts:
            barray += milepost.unk1
            barray += milepost.unk2
            barray += milepost.name_len.to_bytes(INTLEN, 'little')
            # Unpack name
            for j in range(0, milepost.name_len):
                barray += milepost.enc_name[j].to_bytes(BYTLEN, 'little')
            barray += milepost.tile_x.to_bytes(INTLEN, 'little', signed=True)
            barray += milepost.tile_z.to_bytes(INTLEN, 'little', signed=True)
            barray += struct.pack('f', milepost.cam_x)
            barray += struct.pack('f', milepost.cam_y)
            barray += struct.pack('f', milepost.cam_z)
        return barray


class industry_tag:
    '''
        name_len        : 4
        enc_name        : (2*name_len)
    '''

    def __init__(self, mem_map, mem_offset):
        ptr = mem_offset
        self.name_len = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.enc_name = bytes(mem_map[ptr:ptr + self.name_len])  # name in encoded (4-bit rotated) format
        ptr += self.name_len
        self.name = ''
        # Decode characters of name via left-rotating 2 bytes (UTF-16) by 4 bits
        # This routine takes two consecutive bytes and decodes them to a single character byte (UTF-8)
        for n in range(mem_offset + 4, mem_offset + 4 + self.name_len, 2):
            self.name += chr(mem_map[n] << 4 | mem_map[n + 1] >> 4)

        self.len_in_bytes = ptr - mem_offset

    def __len__(self):
        return self.len_in_bytes

    def to_bytes(self):
        # Return a bytearray of this object
        barray = bytearray()
        barray += self.name_len.to_bytes(INTLEN, 'little', signed=True)
        for j in range(0, self.name_len):
            barray += self.enc_name[j].to_bytes(BYTLEN, 'little')
        return barray

    def returnAttrs(self, prefix):
        retstr = ''
        retstr += f'{prefix}{self.name}'

        return retstr

    def replaceName(self, new_name):
        """Replace the tag name with a new name"""
        self.name = new_name
        self.enc_name = encode_run8string(new_name)
        self.name_len = len(self.enc_name)


class industry_filter:
    '''
        name_len        : 4
        enc_name        : (2*name_len)
    '''

    def __init__(self, mem_map, mem_offset):
        ptr = mem_offset
        self.name_len = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.enc_name = bytes(mem_map[ptr:ptr + self.name_len])  # name in encoded (4-bit rotated) format
        ptr += self.name_len
        self.name = ''
        # Decode characters of name via left-rotating 2 bytes (UTF-16) by 4 bits
        # This routine takes two consecutive bytes and decodes them to a single character byte (UTF-8)
        for n in range(mem_offset + 4, mem_offset + 4 + self.name_len, 2):
            self.name += chr(mem_map[n] << 4 | mem_map[n + 1] >> 4)

        self.len_in_bytes = ptr - mem_offset

    def __len__(self):
        return self.len_in_bytes

    def returnAttrs(self, prefix):
        retstr = ''
        retstr += f'{prefix}{self.name}'

        return retstr

    def to_bytes(self):
        # Return a bytearray of this object
        barray = bytearray()
        barray += self.name_len.to_bytes(INTLEN, 'little', signed=True)
        for j in range(0, self.name_len):
            barray += self.enc_name[j].to_bytes(BYTLEN, 'little')
        return barray


class producer:
    '''
    Size in bytes of producer attributes:
        rec_type        : 4  // Some kind of record type. When 2, contains filters, when 1 does not
        bIndex          : 1  // Index to determine train car type
        produce_empties : 1  // Boolean: when true (1), indicates producing empty cars (instead of loads)
        proc_hours      : 4  // How many hours to process
        capacity        : 4
        num_tags        : 4  // Number of entries in "processed tags to choose from" field (this is a comma delimited entry in Run8)
        tags            : (num_tags * sizeof(industry_tag)) --> class: industry_tag
        num_filters     : 4
        filters         : (num_filters * sizeof(industry_filter)) --> class: industry_filter
    '''

    def __init__(self, mem_map, mem_offset):
        ptr = mem_offset
        self.rec_type = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.bIndex = mem_map[ptr]
        ptr += BYTLEN
        self.produce_empties = bool(mem_map[ptr])
        ptr += BYTLEN
        self.proc_hours = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.capacity = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.num_tags = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        if self.num_tags > 0:
            self.tags = list()
            for i in range(self.num_tags):
                self.tags.append(industry_tag(mem_map, ptr))
                ptr += len(self.tags[-1])
        self.num_filters = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        if self.num_filters > 0:
            self.filter = list()
            for i in range(self.num_filters):
                self.filter.append(industry_filter(mem_map, ptr))
                ptr += len(self.filter[-1])

        self.len_in_bytes = ptr - mem_offset

    def __len__(self):
        return self.len_in_bytes

    def returnTags(self):
        retStr = ''
        for tag in self.tags:
            retStr += f'{tag.name}, '
        return retStr[:-2] if retStr else ''

    def deleteTag(self, tag):
        for i in range(self.num_tags):
            if self.tags[i].name == tag:
                self.tags.pop(i)
                self.num_tags -= 1
                break  # What happens here if a tag is duplicated?

    def replaceTag(self, orig_tag, new_tag=''):
        if not new_tag:
            self.deleteTag(orig_tag)
            return
        for i in range(self.num_tags):
            if self.tags[i].name == orig_tag:
                self.tags[i].name = new_tag
                self.tags[i].enc_name = encode_run8string(new_tag)
                self.tags[i].name_len = len(self.tags[i].enc_name)
                break

    def returnAttrs(self, prefix, cardict):
        retstr = ''
        if self.num_tags == 0:
            retstr += f'{prefix}<null producer>'
            return retstr
        retstr += f'{prefix}Header      : {self.rec_type}\n'
        retstr += f'{prefix}Car type id : {self.bIndex} ({cardict[str(self.bIndex)]})\n'
        retstr += f'{prefix}Prod Mty    : {self.produce_empties}\n'
        retstr += f'{prefix}Hours       : {self.proc_hours}\n'
        retstr += f'{prefix}Capacity    : {self.capacity}\n'
        for i in range(self.num_tags):
            retstr += f'{prefix}Tag {i}: {self.tags[i].returnAttrs("")}\n'
        for i in range(self.num_filters):
            retstr += f'{prefix}Filter {i}: {self.filter[i].returnAttrs("")}\n'
        return retstr

    def to_bytes(self):
        # Return a bytearray of this object
        barray = bytearray()
        barray += self.rec_type.to_bytes(INTLEN, 'little', signed=True)
        barray += self.bIndex.to_bytes(BYTLEN, 'little')
        barray += self.produce_empties.to_bytes(BYTLEN, 'little')
        barray += self.proc_hours.to_bytes(INTLEN, 'little', signed=True)
        barray += self.capacity.to_bytes(INTLEN, 'little', signed=True)
        barray += self.num_tags.to_bytes(INTLEN, 'little', signed=True)
        for j in range(0, self.num_tags):
            barray += self.tags[j].to_bytes()
        barray += self.num_filters.to_bytes(INTLEN, 'little', signed=True)
        for j in range(0, self.num_filters):
            barray += self.filter[j].to_bytes()
        return barray


class industry_track:
    '''
    Size in bytes of Industry track attributes:
        unk1            : 4
        route_prefix    : 4
        track_section   : 4
        track_direction : 4
    '''

    def __init__(self, mem_map, mem_offset):
        ptr = mem_offset
        self.unk1 = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.route_prefix = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.track_section = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.track_direction = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)

    def __len__(self):
        return INTLEN * 4

    def returnAttrs(self, prefix):
        retstr = ''
        retstr += f'{prefix}Route Prefix    : {self.route_prefix}\n'
        retstr += f'{prefix}Track section   : {self.track_section}\n'
        retstr += f'{prefix}Track direction : {self.track_direction}\n'
        return retstr

    def to_bytes(self):
        # Return a bytearray of this object
        barray = bytearray()
        barray += self.unk1.to_bytes(INTLEN, 'little', signed=True)
        barray += self.route_prefix.to_bytes(INTLEN, 'little', signed=True)
        barray += self.track_section.to_bytes(INTLEN, 'little', signed=True)
        barray += self.track_direction.to_bytes(INTLEN, 'little', signed=True)
        return barray


class Track:
    def __init__(self, mem_map, mem_offset):
        ptr = mem_offset
        self.unk1 = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.number_of_sections = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN


class TrackNode:
    '''
    Size in bytes of TrackNode attributes (names/sizes from Puyodead):
        unk1            : 4 [int]
        tile_index      : 8 ('TileIndex' type) [int[2]]
        start_position  : 12 ('Vector3' type) [float[3]]
        Tangent_deg     : 12 ('Vector3' type) [float[3]]
        end_position    : 12 ('Vector3' type) [float[3]]
        index           : 4 [int]
        is_switch_node  : 1 [bool]
        is_reverse_path : 1 [bool]
        curve_deg       : 4 [float]
        curve_sign      : 4 [int]
        radius_meters   : 4 [float]
        arclen_meters   : 4 [float]
        num_segments    : 4 [int]
        belong_to_track : 4 [int]
        is_selected     : 1 [bool]
    '''

    def __init__(self, mem_map, mem_offset):
        ptr = mem_offset
        self.unk1 = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.tile_index = [int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True),
                           int.from_bytes(mem_map[ptr + INTLEN:ptr + INTLEN * 2], 'little', signed=True)]
        ptr += INTLEN * 2
        self.start_position = [struct.unpack('<f', mem_map[ptr:ptr + FLTLEN])[0],
                               struct.unpack('<f', mem_map[ptr + FLTLEN:ptr + FLTLEN * 2])[0],
                               struct.unpack('<f', mem_map[ptr + FLTLEN * 2:ptr + FLTLEN * 3])[0]]
        ptr += FLTLEN * 3
        self.tangent_deg = [struct.unpack('<f', mem_map[ptr:ptr + FLTLEN])[0],
                            struct.unpack('<f', mem_map[ptr + FLTLEN:ptr + FLTLEN * 2])[0],
                            struct.unpack('<f', mem_map[ptr + FLTLEN * 2:ptr + FLTLEN * 3])[0]]
        ptr += FLTLEN * 3
        self.end_position = [struct.unpack('<f', mem_map[ptr:ptr + FLTLEN])[0],
                             struct.unpack('<f', mem_map[ptr + FLTLEN:ptr + FLTLEN * 2])[0],
                             struct.unpack('<f', mem_map[ptr + FLTLEN * 2:ptr + FLTLEN * 3])[0]]
        ptr += FLTLEN * 3
        self.index = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.is_switch_node = bool(mem_map[ptr])
        ptr += BYTLEN
        self.is_reverse_path = bool(mem_map[ptr])
        ptr += BYTLEN
        self.curve_deg = struct.unpack('<f', mem_map[ptr:ptr + FLTLEN])[0]
        ptr += FLTLEN
        self.curve_sign = int.from_bytes(mem_map[ptr:ptr + FLTLEN], 'little', signed=True)
        ptr += INTLEN
        self.radius_meters = struct.unpack('<f', mem_map[ptr:ptr + FLTLEN])[0]
        ptr += FLTLEN
        self.arclen_meters = struct.unpack('<f', mem_map[ptr:ptr + FLTLEN])[0]
        ptr += FLTLEN
        self.num_segments = int.from_bytes(mem_map[ptr:ptr + FLTLEN], 'little', signed=True)
        ptr += INTLEN
        self.belong_to_track = int.from_bytes(mem_map[ptr:ptr + FLTLEN], 'little', signed=True)
        ptr += INTLEN
        self.is_selected = bool(mem_map[ptr])
        ptr += BYTLEN

    def returnAttrs(self, prefix):
        retstr = ''
        retstr += f'{prefix}Route Prefix    : {self.route_prefix}\n'
        retstr += f'{prefix}Track section   : {self.track_section}\n'
        retstr += f'{prefix}Track direction : {self.track_direction}\n'
        return retstr

    def to_bytes(self):
        # Return a bytearray of this object
        barray = bytearray()
        barray += self.unk1.to_bytes(INTLEN, 'little', signed=True)
        barray += self.route_prefix.to_bytes(INTLEN, 'little', signed=True)
        barray += self.track_section.to_bytes(INTLEN, 'little', signed=True)
        barray += self.track_direction.to_bytes(INTLEN, 'little', signed=True)
        return barray


class TrackSection:
    '''
    Size in bytes of TrackSection attributes (names/sizes from Puyodead):
        unk             : 4 [int]
        nbr_nodes       : 4 [int]
        track_nodes     : --> class TrackNode
        index           : 4 [int]
        switch_pos      : 1 [byte]
        num_section_indices : 4 [int]
        next_section    : List of indices, size of list = num_section_indices
        track_type      : 1 [byte]
        retarder_mph    : 8 [double]
        is_occupied     : 1 [bool]
        switch_stand_lft: 1 [byte]
        switch_stand_typ: 4 [int]
        is_ctc_switch   : 1 [bool]
    '''

    def __init__(self, mem_map, mem_offset):
        ptr = mem_offset
        self.unk = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.nbr_nodes = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.track_nodes = list()
        for i in range(self.nbr_nodes):
            self.track_nodes.append(TrackNode(mem_map, ptr))
            ptr += 79   # Size of track_nodes record
        self.index = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.switch_pos = mem_map[ptr]
        ptr += BYTLEN
        self.num_section_indices = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.next_section = list()
        for i in range(self.num_section_indices):
            self.next_section.append(int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True))
            ptr += INTLEN
        self.track_type = mem_map[ptr]
        ptr += BYTLEN
        self.retarder_mph = struct.unpack('<d', mem_map[ptr:ptr + 8])[0]
        ptr += 8
        self.is_occupied = mem_map[ptr]
        ptr += BYTLEN
        self.switch_stand_lft = bool(mem_map[ptr])
        ptr += BYTLEN
        self.switch_stand_typ = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.is_ctc_switch = bool(mem_map[ptr])
        ptr += BYTLEN

    def __len__(self):
        return (INTLEN * 5) + (79 * self.nbr_nodes) + (BYTLEN * 5) + (self.num_section_indices * INTLEN) + 8


class TrackFile:
    def __init__(self):
        self.unk1 = bytes(INTLEN)  # Unknown 4 bytes
        self.num_rec = 0  # Number of industries defined in the file
        self.sections = list()


class Industry:
    '''
    Size in bytes of Industry attributes:
        unk1            : 4
        name_len        : 4
        enc_name        : (2*name_len)
        local_name_len  : 4
        enc_local_name  : (2*local_name_len)
        trk_sym_len     : 4
        enc_trk_sym     : (2*trk_sym_len)
        proc_as_block   : 1
        nbr_tracks      : 4
        tracks          : (4*4*nbr_tracks) --> class industry_track
        num_producers   : 4
        producers       : (4*num_producers) --> class producer

    '''

    def _decodeString(self, mem_map, range_start, range_end):
        # Decode characters of name via left-rotating 2 bytes (UTF-16) by 4 bits
        # This routine takes two consecutive bytes and decodes them to a single character byte (UTF-8)
        retstr = ''
        for n in range(range_start, range_end, 2):
            retstr += chr(mem_map[n] << 4 | mem_map[n + 1] >> 4)
        return retstr

    def __init__(self, mem_map, mem_offset):
        ptr = mem_offset
        self.unk1 = mem_map[ptr:ptr + INTLEN]
        ptr += INTLEN
        self.name_len = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.enc_name = bytes(mem_map[ptr:ptr + self.name_len])  # name in encoded (4-bit rotated) format
        ptr += self.name_len
        self.name = self._decodeString(mem_map, mem_offset + 8, mem_offset + 8 + self.name_len)
        self.local_name_len = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.enc_local_name = bytes(mem_map[ptr:ptr + self.local_name_len])  # name in encoded (4-bit rotated) format
        ptr += self.local_name_len
        self.local_name = self._decodeString(mem_map, mem_offset + 12 + self.name_len,
                                             mem_offset + 12 + self.name_len + self.local_name_len)
        self.trk_sym_len = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        self.enc_trk_sym = bytes(mem_map[ptr:ptr + self.name_len])  # name in encoded (4-bit rotated) format
        ptr += self.trk_sym_len
        self.trk_sym = self._decodeString(mem_map, mem_offset + 16 + self.name_len + self.local_name_len,
                                          mem_offset + 16 + self.name_len + self.local_name_len + self.trk_sym_len)
        self.process_in_blocks = bool(mem_map[ptr])
        ptr += BYTLEN
        self.number_of_tracks = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        if self.number_of_tracks > 0:
            self.track = list()
            for i in range(self.number_of_tracks):
                self.track.append(industry_track(mem_map, ptr))
                ptr += len(self.track[-1])

        self.num_producers = int.from_bytes(mem_map[ptr:ptr + INTLEN], 'little', signed=True)
        ptr += INTLEN
        if self.num_producers > 0:
            self.producer = list()
            for i in range(self.num_producers):
                self.producer.append(producer(mem_map, ptr))
                ptr += len(self.producer[-1])

        self.len_in_bytes = ptr - mem_offset

    def __str__(self):
        return str(self.__class__) + ": " + str(self.__dict__)

    def __len__(self):
        return self.len_in_bytes

    def dumpAttrs(self):
        return [self.name, self.local_name, self.trk_sym]

    def dumpHeader(self):
        return

    def printAttrs(self, cardict):
        print(f'Name            : {self.name}')
        print(f'local           : {self.local_name}')
        print(f'Symbol          : {self.trk_sym}\n')
        print(f'# of tracks     : {self.number_of_tracks}')
        print(f'-----------------')
        for i in range(self.number_of_tracks):
            print(self.track[i].returnAttrs(f'T{i + 1}> '))
        print(f'# of production rules : {self.num_producers}')
        print(f'---------------------')
        for i in range(self.num_producers):
            if self.producer[i].num_tags > 0:
                print(self.producer[i].returnAttrs(f'P{i + 1}> ', cardict))

    def replaceName(self, new_name):
        self.name = new_name
        self.enc_name = encode_run8string(new_name)
        self.name_len = len(self.enc_name)

    def replaceLocalName(self, new_name):
        self.local_name = new_name
        self.enc_local_name = encode_run8string(new_name)
        self.local_name_len = len(self.enc_local_name)

    def replaceSymbol(self, new_name):
        self.trk_sym = new_name
        self.enc_trk_sym = encode_run8string(new_name)
        self.trk_sym_len = len(self.enc_trk_sym)

    def to_dict(self):
        """Convert Industry to dictionary for table display"""
        return {
            'Industry Name': self.name,
            'Tag': self.trk_sym,
            'Local Name': self.local_name,
            f'Nbr of\ntrack nodes': self.number_of_tracks,
            #f'Incoming cars': self.num_producers,
            f'Process in\n Blocks': 'Yes' if self.process_in_blocks else 'No'
        }


class IndustryFile:
    def __init__(self):
        self.unk1 = bytes(INTLEN)  # Unknown 4 bytes
        self.num_rec = 0  # Number of industries defined in the file
        self.industries = list()

    def to_bytes(self):
        # Return a bytearray of this object
        barray = bytearray()
        barray += self.unk1
        barray += self.num_rec.to_bytes(INTLEN, 'little')
        for industry in self.industries:
            barray += industry.unk1
            barray += industry.name_len.to_bytes(INTLEN, 'little')
            # Unpack name
            for j in range(0, industry.name_len):
                barray += industry.enc_name[j].to_bytes(BYTLEN, 'little')
            barray += industry.local_name_len.to_bytes(INTLEN, 'little')
            # Unpack local name
            for j in range(0, industry.local_name_len):
                barray += industry.enc_local_name[j].to_bytes(BYTLEN, 'little')
            barray += industry.trk_sym_len.to_bytes(INTLEN, 'little')
            # Unpack track symbol
            for j in range(0, industry.trk_sym_len):
                barray += industry.enc_trk_sym[j].to_bytes(BYTLEN, 'little')
            barray += industry.process_in_blocks.to_bytes(BYTLEN, 'little')
            barray += industry.number_of_tracks.to_bytes(INTLEN, 'little')
            for j in range(0, industry.number_of_tracks):
                barray += industry.track[j].to_bytes()
            barray += industry.num_producers.to_bytes(INTLEN, 'little')
            for j in range(0, industry.num_producers):
                barray += industry.producer[j].to_bytes()
        return barray
