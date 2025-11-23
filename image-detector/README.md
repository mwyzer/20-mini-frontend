# Image Detector (FastAPI + React)

A small demo that exposes an async FastAPI backend for image object detection and a React dashboard for uploading images, viewing bounding boxes, and managing detection records.

## Backend (FastAPI)

1. Create a virtual environment and install dependencies:

```bash
cd image-detector/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Start the API server:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints:
- `POST /detect-image` — upload an image file and receive mocked detection results saved to SQLite.
- `GET /detections` — list detections.
- `GET /detections/{id}` — fetch a single detection.
- `PUT /detections/{id}` — update filename and detection objects.
- `DELETE /detections/{id}` — remove a detection.

The service enables CORS for typical Vite/React dev ports.

## Frontend (React + Vite)

1. Install dependencies:

```bash
cd image-detector/frontend
npm install
```

2. Run the development server (default `http://localhost:5173`):

```bash
npm run dev
```

3. Build for production:

```bash
npm run build
```

The UI lets you upload an image, sends it to the FastAPI backend, renders returned bounding boxes, and provides CRUD controls for stored detections.
