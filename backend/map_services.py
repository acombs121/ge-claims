import os
import logging

logger = logging.getLogger(__name__)

def build_map_payload(center: list, zoom: int, heatmap_points: list, markers: list, routes: dict, config: dict) -> dict:
    """Builds a CustomView payload for the base_map template with specific config flags."""
    
    payload = {
        "CustomView": {
            "template": "base_map",
            "data": {
                "center": center,
                "zoom": zoom,
                "heatmap_points": heatmap_points,
                "markers": markers,
                "routes": routes,
                "config": config,
                "maps_api_key": os.environ.get("GOOGLE_MAPS_API_KEY")
            }
        }
    }
    return payload
