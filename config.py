import sqlite3
from contextlib import closing
from os import path, makedirs, remove
from shutil import rmtree

db_file = 'spritemap.db'


def purge_processed():
    processed_directory = get_config('processed', 'directory')
    archive_directory = get_config('archive', 'directory')
    rmtree(processed_directory)
    rmtree(archive_directory)


def reset_database():
    remove('spritemap.db')


def db_exists():
    conn = sqlite3.connect(db_file)
    with closing(conn.cursor()) as c:
        c.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        count = c.fetchone()
    if count[0] > 0:
        return True
    else:
        return False


def setup_db():
    conn = sqlite3.connect(db_file)
    with closing(conn.cursor()) as c:
        c.executescript("""
            create table sprite_tile (
              id INTEGER PRIMARY KEY,
              import_file_id INTEGER,
              discard BOOLEAN,
              FOREIGN KEY(import_file_id) REFERENCES import_file(id)
            );

            create table sprite_tile_x_object_store (
              id INTEGER PRIMARY KEY,
              sprite_tile_id INTEGER,
              game_object_id INTEGER,
              x INTEGER,
              y INTEGER,
              main BOOLEAN,
              committed BOOLEAN,
              FOREIGN KEY(sprite_tile_id) REFERENCES sprite_tile(id),
              FOREIGN KEY(game_object_id) REFERENCES game_object(id),
              UNIQUE (sprite_tile_id, game_object_id)
            );

            create table game_object (
              id INTEGER PRIMARY KEY,
              name TEXT,
              description TEXT,
              object_store_id INTEGER,
              FOREIGN KEY(object_store_id) REFERENCES object_store(id)
            );

            create table object_store (
              id INTEGER PRIMARY KEY,
              version TEXT NOT NULL,
              x_size INTEGER,
              y_size INTEGER
            );

            create table import_file (
              id INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              license TEXT
            );

            create table application_setting (
              id INTEGER PRIMARY KEY,
              name TEXT NOT NULL,
              setting_value TEXT NOT NULL,
              setting_type TEXT,
              UNIQUE (name, setting_type)
            );

            INSERT INTO application_setting (name, setting_value, setting_type)
              SELECT 'active_version' AS name, '0.0.1' AS setting_value, '' AS setting_type
              UNION ALL SELECT 'processed','processed','directory'
              UNION ALL SELECT 'archive','archive','directory'
              UNION ALL SELECT 'output_padding','0','image'
              UNION ALL SELECT 'input_padding','0','image'
              UNION ALL SELECT 'default_x_pixels','32','image'
              UNION ALL SELECT 'default_y_pixels','32','image'
            ;
            """)


def get_config(setting_name, category):
    conn = sqlite3.connect(db_file)
    with closing(conn.cursor()) as c:
        c.execute('''
          select setting_value
          from application_setting
          where name = ?
            and setting_type = ?
        ''', (setting_name, category))
        value = c.fetchone()[0]
        return value


def setup_folders():
    processed_directory = get_config('processed', 'directory')
    archive_directory = get_config('archive', 'directory')
    if not path.exists(processed_directory):
        makedirs(processed_directory)
    if not path.exists(archive_directory):
        makedirs(archive_directory)


def setup_all():
    if not db_exists():
        setup_db()
    setup_folders()


def insert_newlines(string, every=64):
    # Strip newlines with: mystring.replace('\n', '')
    lines = []
    for i in range(0, len(string), every):
        lines.append(string[i:i+every])
    return '\n'.join(lines)
