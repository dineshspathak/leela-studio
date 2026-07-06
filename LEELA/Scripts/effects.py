#!/usr/bin/env python3
import os
import sys
import subprocess
import random

try:
    from PIL import Image, ImageFilter, ImageOps, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow is required. Install it using: pip install pillow")
    sys.exit(1)

# Try importing cv2 for face-aware zoom, fall back gracefully if not present
OPENCV_AVAILABLE = False
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    pass

def detect_face_center(image_path):
    """Detect the primary face center in the image using OpenCV.
    Returns (x_ratio, y_ratio) or (0.5, 0.5) if not found or CV2 not available."""
    if not OPENCV_AVAILABLE:
        return 0.5, 0.5
        
    try:
        img = cv2.imread(image_path)
        if img is None:
            return 0.5, 0.5
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        face_cascade = cv2.CascadeClassifier(cascade_path)
        
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
        
        if len(faces) > 0:
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            fx, fy, fw, fh = largest_face
            face_center_x = fx + fw / 2.0
            face_center_y = fy + fh / 2.0
            
            h, w = img.shape[:2]
            return face_center_x / w, face_center_y / h
    except Exception as e:
        print(f"Warning: Face detection failed, using center fallback. Details: {e}")
        
    return 0.5, 0.5

def draw_subtitle_on_frame(image, text, font_size=32):
    """Draw white subtitle text with a black outline at the bottom center of the frame."""
    draw = ImageDraw.Draw(image)
    width, height = image.size
    
    font = None
    # Try various system fonts that support Hindi Devanagari
    fonts_to_try = [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/KohinoorDevanagari.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "Arial"
    ]
    for f in fonts_to_try:
        try:
            font = ImageFont.truetype(f, font_size)
            break
        except:
            continue
            
    if not font:
        font = ImageFont.load_default()
        
    # Get text dimensions
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
    except AttributeError:
        text_w, text_h = draw.textsize(text, font=font)
        
    x = (width - text_w) // 2
    # Place it at y = height - 55 so it sits centered inside the bottom black bar (y=height-80 to height)
    y = height - 55
    
    # Draw black outline
    outline_size = 2
    for dx in range(-outline_size, outline_size + 1):
        for dy in range(-outline_size, outline_size + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill="black")
                
    # Draw main white text
    draw.text((x, y), text, font=font, fill="white")

