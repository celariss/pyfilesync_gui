import asyncio
from functools import partial
import flet as ft

from ui.components.folder_pairs import FolderPairs
from ui.components.listviewex import *
from ui.components.results_list import ResultsList
from core.app_controller import AppController
from ui.ui_interface import *
from ui.ui_common import *


class MainView(ft.View, UIInterface):

    def __init__(self, controller:AppController, app_version:str):
        self.app_version = app_version
        self.controller:AppController = controller
        self.cmp_results_list:ResultsList = ResultsList()
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
                                    ft.ExpansionPanelList(
                                        expand=True,
                                        scroll=ft.ScrollMode.AUTO,
                                        controls=[
                                            self._build_folders_panel(),
                                            self._build_warning_panel(),
                                            self._build_compare_panel(),
                                            self._build_sync_log_panel(),
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                )
            ]
        )

    def show_error_snackbar(self, message:str):
        self.page.show_dialog(ft.SnackBar(ft.Text(message, weight=ft.FontWeight.BOLD), bgcolor=ft.Colors.RED_ACCENT, duration=5000))

    def show_error_banner(self, message:str):
        def close(e):
            banner.open = False
            self.page.update()

        banner = ft.Banner(
            bgcolor=ft.Colors.AMBER_100,
            leading=ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.AMBER, size=40),
            content=ft.Text(
                message,
                color="black"
            ),
            actions=[
                ft.Button(content="OK", on_click=close),
            ],
        )
        self.page.show_dialog(banner)
        self.page.update()

    def update_title(self):
        self.page.title = f"Synchroniseur v{self.app_version} - {self.controller.get_config_path() or 'Nouveau projet'}"
        self.main_toolbar.title = ft.Text(
            value=os.path.basename(self.controller.get_config_path()) if self.controller.get_config_path() else 'Nouveau projet',
            weight=ft.FontWeight.BOLD,
        )
    
    #Implementation of UIInterface methods#
    def show_error(self, message:str):
        self.show_error_banner(message)
        
    def refresh(self):
        self.update_title()
        self.load_popupmenu.controls = self._build_load_menu_items()
        self.page.update()

    def set_config_data(self, config:SyncConfig):
        self.folderpairs.set_config(config)

    def clear_cmp_results(self):
        self.cmp_results_list.clear()
        self.cmp_results_list.update()
        self.run_sync_btn.disabled = True

    def clear_sync_results(self):
        self.sync_results_list.clear()
        self.sync_results_list.update()

    def clear_cmp_errors(self):
        self.errors_list.controls.clear()
        self.errors_list.update()
        self._update_warning_title()
        self._expand_panel(self.errors_panel, False)

    def refresh_results(self):
        self.cmp_results_list.update()
    
    def on_start_compare(self):
        self._expand_panel(self.errors_panel, False)
        self._expand_panel(self.compare_panel, True)
        self._expand_panel(self.sync_panel, False)

    def on_start_sync(self):
        self._expand_panel(self.errors_panel, False)
        self._expand_panel(self.compare_panel, False)
        self._expand_panel(self.sync_panel, True)

    def append_cmp_result(self, item: ResultItem):
        self.cmp_results_list.append_result(item)
        self.run_sync_btn.disabled = False
        self.run_sync_btn.update()

    def append_warning(self, text:str, target:str, is_warning:bool):
        self.errors_list.controls.append(
            ft.Row(
                spacing=0,
                controls=[
                    ft.Container(
                        expand=1,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Icon(
                            ft.Icons.WARNING if is_warning else ft.Icons.ERROR_OUTLINE,
                            color=ft.Colors.ORANGE if is_warning else ft.Colors.RED,
                        )
                    ),
                    ft.Container(
                        expand=5,
                        padding=5,
                        #tooltip=tooltip,
                        content=ft.Text(
                            target,
                            no_wrap=True,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            size=13,
                        )
                    ),
                    ft.Container(
                        expand=10,
                        padding=5,
                        #tooltip=tooltip,
                        content=ft.Text(
                            text,
                            no_wrap=True,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            size=13,
                        )
                    ),
                ]
            )
        )
        self._expand_panel(self.errors_panel, True)
        self.errors_panel.update()
        self._update_warning_title()

    def append_sync_result(self, action:str, filepath:str, leftdir:str, rightdir:str):
        asyncio.create_task(self._append_sync_result(action, filepath, leftdir, rightdir))

    async def _append_sync_result(self, action:str, filepath:str, leftdir:str, rightdir:str):
        self._expand_panel(self.compare_panel, False)
        self._expand_panel(self.sync_panel, True)
        display_action = None
        weight = ft.FontWeight.BOLD
        left = ''
        right = ''
        if action == 'start_deleting':
            display_action = "Suppression des fichiers côté droit ..."
            right = rightdir
        elif action == 'start_copying':
            display_action = "Copie des fichiers ..."
            left = leftdir
            right = rightdir
        elif action == 'start_updating':
            display_action = "Mise à jour des fichiers ..."
            left = leftdir
            right = rightdir
        else:
            weight = ft.FontWeight.NORMAL
            filepath = '.'+os.path.sep+filepath
            if action == 'delete':
                display_action = "Suppression de"
                right = filepath
            elif action == 'copy':
                display_action = "Copie de"
                left = filepath
                right = filepath
            elif action == 'update':
                display_action = "Mise à jour de"
                left = filepath
                right = filepath

        if display_action:
            self.sync_results_list.append_row(
                [
                    (display_action, display_action),
                    (f'  | {left}', left),
                    (f'  | {right}', right),
                ],
                weight=weight,
            )
            self.sync_results_list.update()
    #ENDOF Implementation of UIInterface methods#

    async def sync_from_results_list(self):
        items:list[ResultItem] = []
        for row in self.cmp_results_list.listview.controls:
            if row.content.data.include:
                items.append(row.content.data)
        if items:
            await self.controller.run_sync_items(items)

    def _update_warning_title(self):
        self.errors_title.value = f"Avertissements ({len(self.errors_list.controls)})"
        if self.errors_list.controls:
            self.errors_title.color = ft.Colors.RED
        else:
            self.errors_title.color = PANEL_TEXT_COLOR
        self.errors_panel.update()

    def _expand_panel(self, panel:ft.ExpansionPanel, expanded:bool):
        if expanded != panel.expanded:
            panel.expanded = expanded
            panel.update()

    def build(self):
        self.update_title()
        super().build()
        self.folderpairs.set_page(self.page)
    
    def _build_load_menu_items(self) -> list:
        async def load_config_file(e: ft.Event[ft.Button], path:str):
            errors:list = await self.controller.load_config_file(path)
            if errors:
                self.show_error_banner("Please fix error in config file : "+errors[0])
            else:
                self._expand_panel(self.compare_panel, False)
                self._expand_panel(self.sync_panel, False)

        async def remove_item(e: ft.Event[ft.Button], path:str):
            asyncio.create_task(self.controller.remove_recent_file(path))

        items = []
        items.append(
            ft.MenuItemButton(
                content=ft.Text("Choisir..."),
                on_click=self._choose_config_file
            )
        )
        for path in self.controller.recent_files:
            t:ft.MenuItemButton = ft.MenuItemButton(
                content = ft.Row(
                    tight=True,
                    expand=False,
                    controls=[
                        ft.Text(path,expand=10),
                        ft.IconButton(
                            ft.Icons.CANCEL,
                            icon_color=ICON_COLOR,
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
            content=ft.Icon(
                icon=ft.Icons.FILE_OPEN,
                color=ICON_COLOR,
                size=icon_size-2,
                align=ft.Alignment.CENTER
            ),
            tooltip="Ouvrir un projet",
            controls=self._build_load_menu_items()
        )
        return ft.AppBar(
            #title=ft.Text("Main"),
            bgcolor=ft.Colors.PRIMARY_CONTAINER,
            color=ft.Colors.ON_PRIMARY_CONTAINER,
            actions = [
                ft.MenuBar(
                    style=ft.MenuStyle(bgcolor=ICON_BAR_COLOR),
                    controls=[
                        self.load_popupmenu,
                        ft.SubmenuButton(content=ft.IconButton(icon=ft.Icons.NEW_LABEL, tooltip="Nouveau", icon_color=ICON_COLOR, icon_size=icon_size, on_click=self._new_project)),
                        ft.SubmenuButton(content=ft.IconButton(icon=ft.Icons.SAVE, tooltip="Enregistrer", icon_color=ICON_COLOR, icon_size=icon_size, on_click=self._save_config_file)),
                        ft.SubmenuButton(content=ft.IconButton(icon=ft.Icons.SAVE_AS, tooltip="Enregistrer sous", icon_color=ICON_COLOR, icon_size=icon_size, on_click=self._save_as_config_file)),
                    ]
                )
            ]
        )
    
    async def _new_project(self, e: ft.Event[ft.Button]):
        await self.controller.new_project()
        self._expand_panel(self.compare_panel, False)
        self._expand_panel(self.sync_panel, False)

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

    async def _run_compare(self):
        self._expand_panel(self.compare_panel, True)
        self._expand_panel(self.sync_panel, False)
        await self.controller.run_compare()
    
    def _build_project_toolbar(self):
        return ft.Container(
            bgcolor=ICON_BAR_COLOR,
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icon(ft.Icons.SYNC_LOCK),
                        icon_color=ICON_COLOR,
                        tooltip="Lancer la comparaison (projet entier)",
                        on_click=lambda _:  asyncio.create_task(self._run_compare())
                    ),
                    ft.IconButton(
                        icon=ft.Icon(ft.Icons.PLAY_ARROW),
                        icon_color=ICON_COLOR,
                        tooltip="Lancer la synchronisation (projet entier)",
                        on_click=lambda _:  asyncio.create_task(self.controller.run_sync()),
                        visible=False,
                    ),
                    ft.IconButton(
                        icon=ft.Icon(ft.Icons.SETTINGS),
                        icon_color=ICON_COLOR,
                        tooltip="Paramètres du projet",
                        on_click=self._show_project_settings
                    ),
                    ft.Text("", expand=True),
                    ft.IconButton(
                        alignment=ft.Alignment.CENTER_LEFT,
                        expand=0,
                        icon=ft.Icon(ft.Icons.ADD),
                        icon_color=ICON_COLOR,
                        tooltip="Ajouter une paire de dossiers",
                        on_click=lambda _:  asyncio.create_task(self.controller.add_folders_pair()),
                    ),
                ]
            ),
        )
    
    def _build_panel(self, title:str, icon:ft.IconData, content:ft.Control, expanded:bool = False, height:ft.Number = None) -> ft.ExpansionPanel:
        return ft.ExpansionPanel(
            margin=ft.Margin.only(bottom=MARGIN_BETWEEN_PANELS),
            expand=True,
            bgcolor=PANEL_BG_COLOR,
            header=ft.ListTile(
                title=title,
                leading=ft.Icon(icon),
                icon_color=ICON_COLOR,
                text_color=PANEL_TEXT_COLOR,
                title_text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
            ),
            # Le contenu qui s'affiche en dessous
            content=ft.Container(
                expand=True,
                height=height,
                margin=ft.Margin.only(left=PANEL_CONTENT_MARGIN,right=PANEL_CONTENT_MARGIN,bottom=PANEL_CONTENT_MARGIN),
                content=content
            ),
            expanded=expanded # État initial
        )
        
    
    def _build_folders_panel(self):
        self.folders_panel:ft.ExpansionPanel = self._build_panel(
            title="Projet",
            icon=ft.Icons.BUILD,
            content=ft.Column(
                controls=[
                    self._build_project_toolbar(),
                    self.folderpairs.build(),
                ]
            ),
            expanded = True
        )
        return self.folders_panel
    
    def _build_warning_panel(self):
        self.errors_list:ft.ListView = ft.ListView(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            padding=0,
            #auto_scroll=False,
            divider_thickness=1
        )
        self.errors_title:ft.Text = ft.Text("Avertissements (0)", color=PANEL_TEXT_COLOR)
        self.errors_panel:ft.ExpansionPanel = self._build_panel(
            title=self.errors_title,
            icon=ft.Icons.WARNING_AMBER,
            content=self.errors_list
        )
        return self.errors_panel
    
    def _build_compare_panel(self):
        async def on_sync(e):
            await self.sync_from_results_list()

        self.run_sync_btn:ft.IconButton = ft.IconButton(
            ft.Icons.PLAY_ARROW,
            icon_color=ICON_COLOR,
            hover_color=ft.Colors.GREEN_800,
            icon_size=40,
            align=ft.Alignment.CENTER_RIGHT,
            tooltip='Lancer la synchronisation à partir de la sélection en cours',
            disabled=True,
            on_click=on_sync,
        )

        self.compare_panel:ft.ExpansionPanel = self._build_panel(
            title="Résultat de la comparaison",
            icon=ft.Icons.INFO,
            content=ft.Column(
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[self.run_sync_btn]
                    ),
                    self.cmp_results_list,
                ]
            ),
            height=400,
        )
        return self.compare_panel
    
    def _build_sync_log_panel(self):
        self.sync_results_list:ListViewEx = ListViewEx(
            [
                Column("action", ColumnType.TEXT, "Action", 3),
                Column("left", ColumnType.TEXT, "Chemin gauche", 6),
                Column("right", ColumnType.TEXT, "Chemin droit", 6),
            ],
            header_bgcolor=HEADER_BG_COLOR,
            header_text_color=HEADER_TEXT_COLOR,
        )

        self.sync_panel:ft.ExpansionPanel =  self._build_panel(
            title="Résultat de la synchronisation",
            icon=ft.Icons.INFO,
            content=self.sync_results_list,
            height=400,
        )

        return self.sync_panel
    
    async def _show_project_settings(self, e: ft.Event[ft.Button]):
        await self.page.push_route("/settings")