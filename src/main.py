APP_VERSION = "0.1.0"

import sys

import flet as ft
import re
from core.app_controller import AppController
from ui.views.main_view import MainView
from ui.views.settings_view import SettingsView


async def main(page: ft.Page):
    controller:AppController = AppController()
    mainview:ft.View = MainView(controller, APP_VERSION)
    controller.set_ui(mainview)

     # Navigation arrière (bouton back Android/web)
    async def view_pop(e:ft.EventHandler[ft.ViewPopEvent]):
        if e.view is not None:
            try:
                func = getattr(e.view, 'on_view_hidden')
                func()
            except:
                pass
                
            page.views.remove(e.view)
            top_view = page.views[-1]
            await page.push_route(top_view.route)

     # Gestion du changement de route
    def route_change():
        page.views.clear()
        page.views.append(mainview)

        if page.route == "/settings":
            page.views.append(SettingsView(controller))

        elif page.route.startswith("/settings["):
            m:re.Match = re.match("\\/settings\\[(\\d)\\]", page.route)
            if m:
                page.views.append(SettingsView(controller, int(m.group(1))))
        page.update()

    page.on_view_pop = view_pop
    page.on_route_change = route_change
    page.theme_mode = ft.ThemeMode.LIGHT
    #page.theme = ft.Theme(color_scheme_seed=ft.Colors.RED_100,)
    # Route initiale
    route_change()

ft.run(main)