import os
import flet as ft

from ui.ui_interface import CmpStatus, CmpResultItem
from ui.ui_common import *
from ui.views.main_view import *


class CMP_STATUS_ICONS:
    LEFT_ONLY = ft.Icons.ARROW_FORWARD_OUTLINED
    RIGHT_ONLY = ft.Icons.CANCEL
    DIFFERENT = ft.Icons.KEYBOARD_DOUBLE_ARROW_RIGHT_OUTLINED

class CmpResultsList(ListViewEx):
    def __init__(self):
        super().__init__(
            [
                Column(id="left_dir", type=ColumnType.TEXT, title="Dossier gauche", expand=2),
                Column(id="left_path", type=ColumnType.TEXT, title="Chemin relatif fichier gauche", expand=4),
                Column(id="include", type=ColumnType.CHECKBOX, title="Inclure", expand=1),
                Column(id="status", type=ColumnType.ICON, title="Etat", expand=1),
                Column(id="right_dir", type=ColumnType.TEXT, title="Dossier droit", expand=2),
                Column(id="right_path", type=ColumnType.TEXT, title="Chemin relatif fichier droit", expand=4),
            ],
            header_bgcolor=HEADER_BG_COLOR,
            header_text_color=HEADER_TEXT_COLOR,
            on_change=self._on_change
        )
      
    def append_result(self, item: CmpResultItem):
        row = self._create_row(item)
        self.append_row(row, data=item)

    def _create_row(self, item:CmpResultItem):
        if item.status == CmpStatus.LEFT_ONLY:
            status_icon = CMP_STATUS_ICONS.LEFT_ONLY
        elif item.status == CmpStatus.RIGHT_ONLY:
            status_icon = CMP_STATUS_ICONS.RIGHT_ONLY
        elif item.status == CmpStatus.DIFFERENT:
            status_icon = CMP_STATUS_ICONS.DIFFERENT
        else:
            status_icon = ft.Icons.HELP
        
        return [
             (item.left_dir, item.left_dir),
             ('.' + os.path.sep + item.left_file if item.left_file else '', os.path.join(item.left_dir,item.left_file) if item.left_file else ''),
             item.include,
             status_icon,
             (item.right_dir, item.right_dir),
             ('.' + os.path.sep + item.right_file if item.right_file else '', os.path.join(item.right_dir,item.right_file) if item.right_file else '')
        ]
    
    def _on_change(self, column_id, e):
        item:CmpResultItem = e.control.data
        item.include = e.data