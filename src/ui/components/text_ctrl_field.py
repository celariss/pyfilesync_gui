import re
import flet as ft

class TextCtrlField(ft.Container):
    def __init__(self, textfield:ft.TextField, regex:str=None, error_message:str="Invalid input"):
        self.textfield:ft.TextField = textfield
        self.regex = regex
        self.error_message = error_message
        self.textfield.error_max_lines = 5
        self.textfield.on_change = self.on_change
        self.on_change(ft.Event('change', self.textfield))
        super().__init__(
            content=self.textfield,
            padding=0,
            expand=self.textfield.expand,
        )

    def set_value(self, value):
        self.textfield.value = value
        self.on_change(ft.Event('change', self.textfield))

    def on_change(self, e: ft.Event[ft.TextField]):
        if self.regex and (not re.match(self.regex, e.control.value)):
            self.textfield.error = self.error_message
            self.valid_input = False
        else:
            self.textfield.error = None
            self.valid_input = True