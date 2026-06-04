import os
import argparse
import requests
import cv2
from datetime import datetime
from ultralytics import YOLO
from src.edge_vision.zone_mapper import ZoneMapper
import torch

from dotenv import load_dotenv
load_dotenv()

import torch

# PYTORCH 2.6 SECURITY OVERRIDE (MONKEY PATCH)
_original_torch_load = torch.load
def _patched_torch_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)
torch.load = _patched_torch_load

parser = argparse.ArgumentParser()
parser.add_argument("--store", type=str, required=True)
parser.add_argument("--camera", type=str, required=True)
parser.add_argument("--video", type=str, required=True)
args = parser.parse_args()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api/live-events")
mapper = ZoneMapper(config_path="data/zones.json")
mapper.load_store(args.store, args.camera)

def send_event_to_cloud(visitor_id: str, event_type: str, zone_id: str | None = None):
    payload = {
        "store_id": args.store,
        "visitor_id": f"{args.camera}_ID_{visitor_id}", 
        "event_type": event_type,
        "zone_id": zone_id,
        "timestamp": datetime.utcnow().isoformat(),
        "camera_id": args.camera 
    }
    try:
        requests.post(API_URL, json=payload)
    except:
        pass

def run_tracker():
    print(f"Starting YOLOv8 tracking on {args.video}...")
    cap = cv2.VideoCapture(args.video)
    model = YOLO("yolov8n.pt") 
    
    active_track_ids = set()
    visitor_current_zone = {} 

    frame_skip = 3
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break

        if frame_count % frame_skip != 0:
            continue

        compute_device = 0 if torch.cuda.is_available() else "cpu"
        results = model.track(frame, persist=True, classes=[0], verbose=False, device=compute_device)

        if results[0].boxes is not None and results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            track_ids = results[0].boxes.id.int().cpu().numpy()
            
            for box, track_id in zip(boxes, track_ids):
                track_id = str(track_id)
                x1, y1, x2, y2 = box
                
                # Entry
                if track_id not in active_track_ids:
                    active_track_ids.add(track_id)
                    send_event_to_cloud(track_id, "entry")
                
                # Dwell Time Tracking
                feet_x, feet_y = int((x1 + x2) / 2), int(y2)
                zone_info = mapper.get_zone_for_point(feet_x, feet_y)
                current_zone_id = zone_info["zone_id"] if zone_info else None
                
                previous_zone_id = visitor_current_zone.get(track_id)
                
                if current_zone_id != previous_zone_id:
                    # Exit old zone
                    if previous_zone_id is not None:
                        send_event_to_cloud(track_id, "zone_exit", previous_zone_id)
                    # Enter new zone
                    if current_zone_id is not None:
                        send_event_to_cloud(track_id, "zone_entry", current_zone_id)
                    
                    visitor_current_zone[track_id] = current_zone_id

                if zone_info:
                    cv2.putText(frame, zone_info["zone_name"], (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Exit
    for track_id, z_id in visitor_current_zone.items():
        if z_id is not None:
            send_event_to_cloud(track_id, "zone_exit", z_id)
            
    for track_id in active_track_ids:
        send_event_to_cloud(track_id, "exit")
        
    cap.release()
    cv2.destroyAllWindows()
    print(f"Finished processing {args.camera}")

if __name__ == "__main__":
    run_tracker()