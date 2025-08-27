# src/calibrate_rois.py
import argparse, cv2, json
from .utils import open_capture
from .config import save_rois

def main():
    parser = argparse.ArgumentParser(description="Calibrar vagas em VÍDEO (desenha retângulos 1 a 1).")
    parser.add_argument("--source", required=True, help="0 (webcam) ou URL (RTSP/MJPEG/HTTP)")
    args = parser.parse_args()

    cap = open_capture(args.source)
    ok, frame = cap.read()
    if not ok:
        raise RuntimeError("Não foi possível ler a fonte de vídeo.")

    rois = []          # [{id,name,x,y,w,h}, ...]
    drawing = [False]  # usar lista p/ mutabilidade dentro do callback
    start = [(0, 0)]
    current = [None]

    win = "Calibração (ENTER=guardar | U=undo | C=limpar | Q=sair)"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing[0] = True
            start[0] = (x, y)
            current[0] = (x, y, 0, 0)
        elif event == cv2.EVENT_MOUSEMOVE and drawing[0]:
            x0, y0 = start[0]
            x1, y1 = x, y
            x_, y_ = min(x0, x1), min(y0, y1)
            w_, h_ = abs(x1 - x0), abs(y1 - y0)
            current[0] = (x_, y_, w_, h_)
        elif event == cv2.EVENT_LBUTTONUP and drawing[0]:
            drawing[0] = False
            if current[0]:
                x_, y_, w_, h_ = current[0]
                if w_ > 5 and h_ > 5:  # ignora cliques mínimos
                    rid = len(rois) + 1
                    rois.append({"id": rid, "name": f"Vaga {rid}", "x": int(x_), "y": int(y_), "w": int(w_), "h": int(h_)})
            current[0] = None

    cv2.setMouseCallback(win, on_mouse)

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        view = frame.copy()

        # desenha ROIs já confirmadas
        for r in rois:
            x, y, w, h = r["x"], r["y"], r["w"], r["h"]
            cv2.rectangle(view, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(view, r["name"], (x, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(view, r["name"], (x, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)

        # retângulo em desenho (mouse)
        if current[0]:
            x, y, w, h = current[0]
            cv2.rectangle(view, (x, y), (x + w, y + h), (0, 255, 255), 2)

        # instruções rápidas
        txt = f"Vagas: {len(rois)} | ENTER=guardar | U=undo | C=limpar | Q=sair"
        cv2.rectangle(view, (0, 0), (len(txt)*9+16, 32), (50, 50, 50), -1)
        cv2.putText(view, txt, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1, cv2.LINE_AA)

        cv2.imshow(win, view)
        k = cv2.waitKey(1) & 0xFF

        if k in (13, 10):  # ENTER
            if rois:
                save_rois(rois)
                print(f"{len(rois)} ROIs guardadas em data/rois.json.")
                break
            else:
                print("Nenhuma ROI para guardar.")
        elif k in (ord('u'), ord('U')):
            if rois: rois.pop()
        elif k in (ord('c'), ord('C')):
            rois.clear()
        elif k in (ord('q'), ord('Q'), 27):  # Q ou ESC
            print("Saída sem guardar.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
