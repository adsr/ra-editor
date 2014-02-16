class Editor:

    def __init__(self, rack_attack, editor_view):
        self.rack_attack = rack_attack
        self.editor_view = editor_view

    def run(self):
        self.editor_view.set_observer(self)
        self.editor_view.set_state(self.rack_attack.get_state())
        self.editor_view.run()

    def load_program(self, num):
        self.rack_attack.load_from_device(num)
        self.editor_view.set_state(self.rack_attack.get_state())

    def store_program(self, num):
        print "TODO"

    def init_current_program(self):
        self.rack_attack.init_current_program()
        self.editor_view.set_state(self.rack_attack.get_state())

    def edit_sound(self, cur_sound, param, *L):
        self.rack_attack.get_program().get_sound(cur_sound).change_param(param, int(L[0]))

    def edit_effect(self, cur_effect, param, *L):
        self.rack_attack.get_program().get_effect(cur_effect).change_param(param, int(L[0]))

    def edit_program_name(self, name):
        self.rack_attack.get_program().change_name(name)

    def send_midi(self, msgs):
        self.rack_attack.send_midi(msgs)
