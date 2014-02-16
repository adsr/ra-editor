import random
import rack_attack
import Tkinter as tk
import tkSimpleDialog as tkdialog
import tkFont as tkfont

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
FIFTHS = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]
RELATED_MAJ = [-1, 1]
RELATED_MIN = [2, 4]
PITCHES_MAJ = [0, 4, 7, 11]
PITCHES_MIN = [0, 3, 7, 10]
PITCHES_SUS4 = [0, 5, 7]
ADD_TONES = [i for i in range(-24, 0)] + [i for i in range(1, 25)]

class EditorView(tk.Frame):

    def __init__(self, master):
        self.editor = None
        self.master = master
        self.state = None
        self.sound_group = ItemGroup("SDAT", rack_attack.SDAT)
        self.effect_group = ItemGroup("FDAT", rack_attack.FDAT)
        self.program_name = None
        self.initialized = False
        self.ignore_events = False
        self.play_channel = 0
        self.play_octave = 4
        self.play_add_tone = False
        self.play_velocity_fn = lambda: 100

    def set_observer(self, editor):
        self.editor = editor

    def run(self):
        tk.Frame.__init__(self, self.master)
        self.create_widgets()
        self.grid()
        self.initialized = True
        self.mainloop()

    def create_widgets(self):
        self.master.title("Rack Attack Editor")

        self.program_frame = tk.LabelFrame(self, text="Program")
        self.sound_select_frame = tk.LabelFrame(self, text="Sound Select")
        self.sound_params_frame = tk.LabelFrame(self, text="Sound Params")
        self.effect_select_frame = tk.LabelFrame(self, text="Effect Select")
        self.effect_params_frame = tk.LabelFrame(self, text="Effect Params")
        self.keyboard_frame = tk.LabelFrame(self, text="Keyboard")

        self.create_program_widgets(self.program_frame)
        self.create_keyboard_widgets(self.keyboard_frame)
        self.create_select_widgets(self.sound_select_frame, "Sound", 24, lambda *L: self.select_item(self.sound_group, *L))
        self.create_select_widgets(self.effect_select_frame, "Effect", 4, lambda *L: self.select_item(self.effect_group, *L))
        self.create_params_widgets(self.sound_params_frame, self.sound_group, [21, 23, 20])
        self.create_params_widgets(self.effect_params_frame, self.effect_group, [2, 4, 4, 3])

        self.program_frame.grid(row=0, column=0, sticky=tk.W)
        self.sound_select_frame.grid(row=1, column=0, sticky=tk.W)
        self.effect_select_frame.grid(row=2, column=0, sticky=tk.W)
        self.keyboard_frame.grid(row=0, column=1, rowspan=3, sticky=tk.W)
        self.sound_params_frame.grid(row=3, columnspan=2, sticky=tk.W)
        self.effect_params_frame.grid(row=4, columnspan=2, sticky=tk.W)

    def create_program_widgets(self, frame):
        tk.Label(frame, text="Program").grid(row=0, column=0, sticky=tk.E)
        tk.Button(frame, text="Load...", command=self.load_program).grid(row=0, column=1, sticky=tk.W)
        tk.Button(frame, text="Store...", command=self.store_program).grid(row=0, column=2, sticky=tk.W)
        tk.Button(frame, text="Init...", command=self.init_program).grid(row=0, column=3, sticky=tk.W)
        tk.Label(frame, text="Name").grid(row=1, column=0, sticky=tk.E)
        self.program_name = tk.StringVar()
        tk.Entry(frame, textvariable=self.program_name).grid(row=1, column=1, columnspan=3, sticky=tk.W)
        self.program_name.trace("w", lambda name, index, mode: self.edit_program_name())

    def create_select_widgets(self, frame, caption, num, fn):
        ScaleEx(self, frame, (caption, None, None, [1, num], ), command=fn).grid(sticky=tk.W)

    def create_params_widgets(self, frame, item_group, cutoffs):
        item_group.widgets = {}
        widgets = item_group.widgets
        row = 0
        col = 0
        default_cutoff = cutoffs[len(cutoffs) - 1]
        cutoff_i = 0
        def make_param_widget(stuple, frame, row, col):
            widgets[stuple[0]] = ScaleEx(self, frame, stuple, command=lambda *L: self.edit_item_param(item_group, stuple[0], *L))
            widgets[stuple[0]].grid(row=row, column=col, sticky=tk.W)
        for stuple in item_group.tuples:
            if stuple:
                make_param_widget(stuple, frame, row, col)
                row += 1
                if row >= (cutoffs[cutoff_i] if cutoff_i < len(cutoffs) else default_cutoff):
                    row = 0
                    col += 1
                    cutoff_i += 1

    def create_keyboard_widgets(self, frame):
        ScaleEx(self, frame, ("Channel", None, None, [1, 16], ), command=self.set_channel).grid(row=0, sticky=tk.W)
        octave_widget = ScaleEx(self, frame, ("Octave", None, None, [-1, 8], ), command=self.set_octave)
        octave_widget.set_value(self.play_octave)
        octave_widget.grid(row=1, sticky=tk.W)
        ScaleEx(self, frame, ("Velocity", None, None, ("Normal", "Lo", "Hi", "Random", ), ), command=self.set_velocity).grid(row=2, sticky=tk.W)
        ScaleEx(self, frame, ("Add tone", None, None, tuple(["Off"] + [str(i) for i in ADD_TONES]), ), command=self.set_add_tone).grid(row=3, sticky=tk.W)
        col = 1
        small_font = tkfont.Font(family="TkDefaultFont", size=6)
        def make_note_button(caption, note, pitches, row, col):
            btn = tk.Button(frame, text=caption, height=1, font=small_font)
            btn.bind("<Button-1>", lambda e: self.play_notes(note, pitches, e))
            btn.bind("<ButtonRelease-1>", lambda e: self.play_notes(note, pitches, e, off=True))
            btn.grid(row=row, column=col, sticky=tk.W)
        for fifth_i in range(len(FIFTHS)):
            note = FIFTHS[fifth_i]
            row = 0
            note_name = NOTES[note]
            make_note_button(note_name, note, [0], row, col)
            row += 1
            make_note_button(note_name + "maj", note, PITCHES_MAJ, row, col)
            row += 1
            for delta in RELATED_MAJ:
                rel_i = (fifth_i + delta) % 12
                make_note_button(NOTES[FIFTHS[rel_i]] + "maj", FIFTHS[rel_i], PITCHES_MAJ, row, col)
                row += 1
            for delta in RELATED_MIN:
                rel_i = (fifth_i + delta) % 12
                make_note_button(NOTES[FIFTHS[rel_i]] + "min", FIFTHS[rel_i], PITCHES_MIN, row, col)
                row += 1
            make_note_button(note_name + "sus4", note, PITCHES_SUS4, row, col)
            row += 1
            make_note_button(note_name + "min", note, PITCHES_MIN, row, col)
            col += 1

    def set_channel(self, *L):
        self.play_channel = int(L[0]) - 1

    def set_octave(self, *L):
        self.play_octave = int(L[0])

    def set_velocity(self, *L):
        vel = int(L[0])
        if vel == 0:
            self.play_velocity_fn = lambda: 100
        elif vel == 1:
            self.play_velocity_fn = lambda: 30
        elif vel == 2:
            self.play_velocity_fn = lambda: 127
        else:
            self.play_velocity_fn = lambda: random.randint(1, 127)

    def set_add_tone(self, *L):
        val = int(L[0])
        if val == 0:
            self.play_add_tone = None
        else:
            self.play_add_tone = ADD_TONES[val - 1]

    def play_notes(self, note, pitches, event, off=False):
        msgs = []
        root = note + ((self.play_octave + 1) * 12)
        vel = 0 if off else self.play_velocity_fn()
        cmd = (0x80 if off else 0x90) + self.play_channel
        for p in pitches:
            msgs.append((cmd, root + p, vel, ))
        if self.play_add_tone:
            msgs.append((cmd, root + self.play_add_tone, vel, ))
        self.editor.send_midi(msgs)

    def init_program(self):
        ig = tkdialog.askstring("Init current program on RackAttack", "Confirm by clicking OK.")
        if ig is None:
            return
        self.editor.init_current_program()

    def load_program(self):
        num = tkdialog.askinteger("Load program from RackAttack", "Enter program number (1-50) or 0 for current.")
        if num is None:
            return
        self.editor.load_program(num)

    def store_program(self):
        num = tkdialog.askinteger("Store program on RackAttack", "Enter program number (1-50) or 0 for current.")
        if num is None:
            return
        self.editor.store_program(num)

    def set_state(self, state):
        self.state = state
        if not self.initialized:
            return
        self.ignore_events = True
        self.update_widgets(self.sound_group)
        self.update_widgets(self.effect_group)
        self.update_program_name()
        self.update_effect_labels()
        self.update()
        self.ignore_events = False

    def edit_program_name(self):
        if self.ignore_events:
            return
        self.editor.edit_program_name(self.program_name.get())

    def update_program_name(self):
        name = ""
        for i in range(16):
            i = self.state["KDAT"]["Name_" + str(i)]
            name += chr(i)
        name = name.strip()
        self.program_name.set(name)

    def update_widgets(self, item_group):
        dat_key = item_group.dat_key
        widgets = item_group.widgets
        item_num = item_group.cur_item
        for param in self.state[dat_key][item_num]:
            scale_widget = widgets[param]
            scale_widget.set_value(self.state[dat_key][item_num][param])

    def select_item(self, item_group, *L):
        num = int(L[0]) - 1
        item_group.cur_item = num
        self.ignore_events = True
        self.update_widgets(item_group)
        self.update_effect_labels()
        self.update()
        self.ignore_events = False

    def edit_item_param(self, item_group, param, *L):
        num = item_group.cur_item
        self.state[item_group.dat_key][num][param] = int(L[0])
        if item_group == self.sound_group:
            self.editor.edit_sound(num, param, *L)
        else:
            self.editor.edit_effect(num, param, *L)
            if param == "Type":
                self.update_effect_labels()

    def update_effect_labels(self):
        fx_num = int(self.state[self.effect_group.dat_key][self.effect_group.cur_item]["Type"])
        param_num = 1
        for label in rack_attack.FPARAMS[fx_num]:
            label_text = label if label else "N/A"
            self.effect_group.widgets["Param" + str(param_num)].set_label(label_text)
            param_num += 1

