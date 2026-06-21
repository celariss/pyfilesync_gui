import re
import flet as ft

class TextCtrlField(ft.Container):
    def __init__(self, textfield:ft.TextField, regex:str=None, error_message:str="Invalid input", on_validate_entry=None):
        """A wrapper around a TextField that adds regex validation and error display.
        Args:
            textfield (ft.TextField): The TextField to wrap.
            regex (str, optional): A regular expression that the input must match. Defaults to None.
            error_message (str, optional): The error message to display if validation fails. Defaults to "Invalid input".
            on_validate_entry (callable, optional): A callback function that takes the current value and returns None if it's valid,
                                                    or a string containing the error message. Overrides regex and error_messageif provided. Defaults to None.
        """
        self.textfield:ft.TextField = textfield
        self.regex = regex
        self.error_message = error_message
        self.on_validate_entry = on_validate_entry
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
        if self.on_validate_entry and callable(self.on_validate_entry):
            error = self.on_validate_entry(e.control.value)
            if error:
                self.textfield.error = error
                self.valid_input = False
                return
        elif self.regex:
            if not re.match(self.regex, e.control.value):
                self.textfield.error = self.error_message
                self.valid_input = False
                return
        
        self.textfield.error = None
        self.valid_input = True