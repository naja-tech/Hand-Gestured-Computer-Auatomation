import cv2
from cvzone.HandTrackingModule import HandDetector
import mouse
import threading
import numpy as np
import time
import pyautogui

frameR = 10
cap = cv2.VideoCapture(0)
screen_width, screen_height = pyautogui.size()
detector = HandDetector(detectionCon=0.9, maxHands=2)

#For mouse control
l_delay = 0
r_delay = 0
double_delay = 0

def l_clk_delay():
    global l_delay
    global l_clk_thread
    time.sleep(1)
    l_delay = 0
    l_clk_thread = threading.Thread(target=l_clk_delay)

def r_clk_delay():
    global r_delay
    global r_clk_thread
    time.sleep(1)
    r_delay = 0
    r_clk_thread = threading.Thread(target=r_clk_delay)

def double_clk_delay():
    global double_delay
    global double_clk_thread
    time.sleep(2)
    double_delay = 0
    double_clk_thread = threading.Thread(target=double_clk_delay)


l_clk_thread = threading.Thread(target=l_clk_delay)
r_clk_thread = threading.Thread(target=r_clk_delay)
double_clk_thread = threading.Thread(target=double_clk_delay)


while True:
    success, img = cap.read()
    if success:
        img = cv2.flip(img, 1)
        img_height, img_width, _ = img.shape
        hands, img = detector.findHands(img, flipType=False)
        cv2.rectangle(img, (frameR, frameR), (img_width - frameR, img_height - frameR), (255, 0, 255), 2)
        if hands:
            lmlist = hands[0]['lmList']
            ind_x, ind_y = lmlist[8][0], lmlist[8][1]
            mid_x, mid_y = lmlist[12][0], lmlist[12][1]
            thumb_x, thumb_y= lmlist[4][0], lmlist[4][1]
            handtype = hands[0]["type"]
            print(handtype)
            cv2.circle(img, (ind_x, ind_y), 5, (0, 255, 255), 2)
            cv2.circle(img, (mid_x, mid_y), 5, (0, 255, 255), 2)
            fingers = detector.fingersUp(hands[0])
            print(fingers)

            if len(hands) == 2:
                # Hand 2
                hand2 = hands[1]
                lmlist2 = hand2["lmList"]
                handtype2 = hand2["type"]
                fingers2 = detector.fingersUp(hand2)
                ind_x2, ind_y2 = lmlist2[8][0], lmlist2[8][1]
                mid_x2, mid_y2 = lmlist2[12][0], lmlist2[12][1]
                thumb_x2, thumb_y2 = lmlist2[4][0], lmlist2[4][1]
                cv2.circle(img, (ind_x2, ind_y2), 5, (0, 255, 255), 2)
                cv2.circle(img, (mid_x2, mid_y2), 5, (0, 255, 255), 2)

                # Screen shot (thumbs + index -> both hands with thumb tips touching)
                if fingers[0] == 0 and fingers[1] == 1 and fingers2[0] == 0 and fingers2[1] == 1:
                    if abs(thumb_x - thumb_x2) < 25:
                        print('screen shot')
                        im1 = pyautogui.screenshot()
                        im1.save('screenshot.png')
                        time.sleep(2)
                # Control media player (one hand fist)
                if fingers[0] == 1 and fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
                    # Pause/play video or press space key (other hand all fingers)
                    if fingers2[0] == 0 and fingers2[1] == 1 and fingers2[2] == 1 and fingers2[3] == 1 and fingers2[4] == 1:
                        pyautogui.press('space')
                        print('Pause/Play/spacebar')
                        time.sleep(1)
                    # Fast Forward (other hand index)
                    if fingers2[0] == 1 and fingers2[1] == 1 and fingers2[2] == 0 and fingers2[3] == 0 and fingers2[4] == 0:
                        pyautogui.press('right')
                        print('Fast forward/Move Right')
                        time.sleep(1)
                    # Rewind (other hand thumb)
                    if fingers2[0] == 0 and fingers2[1] == 0 and fingers2[2] == 0 and fingers2[3] == 0 and fingers2[4] == 0:
                        pyautogui.press('left')
                        print('Rewind/Move left')
                        time.sleep(1)

                # Control System volume (one hand index and middle fingers like 'v')
                if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
                    #Volume up (other hand index)
                    if fingers2[0] == 1 and fingers2[1] == 1 and fingers2[2] == 0 and fingers2[3] == 0 and fingers2[4] == 0:
                        pyautogui.press('volumeup')
                        print('Volume Up')
                    #Volume down (other hand thumb)
                    if fingers2[0] == 0 and fingers2[1] == 0 and fingers2[2] == 0 and fingers2[3] == 0 and fingers2[4] == 0:
                        pyautogui.press('volumedown')
                        print('Volume down')


            # Mouse movement (only index finger)
            if fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 1:
                conv_x = int(np.interp(ind_x, (frameR, img_width - frameR), (-20,  screen_width)))
                conv_y = int(np.interp(ind_y, (frameR, img_height - frameR), (0,2* screen_height)))
                mouse.move(conv_x, conv_y)
                print("cursor movement")
                #print(conv_x, conv_y)

            # Mouse Button Clicks (only index and middle fingers => close together)
            if fingers[1] == 1 and fingers[2] == 1 and fingers[0]==1:
                if abs(ind_x - mid_x) < 25:
                    # Left Click (index + middle)
                    if fingers[3] == 0 and l_delay == 0:
                        mouse.click(button="left")
                        print('left click')
                        l_delay = 1
                        l_clk_thread.start()

                    # Right Click (index + middle + ring fingers)
                    if fingers[3] == 1 and fingers[4]==0 and r_delay == 0:
                        mouse.click(button="right")
                        print('right click')
                        r_delay = 1
                        r_clk_thread.start()

            # Mouse Scroll down (index + middle + thumb + ring)
            if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[3] == 1 :
                if abs(ind_x - mid_x) < 25:
                    mouse.wheel(delta=-1)
                    print('scroll down')
            # Mouse Scroll up (index + middle + thumb)
            if fingers[1] == 1 and fingers[2] == 1 and fingers[0] == 0 and fingers[3] == 0:
                if abs(ind_x - mid_x) < 25:
                    mouse.wheel(delta=1)
                    print('scroll up')


            # Double Mouse Click (index + thumb only)
            if fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 0 and fingers[3] == 0 and double_delay == 0:
                double_delay = 1
                mouse.double_click(button="left")
                print('double click')
                double_clk_thread.start()

        cv2.imshow("Camera Feed", img)
        cv2.waitKey(1)