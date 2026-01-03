from flask import Flask, render_template, request, send_file, jsonify
from PIL import Image, ImageDraw, ImageFont
import os
import math

app = Flask(__name__)

def generate_image(name, color_top, color_bottom, alpha=10.0, shadow_angle=45):
    width, height = 800, 1200

    # Convert angle from degrees to radians
    angle_rad = math.radians(shadow_angle)
    dx = math.cos(angle_rad)
    dy = math.sin(angle_rad)

    def hex_to_rgb(h):
        return tuple(int(h[i : i + 2], 16) for i in (1, 3, 5))

    bg_color_top = hex_to_rgb(color_top)
    bg_color_bottom = hex_to_rgb(color_bottom)
    text_color = (255, 255, 255)
    shadow_color = (15, 18, 21, 20)  # alpha added for subtlety in shadow

    image = Image.new("RGBA", (width, height), bg_color_bottom + (255,))
    draw = ImageDraw.Draw(image)

    for y in range(height):
        r = int(bg_color_top[0] + (bg_color_bottom[0] - bg_color_top[0]) * y / height)
        g = int(bg_color_top[1] + (bg_color_bottom[1] - bg_color_top[1]) * y / height)
        b = int(bg_color_top[2] + (bg_color_bottom[2] - bg_color_top[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))

    try:
        font = ImageFont.truetype("arial.ttf", 72)
    except IOError:
        font = ImageFont.load_default()

    # Split text into lines for multiline support
    lines = name.split('\n')

    # Calculate total height of all lines + spacing
    line_heights = []
    line_widths = []
    spacing = 15  # pixels between lines

    for line in lines:
        bbox = font.getbbox(line)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        line_widths.append(w)
        line_heights.append(h)

    total_text_height = sum(line_heights) + spacing * (len(lines) - 1)

    # Starting Y to center the block of text vertically at about 1/3 height
    y_start = (height - total_text_height) // 2

    # Shadow layer for multi-line
    shadow_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)

    max_offset = 1000
    for offset in range(1, max_offset, 1):
        base_alpha = max(5, 25 - offset // 6)
        shadow_alpha = int(base_alpha * alpha)

        y_offset = y_start
        for i, line in enumerate(lines):
            x = (width - line_widths[i]) // 2
            # shadow_draw.text((x + offset, y_offset + offset), line, font=font, fill=(*shadow_color[:3], shadow_alpha))
            shadow_draw.text((x + int(offset * dx), y_offset + int(offset * dy)), line, font=font, fill=(*shadow_color[:3], shadow_alpha))
            y_offset += line_heights[i] + spacing

    # Composite shadow
    image = Image.alpha_composite(image, shadow_layer)
    draw = ImageDraw.Draw(image)

    # Draw main text lines
    y_offset = y_start
    for i, line in enumerate(lines):
        x = (width - line_widths[i]) // 2
        draw.text((x, y_offset), line, font=font, fill=text_color + (255,))
        y_offset += line_heights[i] + spacing

    final_image = image.convert("RGB")
    output_path = "static/generated.png"
    final_image.save(output_path, "PNG", optimize=True)

    return output_path


@app.route("/", methods=["GET", "POST"])
def index():
    # Since no longer need POST form submission, just serve the page with defaults
    return render_template("index.html", image_path=None, theme="dark")



@app.route("/download")
def download():
    path = "static/generated.png"
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "No image to download.", 404


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    name = data.get("name", "RASIKH ALI").strip()
    color_top = data.get("color_top", "#8C1F7A")
    color_bottom = data.get("color_bottom", "#DD64C8")
    alpha = float(data.get("alpha", 1.0))
    # modify generate_image to accept alpha parameter for shadow transparency
    # path = generate_image(name, color_top, color_bottom, alpha)
    
    shadow_angle = int(data.get("angle", 45))
    path = generate_image(name, color_top, color_bottom, alpha, shadow_angle)
    return jsonify({"image_path": "/" + path})

@app.route("/Crop", methods=["GET"])
def crop():
    path = "static/generated.png"
    if not os.path.exists(path):
        return "No image to crop.", 404

    with Image.open(path) as img:
        width, height = img.size
        # Crop square from center, side = width of image
        left = 0
        top = max((height - width) // 2, 0)
        right = width
        bottom = top + width

        cropped_img = img.crop((left, top, right, bottom))

        cropped_path = "static/generated_cropped.png"
        cropped_img.save(cropped_path, "PNG", optimize=True)

    return send_file(cropped_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
