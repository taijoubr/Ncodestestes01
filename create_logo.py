import os
import math
import base64
import json
import hashlib
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 1024x1024 High Resolution Canvas
width, height = 1024, 1024
image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

cx, cy = 512, 512
radius = 470

# Load Fonts
try:
    font_top = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 46)
    font_bottom = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", 52)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", 28)
except Exception:
    font_top = font_bottom = font_sub = ImageFont.load_default()

# --- 1. OUTER ORNATE BRONZE / GOLD RING ---
# Draw metallic gradient ring
for r in range(radius, radius - 55, -1):
    factor = (radius - r) / 55.0
    # Gold/Bronze gradient shades
    red = int(190 + 45 * math.sin(factor * math.pi))
    green = int(150 + 35 * math.sin(factor * math.pi))
    blue = int(85 + 25 * math.sin(factor * math.pi))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(red, green, blue, 255), width=2)

# Outer and Inner Rim Borders
draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=(100, 75, 35, 255), width=4)
draw.ellipse([cx - radius + 55, cy - radius + 55, cx + radius - 55, cy + radius - 55], outline=(90, 65, 30, 255), width=4)

# Inner background inside frame
inner_r = radius - 55
draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r], fill=(255, 255, 255, 255))

# Ornate Flourish Accents at 12, 3, 6, 9 o'clock on outer frame
def draw_filigree(draw_obj, x, y, size=24):
    draw_obj.ellipse([x - size, y - size, x + size, y + size], fill=(210, 165, 80, 255), outline=(100, 70, 30, 255), width=3)
    draw_obj.ellipse([x - size/2, y - size/2, x + size/2, y + size/2], fill=(240, 200, 110, 255))

draw_filigree(draw, cx, cy - radius + 28, 18)
draw_filigree(draw, cx, cy + radius - 28, 18)
draw_filigree(draw, cx - radius + 28, cy, 18)
draw_filigree(draw, cx + radius - 28, cy, 18)


# --- 2. TOP BLUE RIBBON BANNER ---
top_outer_r = inner_r
top_inner_r = inner_r - 95

points_top = []
# Top arc from 210 deg to 330 deg (where 270 is 12 o'clock top)
for angle in range(205, 336, 1):
    rad = math.radians(angle)
    points_top.append((cx + top_outer_r * math.cos(rad), cy + top_outer_r * math.sin(rad)))
for angle in range(335, 204, -1):
    rad = math.radians(angle)
    points_top.append((cx + top_inner_r * math.cos(rad), cy + top_inner_r * math.sin(rad)))

banner_mask_top = Image.new("L", (width, height), 0)
d_mask_top = ImageDraw.Draw(banner_mask_top)
d_mask_top.polygon(points_top, fill=255)

blue_ribbon = Image.new("RGBA", (width, height), (18, 65, 135, 255))
image.paste(blue_ribbon, (0, 0), banner_mask_top)
draw.polygon(points_top, outline=(220, 180, 95, 255), width=4)


# --- 3. BOTTOM BLUE RIBBON BANNER ---
bottom_outer_r = inner_r - 20
bottom_inner_r = inner_r - 110

points_bottom = []
for angle in range(30, 151, 1):
    rad = math.radians(angle)
    points_bottom.append((cx + bottom_outer_r * math.cos(rad), cy + bottom_outer_r * math.sin(rad)))
for angle in range(150, 29, -1):
    rad = math.radians(angle)
    points_bottom.append((cx + bottom_inner_r * math.cos(rad), cy + bottom_inner_r * math.sin(rad)))

banner_mask_bottom = Image.new("L", (width, height), 0)
d_mask_bottom = ImageDraw.Draw(banner_mask_bottom)
d_mask_bottom.polygon(points_bottom, fill=255)

image.paste(blue_ribbon, (0, 0), banner_mask_bottom)
draw.polygon(points_bottom, outline=(220, 180, 95, 255), width=4)


