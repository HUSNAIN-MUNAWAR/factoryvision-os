from __future__ import annotations
from pathlib import Path
import cv2, time
class VideoCameraSimulator:
    def __init__(self,path:Path,realtime:bool=False,loop:bool=False): self.path=Path(path); self.realtime=realtime; self.loop=loop
    def frames(self):
        cap=cv2.VideoCapture(str(self.path)); fps=cap.get(cv2.CAP_PROP_FPS) or 25
        try:
            while True:
                ok,frame=cap.read()
                if not ok:
                    if self.loop: cap.set(cv2.CAP_PROP_POS_FRAMES,0); continue
                    break
                yield {'frame':frame,'timestamp':time.time(),'fps':fps}
                if self.realtime: time.sleep(1/fps)
        finally: cap.release()
