import cv2
import mediapipe as mp
import pyautogui
import time

# Initialize MediaPipe Hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# State variable to prevent multiple screenshots for one fist
hand_was_open = False

print("Hand Gesture Screenshot Tool Started...")

while cap.isOpened():
    success, img = cap.read()
    if not success:
        break

    # Flip image for a mirror effect and convert to RGB
    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            # Draw hand landmarks on the screen
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
            
            # Get the IDs for the tips of the fingers
            # 8=Index, 12=Middle, 16=Ring, 20=Pinky
            tips = [8, 12, 16, 20]
            fingers_open = []

            # Check if fingers are open (tip is higher than the joint below it)
            for tip in tips:
                if hand_lms.landmark[tip].y < hand_lms.landmark[tip - 2].y:
                    fingers_open.append(True)
                else:
                    fingers_open.append(False)

            # Logic for Screenshot
            # 1. If all 4 fingers are open, set hand_was_open to True
            if all(fingers_open):
                hand_was_open = True
                cv2.putText(img, "Hand Open: Ready", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # 2. If hand was open and now all fingers are closed (fist)
            elif hand_was_open and not any(fingers_open):
                print("Fist detected! Taking screenshot...")
                cv2.putText(img, "SCREENSHOT TAKEN!", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
                
                # Take screenshot and save it with a timestamp
                ts = time.strftime("%Y%m%d-%H%M%S")
                pyautogui.screenshot(f"screenshot_{ts}.png")
                
                # Reset state and add a small delay to prevent double-triggering
                hand_was_open = False
                time.sleep(1)

    cv2.imshow("Hand Tracker", img)
    
    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()