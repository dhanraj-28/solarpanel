import requests
import os

def download_satellite_image(latitude, longitude, save_path, zoom=19):
    """
    Download satellite image using free tile services.
    
    Args:
        latitude: Location latitude
        longitude: Location longitude
        save_path: Where to save the image
        zoom: Zoom level (19 is good for solar panels)
    """
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        # Using Esri World Imagery (Free, no API key needed)
        # Alternative free satellite tile services
        
        # Convert lat/lon to tile coordinates
        import math
        
        def deg2num(lat_deg, lon_deg, zoom):
            lat_rad = math.radians(lat_deg)
            n = 2.0 ** zoom
            xtile = int((lon_deg + 180.0) / 360.0 * n)
            ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
            return (xtile, ytile)
        
        x, y = deg2num(latitude, longitude, zoom)
        
        # Free satellite imagery sources (no API key needed):
        urls = [
            # Esri World Imagery
            f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{zoom}/{y}/{x}",
            # Google Satellite (use with caution - may have rate limits)
            f"https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={zoom}",
        ]
        
        # Try each URL until one works
        for url in urls:
            try:
                response = requests.get(url, timeout=15, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"  ✓ Satellite image downloaded: {save_path}")
                    return
            except:
                continue
        
        raise Exception("Could not download from any source")
        
    except Exception as e:
        print(f"  ✗ Error downloading satellite image: {e}")
        raise


def download_image(url, save_path):
    """Download an image from a URL."""
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        print(f"Downloaded: {save_path}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")
        raise