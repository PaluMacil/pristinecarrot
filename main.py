#!/usr/bin/kivy
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.factory import Factory
from os.path import join
from config import db_exists, setup_db
from spritemapper import analyze_spritesheet


class Root(TabbedPanel):
    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        if len(filename) > 0:
            analyze_spritesheet(join(path, filename[0]), 32, 32)

        self.dismiss_popup()


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class PristineCarrotApp(App):
    pass


Factory.register('Root', cls=Root)
Factory.register('LoadDialog', cls=LoadDialog)

if __name__ == '__main__':
    if not db_exists():
        setup_db()
    PristineCarrotApp().run()
