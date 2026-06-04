import json
import cv2
import numpy as np
from typing import Optional

class ZoneMapper:
    def __init__(self, config_path: str = "data/zones.json"):
        with open(config_path, 'r') as f:
            self.all_zones = json.load(f)
            
        self.store_id = None
        self.camera_id = None
        self.active_zones = {}

    def load_store(self, store_id: str, camera_id: str):
        """Loads the specific spatial layout for the given store and camera."""
        if store_id not in self.all_zones or camera_id not in self.all_zones[store_id]:
            print(f"Warning: No zone configuration found for {store_id} -> {camera_id}")
            self.active_zones = {}
            return
            
        self.store_id = store_id
        self.camera_id = camera_id
        self.active_zones = self.all_zones[store_id][camera_id]
        print(f"Loaded {len(self.active_zones)} spatial zones for {camera_id}")

    # Notice the updated return type hint below!
    def get_zone_for_point(self, x: int, y: int) -> Optional[dict]:
        """
        Takes the bottom-center coordinates of a YOLO bounding box (the person's feet)
        and returns the zone they are standing in.
        """
        if not self.active_zones:
            return None

        point = (float(x), float(y))

        for zone_id, zone_data in self.active_zones.items():
            # Convert python list to OpenCV contour format
            polygon = np.array(zone_data["polygon"], np.int32).reshape((-1, 1, 2))
            
            # Returns 1 if the point is inside the polygon else -1
            is_inside = cv2.pointPolygonTest(polygon, point, measureDist=False)
            
            if is_inside >= 0:
                return {
                    "zone_id": zone_id,
                    "zone_name": zone_data["name"],
                    "zone_type": zone_data["type"]
                }
                
        return None