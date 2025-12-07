import math
import requests
from PIL import Image
from io import BytesIO

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int(
        (1 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2 * n
    )
    return xtile, ytile

def fetch_satellite_image(lat, lon, save_path, zoom=18):
    url_template = (
        "https://services.arcgisonline.com/ArcGIS/rest/services/"
        "World_Imagery/MapServer/tile/{z}/{y}/{x}"
    )

    x, y = deg2num(lat, lon, zoom)
    url = url_template.format(z=zoom, x=x, y=y)

    print("Downloading:", url)

    response = requests.get(url)

    if response.status_code == 200:
        img = Image.open(BytesIO(response.content))
        img.save(save_path)
        print("Saved:", save_path)
        return True
    else:
        print("ERROR downloading:", response.status_code)
        return False
