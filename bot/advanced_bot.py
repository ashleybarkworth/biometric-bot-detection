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
    box_width, box_height = 480, 255  # Dimensions of sorting boxes, used to place objects in random locations in boxes
    padding = 60
    tweens = [pyautogui.easeInOutBack, pyautogui.easeInOutBounce, pyautogui.easeInOutElastic]

    for obj in objects:
        fruits = ['apple', 'orange', 'banana', 'strawberry']
        animals = ['beaver', 'cat', 'dog', 'monkey']
        img = ''.join([obj, '.png'])
        x, y = find_center(find_image(img, False))
        bezier_curve.moveTo(x, y)
        tween = random.choice(tweens)
        duration = random.uniform(0.6, 2.0)

        x_rand = random.randint(-box_width // 2 + padding, box_width // 2 - padding)
        y_rand = random.randint(-box_height // 2 + padding, box_height // 2 - padding)

        if obj in fruits:
            pyautogui.dragTo(fx + x_rand, fy + y_rand, duration=duration, button='left', tween=tween)
        elif obj in animals:
            pyautogui.dragTo(ax + x_rand, ay + y_rand, duration=duration, button='left', tween=tween)


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
        for c in text:
            # Random wait time between characters
            seconds = random.uniform(0.01, 0.6)
            pyautogui.keyDown(c)
            time.sleep(seconds)
            pyautogui.keyUp(c)
        # Enter new line after all but last word
        if i < times - 1:
            # Random wait time after finishing word
            seconds = random.uniform(0.5, 2.0)
            time.sleep(seconds)
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
    time.sleep(5)
    exit()


if __name__ == '__main__':
    main()
