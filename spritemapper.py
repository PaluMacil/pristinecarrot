from PIL import Image
from os import path
from config import get_config


def analyze_spritesheet(filename, x_size, y_size):
    spritesheet = Image.open(filename)
    spritesheet.load()
    x_tiles = int(spritesheet.size[0] / x_size)
    y_tiles = int(spritesheet.size[1] / y_size)
    return spritesheet.format, spritesheet.size, spritesheet.mode, x_tiles, y_tiles


def slice_spritesheet(filename, x_size, y_size):
    spritesheet = Image.open(filename)
    spritesheet.load()
    processed_directory = get_config('processed', 'directory')

    x_tiles = int(spritesheet.size[0] / x_size)
    y_tiles = int(spritesheet.size[1] / y_size)

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
