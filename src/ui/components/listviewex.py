from enum import Enum
from functools import partial
import flet as ft

class ColumnType(Enum):
    TEXT = 1
    CHECKBOX = 2
    ICON = 3

class Column:
    def __init__(self, id:any, type: ColumnType, title:str, expand:int):
        self.id:any = id
        self.type:ColumnType = type
        self.title:str = title
        self.expand:int = expand

class ListViewEx(ft.Container):

    class HeaderRow(ft.Container):
        def __init__(self, columns:list[Column], bgcolor=None, text_color=None):
            super().__init__(
                bgcolor=bgcolor,
                padding=8,
                content=ft.Row(
                    spacing=0,
                    controls=[self._build_header(column, text_color) for column in columns]
                )
            )

        def _build_header(self, column:Column, text_color=None):
            if column.type == ColumnType.CHECKBOX:
                return self._header_cell(column.title, column.expand, alignment=ft.Alignment.CENTER, color=text_color)
            elif column.type == ColumnType.ICON:
                return self._header_cell(column.title, column.expand, alignment=ft.Alignment.CENTER, color=text_color)
            return self._header_cell(column.title, column.expand, color=text_color)

        def _header_cell(self, text, expand, alignment=ft.Alignment.CENTER_LEFT, color=None):
            return ft.Container(
                expand=expand,
                alignment=alignment,
                content=ft.Text(
                    text,
                    weight=ft.FontWeight.BOLD,
                    size=14,
                    color=color,
                )
            )

    def __init__(self, columns:list[Column], header_bgcolor=None, header_text_color=None, bgcolor=None, text_color=None, on_change=None):
        self.columns:list[Column] = columns
        self.on_change = on_change
        self.text_color = text_color
        self.listview = ft.ListView(
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
            bgcolor=bgcolor,
            content=ft.Column(
                spacing=0,
                controls=[
                    ListViewEx.HeaderRow(self.columns, header_bgcolor, header_text_color),
                    ft.Divider(height=1),
                    self.listview,
                ]
            )
        )

    def append_row(self, values:list, weight=None, bgcolor=None, text_color=None, data=None):
        row:ft.Row = ft.Row(
            data=data,
            spacing=0,
            controls=[self._build_cell(values[idx], column, weight, bgcolor, text_color, data) for idx, column in enumerate(self.columns)]
        )
        self.listview.controls.append(
            ft.Container(
                border=ft.Border.only(
                    bottom=ft.BorderSide(1, ft.Colors.OUTLINE_VARIANT)
                ),
                padding=5,
                content=row,
            ),
        )
    
    def clear(self):
        self.listview.controls.clear()
    
    def _build_cell(self, value, column:Column, weight, bgcolor, text_color, data):
        value_=value[0] if isinstance(value, tuple) else value
        tooltip=value[1] if isinstance(value, tuple) and len(value) > 1 else None
        alignment = None
        if column.type == ColumnType.CHECKBOX:
            content = ft.Checkbox(
                value=bool(value_),
                data=data,
                on_change=partial(self.on_change, column.id) if self.on_change else None
            )
            alignment = ft.Alignment.CENTER
        elif column.type == ColumnType.ICON:
            content = ft.Icon(value_)
            alignment = ft.Alignment.CENTER
        else:
            content = ft.Text(
                value=str(value_),
                color=text_color or self.text_color,
                no_wrap=True,
                overflow=ft.TextOverflow.ELLIPSIS,
                size=13,
                weight=weight
            )
        return ft.Container(
            expand=column.expand,
            bgcolor=bgcolor or self.bgcolor,
            padding=5,
            alignment=alignment,
            content=content,
            tooltip=tooltip,
        )