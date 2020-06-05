from threading import Thread
from pynput.mouse import Button, Controller
from spotipy import Spotify
from os import sep, kill, getpid
from shortcuts import listener
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QMenu, QAction, QSystemTrayIcon
from spotlight.ui import Ui
from time import sleep
from spotlight.interactions import Interactions
from definitions import ASSETS_DIR
from caching import CacheManager, SongQueue, ImageQueue
from colors import colors

from auth import Config


class App:
    def __init__(self):
        print(f"{colors.PINK}{colors.BOLD}Welcome to Spotlightify{colors.RESET}\n\n")

        self.app = QApplication([])
        self.app.setQuitOnLastWindowClosed(False)

        self.tray = None

        self.config = Config()
        # if self.config.is_valid():
        self.oauth = self.config.get_oauth()
        # else:
        # prompt user to input keys / username

        token_info = self.oauth.get_access_token(as_dict=True)
        token = token_info["access_token"]

        try:
            self.sp = Spotify(auth=token)
        except:
            print("User token could not be created")

        self.song_queue = SongQueue()
        self.image_queue = ImageQueue()

        self.create_tray()

        # creates the interactions object
        self.interactions = Interactions(self.sp, token_info, self.oauth, self.exit_app, self.song_queue)

        self.spotlight_ui = Ui(self.interactions, self.sp)

        self.listener_thread = Thread(target=listener, daemon=True, args=(self.show_ui,))
        self.listener_thread.start()

        self.cache_manager = CacheManager(self.sp, self.song_queue, self.image_queue)
        self.app.exec_()

    def create_tray(self):
        def create_context_menu():
            # TODO fix
            menu = QMenu()
            open_action = QAction("Open")
            open_action.triggered.connect(self.show_ui)
            menu.addAction(open_action)

            exit_action = QAction("Exit")
            exit_action.triggered.connect(self.exit_app)
            menu.addAction(exit_action)

            return menu

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon(f"{ASSETS_DIR}img{sep}logo_small.png"))
        self.tray.setVisible(True)
        self.tray.setToolTip("Spotlightify")
        self.tray.setContextMenu(create_context_menu())
        self.tray.activated.connect(self.tray_icon_activated)

    def exit_app(self):
        self.spotlight_ui.close()  # visually removes ui quicker
        kill(getpid(), 9)

    def show_ui(self):
        if not self.spotlight_ui.isActiveWindow() or self.spotlight_ui.isHidden():
            self.spotlight_ui.show()
        sleep(0.1)
        self.interactions.refresh_token()
        self.spotlight_ui.raise_()
        self.spotlight_ui.activateWindow()
        self.focus_ui()
        self.spotlight_ui.function_row.refresh(None)  # refreshes function row buttons

    def focus_ui(self):  # Only way I could think of to properly focus the ui
        mouse = Controller()
        # mouse position before focus
        mouse_pos_before = mouse.position
        # changing the mouse position for click
        target_pos_x = self.spotlight_ui.pos().x() + self.spotlight_ui.textbox.pos().x()
        target_pos_y = self.spotlight_ui.pos().y() + self.spotlight_ui.textbox.pos().y()
        mouse.position = (target_pos_x, target_pos_y)
        mouse.click(Button.left)
        mouse.position = mouse_pos_before

    def tray_icon_activated(self, reason):
        if reason == self.tray.Trigger:  # tray.Trigger is left click
            self.show_ui()


if __name__ == "__main__":
    App()
