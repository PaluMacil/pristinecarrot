#!/usr/bin/kivy
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from os.path import join
from config import setup_all, insert_newlines, purge_processed, reset_database, setup_folders, setup_db
from spritemapper import analyze_spritesheet, slice_spritesheet


class Root(TabbedPanel):
    def dismiss_popup(self):
        self._popup.dismiss()

    def split_and_import(self):
        no_newlines = self.ids.path.text.replace('\n', '')
        slice_spritesheet(filename=no_newlines,
                          x_size=int(self.ids.x_px_size.text),
                          y_size=int(self.ids.y_px_size.text))
        info_dialog = InfoDialog(okay=self.dismiss_popup,
                                 message="Tiles have been added to the library.")
        self._popup = Popup(title="Split and Import", content=info_dialog,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def show_load(self):

        if is_int(self.ids.x_px_size.text) and is_int(self.ids.y_px_size.text):
            if not self.ids.x_px_size.text or int(self.ids.x_px_size.text) < 1:
                info_dialog = InfoDialog(okay=self.dismiss_popup,
                                         message="You must pick x-pixels per tile.")
                self._popup = Popup(title="Info", content=info_dialog,
                                    size_hint=(0.9, 0.9))
            elif not self.ids.y_px_size.text or int(self.ids.y_px_size.text) < 1:
                info_dialog = InfoDialog(okay=self.dismiss_popup,
                                         message="You must pick y-pixels per tile.")
                self._popup = Popup(title="Info", content=info_dialog,
                                    size_hint=(0.9, 0.9))
            else:
                load_dialog = LoadDialog(load=self.load, cancel=self.dismiss_popup)
                self._popup = Popup(title="Load file", content=load_dialog,
                                    size_hint=(0.9, 0.9))
        else:
            invalid_dialog = InfoDialog(okay=self.dismiss_popup,
                                        message="You must pick valid pixel values.")
            self._popup = Popup(title="Invalid Data", content=invalid_dialog,
                                size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        if filename:
            x_tile_size_px = int(self.ids.x_px_size.text)
            y_tile_size_px = int(self.ids.y_px_size.text)
            sheet_data = analyze_spritesheet(join(path, filename[0]), x_tile_size_px, y_tile_size_px)
            sheet_format = sheet_data[0]
            x_sheet_size_px = sheet_data[1][0]
            y_sheet_size_px = sheet_data[1][1]
            sheet_mode = sheet_data[2]
            x_sheet_size_tiles = sheet_data[3]
            y_sheet_size_tiles = sheet_data[4]

            self.ids.path.text = insert_newlines(join(path, filename[0]),
                                                 every=40)
            self.ids.x_tile_size.text = str(x_sheet_size_tiles)
            self.ids.y_tile_size.text = str(y_sheet_size_tiles)
            self.ids.image_mode.text = sheet_mode

            self.ids.import_button.disabled = False

            self.dismiss_popup()

        else:
            self.dismiss_popup()
            info_dialog = InfoDialog(okay=self.dismiss_popup,
                                     message="Could not load file.")
            self._popup = Popup(title="Info", content=info_dialog,
                                size_hint=(0.9, 0.9))

    def reset_db(self):
        reset_database()
        setup_db()

    def reset_processed_folder(self):
        purge_processed()
        setup_folders()


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class InfoDialog(FloatLayout):
    message = StringProperty(None)
    okay = ObjectProperty(None)


class PristineCarrotApp(App):
    pass


def is_int(s):
    s = str(s).strip()
    return s == '0' \
        or (s if s.find('..') > -1
            else s.lstrip('-+').rstrip('0').rstrip('.')).isdigit()


if __name__ == '__main__':
    setup_all()
    PristineCarrotApp().run()
