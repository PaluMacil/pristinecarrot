from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from config import db_file


Base = automap_base()
engine = create_engine('sqlite:///' + db_file)
Base.prepare(engine, reflect=True)
db = Session(engine)

GameObject = Base.classes.game_object
ImportFile = Base.classes.import_file
ObjectStore = Base.classes.object_store
SpriteTile = Base.classes.sprite_tile
SpriteTileObjectStore = Base.classes.sprite_tile_x_object_store


if __name__ == '__main__':
    import code
    all_vars = globals().copy()
    all_vars.update(locals())
    shell = code.InteractiveConsole(all_vars)
    shell.interact()
