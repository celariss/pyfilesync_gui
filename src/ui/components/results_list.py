from enum import Enum
import os

import flet as ft

from ui.ui_interface import CmpStatus, ResultItem

COLUMN_LAYOUT = {
    "left_dir": 2,
    "left_path": 4,
    "include": 1,
    "status": 1,
    "right_dir": 2,
    "right_path": 4,
}

class CMP_STATUS_ICONS:
    LEFT_ONLY = ft.Icons.ARROW_FORWARD_OUTLINED
    RIGHT_ONLY = ft.Icons.CANCEL
    DIFFERENT = ft.Icons.KEYBOARD_DOUBLE_ARROW_RIGHT_OUTLINED
    

class ResultsHeader(ft.Container):
    def __init__(self):
        super().__init__(
            bgcolor=ft.Colors.BLUE_GREY_900,
            padding=8,
            content=ft.Row(
                spacing=0,
                controls=[
                    self.header_cell("Dossier gauche", COLUMN_LAYOUT["left_dir"]),
                    self.header_cell("Chemin relatif fichier gauche", COLUMN_LAYOUT["left_path"]),
                    self.header_cell("Inclure", COLUMN_LAYOUT["include"], alignment=ft.Alignment.CENTER),
                    self.header_cell("Etat", COLUMN_LAYOUT["status"], alignment=ft.Alignment.CENTER),
                    self.header_cell("Dossier droit", COLUMN_LAYOUT["right_dir"]),
                    self.header_cell("Chemin relatif fichier droit", COLUMN_LAYOUT["right_path"]),
                ]
            )
        )

    def header_cell(self, text, expand, alignment=ft.Alignment.CENTER_LEFT):
        return ft.Container(
            expand=expand,
            alignment=alignment,
            content=ft.Text(
                text,
                weight=ft.FontWeight.BOLD,
                size=14,
            )
        )


class ResultRow(ft.Container):
    def __init__(self, item):
        if item.status == CmpStatus.LEFT_ONLY:
            status_icon = CMP_STATUS_ICONS.LEFT_ONLY
        elif item.status == CmpStatus.RIGHT_ONLY:
            status_icon = CMP_STATUS_ICONS.RIGHT_ONLY
        elif item.status == CmpStatus.DIFFERENT:
            status_icon = CMP_STATUS_ICONS.DIFFERENT
        else:
            status_icon = ft.Icons.HELP
        
        super().__init__(
            border=ft.Border.only(
                bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)
            ),
            padding=5,
            content=ft.Row(
                spacing=0,
                controls=[
                    self.text_cell(item.left_dir, COLUMN_LAYOUT["left_dir"], tooltip=item.left_dir),
                    self.text_cell('.' + os.path.sep + item.left_file if item.left_file else '', COLUMN_LAYOUT["left_path"], tooltip=os.path.join(item.left_dir,item.left_file)),
                    self.checkbox_cell(item.include, COLUMN_LAYOUT["include"]),
                    self.icon_cell(status_icon, COLUMN_LAYOUT["status"]),
                    self.text_cell(item.right_dir, COLUMN_LAYOUT["right_dir"], tooltip=item.right_dir),
                    self.text_cell('.' + os.path.sep + item.right_file if item.right_file else '', COLUMN_LAYOUT["right_path"], tooltip=os.path.join(item.right_dir,item.right_file)),
                ]
            ),
        )

    def text_cell(self, value, expand, tooltip=None):
        return ft.Container(
            expand=expand,
            padding=5,
            tooltip=tooltip,
            content=ft.Text(
                value,
                no_wrap=True,
                overflow=ft.TextOverflow.ELLIPSIS,
                size=13,
            )
        )

    def checkbox_cell(self, value, expand):
        return ft.Container(
            expand=expand,
            alignment=ft.Alignment.CENTER,
            content=ft.Checkbox(
                value=value
            )
        )

    def icon_cell(self, icon, expand):
        return ft.Container(
            expand=expand,
            alignment=ft.Alignment.CENTER,
            content=ft.Icon(icon)
        )


class ResultsList(ft.Container):
    def __init__(self):
        self.results_list = ft.ListView(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=0,
            padding=0,
            #auto_scroll=False,
            divider_thickness=1
        )
        super().__init__(
            expand=True,
            border=ft.Border.all(1),
            content=ft.Column(
                spacing=0,
                controls=[
                    ResultsHeader(),
                    ft.Divider(height=1),
                    self.results_list,
                ]
            )
        )
      
    def append_result(self, item: ResultItem):
        row = ResultRow(item)
        self.results_list.controls.append(row)

    def refresh(self):
        self.update()

    def clear(self):
        self.results_list.controls.clear()
        self.update()