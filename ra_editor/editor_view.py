import Tkinter as tk
import rack_attack
import tkSimpleDialog as tkdialog

class EditorView(tk.Frame):

    def __init__(self, master=None):
        self.editor = None
        self.master = master
        self.cur_sound_num = 1
        self.state = None

    def set_observer(self, editor):
        self.editor = editor

    def run(self):
        tk.Frame.__init__(self, self.master)
        self.create_widgets()
        self.grid()
        self.mainloop()

    def create_widgets(self):
        self.master.title("Rack Attack Editor")

        self.program_frame = tk.LabelFrame(self, text="Program")
        self.soundselect_frame = tk.LabelFrame(self, text="Sound")
        self.params_frame = tk.LabelFrame(self, text="Params")

        self.create_program_widgets(self.program_frame)
        self.create_soundselect_widgets(self.soundselect_frame)
        self.create_params_widgets(self.params_frame)

        self.program_frame.grid(row=0, sticky=tk.W)
        self.soundselect_frame.grid(row=1, sticky=tk.W)
        self.params_frame.grid(row=2, sticky=tk.W)

    def create_program_widgets(self, frame):
        tk.Label(frame, text="Program").grid(row=0, column=0, sticky=tk.E)
        tk.Button(frame, text="Load...", command=self.load_program).grid(row=0, column=1, sticky=tk.W)
        tk.Button(frame, text="Store...", command=self.store_program).grid(row=0, column=2, sticky=tk.W)

        tk.Label(frame, text="Name").grid(row=1, column=0, sticky=tk.E)
        tk.Entry(frame).grid(row=1, column=1, columnspan=2, sticky=tk.W)

    def create_soundselect_widgets(self, frame):
        ScaleEx(frame, ("Sound", None, None, [1, 24], ), command=self.switch_sound).grid(sticky=tk.W)

    def create_params_widgets(self, frame):
        self.params_widgets = {}
        row = 0
        col = 0
        cutoffs = [21, 23, 20]
        default_cutoff = 20
        cutoff_i = 0
        for stuple in rack_attack.SDAT:
            if stuple:
                constraint = stuple[3] if len(stuple) > 3 else [0, 127]
                self.params_widgets[stuple[0]] = ScaleEx(frame, stuple, command=self.editor.edit_sound).grid(row=row, column=col, sticky=tk.W)
                row += 1
                if row >= (cutoffs[cutoff_i] if cutoff_i < len(cutoffs) else default_cutoff):
                    row = 0
                    col += 1
                    cutoff_i += 1

    def load_program(self):
        num = tkdialog.askinteger("Load program", "Enter program number (1-50) or 0 for current.")
        if num is None:
            return
        self.editor.load_program(num)

    def store_program(self):
        num = tkdialog.askinteger("Store program", "Enter program number (1-50).")
        if num is None:
            return
        self.editor.store_program(num)

    def switch_sound(self, *L):
        self.cur_sound_num = int(L[0])
        self.set_sound(self.cur_sound_num)

    def update_state(self, state):
        self.state = state
        self.set_sound(self.cur_sound_num)

    def set_sound(self, sound_num):
        sound_num -= 1
        if not "SDAT" in self.stat:
            return
        for param in self.state["SDAT"][sound_num]:
            self.params_widgets[param].set_value(self.state["SDAT"][sound_num][param])

class ScaleEx:
    def __init__(self, parent, stuple, command=None):
        self.frame = tk.Frame(parent)
        constraint = stuple[3] if len(stuple) > 3 else [0, 127]
        self.display_value_var = tk.StringVar()
        self.constraint = constraint
        self.command = command
        self.schema_tuple = stuple
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
        self.label = tk.Label(self.frame, text=stuple[0], width=18, height=1, anchor=tk.SE)
        self.scale = tk.Scale(self.frame, **scale_kwargs)
        self.display_value = tk.Label(self.frame, textvariable=self.display_value_var, width=8)
        self.label.grid(row=0, column=0, sticky=tk.W)
        self.scale.grid(row=0, column=1, sticky=tk.W)
        self.display_value.grid(row=0, column=2, sticky=tk.W)

    def handle_command(self, *L):
        self.display_value_var.set(self.get_display_value())
        if self.command:
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

    def __getattr__(self, attr):
        def default_method(*args, **kwargs):
            getattr(self.frame, attr)(*args, **kwargs)
        return default_method
