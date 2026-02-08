import cv2
from PIL import Image
import os
import math

# Import our existing functions from mosaic_maker
from mosaic_maker import color_distance, get_average_color, load_tiles, find_best_tile

# Configuration
TARGET_WIDTH = 2160
TARGET_HEIGHT = 3840
TILES_WIDE = 100
FPS = 15

# Calculate tile dimensions (9:16 aspect ratio for vertical tiles)
TILE_WIDTH = TARGET_WIDTH // TILES_WIDE
TILE_HEIGHT = int(TILE_WIDTH * (16/9))
TILES_HIGH = TARGET_HEIGHT // TILE_HEIGHT

# File paths
VIDEO_INPUT = "images/Disco Video.MOV"
TILES_FOLDER = "tiles"
OUTPUT_VIDEO = "output/mosaic_video.mp4"
TEMP_FRAMES_FOLDER = "temp_frames"

def extract_frames_from_video(video_path, target_fps):
    """Extract frames from video at specified fps"""
    print(f"Opening video: {video_path}")
    
    # Open the video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return []
    
    # Get video properties
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / original_fps
    
    print(f"Video info:")
    print(f"  Original FPS: {original_fps}")
    print(f"  Total frames: {total_frames}")
    print(f"  Duration: {duration:.2f} seconds")
    print(f"  Extracting at: {target_fps} fps")
    
    # Calculate frame interval
    frame_interval = int(original_fps / target_fps)
    
    frames = []
    frame_count = 0
    extracted_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Extract frame at intervals
        if frame_count % frame_interval == 0:
            # Convert BGR (OpenCV) to RGB (PIL)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Resize to target dimensions
            pil_image = pil_image.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
            
            frames.append(pil_image)
            extracted_count += 1
            
            if extracted_count % 10 == 0:
                print(f"  Extracted {extracted_count} frames...")
        
        frame_count += 1
    
    cap.release()
    print(f"✓ Extracted {len(frames)} frames total")
    return frames

def create_mosaic_frame(frame, tiles, tile_width, tile_height, tiles_wide, tiles_high):
    """Apply mosaic effect to a single frame"""
    mosaic = Image.new('RGB', (tiles_wide * tile_width, tiles_high * tile_height))
    
    for row in range(tiles_high):
        for col in range(tiles_wide):
            x = col * tile_width
            y = row * tile_height
            
            # Get region from frame
            region = frame.crop((x, y, x + tile_width, y + tile_height))
            
            # Get average color
            target_color = get_average_color(region)
            
            # Find best matching tile
            best_tile = find_best_tile(target_color, tiles)
            
            # Paste tile
            mosaic.paste(best_tile['image'], (x, y))
    
    return mosaic

def create_video_mosaic():
    """Main function to create video mosaic"""
    print("="*50)
    print("VIDEO MOSAIC CREATOR")
    print("="*50)
    
    # Show tile configuration
    print(f"\nMosaic grid: {TILES_WIDE} × {TILES_HIGH} tiles")
    print(f"Tile size: {TILE_WIDTH}x{TILE_HEIGHT} pixels (9:16 aspect ratio)")
    
    # Load tiles
    print("\nLoading disco ball tiles...")
    tiles = load_tiles(TILES_FOLDER, (TILE_WIDTH, TILE_HEIGHT))
    
    if len(tiles) == 0:
        print("Error: No tiles loaded!")
        return
    
    # Extract frames from video
    print("\nExtracting frames from video...")
    frames = extract_frames_from_video(VIDEO_INPUT, FPS)
    
    if len(frames) == 0:
        print("Error: No frames extracted!")
        return
    
    # Create temp directory for processed frames
    os.makedirs(TEMP_FRAMES_FOLDER, exist_ok=True)
    
    # Process each frame
    print(f"\nProcessing {len(frames)} frames into mosaics...")
    print("This will take a while - grab a coffee! ☕")
    
    for i, frame in enumerate(frames):
        print(f"  Frame {i+1}/{len(frames)}...", end='\r')
        
        # Create mosaic for this frame
        mosaic_frame = create_mosaic_frame(frame, tiles, TILE_WIDTH, TILE_HEIGHT, TILES_WIDE, TILES_HIGH)
        
        # Save as temp file
        temp_path = os.path.join(TEMP_FRAMES_FOLDER, f"frame_{i:04d}.jpg")
        mosaic_frame.save(temp_path, quality=95)
    
    print(f"\n✓ All frames processed!")
    
    # Compile frames into video
    print("\nCompiling frames into video...")
    
    # Read first frame to get dimensions
    first_frame = cv2.imread(os.path.join(TEMP_FRAMES_FOLDER, "frame_0000.jpg"))
    height, width, _ = first_frame.shape
    
    # Create video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, FPS, (width, height))
    
    # Write all frames
    for i in range(len(frames)):
        frame_path = os.path.join(TEMP_FRAMES_FOLDER, f"frame_{i:04d}.jpg")
        frame = cv2.imread(frame_path)
        out.write(frame)
    
    out.release()
    
    # Clean up temp files
    print("Cleaning up temporary files...")
    for i in range(len(frames)):
        frame_path = os.path.join(TEMP_FRAMES_FOLDER, f"frame_{i:04d}.jpg")
        os.remove(frame_path)
    os.rmdir(TEMP_FRAMES_FOLDER)
    
    print("="*50)
    print("✓ VIDEO MOSAIC COMPLETE!")
    print(f"Saved to: {OUTPUT_VIDEO}")
    print("="*50)

if __name__ == "__main__":
    create_video_mosaic()
