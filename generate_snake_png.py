import os, base64

JPEG_BASE64 = (
    "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAAIAAgDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/8VAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIRAxEAPwCwAA8A/9k="
)

def main():
    base = os.path.dirname(__file__) or os.getcwd()
    static_dir = os.path.join(base, "static")
    os.makedirs(static_dir, exist_ok=True)
    out_path = os.path.join(static_dir, "snake3d.jpeg")
    data = base64.b64decode(JPEG_BASE64)
    with open(out_path, "wb") as f:
        f.write(data)
    print("Wrote:", out_path)

if __name__ == '__main__':
    main()
