# Parking Vision (Python + OpenCV)

Sistema de visão computacional para detetar ocupação de vagas (livre/ocupada) em tempo real.
- Câmara de telemóvel (stream via Wi‑Fi/RTSP/MJPEG) ou webcam
- Processamento no PC (Python + OpenCV)
- Overlays: VERDE = livre | VERMELHO = ocupada

## Setup rápido
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

## Fluxo
1) **Calibrar ROIs (5 vagas)**  
```bash
python -m src.calibrate_rois --source "URL_OU_0"
```
2) **Capturar baseline com vagas vazias**  
```bash
python -m src.capture_baseline --source "URL_OU_0"
```
3) **Executar detetor**  
```bash
python -m src.run --source "URL_OU_0"
```
Teclas: `q` sair | `b` atualizar baseline | `s` screenshot

> Se mudares a posição/zoom da câmara, refaz ROIs e baseline.