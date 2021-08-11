import cv2
import time
import numpy as np
import HandGesturesModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#############
wCam, hcam = 640, 480
############

cap = cv2.VideoCapture(1)
cap.set(3, wCam)
cap.set(4, hcam)
pTime = 0

detector = htm.handDetector(DetectConf=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
print(volRange)
vol = 0
volBar = 40
volPercent = 0

while True:
        success, img = cap.read()
        img = detector.findHands(img)

        lmList = detector.findPosition(img, draw=False)
        #print(lmList)
        #lmList2 = detector.findPosition(img, handNo=1, draw=False)
        if len(lmList) != 0:
            #print(lmList[4], lmList[8])

            x1, y1 = lmList[4][1], lmList[4][2]
            x2, y2 = lmList[8][1], lmList[8][2]

            #if len(lmList2) != 0:
            #    x2, y2 = lmList2[4][1], lmList2[4][2]

            cx, cy = (x1+x2)//2, (y1+y2)//2

            cv2.circle(img, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)

            length = int(math.hypot(x2-x1, y2-y1))
            #print(length)

            #Hand Range 50 to 200
            #Vol Range -48 to 12
            vol = np.interp(length, [30,250], [minVol, maxVol])
            volBar = np.interp(length, [30,250], [40, 600])
            volPercent = np.interp(length, [30,250], [0, 100])
            #print(length, vol)

            if length <= 30:
                    cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
            if length >= 250:
                    cv2.circle(img, (cx, cy), 10, (255, 0, 0), cv2.FILLED)

            #if length > 30 or length < 250:
            #    volume.SetMasterVolumeLevel(vol, None)

        #drawing the volume bar
        cv2.rectangle(img, (40, 460), (600, 470), (0,255,0), 1)
        cv2.rectangle(img, (40, 460), (int(volBar), 470), (0,255,0), cv2.FILLED)
        cv2.putText(img, f'{int(volPercent)}%', (40, 445), cv2.FONT_HERSHEY_COMPLEX,
                    0.5, (0, 255, 0), 1)

        cTime =time.time()
        fps = 1/(cTime-pTime)
        pTime = cTime

        #cv2.putText(img, f'FPS: {int(fps)}', (0, 20), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 0, 255), 2)

        cv2.imshow("Img", img)
        cv2.waitKey(1)
