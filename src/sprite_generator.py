from PIL import Image

spritesheet = Image.open("../assets/sprite.png").convert("RGBA")
width, height = spritesheet.size

filename = "dino_sprites.h"
with open(filename, "w") as f:
    f.write("#include <Arduino.h>\n\n")

    sprites_to_extract = [
        ("dino_run_1", 1518, 6, 80, 86),   
        ("dino_run_2", 1606, 6, 80, 86),   
    ]

    print(f"Reading spritesheet of {width}x{height}...\n")

    for name, x, y, w, h in sprites_to_extract:
        sprite_img = spritesheet.crop((x, y, x + w, y + h))
        
        # 2. 2X Reduction
        new_w = w // 2
        new_h = h // 2
        
        sprite_img = sprite_img.resize((new_w, new_h), Image.NEAREST)
        
        num_pixels = new_w * new_h
        f.write(f"// Sprite: {name} | Original Size: {w}x{h} | New Size: {new_w}x{new_h} ({num_pixels} pixels)\n")
        f.write(f"const uint16_t sprite_{name}[{num_pixels}] PROGMEM = {{\n")
        
        bytes_count = 0
        for pixel_y in range(new_h):
            for pixel_x in range(new_w):
                r, g, b, a = sprite_img.getpixel((pixel_x, pixel_y))
                
                if a < 128 or (r > 128 and g > 128 and b > 128):
                    rgb565 = 0x0000
                else:
                    rgb565 = 0xFFFF
                
                f.write(f"0x{rgb565:04X}, ")
                bytes_count += 2
                
            f.write("\n")
        
        f.write("};\n\n")
        print(f"Sprite '{name}' reduced to {new_w}x{new_h} generated ({bytes_count} bytes).")

print(f"\nFile {filename} generated successfully! Contains only the 4 sprites.")
