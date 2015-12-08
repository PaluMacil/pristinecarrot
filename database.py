from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, join, select
from config import db_file


Base = automap_base()
engine = create_engine('sqlite:///' + db_file)
Base.prepare(engine, reflect=True)
db = Session(engine)

GameObject = Base.classes.game_object
ImportFile = Base.classes.import_file
SpriteTile = Base.classes.sprite_tile


def get_first_object(batch, ignore_committed=None, ignore_discarded=None):
    if ignore_committed is None:
        ignore_committed = True
    if ignore_discarded is None:
        ignore_discarded = True

    if ignore_committed and ignore_discarded:
        object = join(SpriteTile, ImportFile, GameObject).select(
            (ImportFile.c.name == batch) &
            (GameObject.c.committed == False) &
            (SpriteTile.c.discard == False))


if __name__ == '__main__':
    import code
    all_vars = globals().copy()
    all_vars.update(locals())
    shell = code.InteractiveConsole(all_vars)
    shell.interact()