def generate_ken_burns(image_path, output_path, duration, fps=30, motion_type="random", width=1920, height=1080, subtitle_text=None):
    """
    Generate a Ken Burns effect MP4 from a still image using Pillow.
    Frames are piped directly into FFmpeg to avoid disk writes.
    """
    try:
        img = Image.open(image_path)
    except Exception as e:
        print(f"Error opening image {image_path}: {e}")
        return False
        
    img_w, img_h = img.size
    total_frames = int(duration * fps)
    
    # Get primary subject center
    center_x_ratio, center_y_ratio = detect_face_center(image_path)
    
    # If motion is random, choose one
    motions = ["zoom_in", "zoom_out", "pan_left", "pan_right", "pan_up", "pan_down", "zoom_pan"]
    if motion_type == "random":
        motion_type = random.choice(motions)
        
    aspect_ratio = width / height
    
    crop_w = int(img_w * 0.85)
    crop_h = int(crop_w / aspect_ratio)
    if crop_h > img_h:
        crop_h = int(img_h * 0.85)
        crop_w = int(crop_h * aspect_ratio)
        
    # FFmpeg pipe setup
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{width}x{height}",
        "-r", str(fps),
        "-i", "-",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "medium",
        output_path
    ]
    
    try:
        process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"Error starting FFmpeg process: {e}")
        return False
        
    print(f"Generating Ken Burns '{motion_type}' for {os.path.basename(image_path)} ({duration}s)...")
    
    try:
        for f in range(total_frames):
            t = f / max(1, total_frames - 1)  # 0.0 to 1.0
            
            if motion_type == "zoom_in":
                current_scale = 1.0 - (0.2 * t)
                w_box = int(img_w * current_scale)
                h_box = int(w_box / aspect_ratio)
                if h_box > img_h:
                    h_box = img_h
                    w_box = int(h_box * aspect_ratio)
                
                target_cx = int(img_w * center_x_ratio)
                target_cy = int(img_h * center_y_ratio)
                current_cx = int((img_w / 2) * (1 - t) + target_cx * t)
                current_cy = int((img_h / 2) * (1 - t) + target_cy * t)
                
            elif motion_type == "zoom_out":
                current_scale = 0.8 + (0.2 * t)
                w_box = int(img_w * current_scale)
                h_box = int(w_box / aspect_ratio)
                if h_box > img_h:
                    h_box = img_h
                    w_box = int(h_box * aspect_ratio)
                
                target_cx = int(img_w * center_x_ratio)
                target_cy = int(img_h * center_y_ratio)
                current_cx = int(target_cx * (1 - t) + (img_w / 2) * t)
                current_cy = int(target_cy * (1 - t) + (img_h / 2) * t)
                
            elif motion_type == "pan_left":
                w_box, h_box = crop_w, crop_h
                current_cy = img_h // 2
                max_shift = (img_w - w_box) // 2
                current_cx = (img_w // 2) + int(max_shift * (1 - 2 * t))
                
            elif motion_type == "pan_right":
                w_box, h_box = crop_w, crop_h
                current_cy = img_h // 2
                max_shift = (img_w - w_box) // 2
                current_cx = (img_w // 2) - int(max_shift * (1 - 2 * t))
                
            elif motion_type == "pan_up":
                w_box, h_box = crop_w, crop_h
                current_cx = img_w // 2
                max_shift = (img_h - h_box) // 2
                current_cy = (img_h // 2) + int(max_shift * (1 - 2 * t))
                
            elif motion_type == "pan_down":
                w_box, h_box = crop_w, crop_h
                current_cx = img_w // 2
                max_shift = (img_h - h_box) // 2
                current_cy = (img_h // 2) - int(max_shift * (1 - 2 * t))
                
            elif motion_type == "zoom_pan":
                current_scale = 1.0 - (0.15 * t)
                w_box = int(img_w * current_scale)
                h_box = int(w_box / aspect_ratio)
                max_x_shift = (img_w - w_box) // 2
                current_cx = (img_w // 2) - int(max_x_shift * 0.5 * t)
                current_cy = img_h // 2
                
            else:
                w_box, h_box = crop_w, crop_h
                current_cx, current_cy = img_w // 2, img_h // 2
                
            x1 = max(0, current_cx - w_box // 2)
            y1 = max(0, current_cy - h_box // 2)
            x2 = min(img_w, x1 + w_box)
            y2 = min(img_h, y1 + h_box)
            
            if x2 - x1 < w_box:
                x1 = max(0, x2 - w_box)
            if y2 - y1 < h_box:
                y1 = max(0, y2 - h_box)
                
            cropped = img.crop((x1, y1, x2, y2))
            resized = cropped.resize((width, height), Image.Resampling.LANCZOS)
            
            # Draw subtitles if specified
            if subtitle_text:
                draw_subtitle_on_frame(resized, subtitle_text)
                
            rgb_data = resized.convert("RGB").tobytes()
            process.stdin.write(rgb_data)
            
        process.stdin.close()
        process.wait()
        return True
    except Exception as e:
        print(f"Error rendering frames: {e}")
        if process:
            try:
                process.kill()
            except:
                pass
        return False

if __name__ == "__main__":
    if len(sys.argv) > 2:
        generate_ken_burns(sys.argv[1], sys.argv[2], 5, motion_type="zoom_in")
    else:
        print("Usage: python3 effects.py <input_image> <output_video>")
