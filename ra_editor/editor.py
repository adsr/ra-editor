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
        print num

    def edit_sound(self, cur_sound, param, *L):
        print cur_sound, param, L
