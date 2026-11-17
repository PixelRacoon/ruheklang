"""Render the Ruheklang app icon without external artwork."""
from pathlib import Path
from PIL import Image, ImageDraw
import math
ROOT = Path(__file__).resolve().parent / "icons"
ROOT.mkdir(parents=True, exist_ok=True)
S = 1024
im = Image.new("RGB", (S,S))
px = im.load()
for y in range(S):
    for x in range(S):
        radius = math.hypot((x-S*.49)/S,(y-S*.43)/S)
        glow = max(0,1-radius/.69)**2
        px[x,y] = (int(13+39*glow),int(24+50*glow),int(37+53*glow))
d = ImageDraw.Draw(im)
mint = (173,232,209)
d.rounded_rectangle((107,107,917,917),radius=248,outline=mint,width=4)
# Seven gentle vertical sound-wave bars.
bars = [(193,466,266,558),(287,413,358,612),(381,354,455,672),
        (475,293,549,734),(569,392,643,636),(663,433,735,592),
        (759,466,831,558)]
for a,b,c,e in bars:
    d.rounded_rectangle((a,b,c,e),radius=(c-a)//2,fill=mint)
for size in (180,192,512):
    im.resize((size,size),Image.Resampling.LANCZOS).save(ROOT / f"icon-{size}.png",optimize=True)
