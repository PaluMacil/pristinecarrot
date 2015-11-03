import sqlite3
from contextlib import closing

conn = sqlite3.connect('spritemap.db')


def db_exists():
    with closing(conn.cursor()) as c:
        c.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
        count = c.fetchone()
    if count[0] > 0:
        return True
    else:
        return False


def setup_db():
    with closing(conn.cursor()) as c:
        c.executescript("""
            create table sprite_tile (
              id INTEGER PRIMARY KEY,
              import_file_id INTEGER,
              discard BOOLEAN
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
              object_store_id INTEGER
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
    with closing(conn.cursor()) as c:
        c.execute('''
          select setting_value
          from application_settings
          where name = ?
            and setting_type = ?
        ''', (setting_name, category))
        return c.fetchone()[0]
