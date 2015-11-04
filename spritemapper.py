from PIL import Image
from os import path, makedirs
from config import get_config


def analyze_spritesheet(filename, x_size, y_size):
    spritesheet = Image.open(filename)
    spritesheet.load()
    print("analysis completed... yeah, that's all you get for now")


def slice_spritesheet(filename, x_size, y_size):
    spritesheet = Image.open(filename)
    spritesheet.load()
    processed_directory = get_config('processed', 'directory')
    archive_directory = get_config('archive', 'directory')

    print(spritesheet.format, spritesheet.size, spritesheet.mode)

    x_tiles = int(spritesheet.size[0] / x_size)
    y_tiles = int(spritesheet.size[1] / y_size)
    print(x_tiles, y_tiles, sep=',')

    if not path.exists(processed_directory):
        makedirs(processed_directory)
    if not path.exists(archive_directory):
        makedirs(archive_directory)

    tile_number = 0
    # Process row
    for row in range(y_tiles):
        # Process tiles
        for tile in range(x_tiles):
            left = x_size * tile
            top = y_size * row
            right = left + x_size
            bottom = top + y_size
            box = (left, top, right, bottom)

            frame_image = spritesheet.crop(box)
            tile_number += 1
            tile_file = path.join(processed_directory, ''.join([str(tile_number), '.png']))
            frame_image.save(tile_file)
