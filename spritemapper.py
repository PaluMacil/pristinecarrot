from PIL import Image
from os import path, makedirs


size = (32, 32)
filename = 'mega.png'
myimage = Image.open(filename)
myimage.load()
processed_directory = 'processed'
archive_directory = 'archive'

print(myimage.format, myimage.size, myimage.mode)

x_tiles = int(myimage.size[0] / size[0])
y_tiles = int(myimage.size[1] / size[1])
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
        left = size[0] * tile
        top = size[1] * row
        right = left + size[0]
        bottom = top + size[1]
        box = (left, top, right, bottom)

        tile_image = myimage.crop(box)
        tile_number += 1
        tile_file = path.join(processed_directory, ''.join([str(tile_number), '.png']))
        tile_image.save(tile_file)
