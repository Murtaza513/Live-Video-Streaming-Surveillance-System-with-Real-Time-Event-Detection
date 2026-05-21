# SurveillanceOS — Real-Time Video Surveillance Platform

A production-style, full-stack intelligent surveillance system with live webcam streaming, adaptive video compression, motion detection, optional YOLOv8 person detection, timestamped event logging, and a responsive React dashboard. Designed for research and industrial monitoring use cases.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          Browser Dashboard                                │
│                     React + Tailwind CSS (Vite)                           │
│                                                                           │
│   ┌────────────┐  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│   │  LiveFeed  │  │ AlertPanel  │  │ EventHistory │  │ConnectStatus │  │
│   └─────┬──────┘  └──────┬──────┘  └──────┬───────┘  └───────────────┘  │
│         │  (frames+meta) │  (alert msgs)   │  (REST fetch)               │
│         └────────────────┤                 │                              │
│                 WebSocket│/ws/stream        │ GET /api/v1/events           │
└─────────────────────────────────────────────────────────────────────────-┘
                           │                 │
┌──────────────────────────▼─────────────────▼────────────────────────────┐
│                         FastAPI Backend                                   │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                     WebSocket /ws/stream                          │    │
│  │                                                                   │    │
│  │   VideoCapture ──► MotionDetector ──► [YoloDetector] (optional)  │    │
│  │        │                  │                   │                   │    │
│  │        └──────────────────▼───────────────────┘                  │    │
│  │                    AdaptiveCompressor                             │    │
│  │                (quality + scale ∝ motion ratio)                  │    │
│  │                           │                                       │    │
│  │              ┌────────────┴──────────────┐                       │    │
│  │         base64 JPEG               EventOrchestrator              │    │
│  │          payload                (cooldown + dedup)               │    │
│  │              │                        │                           │    │
│  │         WS message             SnapshotService                   │    │
│  └──────────────│────────────────────────│───────────────────────────┘   │
│                 │                        │                                │
│  ┌──────────────│────────────────────────▼───────────────────────────┐   │
│  │         REST GET /api/v1/events          PostgreSQL events table   │   │
│  └───────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## Features

| Feature | Detail |
|---|---|
| **Live webcam streaming** | OpenCV captures frames at configurable FPS; streamed over WebSocket as base64-encoded JPEG |
| **Motion detection** | Frame-differencing pipeline: Gaussian blur → `absdiff` → binary threshold → dilation |
| **YOLOv8 person detection** | Optional; enabled via `ENABLE_YOLO=true`; auto-degrades to motion-only if model load fails |
| **Adaptive compression** | JPEG quality and resolution scale inversely with motion intensity to balance quality vs. bandwidth |
| **Event persistence** | Every alert stored in PostgreSQL with timestamp, confidence, motion ratio, and snapshot path |
| **Snapshot saving** | Event-trigger frames saved as JPEG files; served under `/snapshots/` static endpoint |
| **Real-time alerts** | Alerts broadcast over WebSocket instantly; per-type cooldown prevents log flooding |
| **REST event history** | Paginated, filterable event log at `GET /api/v1/events` |
| **Responsive dashboard** | Dark-theme Tailwind UI: live feed, alert panel, event log, connection status badge |
| **Reconnect resilience** | WebSocket client auto-reconnects with exponential backoff; camera service retries on failure |
| **Docker deployment** | Separate Dockerfiles for backend (Python 3.12 slim) and frontend (Node build → Nginx static) |

---

## Project Structure

