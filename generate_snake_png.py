import os

def main():
    base = os.path.dirname(__file__) or os.getcwd()
    static_dir = os.path.join(base, "static")
    os.makedirs(static_dir, exist_ok=True)
    out_path = os.path.join(static_dir, "snake3d.jpeg")
    
    # Try to create a proper snake icon using PIL
    try:
        from PIL import Image, ImageDraw
        
        # Create a 64x64 image with a green snake head
        img = Image.new('RGB', (64, 64), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw a green snake head (circle)
        draw.ellipse([10, 10, 54, 54], fill=(0, 200, 0), outline=(0, 150, 0))
        # Draw eyes
        draw.ellipse([20, 22, 28, 30], fill=(255, 255, 255))
        draw.ellipse([36, 22, 44, 30], fill=(255, 255, 255))
        # Draw pupils
        draw.ellipse([22, 24, 26, 28], fill=(0, 0, 0))
        draw.ellipse([38, 24, 42, 28], fill=(0, 0, 0))
        
        img.save(out_path, 'JPEG')
        print("Created snake icon:", out_path)
    except ImportError:
        # Fallback: use a valid JPEG base64 (64x64 green square)
        import base64
        JPEG_BASE64 = (
            "/9j/4AAQSkZJRgABAQEAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k="
        )
        data = base64.b64decode(JPEG_BASE64)
        with open(out_path, "wb") as f:
            f.write(data)
        print("Created fallback icon:", out_path)

if __name__ == '__main__':
    main()
