import asyncio
from functools import partial
import flet as ft

from ui.components.folderpairs import FolderPairs
from ui.components.results_list import ResultsList
from core.app_controller import AppController
from ui.ui_interface import *


class MainView(ft.View, UIInterface):

    def __init__(self, controller:AppController):
        self.controller:AppController = controller
        self.resultslist:ResultsList = ResultsList()
        self.folderpairs:FolderPairs = FolderPairs(self.controller)
        self.load_popupmenu:ft.SubmenuButton = None
        self.main_toolbar:ft.AppBar = self._build_main_toolbar()
        super().__init__(
            route="/",
            controls=[
                ft.SafeArea(
                    expand=True,
                    content=ft.Column(
                        expand=True,
                        controls=[
                            self.main_toolbar,
                            ft.Column(
                                expand=True,
                                spacing=10,
                                controls=[
                                    self._build_project_toolbar(),
                                    self._build_folders_section(),
                                    self.resultslist,
                                ]
                            )
                        ]
                    )
                )
            ]
        )

    def show_error(self, message:str):
        self.page.show_dialog(ft.SnackBar(ft.Text(message, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.RED_ACCENT, duration=5000))

    def update_title(self):
        self.page.title = f"Synchroniseur - {self.controller.get_config_path() or 'Nouveau projet'}"
        self.main_toolbar.title = os.path.basename(self.controller.get_config_path()) if self.controller.get_config_path() else 'Nouveau projet'
    
    #Implementation of UIInterface methods#
    def refresh(self):
        self.update_title()
        self.load_popupmenu.controls = self._build_load_menu_items()
        self.page.update()

    def set_config_data(self, config:SyncConfig):
        self.folderpairs.set_config(config)

    def clear_results(self):
        self.resultslist.clear()

    def refresh_results(self):
        self.resultslist.refresh()

    def append_result(self, item: ResultItem):
        self.resultslist.append_result(item)
    #ENDOF Implementation of UIInterface methods#

    def build(self):
        self.update_title()
        super().build()
        self.folderpairs.set_page(self.page)

    """ def _build_load_menu_items(self) -> list:
        async def load_config_file(e: ft.Event[ft.Button], path:str):
            asyncio.create_task(self.controller.load_config_file(path))

        async def remove_item(e: ft.Event[ft.Button], path:str):
            asyncio.create_task(self.controller.remove_recent_file(path))

        items = []
        items.append(ft.PopupMenuItem("Choisir...", on_click=self._choose_config_file))
        for path in self.controller.recent_files:
            t:ft.PopupMenuItem = ft.PopupMenuItem(
                content = ft.Row(
                    tight=True,
                    expand=False,
                    controls=[
                        ft.Text(path,expand=10),
                        ft.IconButton(
                            ft.Icons.CANCEL,
                            align=ft.Alignment.CENTER_RIGHT,
                            on_click=partial(remove_item, path=path)
                        ),
                    ]
                ),
                on_click=partial(load_config_file, path=path)
            )
            items.append(t)
        return items """
    
    def _build_load_menu_items(self) -> list:
        async def load_config_file(e: ft.Event[ft.Button], path:str):
            asyncio.create_task(self.controller.load_config_file(path))

        async def remove_item(e: ft.Event[ft.Button], path:str):
            asyncio.create_task(self.controller.remove_recent_file(path))

        items = []
        items.append(ft.MenuItemButton(content=ft.Text("Choisir..."), on_click=self._choose_config_file))
        for path in self.controller.recent_files:
            t:ft.MenuItemButton = ft.MenuItemButton(
                content = ft.Row(
                    tight=True,
                    expand=False,
                    controls=[
                        ft.Text(path,expand=10),
                        ft.IconButton(
                            ft.Icons.CANCEL,
                            align=ft.Alignment.CENTER_RIGHT,
                            on_click=partial(remove_item, path=path)
                        ),
                    ]
                ),
                on_click=partial(load_config_file, path=path)
            )
            items.append(t)
        return items
    
    def _build_main_toolbar(self):
        icon_size = 32
        self.load_popupmenu = ft.SubmenuButton(
            content=ft.Icon(icon=ft.Icons.FILE_OPEN, size=icon_size-2, align=ft.Alignment.CENTER),
            tooltip="Ouvrir un projet",
            controls=self._build_load_menu_items()
        )
        return ft.AppBar(
            #title=ft.Text("Main"),
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            actions = [
                ft.MenuBar(
                    
                    style=ft.MenuStyle(bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST),
                    controls=[
                        self.load_popupmenu,
                        ft.SubmenuButton(content=ft.IconButton(icon=ft.Icons.NEW_LABEL, tooltip="Nouveau", icon_color=ft.Colors.SECONDARY, icon_size=icon_size, on_click=self._new_project)),
                        ft.SubmenuButton(content=ft.IconButton(icon=ft.Icons.SAVE, tooltip="Enregistrer", icon_color=ft.Colors.SECONDARY, icon_size=icon_size, on_click=self._save_config_file)),
                        ft.SubmenuButton(content=ft.IconButton(icon=ft.Icons.SAVE_AS, tooltip="Enregistrer sous", icon_color=ft.Colors.SECONDARY, icon_size=icon_size, on_click=self._save_as_config_file)),
                    ]
                )
            ]
        )
    
    async def _new_project(self, e: ft.Event[ft.Button]):
        await self.controller.new_project()

    async def _choose_config_file(self, e: ft.Event[ft.Button]):
        files = await ft.FilePicker().pick_files(allow_multiple=False)
        if files:
            asyncio.create_task(self.controller.load_config_file(files[0].path))

    async def _save_as_config_file(self, e: ft.Event[ft.Button]):
        file = await ft.FilePicker().save_file()
        if file:
            asyncio.create_task(self.controller.save_config_file(file))

    async def _save_config_file(self, e: ft.Event[ft.Button]):
        config_path = self.controller.get_config_path()
        if not config_path:
            await self._save_as_config_file(e)
        else:
            asyncio.create_task(self.controller.save_config_file(config_path))
    
    def _build_project_toolbar(self):
        return ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icon(ft.Icons.SYNC_LOCK),
                    tooltip="Lancer la comparaison (projet entier)",
                    on_click=lambda _:  asyncio.create_task(self.controller.run_compare())
                ),
                ft.IconButton(
                    icon=ft.Icon(ft.Icons.PLAY_ARROW),
                    tooltip="Lancer la synchronisation (projet entier)",
                    on_click=lambda _:  asyncio.create_task(self.controller.run_sync())
                ),
                ft.IconButton(
                    icon=ft.Icon(ft.Icons.SETTINGS),
                    tooltip="Paramètres du projet",
                    on_click=self._show_project_settings
                ),
                ft.Text("", expand=True),
                ft.IconButton(
                    alignment=ft.Alignment.CENTER_LEFT,
                    expand=0,
                    icon=ft.Icon(ft.Icons.ADD),
                    tooltip="Ajouter une ligne",
                    on_click=lambda _:  asyncio.create_task(self.controller.add_folders_pair()),
                ),
            ]
        )
    
    def _build_folders_section(self):
        return ft.Container(
            height=220,
            border=ft.Border.all(1),
            content=self.folderpairs.build()
        )

    async def _show_project_settings(self, e: ft.Event[ft.Button]):
        await self.page.push_route("/settings")