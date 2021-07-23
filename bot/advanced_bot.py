import random
import time
import pyautogui
from util import bezier_curve

region = (400, 200, 2200, 1600)

img_folder = 'img/'


def find_center(location):
    """
    Finds the center of an object given its location on screen (left, top,
    :param location: (left, top, width, height) coordinate of the image on the screen
    :return: nothing
    """
    center = pyautogui.center(location)
    return center.x / 2, center.y / 2


def find_image(img, grayscale):
    """
    Returns (left, top, width, height) coordinate of first found instance of the image on the screen. Waits up to
    10 seconds to find image.
    :param img: reference image of the object to be located
    :param grayscale: True if using grayscale to locate image, False otherwise. Grayscale desaturates images =>
    speedier lookup, but greater chance of false positives
    :return: (left, top, width, height) coordinate of first found instance of the image on the screen
    """
    filepath = img_folder + img
    location = None
    timeout = time.time() + 5  # Wait up to 5 seconds to find image
    while location is None and time.time() < timeout:
        try:
            location = pyautogui.locateOnScreen(filepath, confidence=.8, grayscale=grayscale, region=region)
        except Exception as e:
            print(e)

    return location


def click_image(location):
    """
    Locates the center of an object on screen using image recognition and left-clicks it
    :param location: (left, top, width, height) coordinate of the image on the screen
    :return: nothing
    """
    if location is not None:
        x, y = find_center(location)
        bezier_curve.moveTo(x, y)
        # Time between press and release
        click_time = random.uniform(0.05, 0.1)
        pyautogui.mouseDown()
        time.sleep(click_time)
        pyautogui.mouseUp()


def play_sorting_game():
    """
    Locates the fruit and animal boxes, then for each of the objects, locates them on screen and performs
    Drag-and-Drop to place them in box.
    :return: nothing
    """
    objects = ['apple', 'banana', 'beaver', 'cat', 'dog', 'monkey', 'strawberry', 'orange']  # list of objects to sort
    random.shuffle(objects)  # sort objects in random order
    time.sleep(1.5)
    fx, fy = find_center(find_image('fruits_box.png', False))
    ax, ay = find_center(find_image('animals_box.png', False))

    tweens = [pyautogui.easeInOutCirc, pyautogui.easeInOutElastic, pyautogui.easeInOutBack, pyautogui.easeInOutBounce]

    for obj in objects:
        fruits = ['apple', 'orange', 'banana', 'strawberry']
        animals = ['beaver', 'cat', 'dog', 'monkey']
        img = ''.join([obj, '.png'])
        x, y = find_center(find_image(img, False))
        bezier_curve.moveTo(x, y)
        tween = random.choice(tweens)
        print(tween)
        duration = random.uniform(0.1, 1.0)
        if obj in fruits:
            pyautogui.dragTo(fx, fy, duration=duration, button='left', tween=tween)
            # bezier_curve.dragTo(fx, fy)
        elif obj in animals:
            pyautogui.dragTo(ax, ay, duration=duration, button='left', tween=tween)
            # bezier_curve.dragTo(ax, ay)


def play_ball_game():
    """
    Locates the ball and uses Point-and-Click action to move and click on it
    :return: nothing
    """
    click_start_button()
    clicks = 0
    while clicks < 10:
        ball_location = find_image('ball.png', True)
        click_image(ball_location)
        clicks += 1


def type_words():
    times = 10
    text = '123CAPabc!'
    for i in range(times):
        seconds = random.uniform(0.05, 0.55)
        pyautogui.typewrite(text, interval=seconds)
        # Enter new line after all but last word
        if i < times - 1:
            pyautogui.press('enter')


def complete_keyboard_activity():
    # Start capturing keystroke data
    location = find_image('capture_btn.png', True)
    click_image(location)
    # Locate text box and type word
    location = find_image('text_box.png', True)
    click_image(location)
    # Type word
    type_words()
    # Finish capturing
    location = find_image('done_btn.png', True)
    click_image(location)


def click_start_button():
    start_button_location = find_image('start_btn.png', True)
    click_image(start_button_location)


def main():
    time.sleep(1)
    # Click start_time button to begin
    click_start_button()
    # Complete the keyboard activity
    complete_keyboard_activity()
    time.sleep(1)
    # Play the ball clicking game
    play_ball_game()
    # Play the drag-and-drop sorting game
    play_sorting_game()


if __name__ == '__main__':
    main()
