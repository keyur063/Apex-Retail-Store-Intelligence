"Apex Retail Store Intelligence" sounds incredibly professional, and it perfectly matches the header I saw in your dashboard screenshots! It gives the project a true enterprise-grade feel.

Here is your final, polished `README.md` with the updated branding.

Copy and paste this to overwrite your current README:

```markdown
# 🛒 Apex Retail Store Intelligence: Enterprise Edge-to-Cloud Analytics

Apex Retail Store Intelligence is a decoupled, edge-to-cloud computer vision pipeline designed for retail environments. It utilizes YOLOv8 and ByteTrack on edge devices (or cloud GPUs) to track shoppers, calculate dwell times in specific store zones, and transmit live telemetry via HTTP webhooks to a FastAPI backend.

The system dynamically calculates **Unique Visitors**, **Zone Dwell Times** (Entrance, Aisle, Checkout), and **POS Conversion Rates** in real-time.

---

## 🏗️ Architecture Overview

This project is highly scalable and split into two distinct, decoupled components:
1. **The Cloud (Backend):** A FastAPI server and SQLite database that aggregates telemetry and serves the live analytical dashboard.
2. **The Edge (Vision):** A YOLOv8 + ByteTrack Python script that processes static camera footage, utilizes a frame-skip optimization, maps spatial coordinates to store zones, and sends data via webhooks.

---

## 📂 Project Structure

To maintain a clean and lightweight repository, raw video files (`.mp4`) and heavy ML model weights (`.pt`) are intentionally excluded via `.gitignore`. 

```text
apex-retail-intelligence/
├── data/
│   ├── zones.json                  # Spatial boundary mappings
│   ├── Store-1/                    # (Ignored by Git) Place CAM videos here
│   └── Store-2/                    # (Ignored by Git) Place CAM videos here
├── src/
│   ├── backend/
│   │   ├── main.py                 # FastAPI server & Dashboard UI
│   │   └── models.py               # Database schemas
│   └── edge_vision/
│       ├── run_store.py            # Orchestrator script
│       ├── tracker.py              # YOLOv8 + ByteTrack engine
│       └── zone_mapper.py          # Spatial logic
├── .env.example                    # Template for environment variables
├── .gitignore                      # Keeps repo clean of videos and weights
├── requirements.txt                # Python dependencies
└── README.md

```

---

## ⚙️ Prerequisites & Setup

### 1. Install Dependencies

Ensure you have Python 3.9+ installed. Install the required packages using the provided requirements file:

```bash
pip install -r requirements.txt

```

### 2. Configure the Data Directory

Before running the system, you must structure your `data/` folder and insert your `.mp4` camera footages locally:

* `data/Store-1/CAM 1 - zone.mp4`
* `data/Store-2/CAM 1 - zone.mp4`
* *(etc.)*

### 3. Set Up Environment Variables (Security)

To keep the webhook URLs secure, this project uses `python-dotenv`.

1. Create a file named `.env` in the root directory.
2. Add your Ngrok (or production) API URL:

```env
API_URL=https://<YOUR_NGROK_URL>.ngrok-free.dev/api/live-events

```

*(If no `.env` file is found, the system will safely fallback to `http://127.0.0.1:8000/api/live-events` for local testing).*

---

## 🚀 How to Run the Pipeline

Running this system requires establishing a secure tunnel between the Edge AI and the Backend. **You will need three separate terminal windows.**

### Step 1: Start the Backend Server (Terminal 1)

This starts the FastAPI server and initializes the SQLite database.

```bash
python -m uvicorn src.backend.main:app

```

*The live dashboard is now available at: `http://127.0.0.1:8000*`

### Step 2: Establish the Ngrok Tunnel (Terminal 2)

To allow the Edge AI (especially if running on Google Colab) to send webhooks to your local machine, open a new terminal and start Ngrok on port 8000:

```bash
ngrok http 8000

```

**Important:** Copy the public `Forwarding` URL provided by Ngrok and place it in your `.env` file!

### Step 3: Run the Edge AI Orchestrator (Terminal 3)

Launch the computer vision pipeline. This will systematically process all store cameras and stream the telemetry back to your dashboard.

**To run locally (Requires NVIDIA GPU):**

```bash
python src/edge_vision/run_store.py

```

**To run via Google Colab (Recommended for Mac/CPU users):**

1. Zip the project folder (ensure `zones.json` and videos are inside).
2. Upload to a Google Colab notebook with a **T4 GPU** enabled.
3. Unzip the folder.
4. Set your environment variable in Colab: `%env API_URL=https://<YOUR_NGROK_URL>.ngrok-free.dev/api/live-events`
5. Execute the orchestrator: `!python src/edge_vision/run_store.py`

---

## 📊 Viewing the Data

Once the Edge AI begins processing, open **`http://127.0.0.1:8000`** in your browser.
The dashboard will update dynamically. If you stop the Edge AI or restart the FastAPI server, your data remains safely stored in the local SQLite database.

```

```