import argparse
import cv2
from .utils import open_capture
from .config import DATA_DIR, BASELINE_PATH

def main():
    parser = argparse.ArgumentParser(description="Capturar baseline com vagas vazias.")
    parser.add_argument("--source", required=True, help="0 (webcam) ou URL")
    args = parser.parse_args()

    cap = open_capture(args.source)
    print("A capturar baseline em 2s. Garante que todas as vagas estão livres.")
    cv2.waitKey(2000)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError("Não foi possível capturar o baseline.")

    DATA_DIR.mkdir(exist_ok=True, parents=True)
    cv2.imwrite(str(BASELINE_PATH), frame)
    print(f"Baseline guardado em {BASELINE_PATH}.")

if __name__ == "__main__":
    main()