import pyautogui
import random
import numpy as np
import time
from scipy import interpolate
import math


def moveTo(x2, y2):
    disable_pauses()
    x1, y1 = pyautogui.position()
    cp = random.randint(3, 3)  # Number of control points. Must be at least 2.

    # Distribute control points between start_time and destination evenly.
    x = np.linspace(x1, x2, num=cp, dtype='int')
    y = np.linspace(y1, y2, num=cp, dtype='int')

    # Randomise inner points a bit (+-RAND at most).
    RAND = 50
    xr = [random.randint(-RAND, RAND) for k in range(cp)]
    yr = [random.randint(-RAND, RAND) for k in range(cp)]
    xr[0] = yr[0] = xr[-1] = yr[-1] = 0
    x += xr
    y += yr

    # Approximate using Bezier spline.
    degree = 3 if cp > 3 else cp - 1  # Degree of b-spline. 3 is recommended.
    # Must be less than number of control points.
    tck, u = interpolate.splprep([x, y], k=degree)
    # Move up to a certain number of points
    u = np.linspace(0, 1, num=2 + int(point_dist(x1, y1, x2, y2) / 50.0))
    points = interpolate.splev(u, tck)

    # Move mouse.
    duration = random.uniform(0.1, 0.6)
    timeout = duration / len(points[0])
    point_list = zip(*(i.astype(int) for i in points))
    for point in point_list:
        pyautogui.moveTo(*point)
        time.sleep(timeout)

    reset_pauses()


def point_dist(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def disable_pauses():
    pyautogui.MINIMUM_DURATION = 0
    pyautogui.MINIMUM_SLEEP = 0
    pyautogui.PAUSE = 0


def reset_pauses():
    pyautogui.MINIMUM_DURATION = 0.1
    pyautogui.MINIMUM_SLEEP = 0.05
    pyautogui.PAUSE = 0.1