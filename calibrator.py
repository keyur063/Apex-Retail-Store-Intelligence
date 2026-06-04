import cv2
import json
import os
import numpy as np

CAMERAS = [
    {"store": "store-1", "cam": "cam_01", "path": "data/Store-1/CAM 1 - zone.mp4"},
    {"store": "store-1", "cam": "cam_02", "path": "data/Store-1/CAM 2 - zone.mp4"},
    {"store": "store-1", "cam": "cam_03", "path": "data/Store-1/CAM 3 - entry.mp4"},
    {"store": "store-1", "cam": "cam_04", "path": "data/Store-1/CAM 5 - billing.mp4"},
    
    {"store": "store-2", "cam": "cam_01", "path": "data/Store-2/zone.mp4"},
    {"store": "store-2", "cam": "cam_02", "path": "data/Store-2/entry 1.mp4"},
    {"store": "store-2", "cam": "cam_03", "path": "data/Store-2/entry 2.mp4"},
    {"store": "store-2", "cam": "cam_04", "path": "data/Store-2/billing_area.mp4"}
]

STANDARD_ZONES = {
    "Z_ENTRANCE": {"name": "Entrance", "type": "ENTRANCE"},
    "Z_AISLE": {"name": "Aisle", "type": "SHELF"},
    "Z_CHECKOUT": {"name": "Checkout", "type": "BILLING"} 
}

final_zones = {"store-1": {}, "store-2": {}}
current_polygon = []
img_display = None

def click_event(event, x, y, flags, params):
    global current_polygon, img_display
    if event == cv2.EVENT_LBUTTONDOWN:
        current_polygon.append([x, y])
        
def draw_overlay(img, store, cam_id, zone_name):
    overlay = img.copy()
    cv2.rectangle(overlay, (0, 0), (1000, 80), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)
    
    cv2.putText(img, f"[{store} | {cam_id}] Mapping: {zone_name}", (15, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(img, "Click points. 'n'=Save & Next | 's'=Skip Zone | 'c'=Clear Points | 'q'=Quit", (15, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

print("Booting Simplified Auto-Calibrator...")

for cam_info in CAMERAS:
    store = cam_info["store"]
    cam_id = cam_info["cam"]
    video_path = cam_info["path"]
    
    if cam_id not in final_zones[store]:
        final_zones[store][cam_id] = {}
        
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print(f"Could not read {video_path}. Skipping...")
        continue
        
    cv2.namedWindow("Calibrator", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("Calibrator", click_event)
    
    for zone_id, zone_meta in STANDARD_ZONES.items():
        current_polygon = []
        
        while True:
            img_display = frame.copy()
            draw_overlay(img_display, store, cam_id, zone_meta['name'])
            
            for pt in current_polygon:
                cv2.circle(img_display, tuple(pt), 5, (0, 255, 0), -1)
            if len(current_polygon) > 1:
                pts = np.array(current_polygon, np.int32).reshape((-1, 1, 2))
                cv2.polylines(img_display, [pts], isClosed=False, color=(0, 255, 0), thickness=2)
            if len(current_polygon) > 2:
                cv2.line(img_display, tuple(current_polygon[-1]), tuple(current_polygon[0]), (0, 255, 0), 2)
                
            cv2.imshow("Calibrator", img_display)
            key = cv2.waitKey(20) & 0xFF
            
            if key == ord('n'):
                if len(current_polygon) >= 3:
                    final_zones[store][cam_id][zone_id] = {
                        "name": zone_meta["name"],
                        "type": zone_meta["type"],
                        "polygon": current_polygon.copy()
                    }
                    print(f"Saved {zone_meta['name']} on {cam_id}")
                    break
                else:
                    print("Need at least 3 points to save a polygon.")
            
            elif key == ord('s'):
                print(f"Skipped {zone_meta['name']} on {cam_id}")
                break
                
            elif key == ord('c'):
                current_polygon = []
                print("Cleared points.")
                
            elif key == ord('q'):
                print("Emergency Quit.")
                cv2.destroyAllWindows()
                exit()

cv2.destroyAllWindows()

os.makedirs("data", exist_ok=True)
with open("data/zones.json", "w") as f:
    json.dump(final_zones, f, indent=2)

print("\nCalibration Complete! File securely written to data/zones.json")