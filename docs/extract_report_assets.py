import fitz
from PIL import Image
import os

doc = fitz.open('report 4.pdf')
os.makedirs('django_backend/static/img', exist_ok=True)

for p in [40, 41, 42, 43, 44]:
    page = doc[p]
    ilist = page.get_images()
    print(f"Page {p+1} has {len(ilist)} images:")
    for idx, img in enumerate(ilist):
        xref = img[0]
        base_img = doc.extract_image(xref)
        w, h, ext = base_img["width"], base_img["height"], base_img["ext"]
        print(f"  xref {xref}: {w}x{h} {ext}")
        fname = f"django_backend/static/img/fig_{p+1}_{idx+1}.{ext}"
        with open(fname, "wb") as f:
            f.write(base_img["image"])

print("Saved report images to static/img.")
