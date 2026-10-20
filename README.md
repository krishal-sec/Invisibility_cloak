# Invisibility Cloak (OpenCV + Python)

A real-time "invisibility cloak" built with OpenCV. Hold up a plain, vividly colored cloth in front of the webcam(default is blue) and the cloth area is replaced with a picture of the room behind it, so it looks like the cloth is see-through.

## How it works

Nothing is actually made invisible. It is a color-keyed background swap, the same idea as a green screen.

1. **Capture the background.** On launch, you leave the frame during a countdown. The program records 60 frames and takes the per-pixel median, which removes sensor noise and ignores brief intrusions.
2. **Convert each live frame to HSV.** HSV separates color (hue) from brightness, so the cloth is easier to detect when lighting varies.
3. **Build a mask.** `cv2.inRange` marks every pixel inside the cloth's color range. Red's hue wraps around the axis, so the code splits the range in two when needed.
4. **Clean the mask.** Morphological open removes specks, dilate covers the cloth's edge, and close fills small holes.
5. **Feather the edge.** A Gaussian blur turns the mask into a soft alpha channel so the border blends instead of looking cut out.
6. **Blend.** Where alpha is high you see the saved background, where it is low you see the live frame.

## Features

- Captures its own background at launch, so there is no stale image to manage
- Click on any cloth to teach it the color. No sliders and no editing code
- Handles red cloth (hue wrap-around)
- Live mask viewer for debugging
- Soft, feathered edges

## Requirements

- Python 3.11 or newer
- A webcam
- `opencv-python` and `numpy`

## Setup

```bash
git clone https://github.com/krishal-sec/Invisibility_cloak.git
cd Invisibility_cloak

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install opencv-python numpy
```

## Usage

```bash
python cloak.py
```

1. **Step out of the frame** during the countdown. Stay out until capture finishes.
2. Come back and hold the cloth up.
3. **Click on the cloth** (a flat, well-lit spot) to pick its color. The default is blue.

### Controls

| Key / action | What it does |
| --- | --- |
| Left click | Pick the cloth color at that spot |
| `b` | Recapture the background |
| `m` | Show or hide the mask window |
| `q` | Quit |

### Tuning

Edit these at the top of `cloak.py`:

| Setting | Effect |
| --- | --- |
| `HUE_TOL` | How far from the clicked hue still counts as cloth |
| `SAT_TOL` | How much less saturated than the click still counts |
| `VAL_TOL` | How much darker than the click still counts |

If the cloth has holes, raise `SAT_TOL` and `VAL_TOL`. If other things in the scene disappear, lower them.

## Tips for a good result

- Use a **plain, matte, vividly colored** cloth. Green and blue work best because they sit far from skin tones.
- Put the laptop on a stable surface and **do not move it** after the background is captured.
- Use steady lighting. A lamp facing you reduces noise.
- Wear a neutral color. Anything on you that matches the cloth color will vanish too.
- Press `b` if you move the camera or the lighting changes.

## Known limitations

- **The camera must stay still.** The background is a single saved image. If the camera moves, you will see a seam around the cloth.
- **Lighting changes break the match** between the saved background and the live scene.
- **Pale, white, grey, black, shiny, or patterned cloth does not work.** Low saturation or uneven color cannot be separated reliably.
- **Anything else in the cloth's color range also disappears**, such as a matching print on your clothes. Red cloth can also affect skin tones.
- **Slight flicker** can appear on pixels that sit near the edge of the color range.
- **Auto-exposure** on some webcams can shift brightness when you enter the frame. This code does not lock exposure.

## Tested on

- Arch Linux (Hyprland, Wayland), Python 3.14, OpenCV 5.0.0
- Windows and macOS have not been tested. On Windows, if the camera is slow to open or shows a black window, try `cv2.VideoCapture(0, cv2.CAP_DSHOW)`.

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `Cannot open camera` | Close other apps using the webcam. Try camera index `1` instead of `0`. |
| `No module named cv2` | Activate the venv, then run `pip install opencv-python numpy`. |
| Cloth does not vanish | Click a flat, bright part of the cloth. Press `m` to check the mask. |
| Visible seam or ghost | Press `b` to recapture the background, and keep the camera still. |

## Future work

- Replace the color mask with a segmentation model such as MediaPipe Selfie Segmentation, so no cloth is needed
- Lock camera exposure and white balance for a steadier background match
- Handle small camera movement with feature matching and homography

## What I learned

- How HSV color space makes color detection more robust than RGB
- How masks, morphological operations, and alpha blending combine into a real-time effect
- Why a still background and a live video feed need matched lighting and exposure
- Debugging camera and display issues across environments


