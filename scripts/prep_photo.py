"""Prep a photo for ASCII conversion: remove background, boost local contrast, put on white.

Usage: python scripts/prep_photo.py source-photo.jpg   ->  source-prepped.png
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "source-prepped.png"


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: python scripts/prep_photo.py <photo>")

    img = Image.open(sys.argv[1]).convert("RGB")
    cut = np.array(remove(img).convert("RGBA"))          # 1. remove background
    alpha = cut[:, :, 3].astype(np.float32) / 255.0
    gray = cv2.cvtColor(cut[:, :, :3], cv2.COLOR_RGB2GRAY)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))  # 2. local contrast
    gray = clahe.apply(gray)

    out = gray.astype(np.float32) * alpha + 255.0 * (1.0 - alpha)  # 3. composite on white
    out = out.astype(np.uint8)

    ys, xs = np.where(alpha > 0.1)                        # crop to the subject
    if len(xs):
        pad = 10
        y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, out.shape[0])
        x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, out.shape[1])
        out = out[y0:y1, x0:x1]

    Image.fromarray(out, "L").save(OUT)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()