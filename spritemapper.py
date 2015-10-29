from PIL import Image
from os import path, makedirs


frame_size = (32, 32)
filename = 'mega.png'
spritesheet = Image.open(filename)
spritesheet.load()
processed_directory = 'processed'
archive_directory = 'archive'

print(spritesheet.format, spritesheet.size, spritesheet.mode)

x_tiles = int(spritesheet.size[0] / frame_size[0])
y_tiles = int(spritesheet.size[1] / frame_size[1])
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
        left = frame_size[0] * tile
        top = frame_size[1] * row
        right = left + frame_size[0]
        bottom = top + frame_size[1]
        box = (left, top, right, bottom)

        frame_image = spritesheet.crop(box)
        tile_number += 1
        tile_file = path.join(processed_directory, ''.join([str(tile_number), '.png']))
        frame_image.save(tile_file)
