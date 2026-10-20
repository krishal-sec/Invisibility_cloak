import cv2
import numpy as np
import time

# ---------- SETTINGS ----------
COUNTDOWN = 5
HUE_TOL = 12      # how far from the clicked hue still counts as cloth
SAT_TOL = 70      # how much less saturated than the click still counts
VAL_TOL = 70      # how much darker than the click still counts
# Starting color: your blue dress
lower = np.array([90, 80, 50])
upper = np.array([130, 255, 255])
# ------------------------------

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

kernel = np.ones((3, 3), np.uint8)
current_frame = None
show_mask = False
cv2.namedWindow("Cloak")


def build_mask(hsv):
    """inRange that also handles hue wrapping (needed for red)."""
    h_lo, h_hi = int(lower[0]), int(upper[0])
    s_lo, v_lo = int(lower[1]), int(lower[2])
    if h_lo < 0:
        m1 = cv2.inRange(hsv, np.array([0, s_lo, v_lo]), np.array([h_hi, 255, 255]))
        m2 = cv2.inRange(hsv, np.array([h_lo + 180, s_lo, v_lo]), np.array([179, 255, 255]))
        return cv2.bitwise_or(m1, m2)
    if h_hi > 179:
        m1 = cv2.inRange(hsv, np.array([h_lo, s_lo, v_lo]), np.array([179, 255, 255]))
        m2 = cv2.inRange(hsv, np.array([0, s_lo, v_lo]), np.array([h_hi - 180, 255, 255]))
        return cv2.bitwise_or(m1, m2)
    return cv2.inRange(hsv, np.array([h_lo, s_lo, v_lo]), np.array([h_hi, 255, 255]))


def on_mouse(event, x, y, flags, param):
    global lower, upper
    if event != cv2.EVENT_LBUTTONDOWN or current_frame is None:
        return
    h, w = current_frame.shape[:2]
    y0, y1 = max(0, y - 7), min(h, y + 8)
    x0, x1 = max(0, x - 7), min(w, x + 8)
    patch = cv2.cvtColor(current_frame[y0:y1, x0:x1], cv2.COLOR_BGR2HSV)
    H, S, V = [int(np.median(patch[:, :, i])) for i in range(3)]
    if S < 60:
        print(f"Warning: that color is washed out (saturation {S}). "
              "Pale or white cloth will not work well.")
    lower = np.array([H - HUE_TOL, max(S - SAT_TOL, 50), max(V - VAL_TOL, 30)])
    upper = np.array([H + HUE_TOL, 255, 255])
    print(f"Picked H={H} S={S} V={V}")


cv2.setMouseCallback("Cloak", on_mouse)


def capture_background():
    start = time.time()
    while time.time() - start < COUNTDOWN:
        ret, frame = cap.read()
        if not ret:
            continue
        left = int(COUNTDOWN - (time.time() - start)) + 1
        shown = frame.copy()
        cv2.putText(shown, f"Leave the frame! Capturing in {left}",
                    (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Cloak", shown)
        cv2.waitKey(1)

    for _ in range(30):
        cap.read()

    frames = []
    for _ in range(60):
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    if not frames:
        return None
    return np.median(frames, axis=0).astype(np.uint8)


background = capture_background()
if background is None:
    print("Background capture failed")
    exit()

print("Running. Click the cloth to pick its color.")
print("Keys: b = new background, m = show/hide mask, q = quit")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break
    current_frame = frame

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = build_mask(hsv)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=3)
    if show_mask:
        cv2.imshow("Mask", mask)

    mask_soft = cv2.GaussianBlur(mask, (15, 15), 0)
    alpha = (mask_soft.astype(np.float32) / 255.0)[:, :, np.newaxis]
    result = (background * alpha + frame * (1 - alpha)).astype(np.uint8)

    cv2.imshow("Cloak", result)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('b'):
        new_bg = capture_background()
        if new_bg is not None:
            background = new_bg
    elif key == ord('m'):
        show_mask = not show_mask
        if not show_mask:
            cv2.destroyWindow("Mask")

cap.release()
cv2.destroyAllWindows()
