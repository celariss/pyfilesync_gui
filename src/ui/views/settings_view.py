import flet as ft

from core.app_controller import AppController
from ui.components.text_ctrl_field import TextCtrlField

class SettingsView(ft.View):
    def __init__(self, controller:AppController, pair_index=None):
        self.controller:AppController = controller
        if pair_index is None:
             title="Paramètres du projet"
             self.config_target = self.controller.config.globalconfig
        else:
             title="Paramètres de la paire de dossier '"+controller.config.pairs[pair_index].name+"'"
             self.config_target = self.controller.config.pairs[pair_index]

        # References
        self.history_mode_enabled = ft.Ref[ft.Checkbox]()
        self.history_mode_depth_ref = ft.Ref[ft.TextField]()
        self.history_mode_file_max_saved_size_ref = ft.Ref[ft.TextField]()
        
        super().__init__(
            route="/settings",
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.SafeArea(
                    content=ft.Column(
                        controls=[
                            self._build_main_toolbar(title),
                            ft.Column(
                                expand=True,
                                spacing=10,
                                controls=[
                                    self._build_section("Paramètres de comparaison", [
                                         self._build_boolean_field("Comparer le contenu des fichiers", "cmp_files_content"),
                                    ]),
                                    self._build_section("Filtres", [
                                        self._build_text_field("Patterns à inclure", "include"),
                                        self._build_text_field("Patterns à exclure", "exclude"),
                                        self._build_text_field("Expressions régulières à inclure", "include_regex"),
                                        self._build_text_field("Expressions régulières à exclure", "exclude_regex"),
                                    ]),
                                    self._build_section("Sauvegarde automatique (historique) des fichiers", [
                                        self._build_boolean_field("Activer la sauvegarde auto",
                                                                  value=getattr(self.config_target, "history_mode_depth")>0,
                                                                  on_change=self._on_change_history_mode,
                                                                  ref=self.history_mode_enabled
                                        ),
                                        self._build_positive_int_field("Profondeur maximale", "history_mode_depth", ref=self.history_mode_depth_ref),
                                        self._build_positive_int_field("Taille maximale de l'historique d'un fichier", "history_mode_file_max_saved_size", ref=self.history_mode_file_max_saved_size_ref),
                                    ]),
                                ]
                            )
                        ]
                    )
                )
            ]
        )
        self._on_change_history_mode(getattr(self.config_target, "history_mode_depth")>0)

    def on_view_hidden(self):
        if not self.history_mode_enabled.current.value:
            setattr(self.config_target, "history_mode_depth", 0)

    def _on_change_history_mode(self, value:bool):
        if value:
            self.history_mode_depth_ref.current.disabled = False
            self.history_mode_file_max_saved_size_ref.current.disabled = False
        else:
            self.history_mode_depth_ref.current.disabled = True
            self.history_mode_file_max_saved_size_ref.current.disabled = True

    def _build_section(self, title, controls):
        return ft.Column(
            spacing=5,
            controls=[
                ft.Text(title, weight=ft.FontWeight.BOLD),
                ft.Divider(height=5),
                ft.Column(
                    spacing=5,
                    controls=controls
                )
            ]
        )
    
    def _build_text_field(self, label, field_name, regex=None, error_msg=None, ref=None):
        init_value=getattr(self.config_target, field_name)
        multiline = isinstance(init_value, list)
        if multiline:
            init_value = '\n'.join(init_value)
        
        async def on_blur(e: ft.Event[ft.TextField]):
            if name_field.valid_input:
                if isinstance(init_value,int):
                    value = int(e.control.value)
                else:
                    value = e.control.value
                    if multiline:
                        value = e.control.value.split('\n')
                setattr(self.config_target, field_name, value)

        name_field:TextCtrlField = TextCtrlField(
            textfield=ft.TextField(
                label=label,
                ref=ref,
                value=str(init_value),
                on_blur=on_blur,
                multiline=multiline,
                expand=True
            ),
            regex=regex,
            error_message=error_msg
        )

        return ft.Row(
            margin=ft.Margin.only(right=20),
            controls=[
                name_field,
                ft.CircleAvatar(
                    tooltip='TEST',
                    bgcolor=ft.Colors.SECONDARY,
                    radius=11,
                    content=ft.Icon(
                        ft.Icons.QUESTION_MARK,
                        color=ft.Colors.SHADOW,
                        size=15,
                    ),
                )
            ]
        )
    
    def _build_positive_int_field(self, label, field_name, ref=None):
        return self._build_text_field(
            label=label,
            field_name=field_name,
            regex="^\\d{1,}$",
            error_msg="un entier positif est attendu",
            ref=ref
        )
    
    def _build_boolean_field(self, label, field_name=None, value=None, on_change=None, ref=None):
        if value is not None:
            init_value = value
        else:
            init_value=getattr(self.config_target, field_name)
        
        async def on_change_(e: ft.Event[ft.Checkbox]):
            if field_name:
                setattr(self.config_target, field_name, e.control.value)
            if on_change:
                on_change(e.control.value)

        return ft.Checkbox(
            label=label,
            value=init_value,
            ref=ref,
            on_change=on_change_,
            label_position=ft.LabelPosition.LEFT
        )

    def _build_main_toolbar(self, title):
        return ft.AppBar(
            title=ft.Text(title),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        )