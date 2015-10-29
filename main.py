#!/usr/bin/kivy
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel


class ItemEditorWidget(TabbedPanel):
    pass


class ItemEditorApp(App):
    def build(self):
        return ItemEditorWidget()

if __name__ == '__main__':
    ItemEditorApp().run()
