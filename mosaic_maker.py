from PIL import Image
import os
import math

# Configuration - these are the settings for our mosaic
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
TILES_WIDE = 50

# File paths - where to find our images
TILES_FOLDER = "tiles"
TARGET_IMAGE = "images/target.jpg"
OUTPUT_IMAGE = "output/mosaic.jpg"

def color_distance(color1, color2):
    """Calculate how different two colors are"""
    r_diff = color1[0] - color2[0]
    g_diff = color1[1] - color2[1]
    b_diff = color1[2] - color2[2]
    
    distance = math.sqrt(r_diff**2 + g_diff**2 + b_diff**2)
    return distance

def get_average_color(image):
    """Calculate the average color of an image"""
    pixels = list(image.getdata())
    
    total_r = sum(pixel[0] for pixel in pixels)
    total_g = sum(pixel[1] for pixel in pixels)
    total_b = sum(pixel[2] for pixel in pixels)
    
    num_pixels = len(pixels)
    
    avg_r = total_r / num_pixels
    avg_g = total_g / num_pixels
    avg_b = total_b / num_pixels
    
    return (avg_r, avg_g, avg_b)

def load_tiles(tiles_folder, tile_size):
    """Load all disco ball images and resize them"""
    print(f"Loading tiles from {tiles_folder}...")
    
    # Handle both single size (square) and tuple (width, height)
    if isinstance(tile_size, tuple):
        tile_width, tile_height = tile_size
    else:
        tile_width = tile_height = tile_size
    
    tiles = []
    tile_files = sorted(os.listdir(tiles_folder))
    
    for filename in tile_files:
        if filename.endswith('.png') or filename.endswith('.jpg'):
            try:
                filepath = os.path.join(tiles_folder, filename)
                tile_image = Image.open(filepath)
                tile_image = tile_image.resize((tile_width, tile_height), Image.Resampling.LANCZOS)
                
                avg_color = get_average_color(tile_image)
                
                tiles.append({
                    'image': tile_image,
                    'avg_color': avg_color,
                    'filename': filename
                })
                
                print(f"  Loaded {filename} - avg color: ({int(avg_color[0])}, {int(avg_color[1])}, {int(avg_color[2])})")
            except Exception as e:
                print(f"  Skipping {filename} - couldn't load: {e}")
    
    print(f"Loaded {len(tiles)} tiles total")
    return tiles

def find_best_tile(target_color, tiles):
    """Find which disco ball tile best matches a target color"""
    best_tile = tiles[0]
    best_distance = color_distance(target_color, best_tile['avg_color'])
    
    for tile in tiles:
        distance = color_distance(target_color, tile['avg_color'])
        if distance < best_distance:
            best_distance = distance
            best_tile = tile
    
    return best_tile

def create_mosaic(target_path, tiles_folder, output_path, tiles_wide):
    """The main function that creates the mosaic"""
    print("Starting mosaic creation...")
    
    # Load and resize target image
    print(f"Loading target image: {target_path}")
    target = Image.open(target_path)
    target = target.resize((TARGET_WIDTH, TARGET_HEIGHT))
    print(f"Target resized to {TARGET_WIDTH}x{TARGET_HEIGHT}")
    
    # Calculate tile size
    tile_size = TARGET_WIDTH // tiles_wide
    tiles_high = TARGET_HEIGHT // tile_size
    print(f"Each tile will be {tile_size}x{tile_size} pixels")
    print(f"Grid will be {tiles_wide} wide x {tiles_high} high = {tiles_wide * tiles_high} total tiles")
    
    # Load all disco ball tiles
    tiles = load_tiles(tiles_folder, tile_size)
    
    # Create blank canvas for mosaic
    mosaic = Image.new('RGB', (tiles_wide * tile_size, tiles_high * tile_size))
    print(f"Created blank mosaic canvas: {mosaic.size}")
    
    # Build the mosaic tile by tile
    print("Building mosaic...")
    for row in range(tiles_high):
        if row % 10 == 0:
            print(f"  Processing row {row}/{tiles_high}...")
        
        for col in range(tiles_wide):
            # Get the position
            x = col * tile_size
            y = row * tile_size
            
            # Get this section from target image
            region = target.crop((x, y, x + tile_size, y + tile_size))
            
            # Calculate average color of this section
            target_color = get_average_color(region)
            
            # Find best matching disco ball
            best_tile = find_best_tile(target_color, tiles)
            
            # Paste it into the mosaic
            mosaic.paste(best_tile['image'], (x, y))
    
    # Save the final mosaic
    print(f"Saving mosaic to {output_path}...")
    mosaic.save(output_path, quality=95)
    print("✓ Done!")
    
    return mosaic

if __name__ == "__main__":
    print("="*50)
    print("DISCO BALL MOSAIC CREATOR")
    print("="*50)
    
    create_mosaic(
        target_path=TARGET_IMAGE,
        tiles_folder=TILES_FOLDER,
        output_path=OUTPUT_IMAGE,
        tiles_wide=TILES_WIDE
    )
    
    print("="*50)
    print("Your mosaic is ready!")
    print(f"Check the {OUTPUT_IMAGE} file")
    print("="*50)
    