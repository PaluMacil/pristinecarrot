from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, join, select, func
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
        min_sprite_tile_id = (db.query(func.min(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(ImportFile.name == batch)
                                .filter(GameObject.committed == False)
                                .filter(SpriteTile.discard == False)
                                ).scalar()
    elif ignore_committed:
        min_sprite_tile_id = (db.query(func.min(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(ImportFile.name == batch)
                                .filter(GameObject.committed == False)
                                ).scalar()
    elif ignore_discarded:
        min_sprite_tile_id = (db.query(func.min(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(ImportFile.name == batch)
                                .filter(SpriteTile.discard == False)
                                ).scalar()
    else:
        min_sprite_tile_id = (db.query(func.min(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(ImportFile.name == batch)
                                ).scalar()
    if not min_sprite_tile_id:
        return None, None
    game_object_data = (db.query(GameObject, SpriteTile)
                        .join(SpriteTile)
                        .filter(SpriteTile.game_object_id == min_sprite_tile_id)
                        ).all()
    return game_object_data, min_sprite_tile_id


def get_left_object(batch, current_tile_id, ignore_committed=None, ignore_discarded=None):
    if ignore_committed is None:
        ignore_committed = True
    if ignore_discarded is None:
        ignore_discarded = True

    if ignore_committed and ignore_discarded:
        next_sprite_tile_id = (db.query(func.max(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id < current_tile_id)
                                .filter(ImportFile.name == batch)
                                .filter(GameObject.committed == False)
                                .filter(SpriteTile.discard == False)
                                ).scalar()
    elif ignore_committed:
        next_sprite_tile_id = (db.query(func.max(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id < current_tile_id)
                                .filter(ImportFile.name == batch)
                                .filter(GameObject.committed == False)
                                ).scalar()
    elif ignore_discarded:
        next_sprite_tile_id = (db.query(func.max(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id < current_tile_id)
                                .filter(ImportFile.name == batch)
                                .filter(SpriteTile.discard == False)
                                ).scalar()
    else:
        next_sprite_tile_id = (db.query(func.max(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id < current_tile_id)
                                .filter(ImportFile.name == batch)
                                ).scalar()
    if not next_sprite_tile_id:
        return None, None
    game_object_data = (db.query(GameObject, SpriteTile)
                        .join(SpriteTile)
                        .filter(SpriteTile.game_object_id == next_sprite_tile_id)
                        ).all()
    return game_object_data, next_sprite_tile_id


def get_right_object(batch, current_tile_id, ignore_committed=None, ignore_discarded=None):
    if ignore_committed is None:
        ignore_committed = True
    if ignore_discarded is None:
        ignore_discarded = True

    if ignore_committed and ignore_discarded:
        next_sprite_tile_id = (db.query(func.min(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id > current_tile_id)
                                .filter(ImportFile.name == batch)
                                .filter(GameObject.committed == False)
                                .filter(SpriteTile.discard == False)
                                ).scalar()
    elif ignore_committed:
        next_sprite_tile_id = (db.query(func.min(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id > current_tile_id)
                                .filter(ImportFile.name == batch)
                                .filter(GameObject.committed == False)
                                ).scalar()
    elif ignore_discarded:
        next_sprite_tile_id = (db.query(func.min(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id > current_tile_id)
                                .filter(ImportFile.name == batch)
                                .filter(SpriteTile.discard == False)
                                ).scalar()
    else:
        next_sprite_tile_id = (db.query(func.min(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id > current_tile_id)
                                .filter(ImportFile.name == batch)
                                ).scalar()
    if not next_sprite_tile_id:
        return None, None
    game_object_data = (db.query(GameObject, SpriteTile)
                        .join(SpriteTile)
                        .filter(SpriteTile.game_object_id == next_sprite_tile_id)
                        ).all()
    return game_object_data, next_sprite_tile_id


def get_up_object(batch, current_tile_id, ignore_committed=None, ignore_discarded=None):
    if ignore_committed is None:
        ignore_committed = True
    if ignore_discarded is None:
        ignore_discarded = True

    row_size = (db.query(ImportFile.row_size)).filter(ImportFile.name == batch).first()[0]

    if ignore_committed and ignore_discarded:
        next_sprite_tile_id = (db.query(func.max(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id % row_size == current_tile_id % row_size)
                                .filter(SpriteTile.id < current_tile_id)
                                .filter(ImportFile.name == batch)
                                .filter(GameObject.committed == False)
                                .filter(SpriteTile.discard == False)
                                ).scalar()
    elif ignore_committed:
        next_sprite_tile_id = (db.query(func.max(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id % row_size == current_tile_id % row_size)
                                .filter(SpriteTile.id < current_tile_id)
                                .filter(ImportFile.name == batch)
                                .filter(GameObject.committed == False)
                                ).scalar()
    elif ignore_discarded:
        next_sprite_tile_id = (db.query(func.max(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id % row_size == current_tile_id % row_size)
                                .filter(SpriteTile.id < current_tile_id)
                                .filter(ImportFile.name == batch)
                                .filter(SpriteTile.discard == False)
                                ).scalar()
    else:
        next_sprite_tile_id = (db.query(func.max(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id % row_size == current_tile_id % row_size)
                                .filter(SpriteTile.id < current_tile_id)
                                .filter(ImportFile.name == batch)
                                ).scalar()
    if not next_sprite_tile_id:
        return None, None
    game_object_data = (db.query(GameObject, SpriteTile)
                        .join(SpriteTile)
                        .filter(SpriteTile.game_object_id == next_sprite_tile_id)
                        ).all()
    return game_object_data, next_sprite_tile_id


def get_down_object(batch, current_tile_id, ignore_committed=None, ignore_discarded=None):
    if ignore_committed is None:
        ignore_committed = True
    if ignore_discarded is None:
        ignore_discarded = True

    row_size = (db.query(ImportFile.row_size)).filter(ImportFile.name == batch).first()[0]

    if ignore_committed and ignore_discarded:
        next_sprite_tile_id = (db.query(func.min(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id % row_size == current_tile_id % row_size)
                                .filter(SpriteTile.id > current_tile_id)
                                .filter(ImportFile.name == batch)
                                .filter(GameObject.committed == False)
                                .filter(SpriteTile.discard == False)
                                ).scalar()
    elif ignore_committed:
        next_sprite_tile_id = (db.query(func.min(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id % row_size == current_tile_id % row_size)
                                .filter(SpriteTile.id > current_tile_id)
                                .filter(ImportFile.name == batch)
                                .filter(GameObject.committed == False)
                                ).scalar()
    elif ignore_discarded:
        next_sprite_tile_id = (db.query(func.min(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id % row_size == current_tile_id % row_size)
                                .filter(SpriteTile.id > current_tile_id)
                                .filter(ImportFile.name == batch)
                                .filter(SpriteTile.discard == False)
                                ).scalar()
    else:
        next_sprite_tile_id = (db.query(func.min(SpriteTile.id))
                                .join(GameObject)
                                .join(ImportFile)
                                .filter(SpriteTile.id % row_size == current_tile_id % row_size)
                                .filter(SpriteTile.id > current_tile_id)
                                .filter(ImportFile.name == batch)
                                ).scalar()
    if not next_sprite_tile_id:
        return None, None
    game_object_data = (db.query(GameObject, SpriteTile)
                        .join(SpriteTile)
                        .filter(SpriteTile.game_object_id == next_sprite_tile_id)
                        ).all()
    return game_object_data, next_sprite_tile_id


def get_tile_col_num(row_size, tile_id):
    modulo = tile_id % row_size
    if modulo == 0:
        return row_size
    else:
        return modulo


if __name__ == '__main__':
    import code
    all_vars = globals().copy()
    all_vars.update(locals())
    shell = code.InteractiveConsole(all_vars)
    shell.interact()
