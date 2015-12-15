#!/usr/bin/kivy
from kivy.app import App
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.factory import Factory
from os.path import join
from config import setup_all, insert_newlines, purge_processed, \
    reset_database, setup_folders, setup_db, get_config
from spritemapper import analyze_spritesheet, slice_spritesheet
from database import ImportFile, SpriteTile, GameObject, db, \
    get_first_object, get_right_object, get_left_object, get_up_object, get_down_object, \
    commit_game_object, discard_tile, retriage_tile, retriage_object
from os.path import basename


class Root(TabbedPanel):
    def __init__(self):
        super().__init__()
        self._keyboard = Window.request_keyboard(None, self)
        if self._keyboard:
            self._keyboard.bind(on_key_down=self.on_keyboard_down)
        self.popup = None
        # Spritesheet Tab:
        self.new_files = []
        self.new_file_name = 'untitled'
        self.new_file_license = 'unknown'
        # Triage Tab:
        self.triage_area = None
        self.triage_batches = []
        self.current_object = None
        self.current_tile_id = None
        self.ignore_committed = True
        self.ignore_discarded = True

    def dismiss_popup(self):
        self.popup.dismiss()

    def split_and_import(self):
        input_dialog = InputDialog(okay=self.dismiss_popup,
                                   message="What type of licensing governs this import?",
                                   user_input=self.new_file_license)
        self.popup = Popup(title="Split and Import: Imagery License", content=input_dialog,
                           size_hint=(0.9, 0.7))
        self.popup.bind(on_dismiss=self.split_spritesheet)
        self.popup.open()

    def split_spritesheet(self, popup):
        input_text = popup.children[0].children[0].children[0].children[0].children[1].text
        if input_text:
            self.new_file_license = input_text
        no_newlines = self.ids.path.text.replace('\n', '')
        Logger.info('Import path for file splitting: ' + no_newlines)
        self.new_files = slice_spritesheet(filename=no_newlines,
                                           x_size=int(self.ids.x_px_size.text),
                                           y_size=int(self.ids.y_px_size.text))
        input_dialog = InputDialog(okay=self.dismiss_popup,
                                   message="Enter a descriptive name for this import batch.",
                                   user_input='')
        self.popup = Popup(title="Split and Import: Batch Name", content=input_dialog,
                           size_hint=(0.9, 0.7))
        self.popup.bind(on_dismiss=self.add_images_to_db)
        self.popup.open()

    def add_images_to_db(self, popup):
        input_text = popup.children[0].children[0].children[0].children[0].children[1].text
        if input_text:
            self.new_file_name = input_text
        import_file = ImportFile(name=self.new_file_name, license=self.new_file_license,
                                 row_size=int(self.ids.x_tile_size.text))
        db.add(import_file)
        for file in self.new_files:
            file_index = basename(file).split('.')[0]
            game_object = GameObject(id=file_index,
                                     name='(no name)',
                                     description='(no description)',
                                     committed=False,
                                     size=1)
            sprite_tile = SpriteTile(id=file_index,
                                     discard=False,
                                     tile_number=1,
                                     import_file=import_file,
                                     game_object=game_object)
            db.add(sprite_tile)
        db.commit()
        self.split_complete()

    def split_complete(self):
        info_dialog = InfoDialog(okay=self.dismiss_popup,
                                 message=str(len(self.new_files)) + " tiles have been added to the library.")
        self.popup = Popup(title="Split and Import: Complete", content=info_dialog,
                           size_hint=(0.9, 0.7))
        self.popup.open()
        self.ids.triage_batch_spinner.values.append(self.new_file_name)

    def show_load(self):

        if is_int(self.ids.x_px_size.text) and is_int(self.ids.y_px_size.text):
            if not self.ids.x_px_size.text or int(self.ids.x_px_size.text) < 1:
                info_dialog = InfoDialog(okay=self.dismiss_popup,
                                         message="You must pick x-pixels per tile.")
                self.popup = Popup(title="Info", content=info_dialog,
                                   size_hint=(0.9, 0.7))
            elif not self.ids.y_px_size.text or int(self.ids.y_px_size.text) < 1:
                info_dialog = InfoDialog(okay=self.dismiss_popup,
                                         message="You must pick y-pixels per tile.")
                self.popup = Popup(title="Info", content=info_dialog,
                                   size_hint=(0.9, 0.7))
            else:
                load_dialog = LoadDialog(load=self.load, cancel=self.dismiss_popup)
                self.popup = Popup(title="Load file", content=load_dialog,
                                   size_hint=(0.9, 0.95))
        else:
            invalid_dialog = InfoDialog(okay=self.dismiss_popup,
                                        message="You must pick valid pixel values.")
            self.popup = Popup(title="Invalid Data", content=invalid_dialog,
                               size_hint=(0.9, 0.7))
        self.popup.open()

    def load(self, path, filename):
        if filename:
            x_tile_size_px = int(self.ids.x_px_size.text)
            y_tile_size_px = int(self.ids.y_px_size.text)
            sheet_data = analyze_spritesheet(join(path, filename[0]), x_tile_size_px, y_tile_size_px)

            sheet_mode = sheet_data[0]
            x_sheet_size_tiles = sheet_data[1]
            y_sheet_size_tiles = sheet_data[2]

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
            self.popup = Popup(title="Info", content=info_dialog,
                               size_hint=(0.9, 0.7))

    def select_batch(self, batch, triage_area):
        triage_area.clear_widgets()
        self.current_object, self.current_tile_id = get_first_object(batch,
                                                                     ignore_committed=self.ignore_committed,
                                                                     ignore_discarded=self.ignore_discarded)
        self.update_triage_area(triage_area)

    def update_triage_area(self, triage_area):
        if self.current_object:
            self.triage_area = triage_area
            self.ids.triage_tile_id.text = str(self.current_tile_id)
            self.ids.triage_object_id.text = str(self.current_object[0].game_object.id)
            if self.current_object[0].game_object.size == 1:
                image_area = Factory.TilesV1()
                image1 = self.get_image_for(self.current_object, 1)
                if image1:
                    image_area.image1 = image1
            if self.current_object[0].game_object.size == 2:
                image_area = Factory.TilesV2()
                image1 = self.get_image_for(self.current_object, 1)
                if image1:
                    image_area.image1 = image1
                image2 = self.get_image_for(self.current_object, 2)
                if image2:
                    image_area.image2 = image2
                image3 = self.get_image_for(self.current_object, 3)
                if image3:
                    image_area.image3 = image3
                image4 = self.get_image_for(self.current_object, 4)
                if image4:
                    image_area.image4 = image4
            if self.current_object[0].game_object.size == 3:
                # TODO: Finish size 3 triage code.
                image_area = Factory.TilesV3()
                image1 = self.get_image_for(self.current_object, 1)
                if image1:
                    image_area.image1 = image1
            if image_area:
                triage_area.add_widget(image_area)

    @staticmethod
    def get_image_for(object_data, tile_number):
        for row in object_data:
            if row.sprite_tile.tile_number == tile_number:
                return join(get_config('processed', 'directory'), str(row.sprite_tile.id) + '.png')
        else:
            return None

    def on_keyboard_down(self, keyboard, keycode, text, modifiers):

        if self.get_current_tab().text == 'Tile Triage':
            triage_area = App.get_running_app().root.ids.triage_area
            batch = App.get_running_app().root.ids.triage_batch_spinner.text
            if batch != '(select batch)':
                if keycode[1] == 'left':
                    next_object, next_tile_id = get_left_object(batch, self.current_tile_id,
                                                                ignore_committed=self.ignore_committed,
                                                                ignore_discarded=self.ignore_discarded)
                    if next_object and next_tile_id:
                        triage_area.clear_widgets()
                        self.current_object, self.current_tile_id = next_object, next_tile_id
                        self.update_triage_area(triage_area)
                elif keycode[1] == 'right':
                    next_object, next_tile_id = get_right_object(batch, self.current_tile_id,
                                                                 ignore_committed=self.ignore_committed,
                                                                 ignore_discarded=self.ignore_discarded)
                    if next_object and next_tile_id:
                        triage_area.clear_widgets()
                        self.current_object, self.current_tile_id = next_object, next_tile_id
                        self.update_triage_area(triage_area)
                elif keycode[1] == 'up':
                    next_object, next_tile_id = get_up_object(batch, self.current_tile_id,
                                                              ignore_committed=self.ignore_committed,
                                                              ignore_discarded=self.ignore_discarded)
                    if next_object and next_tile_id:
                        triage_area.clear_widgets()
                        self.current_object, self.current_tile_id = next_object, next_tile_id
                        self.update_triage_area(triage_area)
                elif keycode[1] == 'down':
                    next_object, next_tile_id = get_down_object(batch, self.current_tile_id,
                                                                ignore_committed=self.ignore_committed,
                                                                ignore_discarded=self.ignore_discarded)
                    if next_object and next_tile_id:
                        triage_area.clear_widgets()
                        self.current_object, self.current_tile_id = next_object, next_tile_id
                        self.update_triage_area(triage_area)
                else:
                    return False
        return True

    def commit(self):
        commit_game_object(self.current_object[0].game_object.id)
        if self.ignore_committed:
            self.show_available_tile()

    def discard(self):
        discard_tile(self.current_tile_id)
        if self.ignore_discarded:
            self.show_available_tile()

    def show_available_tile(self):
        batch = App.get_running_app().root.ids.triage_batch_spinner.text
        next_object, next_tile_id = get_left_object(batch, self.current_tile_id,
                                                    ignore_committed=self.ignore_committed,
                                                    ignore_discarded=self.ignore_discarded)
        triage_area = App.get_running_app().root.ids.triage_area
        triage_area.clear_widgets()
        if not next_object or not next_tile_id:
            next_object, next_tile_id = get_right_object(batch, self.current_tile_id,
                                                         ignore_committed=self.ignore_committed,
                                                         ignore_discarded=self.ignore_discarded)
        if next_object and next_tile_id:
            self.current_object, self.current_tile_id = next_object, next_tile_id
            self.update_triage_area(triage_area)
        else:
            self.current_object, self.current_tile_id = None, None
            App.get_running_app().root.ids.triage_batch_spinner.text = '(select batch)'

    def retriage(self):
        committed = self.current_object[0].game_object.committed
        discarded = self.current_object[0].sprite_tile.discard
        if discarded:
            retriage_tile(self.current_tile_id)
        if committed:
            retriage_object(self.current_object[0].game_object.id)
        # TODO: Use future goto_tile(tile_id) to reset instead of duplicating label code and modifying current object.

    def on_checkbox_active(self, checkbox, active):
        if checkbox == 'discarded':
            if active:
                self.ignore_discarded = True
            else:
                self.ignore_discarded = False
        if checkbox == 'committed':
            if active:
                self.ignore_committed = True
            else:
                self.ignore_committed = False

    @staticmethod
    def reset_db():
        reset_database()
        setup_db()

    @staticmethod
    def reset_processed_folder():
        purge_processed()
        setup_folders()


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class InfoDialog(FloatLayout):
    message = StringProperty(None)
    okay = ObjectProperty(None)


class InputDialog(FloatLayout):
    message = StringProperty(None)
    user_input = StringProperty(None)
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
