import time
import math
import pprint

# Sysex formats taken from http://synth.stromeko.net/docs/Waldorf.pdf
GDAT = [ # Global settings
    ("Version",                     0x00, 0x00, ),
    None,
    ("Popup_Time",                  0x00, 0x02, ),
    ("Label_Time",                  0x00, 0x03, ),
    ("LCD_Contrast",                0x00, 0x04, ),
    ("Input_Gain",                  0x00, 0x05, ),
    ("Master_Tune",                 0x00, 0x06, ),
    ("Global_Channel",              0x00, 0x07, ("Omni", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", ), ),
    ("Sysex_ID",                    0x00, 0x08, [0, 126], ),
    ("Global_Volume",               0x00, 0x09, ),
    None,
    None,
    ("Active_Program",              0x00, 0x0c, [0, 49], ),
    ("Map_Base_Key",                0x00, 0x0d, ),
    ("Global_Tempo_Hi",             0x00, 0x0e, [0, 24], ),
    ("Global_Tempo_Lo",             0x00, 0x0f, [0, 127], ),
    ("TX_Clock",                    0x00, 0x10, ("On", "Off", ), ),
    ("Ctl_Send",                    0x00, 0x11, ("Off", "Sysex", ), ),
    ("Ctl_Recv",                    0x00, 0x12, ("Off", "On", "MP-Bundle", ), ),
    ("TX_ProgCh",                   0x00, 0x13, ("On", "Off", ), ),
    ("RX_ProgCh",                   0x00, 0x14, ("On", "Off", ), ),
    None,
    ("Screen_Saver",                0x00, 0x16, {0: "On", 58: "Off"}, ),
    None,
    ("Global_Pattern_Mode",         0x00, 0x18, ("On", "Off", ), ),
]
KDAT = [ # Program data
    None,
    ("Name_0",                      0x00, 0x01, [32, 127], ),
    ("Name_1",                      0x00, 0x02, [32, 127], ),
    ("Name_2",                      0x00, 0x03, [32, 127], ),
    ("Name_3",                      0x00, 0x04, [32, 127], ),
    ("Name_4",                      0x00, 0x05, [32, 127], ),
    ("Name_5",                      0x00, 0x06, [32, 127], ),
    ("Name_6",                      0x00, 0x07, [32, 127], ),
    ("Name_7",                      0x00, 0x08, [32, 127], ),
    ("Name_8",                      0x00, 0x09, [32, 127], ),
    ("Name_9",                      0x00, 0x0a, [32, 127], ),
    ("Name_10",                     0x00, 0x0b, [32, 127], ),
    ("Name_11",                     0x00, 0x0c, [32, 127], ),
    ("Name_12",                     0x00, 0x0d, [32, 127], ),
    ("Name_13",                     0x00, 0x0e, [32, 127], ),
    ("Name_14",                     0x00, 0x0f, [32, 127], ),
    ("Name_15",                     0x00, 0x10, [32, 127], ),
    ("Midi_Mode",                   0x00, 0x11, ("Native", "Plug-In Compatible", "Global Channel", ), ),
    ("Tempo_Lo",                    0x00, 0x12, [0, 24], ),
    ("Tempo_Hi",                    0x00, 0x13, [0, 127], ),
    ("InstrumentA_Sound",           0x00, 0x14, [0, 23], ),
    ("InstrumentA_Vel",             0x00, 0x15, [0, 127], ),
    ("InstrumentB_Sound",           0x00, 0x16, [0, 23], ),
    ("InstrumentB_Vel",             0x00, 0x17, [0, 127], ),
    ("InstrumentC_Sound",           0x00, 0x18, [0, 23], ),
    ("InstrumentC_Vel",             0x00, 0x19, [0, 127], ),
    ("InstrumentS_Sound",           0x00, 0x1b, [0, 23], ),
    ("InstrumentS_Vel",             0x00, 0x1c, [0, 127], ),
    ("Time_Sig",                    0x00, 0x1d, ("4/4", "3/4", "5/4", ), ),
]
SDAT = [ # Sound data
    None,
    # Oscillators
    ("Osc1_Shape",                  0x00, 0x01, ("Triangle", "Sine", "Square", "Saw", "S&H", "Noise", "HH Closed", "HH Open", "Crash", "Ext L", "Ext R", "Ext Mono", ), ),
    ("Osc1_Pitch",                  0x00, 0x02,),
    ("Osc1_Detune",                 0x00, 0x03,),
    ("Osc1_Start_Phase",            0x00, 0x04, ("Peak+", "Peak-", "Zero", "Free", ), ),
    ("Osc1_Pitch_Mod",              0x00, 0x05,),
    ("Osc1_Pitch_Ctrl",             0x00, 0x06,),
    ("Osc1_Pitch_Mod_Src",          0x00, 0x07, ("Env1", "Env2", "LFO1", "LFO2", ), ),
    ("Osc1_Pitch_Ctrl_Src",         0x00, 0x08, ("Velocity", "Modwheel", "Pressure", "Breath", "Foot", "Keytrack", ), ),
    ("Osc1_FM_Depth",               0x00, 0x09,),
    ("Osc1_FM_Mod",                 0x00, 0x0a,),
    ("Osc1_FM_Ctrl",                0x00, 0x0b,),
    ("Osc1_FM_Mod_Src",             0x00, 0x0c, ("Env1", "Env2", "LFO1", "LFO2", ), ),
    ("Osc1_FM_Ctrl_Src",            0x00, 0x0d, ("Velocity", "Modwheel", "Pressure", "Breath", "Foot", "Keytrack", ), ),
    None,
    None,
    ("Osc2_Shape",                  0x00, 0x10, ("Triangle", "Sine", "Square", "Saw", "S&H", "Noise", "HH Closed", "HH Open", "Crash", "Ext L", "Ext R", "Ext Mono", ), ),
    ("Osc2_Pitch",                  0x00, 0x11,),
    ("Osc2_Detune",                 0x00, 0x12,),
    ("Osc2_Start_Phase",            0x00, 0x13, ("Peak+", "Peak-", "Zero", "Free", ), ),
    ("Osc2_Pitch_Mod",              0x00, 0x14,),
    ("Osc2_Pitch_Ctrl",             0x00, 0x15,),
    ("Osc2_Pitch_Mod_Src",          0x00, 0x16, ("Env1", "Env2", "LFO1", "LFO2", ), ),
    ("Osc2_Pitch_Ctrl_Src",         0x00, 0x17, ("Velocity", "Modwheel", "Pressure", "Breath", "Foot", "Keytrack", ), ),
    None,
    None,
    # Mixer
    ("Osc1_Level",                  0x00, 0x1a,),
    ("Osc2_Level",                  0x00, 0x1b,),
    ("Ringmod_Level",               0x00, 0x1c,),
    ("Crack_Level",                 0x00, 0x1d,),
    ("Osc2_Level_Mod",              0x00, 0x1e,),
    ("Osc2_Level_Ctrl",             0x00, 0x1f,),
    ("Osc2_Level_Mod_Src",          0x00, 0x20, ("Env1", "Env2", "LFO1", "LFO2", ), ),
    ("Osc2_Level_Ctrl_Src",         0x00, 0x21, ("Velocity", "Modwheel", "Pressure", "Breath", "Foot", "Keytrack", ), ),
    None,
    None,
    # Crack generator
    ("Crack_Speed",                 0x00, 0x24,),
    ("Crack_Length",                0x00, 0x25,),
    # Filter
    ("Filter_Type",                 0x00, 0x26, ("Bypass", "Low", "Band", "High", "Notch", "Shelf", "Bell", "S&H"), ),
    ("Filter_Cutoff",               0x00, 0x27,),
    ("Filter_Res",                  0x00, 0x28,),
    ("Filter_Drive",                0x00, 0x29,),
    ("Filter_KeyTrack",             0x00, 0x2a,),
    ("Filter_Cutoff_Mod_1",         0x00, 0x2b,),
    ("Filter_Cutoff_Ctrl_1",        0x00, 0x2c,),
    ("Filter_Cutoff_Mod_1_Src",     0x00, 0x2d, ("Env1", "Env2", "LFO1", "LFO2", ), ),
    ("Filter_Cutoff_Ctrl_1_Src",    0x00, 0x2e, ("Velocity", "Modwheel", "Pressure", "Breath", "Foot", "Keytrack", ), ),
    ("Filter_Cutoff_Mod_2",         0x00, 0x2f,),
    ("Filter_Cutoff_Ctrl_2",        0x00, 0x30,),
    ("Filter_Cutoff_Mod_2_Src",     0x00, 0x31, ("Env1", "Env2", "LFO1", "LFO2", ), ),
    ("Filter_Cutoff_Ctrl_2_Src",    0x00, 0x32, ("Velocity", "Modwheel", "Pressure", "Breath", "Foot", "Keytrack", ), ),
    None,
    None,
    # Amplifier
    ("Amp_Volume",                  0x00, 0x35,),
    ("Amp_Volume_Mod",              0x00, 0x36,),
    ("Amp_Volume_Ctrl",             0x00, 0x37,),
    ("Amp_Volume_Mod_Src",          0x00, 0x38, ("Env1", "Env2", "LFO1", "LFO2", ), ),
    ("Amp_Volume_Ctrl_Src",         0x00, 0x39, ("Velocity", "Modwheel", "Pressure", "Breath", "Foot", "Keytrack", ), ),
    ("Amp_Pan",                     0x00, 0x3a,),
    ("Amp_Pan_Mod",                 0x00, 0x3b,),
    ("Amp_Pan_Ctrl",                0x00, 0x3c,),
    ("Amp_Pan_Mod_Src",             0x00, 0x3d, ("Env1", "Env2", "LFO1", "LFO2", ), ),
    ("Amp_Pan_Ctrl_Src",            0x00, 0x3e, ("Velocity", "Modwheel", "Pressure", "Breath", "Foot", "Keytrack", ), ),
    # Envelopes
    ("Env1_Attack",                 0x00, 0x3f,),
    ("Env1_Decay",                  0x00, 0x40,),
    ("Env1_Sustain",                0x00, 0x41,),
    ("Env1_Release",                0x00, 0x42,),
    ("Env1_Shape",                  0x00, 0x43,),
    None,
    ("Env2_Attack",                 0x00, 0x45,),
    ("Env2_Decay",                  0x00, 0x46,),
    ("Env2_Sustain",                0x00, 0x47,),
    ("Env2_Release",                0x00, 0x48,),
    ("Env2_Shape",                  0x00, 0x49,),
    None,
    # LFOs
    ("LFO1_Speed",                  0x00, 0x4b,),
    ("LFO1_Shape",                  0x00, 0x4c, ("Sine", "Triangle", "Square", "Saw", "Random", "S&H", ), ),
    ("LFO1_Sync",                   0x00, 0x4d, ("Off", "Key", "8 bars", "4 bars", "2 bars", "1 bar", "1/2", "1/4", "1/8", "1/16", "1/32", "1/64", "1/2.", "1/4.", "1/8.", "1/16.", "1/32.", "1/64.", "1/2t", "1/4t", "1/8t", "1/16t", "1/32t", "1/64t", ), ),
    ("LFO1_OneShot",                0x00, 0x4e, ("Off", "On", ), ),
    ("LFO2_Speed",                  0x00, 0x4f,),
    ("LFO2_Shape",                  0x00, 0x50, ("Sine", "Triangle", "Square", "Saw", "Random", "S&H", ), ),
    ("LFO2_Sync",                   0x00, 0x51, ("Off", "Key", "8 bars", "4 bars", "2 bars", "1 bar", "1/2", "1/4", "1/8", "1/16", "1/32", "1/64", "1/2.", "1/4.", "1/8.", "1/16.", "1/32.", "1/64.", "1/2t", "1/4t", "1/8t", "1/16t", "1/32t", "1/64t", ), ),
    ("LFO2_Mod",                    0x00, 0x52,),
    ("LFO2_Mod_Src",                0x00, 0x53, ("Env1", "Env2", "LFO1", "LFO2", ), ),
    None,
    # Output
    ("Dry_Output",                  0x00, 0x55, ("Mono 1", "Stereo 1/2", "Mono 2", "Mono 3", "Stereo 3/4", "Mono 4", "Mono 5", "Stereo 5/6", "Mono 6", ), ),
    ("FX_Select",                   0x00, 0x56, ("FX1", "FX2", "FX3", "FX4", ), ),
    ("FX_Send_Mix",                 0x00, 0x57,),
    ("Tuned_Channel",               0x00, 0x58, ("Off", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "Global", ), ),
    ("Tuned_Transpose",             0x00, 0x59,),
    ("Tuned_LowKey",                0x00, 0x5a,),
    ("Tuned_HighKey",               0x00, 0x5b,),
    None,
    None,
    ("XOR_Group",                   0x00, 0x5e, ("Off", "1", "2", "3", ), ),
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    None,
    ("Pattern_Mode",                0x00, 0x6c, ("Off", "On", "Latch", "Toggle", "OneShot", ), ),
]
FDAT = [ # Effect data
    ("Type",                        0x00, 0x00, ("Bypass", "Chorus", "Flanger", "Phaser", "Overdrive", "Delay", "ModDelay", "Reverb", "LoFi", ), ),
    ("Output",                      0x00, 0x01, ("Out1", "Out1+2", "Out2", "Out3", "Out3+4", "Out4", "Out5", "Out5+6", "Out6", ), ),
    ("Param1",                      0x00, 0x02, ),
    ("Param2",                      0x00, 0x03, ),
    ("Param3",                      0x00, 0x04, ),
    ("Param4",                      0x00, 0x05, ),
    ("Param5",                      0x00, 0x06, ),
    ("Param6",                      0x00, 0x07, ),
    ("Param7",                      0x00, 0x08, ),
    ("Param8",                      0x00, 0x09, ),
    ("Param9",                      0x00, 0x0a, ),
    ("Param10",                     0x00, 0x0b, ),
    ("Param11",                     0x00, 0x0c, ),
]
FPARAMS = [
    [ "Param1",    "Param2",    "Param3",    "Param4",    "Param5",    "Param6",    "Param7",    "Param8",    "Param9",    "Param10",    "Param11" ],
    [ "Speed",     "Depth",     None,        "Delay",     None,        None,        None,        None,        None,        None,         None ],
    [ "Speed",     "Depth",     None,        None,        "Feedback",  None,        None,        None,        "Polarity",  None,         None ],
    [ "Speed",     "Depth",     None,        None,        "Feedback",  "Center",    "Spacing",   None,        "Polarity",  None,         None ],
    [ None,        "Drive",    "PostGain",   None,        None,        "Cutoff",    None,        None,        None,        None,         None ],
    [ None,        None,        None,        "Length",    "Feedback",  "Cutoff",    None,        None,        "Polarity",  "AutoPan",    "Sync" ],
    [ "Speed",     "Depth",     "Sync",      "Length",    "Feedback",  "LoCut",     "HiCut",     "Spread",    None,        None,         None ],
    [ "Size",      "Shape",     "Decay",     "PreDelay",  None,        "LoCut",     "HiCut",     None,        "Diffusion", "Damping",    None ],
    [ None,        None,        None,        None,        "S&H_Rate",  "Drive",     "Gain",      None,        None,        None,         None ],
]
GDAT_LEN = 199
KDAT_LEN = 40
SDAT_LEN = 109
FDAT_LEN = 18

class RackAttack:
    """A Waldorf RackAttack MIDI controller."""
    def __init__(self, midi_in, midi_out):
        self.sysex_header = [0xf0, 0x3e, 0x11, 0x00]
        self.sysex_footer = 0xf7
        self.midi_in = midi_in
        self.midi_out = midi_out
        self.program = Program(self)
        self.gdat = {}
        self.init_to_zero()
    def init_to_zero(self):
        """Init local representation to zero."""
        self.gdat = parse_dat([0] * GDAT_LEN, GDAT)
        self.program.load_from_dump([0] * KDAT_LEN)
        for i in range(24):
            self.program.get_sound(i).load_from_dump([0] * SDAT_LEN)
        for i in range(4):
            self.program.get_effect(i).load_from_dump([0] * FDAT_LEN)
    def init_current_program(self):
        """Init current program on device."""
        self.send_sysex([0x07, 0x04, 0x20, 0x00]) # MODR MCMD MOV1 MOV2
        time.sleep(0.1)
        self.load_from_device()

    def load_from_device(self, program=0):
        """Load local program from device."""
        prgn = 0x00
        bufn = 0x20
        if program >= 1 and program <= 50:
            # Change program
            prgn = program
            self.midi_out.WriteShort(0xc0, prgn - 1, 0) # Rx PrgChg must be ON
            time.sleep(0.1)
        # Global
        self.send_sysex([0x04, 0x00]) # GLBR GLBN
        gbytes = self.receive_sysex(2 + GDAT_LEN)
        self.gdat = parse_dat(gbytes[2:], GDAT)
        # Program
        self.send_sysex([0x01, prgn, bufn]) # PRGR PRGN BUFN
        kbytes = self.receive_sysex(3 + KDAT_LEN)
        self.program.load_from_dump(kbytes[3:])
        # Sounds
        for i in range(24):
            self.send_sysex([0x00, bufn, i]) # SNDR BUFN SNDN
            sbytes = self.receive_sysex(3 + SDAT_LEN)
            self.program.get_sound(i).load_from_dump(sbytes[3:])
        # Effects
        for i in range(4):
            self.send_sysex([0x05, bufn, i]) # EFXR BUFN EFXN
            fbytes = self.receive_sysex(3 + FDAT_LEN)
            self.program.get_effect(i).load_from_dump(fbytes[3:])
    def change_param(self, param_name, value, do_send_sysex=True):
        """Change GLB param `param_name` to `value`."""
        (pah, pal) = change_dat_param(GDAT, self.gdat, param_name, value)
        if do_send_sysex:
            self.rack_attack.send_sysex([
                # GLBP PAH PAL GLBV
                0x24, pah, pal, self.gdat[param_name]
            ])
    def get_param(self, param_name):
        """Return local value for `param_name`."""
        return self.gdat[param_name]
    def get_program(self):
        """Return `Program` instance."""
        return self.program
    def send_midi(self, msgs):
        """Send MIDI in `msgs`."""
        for msg in msgs:
            cmd, b1, b2 = msg
            self.midi_out.WriteShort(cmd, b1, b2)
    def send_sysex(self, bytes, do_flush_hack=False):
        """Send a sysex message to the RackAttack."""
        msg = []
        msg.extend(self.sysex_header)
        msg.extend(bytes)
        msg.append(self.get_sysex_checksum(bytes))
        msg.append(self.sysex_footer)
        if do_flush_hack:
            msg.extend([0xf0, 0xf7])
        print "sysex out", msg
        self.midi_out.WriteSysEx(0, msg)
    def receive_sysex(self, num_bytes, timeout=3):
        """Receive a sysex message of length `num_bytes` from the
        RackAttack."""
        total_num_bytes = num_bytes
        total_num_bytes += len(self.sysex_header)
        total_num_bytes += 2 # 2 == sysex_footer + checksum
        num_events = int(math.ceil(total_num_bytes / 4.0))
        start = time.time()
        data = []
        for e in range(num_events):
            while not self.midi_in.Poll():
                time.sleep(0.1)
                if time.time() - start > timeout:
                    raise TimeoutError("Timed out waiting for sysex data")
            event = self.midi_in.Read(1)
            data.extend(event[0][0])
        if len(data) < total_num_bytes:
            raise InvalidDataError("Incomplete data")
        elif len(data) > total_num_bytes:
            del data[total_num_bytes:]
        self.validate_sysex_msg(data)
        data = data[len(self.sysex_header):-2] # -2 == sysex_footer + checksum
        return data
    def get_sysex_checksum(self, data):
        """Return a checksum on `data`."""
        return sum(data) & 0x7f
    def validate_sysex_msg(self, data):
        """Validate a sysex message."""
        ndata = len(data)
        if data[0:4] != self.sysex_header:
            pass # raise InvalidDataError("Invalid sysex_header %s" % data[0:4])
        elif data[ndata - 1] != self.sysex_footer:
            raise InvalidDataError("Invalid sysex_footer (data %s)" % data)
        elif data[ndata - 2] != self.get_sysex_checksum(data[4:-2]):
            raise InvalidDataError("Invalid checksum (expected %s, got %s)" % (self.get_sysex_checksum(data[4:-2]), data[ndata - 2]))
    def get_state(self):
        """Get the local representation of the RackAttack as a dict."""
        state = {}
        state["GDAT"] = self.gdat
        state["KDAT"] = self.program.kdat
        state["SDAT"] = []
        for sound in self.program.sounds:
            state["SDAT"].append(sound.sdat)
        state["FDAT"] = []
        for effect in self.program.effects:
            state["FDAT"].append(effect.fdat)
        return state
    def print_state(self):
        """Print the local representation of the RackAttack to stdout."""
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(self.get_state())

class Program:
    """A representation of a single program on a `RackAttack`."""
    def __init__(self, rack_attack):
        self.rack_attack = rack_attack
        self.name = ""
        self.kdat = {}
        self.sounds = []
        self.effects = []
        for i in range(24):
            self.sounds.append(Sound(rack_attack, i))
        for i in range(4):
            self.effects.append(Effect(rack_attack, i))
    def get_sound(self, sound_num):
        """Return a `Sound` instance."""
        sound_num = max(min(sound_num, len(self.sounds) - 1), 0)
        return self.sounds[sound_num]
    def get_effect(self, effect_num):
        """Return a `Effect` instance."""
        effect_num = max(min(effect_num, len(self.effects) - 1), 0)
        return self.effects[effect_num]
    def load_from_dump(self, kbytes):
        """Load from a `KDAT` dump."""
        self.kdat = parse_dat(kbytes, KDAT)
        self.name = ""
        for i in range(16):
            self.name += chr(self.kdat["Name_" + str(i)])
    def change_name(self, name):
        """Change name of program."""
        name = "%-16s" % name
        self.name = name[0:16]
        for i in range(16):
            self.change_param("Name_" + str(i), ord(self.name[i:i+1]))
    def change_param(self, param_name, value, do_send_sysex=True):
        """Change PRG param `param_name` to `value`."""
        (pah, pal) = change_dat_param(KDAT, self.kdat, param_name, value)
        if do_send_sysex:
            self.rack_attack.send_sysex([
                # PRGP PRGN PAH PAL PRGV
                0x21, 0x20, pah, pal, self.kdat[param_name]
            ])
    def get_param(self, param_name):
        """Return local value for `param_name`."""
        return self.kdat[param_name]

class Effect:
    """A representation of a single effect in a `Program`."""
    def __init__(self, rack_attack, effect_num):
        self.rack_attack = rack_attack
        self.effect_num = effect_num
        self.fdat = {}
    def load_from_dump(self, fbytes):
        """Load from a `FDAT` dump."""
        self.fdat = parse_dat(fbytes, FDAT)
    def change_param(self, param_name, value, do_send_sysex=True):
        """Change EFX param `param_name` to `value`."""
        (pah, pal) = change_dat_param(FDAT, self.fdat, param_name, value)
        if do_send_sysex:
            self.rack_attack.send_sysex([
                # EFXP BUFN EFXN PAH PAL EFXV
                0x25, 0x20, self.effect_num, pah, pal, self.fdat[param_name]
            ])
    def get_param(self, param_name):
        """Return local value for `param_name`."""
        return self.fdat[param_name]

class Sound:
    """A representation of a single sound in a `Program`."""
    def __init__(self, rack_attack, sound_num):
        self.rack_attack = rack_attack
        self.sound_num = sound_num
        self.sdat = {}
    def load_from_dump(self, sbytes):
        """Load from an `SDAT` dump."""
        self.sdat = parse_dat(sbytes, SDAT)
    def change_param(self, param_name, value, do_send_sysex=True):
        """Change param `param_name` to `value`."""
        (pah, pal) = change_dat_param(SDAT, self.sdat, param_name, value)
        if do_send_sysex:
            self.rack_attack.send_sysex([
                # SNDP BUFN SNDN PAH PAL SNDV
                0x20, 0x20, self.sound_num, pah, pal, self.sdat[param_name]
            ])
    def get_param(self, param_name):
        """Return local value for `param_name`."""
        return self.sdat[param_name]

def change_dat_param(schema, params, param_name, value):
    """Change `param_name` in `params` to `value` given `schema`.
    Return PAH and PAL values for convenience."""
    schema_tuple = None
    for t in schema:
        if t and t[0] == param_name:
            schema_tuple = t
            break
    if not schema_tuple:
        raise InvalidParamError("Unknown param")
    params[param_name] = parse_value(value, schema_tuple)
    return ( schema_tuple[1], schema_tuple[2], )

def parse_dat(bytes, schema):
    """Return a dict of values in `bytes` given a `schema` like `GDAT`,
    `KDAT`, etc."""
    i = 0
    params = {}
    nbytes = len(bytes)
    for schema_tuple in schema:
        if i >= nbytes:
            break
        elif schema_tuple:
            params[schema_tuple[0]] = parse_value(bytes[i], schema_tuple)
        i += 1
    return params

def parse_value(value, schema_tuple):
    """Return a normalized version of `value` given a `schema_tuple` in a
    `GDAT`, `KDAT`, etc. schema."""
    if len(schema_tuple) >= 4:
        constraint = schema_tuple[3]
    else:
        constraint = [0, 127]
    if isinstance(constraint, list):
        value = max(min(value, constraint[1]), constraint[0])
    elif isinstance(constraint, dict):
        if not value in constraint:
            value = constraint.keys()[0]
    elif isinstance(constraint, tuple):
        value = max(min(value, len(constraint) - 1), 0)
    return value

def get_dat(params, schema, len):
    """Generate a dump of type `schema` and length `len` bytes from a param
    map `params`."""
    bytes = [0] * len
    i = 0
    for schema_tuple in schema:
        if schema_tuple:
            bytes[i] = params[schema_tuple[0]]
        i += 1
    return bytes

class TimeoutError(Exception):
    """Raised when a timeout occurred."""
    pass

class InvalidDataError(Exception):
    """Raised when invalid data is received."""
    pass

class InvalidParamError(Exception):
    """Raised when an invalid param is encountered."""
    pass
