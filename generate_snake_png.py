import os, base64

PNG_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVQYV2NgYAAAAAMAASsJTYQAAAAASUVORK5CYII="
)

def main():
    base = os.path.dirname(__file__) or os.getcwd()
    static_dir = os.path.join(base, "static")
    os.makedirs(static_dir, exist_ok=True)
    out_path = os.path.join(static_dir, "snake.png")
    data = base64.b64decode(PNG_BASE64)
    with open(out_path, "wb") as f:
        f.write(data)
    print("Wrote:", out_path)

if __name__ == '__main__':
    main()