# --- 4. SACRED TREES (BAOBAB / ODÉ TREES) ---
def draw_sacred_tree(draw_obj, base_x, base_y, is_left=True):
    dir_m = -1 if is_left else 1
    trunk_col = (115, 78, 48, 255)
    leaf_dark = (40, 85, 35, 255)
    leaf_light = (65, 125, 50, 255)

    # Thick twisted trunk
    trunk_pts = [
        (base_x, base_y + 140),
        (base_x + 35 * dir_m, base_y + 70),
        (base_x + 20 * dir_m, base_y),
        (base_x + 55 * dir_m, base_y - 90),
        (base_x + 15 * dir_m, base_y - 140)
    ]
    for i in range(len(trunk_pts) - 1):
        draw_obj.line([trunk_pts[i], trunk_pts[i+1]], fill=trunk_col, width=36)
        # Bark lines
        p1 = trunk_pts[i]
        p2 = trunk_pts[i+1]
        draw_obj.line([(p1[0]+4, p1[1]), (p2[0]+4, p2[1])], fill=(85, 55, 30, 255), width=6)

    # Tree Foliage Canopy
    canopy_x = base_x + 30 * dir_m
    canopy_y = base_y - 150
    clusters = [(-45, -30, 65), (45, -30, 65), (0, -70, 80), (-30, 15, 60), (30, 15, 60)]
    for dx, dy, r in clusters:
        cx_c, cy_c = canopy_x + dx, canopy_y + dy
        draw_obj.ellipse([cx_c - r, cy_c - r, cx_c + r, cy_c + r], fill=leaf_dark)
        draw_obj.ellipse([cx_c - r + 6, cy_c - r + 6, cx_c + r - 6, cy_c + r - 6], fill=leaf_light)

    # Hunting Bow & Arrow (Ofá)
    bow_color = (35, 100, 185, 255) # Electric/Sacred Blue
    bow_x = base_x + 25 * dir_m
    bow_y = base_y - 10
    
    # Bow Arc
    bbox = [bow_x - 55, bow_y - 85, bow_x + 55, bow_y + 85]
    s_deg = 270 if is_left else 90
    e_deg = 90 if is_left else 270
    draw_obj.arc(bbox, start=s_deg, end=e_deg, fill=bow_color, width=8)
    
    # Bow String
    str_x = bow_x + (25 if is_left else -25)
    draw_obj.line([(str_x, bow_y - 80), (str_x, bow_y + 80)], fill=(235, 235, 235, 255), width=3)
    
    # Arrow
    arr_dir = 1 if is_left else -1
    arr_start_x = bow_x - 60 * arr_dir
    arr_end_x = bow_x + 85 * arr_dir
    draw_obj.line([(arr_start_x, bow_y), (arr_end_x, bow_y)], fill=(215, 185, 130, 255), width=5)
    # Arrow Head
    tip_x = arr_end_x
    draw_obj.polygon([(tip_x, bow_y - 10), (tip_x + 16 * arr_dir, bow_y), (tip_x, bow_y + 10)], fill=bow_color)

draw_sacred_tree(draw, 270, 480, is_left=True)
draw_sacred_tree(draw, 754, 480, is_left=False)


# --- 5. ELEPHANT HEAD (EFON / AFON) IN CENTER ---
# Large Ears
draw.ellipse([cx - 245, cy - 150, cx - 30, cy + 110], fill=(230, 230, 235, 255), outline=(160, 160, 165, 255), width=4)
draw.ellipse([cx + 30, cy - 150, cx + 245, cy + 110], fill=(230, 230, 235, 255), outline=(160, 160, 165, 255), width=4)
# Ear shading inside
draw.ellipse([cx - 205, cy - 115, cx - 55, cy + 75], fill=(218, 212, 218, 255))
draw.ellipse([cx + 55, cy - 115, cx + 205, cy + 75], fill=(218, 212, 218, 255))

# Head Dome
draw.ellipse([cx - 120, cy - 175, cx + 120, cy + 40], fill=(240, 240, 245, 255), outline=(150, 150, 155, 255), width=4)

# Eyes
draw.ellipse([cx - 70, cy - 45, cx - 44, cy - 25], fill=(50, 50, 55, 255))
draw.ellipse([cx + 44, cy - 45, cx + 70, cy - 25], fill=(50, 50, 55, 255))
draw.ellipse([cx - 62, cy - 40, cx - 56, cy - 34], fill=(255, 255, 255, 255))
draw.ellipse([cx + 56, cy - 40, cx + 62, cy - 34], fill=(255, 255, 255, 255))

# Trunk
trunk_poly = [
    (cx - 45, cy + 15),
    (cx + 45, cy + 15),
    (cx + 32, cy + 190),
    (cx + 18, cy + 275),
    (cx - 18, cy + 275),
    (cx - 32, cy + 190)
]
draw.polygon(trunk_poly, fill=(235, 235, 240, 255), outline=(150, 150, 155, 255))

# Trunk wrinkles
for ty in range(cy + 40, cy + 250, 22):
    w = int(36 - (ty - (cy + 40)) * 0.09)
    draw.line([(cx - w, ty), (cx + w, ty)], fill=(175, 175, 180, 255), width=3)

