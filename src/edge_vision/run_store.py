import subprocess
import sys

# Camera Configuration
STORES_CONFIG = {
    "store-1": [  
        {"id": "cam_01", "video": "data/Store-1/CAM 1 - zone.mp4"},
        {"id": "cam_02", "video": "data/Store-1/CAM 2 - zone.mp4"},
        {"id": "cam_03", "video": "data/Store-1/CAM 3 - entry.mp4"},
        {"id": "cam_04", "video": "data/Store-1/CAM 5 - billing.mp4"},
    ],
    "store-2": [  
        {"id": "cam_01", "video": "data/Store-2/zone.mp4"},
        {"id": "cam_02", "video": "data/Store-2/entry 1.mp4"},
        {"id": "cam_03", "video": "data/Store-2/entry 2.mp4"},
        {"id": "cam_04", "video": "data/Store-2/billing_area.mp4"},
    ]
}

print("Starting Enterprise Edge Orchestrator (Serial Mode)...")
print("Processing 8 videos sequentially.\n")

try:
    for store_id, cameras in STORES_CONFIG.items():
        print(f"Entering {store_id}...")
        
        for cam in cameras:
            print(f"Processing {cam['id']} ({cam['video']})...")
            
            # Run launches tracker.py
            cmd = [
                sys.executable,
                "-m", "src.edge_vision.tracker",
                "--store", store_id,
                "--camera", cam["id"],
                "--video", cam["video"]
            ]
            
            result = subprocess.run(cmd)
            
            if result.returncode == 0:
                print(f"Finished {cam['id']}\n")
            else:
                print(f"Error processing {cam['id']}. Moving to next camera.\n")

    print("All 8 cameras successfully processed.")

except KeyboardInterrupt:
    print("\nManual Interrupt: Exiting orchestrator.")