```
├── backend/
│   ├── main.py                        # FastAPI app — lifespan, routing, static mount
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   └── app/
│       ├── core/
│       │   ├── config.py              # Pydantic Settings (env-driven configuration)
│       │   ├── database.py            # Async SQLAlchemy engine, session factory, Base
│       │   └── logging.py             # Structured log format
│       ├── models/
│       │   └── event.py               # SQLAlchemy Event model (with snapshot_path)
│       ├── schemas/
│       │   └── event.py               # Pydantic response schemas + WS payload shape
│       ├── services/
│       │   ├── video_capture.py       # Webcam source with reconnect logic
│       │   ├── detection.py           # Frame-differencing motion detector
│       │   ├── yolo_detector.py       # Optional YOLOv8 person detector (graceful fallback)
│       │   ├── compression.py         # Adaptive JPEG quality + resolution compressor
│       │   ├── snapshot.py            # Event-frame JPEG persistence
│       │   └── event_service.py       # Alert orchestration, cooldown, DB writes
│       └── api/
│           ├── events.py              # REST — paginated event history
│           └── stream.py              # WebSocket — live frame stream + ConnectionManager
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .env.example
│   ├── nginx.conf
│   ├── Dockerfile
│   └── src/
│       ├── main.jsx                   # React entry point
│       ├── App.jsx                    # Dashboard shell + layout grid
│       ├── index.css                  # Tailwind imports + scrollbar theme
│       ├── context/
│       │   └── SurveillanceContext.jsx  # React Context: state store + WS lifecycle
│       ├── services/
│       │   ├── wsClient.js            # WS transport with exponential-backoff reconnect
│       │   └── api.js                 # Fetch wrapper for REST events endpoint
│       └── components/
│           ├── LiveFeed.jsx           # Streaming video panel + compression metadata
│           ├── AlertPanel.jsx         # Live alert feed (newest first)
│           ├── EventHistory.jsx       # Filterable, sortable event log table
│           └── ConnectionStatus.jsx   # WS connection state badge
│
├── services/                          # Reserved for future microservices
├── .gitignore
└── README.md
```

---

## Quick Start (Local)

### Prerequisites

- **Python 3.12+** with `pip`
- **Node.js 20+** with `npm`
- **PostgreSQL 15+** running locally
- A **webcam** connected (or set `CAMERA_INDEX` to a virtual device index)

---

### 1 — Backend

```bash
cd backend

# 1a. Copy and edit the environment file
cp .env.example .env
# Edit DATABASE_URL, CAMERA_INDEX, ENABLE_YOLO, etc.

# 1b. Create a virtual environment and install dependencies
python -m venv .venv
# macOS / Linux:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt

# 1c. Create the PostgreSQL database (first time)
psql -U postgres -c "CREATE DATABASE surveillance;"

# 1d. Start the backend (tables are auto-created on first run)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API available at **http://localhost:8000**
Interactive docs at **http://localhost:8000/docs**

---

### 2 — Frontend

```bash
cd frontend

# 2a. Copy environment file
cp .env.example .env
# Edit VITE_WS_URL and VITE_API_URL if your backend runs on a different host/port

# 2b. Install and start dev server
npm install
npm run dev
```

Dashboard available at **http://localhost:5173**

---

### 3 — Docker (separate containers)

**Backend**

```bash
cd backend
docker build -t surveillance-backend .
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://postgres:postgres@host.docker.internal:5432/surveillance" \
  -e CAMERA_INDEX=0 \
  --device /dev/video0:/dev/video0 \
  surveillance-backend
```

> **Windows / macOS Docker Desktop:** camera pass-through requires additional configuration (e.g., `--privileged` or a USB sharing tool). For development, running the backend directly on the host is simpler.

**Frontend**

```bash
cd frontend
docker build -t surveillance-frontend .
docker run -p 80:80 surveillance-frontend
```

Dashboard available at **http://localhost**

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/surveillance` | Async PostgreSQL connection string |
| `CAMERA_INDEX` | `0` | OS camera index (0 = default webcam) |
| `TARGET_FPS` | `12` | Target streaming frames per second |
| `BASE_JPEG_QUALITY` | `75` | Baseline JPEG encoding quality (1–100) |
| `MIN_JPEG_QUALITY` | `40` | Minimum quality applied at maximum motion |
| `MAX_JPEG_QUALITY` | `90` | Maximum quality applied at zero motion |
| `MOTION_THRESHOLD` | `0.03` | Fraction of changed pixels to trigger a motion alert |
| `MOTION_BLUR_KERNEL` | `21` | Gaussian blur kernel size for noise reduction (must be odd) |
| `ENABLE_YOLO` | `false` | Enable YOLOv8 person detection |
| `YOLO_MODEL` | `yolov8n.pt` | YOLOv8 model weights (auto-downloaded on first run) |
| `PERSON_CONFIDENCE` | `0.4` | Minimum detection confidence for a person alert |
| `EVENT_COOLDOWN_SECONDS` | `2` | Minimum seconds between same-type events |
| `SNAPSHOT_DIR` | `snapshots` | Directory for event-trigger JPEG snapshots |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | CORS allowed origin |
| `LOG_LEVEL` | `INFO` | Python log level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