# Ivory Tusks
tusk_l = [(cx - 42, cy + 30), (cx - 95, cy + 140), (cx - 75, cy + 160), (cx - 24, cy + 50)]
draw.polygon(tusk_l, fill=(255, 254, 245, 255), outline=(185, 175, 140, 255))

tusk_r = [(cx + 42, cy + 30), (cx + 95, cy + 140), (cx + 75, cy + 160), (cx + 24, cy + 50)]
draw.polygon(tusk_r, fill=(255, 254, 245, 255), outline=(185, 175, 140, 255))


# --- 6. CURVED TEXT ON TOP & BOTTOM BANNERS (RIGHT SIDE UP) ---

# TOP BANNER: "ASE EGBE EFON"
top_text = "ASE EGBE EFON"
top_text_r = inner_r - 48
angle_step = 8.2
start_angle = 270 - ((len(top_text) - 1) * angle_step / 2.0)

for i, char in enumerate(top_text):
    ang_deg = start_angle + i * angle_step
    ang_rad = math.radians(ang_deg)
    tx = cx + top_text_r * math.cos(ang_rad)
    ty = cy + top_text_r * math.sin(ang_rad)
    
    char_img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(char_img)
    cdraw.text((50, 50), char, font=font_top, fill=(255, 255, 255, 255), anchor="mm")
    
    # Correct angle calculation for upright letters along top curve:
    rot_angle = ang_deg - 270
    rotated_char = char_img.rotate(-rot_angle, resample=Image.BICUBIC)
    image.paste(rotated_char, (int(tx - 50), int(ty - 50)), rotated_char)


# BOTTOM BANNER: "Odé Alayo"
bottom_text = "Odé Alayo"
bottom_text_r = inner_r - 65
angle_step_b = 9.5
start_angle_b = 90 - ((len(bottom_text) - 1) * angle_step_b / 2.0)

for i, char in enumerate(bottom_text):
    ang_deg = start_angle_b + i * angle_step_b
    ang_rad = math.radians(ang_deg)
    tx = cx + bottom_text_r * math.cos(ang_rad)
    ty = cy + bottom_text_r * math.sin(ang_rad)
    
    char_img = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(char_img)
    cdraw.text((50, 50), char, font=font_bottom, fill=(255, 255, 255, 255), anchor="mm")
    
    # Correct angle calculation for upright letters along bottom curve:
    rot_angle = ang_deg - 90
    rotated_char = char_img.rotate(-rot_angle, resample=Image.BICUBIC)
    image.paste(rotated_char, (int(tx - 50), int(ty - 50)), rotated_char)


# SUBTEXT BELOW BOTTOM BANNER: "Desde 2024"
draw.text((cx, cy + 400), "Desde 2024", font=font_sub, fill=(210, 170, 95, 255), anchor="mm")


# Save High Quality Logo Image
os.makedirs("static/images", exist_ok=True)
output_path = "static/images/logo.png"
image.save(output_path, "PNG")
print(f"High-res emblem logo generated at {output_path}")

# Encode to base64 and update cache/database
with open(output_path, "rb") as f:
    data = f.read()

b64_str = base64.b64encode(data).decode("utf-8")
ver_str = hashlib.md5(data).hexdigest()[:10]

with open("static/images/logo_b64.json", "w") as f:
    json.dump({"b64": b64_str, "mime": "image/png", "version": ver_str}, f)

# Save to /tmp/logo.png
with open("/tmp/logo.png", "wb") as f:
    f.write(data)

# Update SQLite Database
try:
    from app.database import SessionLocal
    from app.models import ConfiguracaoSistema
    db = SessionLocal()
    
    c_b64 = db.query(ConfiguracaoSistema).filter(ConfiguracaoSistema.chave == "logo_b64").first()
    if not c_b64:
        db.add(ConfiguracaoSistema(chave="logo_b64", valor=b64_str))
    else:
        c_b64.valor = b64_str

    c_mime = db.query(ConfiguracaoSistema).filter(ConfiguracaoSistema.chave == "logo_mime").first()
    if not c_mime:
        db.add(ConfiguracaoSistema(chave="logo_mime", valor="image/png"))
    else:
        c_mime.valor = "image/png"
        
    db.commit()
    db.close()
    print("Successfully updated logo in SQLite DB!")
except Exception as e:
    print(f"Error updating SQLite: {e}")

# Update global logo cache in main module
try:
    from app.main import set_global_logo_cache
    set_global_logo_cache(data, "image/png")
    print("Successfully updated global logo cache in memory!")
except Exception as e:
    print(f"Error updating memory cache: {e}")

