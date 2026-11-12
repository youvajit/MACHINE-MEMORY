# MACHINE-MEMORY

AI-assisted machine sound anomaly detection using uploaded WAV recordings. The app extracts MFCC, RMS energy, spectral centroid and zero-crossing-rate features, learns a per-machine normal baseline with Isolation Forest, and flags recordings that differ from that baseline.

IMPORTANT: An acoustic anomaly is an unusual sound pattern, not proof of a mechanical fault. Treat results as decision-support signals alongside inspection and maintenance procedures. The displayed health index is relative, not a calibrated probability or certified machine-health measurement.

## Features
- Industrial dark dashboard and recent analysis counters.
- WAV upload and acoustic feature extraction.
- Per-machine baseline training from at least five normal recordings.
- Isolation Forest anomaly detection.
- NORMAL / ABNORMAL result, relative anomaly score and health index.
- SQLite history, machine profiles and record deletion.
- Feature chart visualization.

## Windows setup
1. Install Python 3.10–3.12 and enable Add Python to PATH.
2. Download this repository as ZIP and extract it.
3. Open Command Prompt in the extracted project folder.
4. Create and activate a virtual environment:
   py -3.11 -m venv .venv
   .venv\Scripts\activate
5. Install packages:
   python -m pip install --upgrade pip
   pip install -r requirements.txt
6. Start:
   python app.py
7. Open http://127.0.0.1:5000

## First use
1. Select a machine profile or add one.
2. Upload at least 5 WAV recordings captured during normal operation and click Train baseline.
3. Upload a separate WAV file and click Analyze sound.
4. Review the result and analysis history.

## Limits
- WAV only in this initial version.
- Maximum upload size: 25 MB.
- Up to 30 seconds are analyzed per recording.
- Audio shorter than 0.25 seconds is rejected.
- Keep baseline recordings representative of normal machine speed, load, microphone position and environment. Recording conditions affect results.

## Project structure
app.py, config.py, requirements.txt, database/, services/, templates/, static/, tests/.

## Tests
Run: pytest

## Privacy and security
Audio is processed by the local Flask app. Uploaded audio is deleted after feature extraction; analysis metadata is saved in local SQLite. Do not expose the development server publicly without authentication, HTTPS, production server configuration and security review.

## Current scope
This is an educational MVP. PDF reports, downloadable waveform preview, production deployment hardening and advanced threshold calibration are not yet implemented.
