# LAB_DST_Robocoffee

Source code and supporting files for **Robocoffee**, a table-side coffee delivery system built on the OAK9 differential-drive mobile robot, developed in the Laboratorio de Desarrollo de Soluciones Tecnológicas (LabDST) at ITESO, Fall 2026.

The system combines an information server, a Smart Cup-holder Module (ESP32 with a load cell) and the OAK9 robot. The server coordinates the app and the robot, and receives `CUP_PRESENT` / `CUP_ABSENT` events from the cup-holder over Wi-Fi (HTTP).

## Repository structure

| Folder / file | Content |
|---|---|
| `server/` | Information server (FastAPI): orders, robot state machine and cup-holder events |
| `testing/` | Scripts used to move, calibrate and test the OAK9 (straight-line and turn tests, IMU calibration, plots) |
| `oak9lib-main/` | OAK9 Python library provided by the course instructors to control the robot (see its own `LICENSE`) |
| `Graficas/` | Plots generated from the experiments |
| `Plantilla/`, `txt/`, `borroador_methods.txt` | Paper template and drafts |

## Running the server

Requires Python 3.10 or newer.

```bash
pip install -e oak9lib-main
pip install fastapi uvicorn
cd server
uvicorn main:app --reload
```

Then open `http://localhost:8000/docs` to try the endpoints. To accept connections from other devices (for example the ESP32), add `--host 0.0.0.0`.

Main endpoints: `GET /status`, `POST /orders`, `GET /orders`, `GET /orders/{id}`, `POST /cup`, `POST /robot/reset`.

> In the current version the robot motion is simulated inside the server with timers. Real OAK9 commands are sent through the library in `oak9lib-main/`.

## Authors

Adrián R. Oviedo Norieda, Alexis E. Hernández Paredes, César A. Solano Chávez, Mauricio Pérez Narváez and Raúl Bracamontes Plasencia. Supervised by Jorge A. Lizárraga and Graciela Baca, with Luis Enrique González-Jiménez and Luis F. Luque-Vega.
