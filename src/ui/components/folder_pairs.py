import asyncio

import flet as ft

from syncconfig import *
from core.app_controller import AppController
from ui.components.text_ctrl_field import TextCtrlField

class FolderPairs:
    def __init__(self, controller:AppController):
        self.controller:AppController = controller
        self.config = SyncConfig()
        self.list_view = ft.ListView(
                spacing=2,
                expand=True,
                controls=[]
            )
        
    def set_page(self, page:ft.Page):
        self.page = page

    def set_config(self, config:SyncConfig):
        self.config = config
        self.list_view.controls.clear()
        self.list_view.controls.extend([ self._folder_row(pair, idx) for idx, pair in enumerate(self.config.pairs) ])
        self.list_view.update()

    def build(self):
        self.list_view.controls.clear()
        self.list_view.controls.extend([ self._folder_row(pair, idx) for idx, pair in enumerate(self.config.pairs) ])
        return self.list_view
    
    def _folder_row(self, pair:PairSection, pair_index:int):
        async def change_path(e: ft.Event[ft.TextField]):
            if e.control.data == 'left':
                pair.left = e.control.value
            else:
                pair.right = e.control.value
            asyncio.create_task(self.controller.change_pair(pair_index, pair))

        async def change_name(e: ft.Event[ft.TextField]):
            if not name_field.valid_input:
                name_field.set_value(pair.name)
            else:
                pair.name = e.control.value
                asyncio.create_task(self.controller.change_pair(pair_index, pair))
        
        async def choose_path(e: ft.Event[ft.Button]):
            await self._choose_path(e, e.control.data, pair, pair_index)
        
        async def run_compare(e: ft.Event[ft.Button]):
            asyncio.create_task(self.controller.run_compare(pair_index))

        async def run_sync(e: ft.Event[ft.Button]):
            asyncio.create_task(self.controller.run_sync(pair_index))

        async def on_show_pair_settings(e: ft.Event[ft.Button]):
            await self.page.push_route(f"/settings[{pair_index}]")

        async def on_remove_pair(e: ft.Event[ft.Button]):
            asyncio.create_task(self.controller.remove_folders_pair(pair_index))

        name_field:TextCtrlField = TextCtrlField(
            textfield=ft.TextField(
                value=pair.name,
                expand=1,
                on_blur=change_name,
            ),
            regex="^[A-Za-z0-9_-]*$",
            error_message="pair names may only contain '-', '_' and alphanumeric characters"
        )

        return ft.Row(
            alignment=ft.MainAxisAlignment.START,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.SYNC_LOCK,
                    tooltip="Lancer la comparaison",
                    on_click=run_compare,
                ),
                ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW,
                    tooltip="Lancer la synchronisation",
                    on_click=run_sync,
                    visible=False,
                ),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    tooltip="Paramètres",
                    on_click=on_show_pair_settings,
                ),
                ft.Text("Nom :"),
                name_field,
                ft.Text("Dossier gauche :"),
                ft.IconButton(
                    data='left',
                    icon=ft.Icons.FOLDER_OPEN,
                    tooltip="Choisir le dossier gauche",
                    on_click=choose_path
                ),
                ft.TextField(
                    data='left',
                    value=pair.left,
                    expand=2,
                    on_blur=change_path
                ),
                ft.Text("Dossier droit :"),
                ft.IconButton(
                    data='right',
                    icon=ft.Icons.FOLDER_OPEN,
                    tooltip="Choisir le dossier droit",
                    on_click=choose_path
                ),
                ft.TextField(
                    data='right',
                    value=pair.right,
                    expand=2,
                    on_blur=change_path
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE, tooltip="Supprimer la ligne",
                    on_click=on_remove_pair
                ),
            ]
        )
    
    async def _choose_path(self, e: ft.Event[ft.Button], side:str, pair:PairSection, pair_index:int):
        init_dir = pair.left if side == 'left' else pair.right
        old_init_dir = None
        while not os.path.exists(init_dir) and init_dir != '' and old_init_dir != init_dir:
            old_init_dir = init_dir
            init_dir = os.path.dirname(init_dir)
        if init_dir == '' or old_init_dir == init_dir:
            init_dir = None
        path = await ft.FilePicker().get_directory_path(initial_directory=init_dir)
        if path:
            if side == 'left':
                pair.left = path
            else:
                pair.right = path
            asyncio.create_task(self.controller.change_pair(pair_index, pair))