### Frontend (`frontend/.env`)

| Variable | Default | Description |
|---|---|---|
| `VITE_WS_URL` | `ws://localhost:8000/ws/stream` | WebSocket stream URL |
| `VITE_API_URL` | `http://localhost:8000/api/v1` | Backend REST API base URL |

---

## API Reference

### REST Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Liveness check → `{ status, app, env }` |
| `GET` | `/api/v1/events` | Paginated event history (see params below) |
| `GET` | `/snapshots/{filename}` | Serve an event-trigger snapshot JPEG |

**`GET /api/v1/events` — query parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page` | int | 1 | Page number (1-based) |
| `page_size` | int | 20 | Results per page (max 100) |
| `event_type` | string | — | Filter: `motion` or `person` |

**Response shape**

```json
{
  "events": [
    {
      "id": 42,
      "event_type": "person",
      "confidence": 0.87,
      "motion_ratio": 0.12,
      "timestamp": "2026-05-21T10:30:00.123456",
      "message": "Person detected (confidence 87%)",
      "snapshot_path": "snapshots/person_20260521_103000_123456.jpg"
    }
  ],
  "total": 57
}
```

### WebSocket

**`ws://localhost:8000/ws/stream`**

Each message is a JSON object sent at `TARGET_FPS`:

```json
{
  "frame":           "<base64-JPEG string>",
  "timestamp":       "2026-05-21T10:30:00.456789",
  "motion_detected": true,
  "person_detected": false,
  "motion_ratio":    0.047,
  "jpeg_quality":    63,
  "scale":           0.78,
  "alert":           "Motion detected (4.7% of frame changed)"
}
```

`alert` is `null` when no event fires. On camera failure, a reduced payload is sent:

```json
{ "error": "camera_unavailable", "timestamp": "..." }
```

---

## Adaptive Compression

Quality and resolution scale **inversely** with motion intensity, keeping bandwidth low during busy scenes and quality high when the scene is calm:

| Motion Intensity | JPEG Quality | Resolution Scale |
|---|---|---|
| 0 % (still) | 90 (max) | 100 % |
| 25 % | ~73 | ~88 % |
| 50 % | ~65 | ~75 % |
| 75 % | ~53 | ~63 % |
| 100 % (maximum motion) | 40 (min) | 50 % |

---

## Performance Notes

- **Default 12 FPS** is conservative for CPU-only hosts. Increase `TARGET_FPS` on machines with capable hardware.
- **YOLOv8n** (nano) adds ~30–80 ms per frame on CPU. Lower `TARGET_FPS` to 6–8 if latency spikes occur when YOLO is enabled.
- **Model download:** YOLOv8 weights are downloaded automatically by `ultralytics` on first use (~6 MB for `yolov8n.pt`). Pre-download and bind-mount the file to avoid network access in production.
- **Snapshot accumulation:** Snapshots grow on disk indefinitely. Add a cron job or retention policy for long-running deployments.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `RuntimeError: Unable to open camera index 0` | Verify the webcam is connected; try `CAMERA_INDEX=1` or higher |
| `asyncpg: … Connection refused` | Ensure PostgreSQL is running and `DATABASE_URL` is correct |
| YOLO model download fails at startup | Set `ENABLE_YOLO=false` to use motion-only mode |
| Frontend shows "No signal" | Check the backend is running and `VITE_WS_URL` points to the correct host |
| Black screen inside Docker | Pass `--device /dev/video0:/dev/video0` to grant container camera access |
| `Module not found: ultralytics` | Install requirements: `pip install -r requirements.txt` |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | Python 3.12 · FastAPI · Uvicorn |
| Computer vision | OpenCV 4.10 · NumPy |
| AI detection | YOLOv8 (Ultralytics) — optional |
| Database ORM | SQLAlchemy 2.0 async · asyncpg |
| Database | PostgreSQL 15 |
| Streaming | FastAPI WebSocket (Starlette) |
| Frontend framework | React 18 · Vite 5 |
| Styling | Tailwind CSS 3 |
| State management | React Context API + useReducer |
| Deployment | Docker (separate backend / frontend images) |

---

## License

MIT
