import re
import urllib.request

url = "https://33komoda.ru/catalog/shkafy_raspashnye/shkaf_mori_msh900_1_2dveri_2_yashchika_belyy/"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
pattern = r"https?://[^\s\"'<>]+\.(?:jpg|jpeg|png|webp)"
imgs = sorted(set(re.findall(pattern, html, re.I)))
for u in imgs:
    low = u.lower()
    if any(x in low for x in ("logo", "icon", "sprite", "banner", "payment")):
        continue
    print(u)