class ScaleEx:
    def __init__(self, editor_view, parent, stuple, command=None):
        self.frame = tk.Frame(parent)
        self.editor_view = editor_view
        constraint = stuple[3] if len(stuple) > 3 else [0, 127]
        self.display_value_var = tk.StringVar()
        self.label_value_var = tk.StringVar()
        self.constraint = constraint
        self.command = command
        self.param_name = stuple[0]
        self.schema_tuple = stuple
        self.first_set_value = True
        if isinstance(constraint, list):
            scale_from = constraint[0]
            scale_to = constraint[1]
        elif isinstance(constraint, tuple):
            scale_from = 0
            scale_to = len(constraint) - 1
        elif isinstance(constraint, dict):
            scale_from = min(constraint.keys)
            scale_to = max(constraint.keys)
        scale_kwargs = {
            "from_": scale_from,
            "to": scale_to,
            "orient": tk.HORIZONTAL,
            "command": self.handle_command,
            "showvalue": 0,
        }
        self.label_value_var.set(stuple[0])
        self.label = tk.Label(self.frame, textvariable=self.label_value_var, width=18, height=1, anchor=tk.SE)
        self.scale = tk.Scale(self.frame, **scale_kwargs)
        self.display_value = tk.Label(self.frame, textvariable=self.display_value_var, width=8)
        self.label.grid(row=0, column=0, sticky=tk.W)
        self.scale.grid(row=0, column=1, sticky=tk.W)
        self.display_value.grid(row=0, column=2, sticky=tk.W)

    def handle_command(self, *L):
        self.display_value_var.set(self.get_display_value())
        if self.first_set_value:
            self.first_set_value = False
        elif self.command and not self.editor_view.ignore_events:
            self.command(*L)

    def get_display_value(self):
        val = rack_attack.parse_value(self.scale.get(), self.schema_tuple)
        if isinstance(self.constraint, list):
            pass
        elif isinstance(self.constraint, tuple):
            val = self.constraint[val]
        elif isinstance(constraint, dict):
            val = self.constraint[val]
        return str(val)

    def set_value(self, val):
        self.scale.set(val)

    def set_label(self, val):
        self.label_value_var.set(val)

    def __getattr__(self, attr):
        def default_method(*args, **kwargs):
            getattr(self.frame, attr)(*args, **kwargs)
        return default_method

class ItemGroup:
    def __init__(self, dat_key, tuples):
        self.dat_key = dat_key
        self.cur_item = 0
        self.tuples = tuples
        self.widgets = {}
