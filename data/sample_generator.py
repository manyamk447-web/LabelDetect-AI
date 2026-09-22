from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def _create_label(path, title, lines):

    width = 1000
    height = 900

    image = Image.new(
        "RGB",
        (width, height),
        "white"
    )

    draw = ImageDraw.Draw(image)

    try:
        title_font = ImageFont.truetype(
            "arial.ttf",
            40
        )

        text_font = ImageFont.truetype(
            "arial.ttf",
            28
        )

    except Exception:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()

    draw.text(
        (40, 30),
        title,
        fill="black",
        font=title_font
    )

    y = 110

    for line in lines:

        draw.text(
            (50, y),
            line,
            fill="black",
            font=text_font
        )

        y += 80

    image.save(path)


def generate_samples(output_dir="data/sample_labels"):

    output_path = Path(output_dir)

    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    _create_label(
        output_path / "compliant_snack.png",
        "PACKAGED FOOD LABEL",
        [
            "Product Name: Healthy Snack",
            "Manufactured By: ABC Foods Pvt Ltd",
            "Address: 123 Industrial Area, Bengaluru",
            "Net Quantity: 200 g",
            "MRP: Rs. 120",
            "Packed On: 01/09/2026",
            "Consumer Care: 1800-123-4567",
            "Country of Origin: India"
        ]
    )

    _create_label(
        output_path / "non_compliant_beverage.png",
        "BEVERAGE LABEL",
        [
            "Product Name: Fresh Drink",
            "Manufactured By: XYZ Beverages",
            "Address: Industrial Area, Bengaluru",
            "Net Quantity: 500 ml",
            "Packed On: 01/09/2026",
            "Consumer Care: 1800-111-2222"
        ]
    )

    _create_label(
        output_path / "warning_cosmetics.png",
        "COSMETIC LABEL",
        [
            "Product Name: Skin Cream",
            "Manufactured By: Beauty Care Pvt Ltd",
            "Address: Mumbai, Maharashtra",
            "Net Quantity: 100 g",
            "MRP: Rs. 250",
            "Packed On: 01/09/2026",
            "Consumer Care: 1800-333-4444",
            "Country of Origin: India"
        ]
    )

    return str(output_path)