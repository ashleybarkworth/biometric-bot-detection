import time

import pyautogui

region = (600, 200, 2200, 1600)

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
    timeout = time.time() + 10  # Wait up to 10 seconds to find image
    while location is None and time.time() < timeout:
        try:
            location = pyautogui.locateOnScreen(filepath, confidence=.65, grayscale=grayscale, region=region)
        except Exception as e:
            print(e)

    return location


def click_image(location):
    """
    Locates the center of an object on screen using image recognition and left-clicks it
    :param location:  (left, top, width, height) coordinate of the image on the screen
    :return:nothing
    """
    # Calculates and clicks the image centre
    if location is not None:
        x, y = find_center(location)
        pyautogui.moveTo(x, y, duration=0.05)
        pyautogui.leftClick()


def type_word(word):
    """
    Types word by performing a keyboard key press down, followed by a release, for each of
    the characters in it
    :param word: the word to be typed
    :return: nothing
    """
    pyautogui.typewrite(word)
    pyautogui.press('enter')


def play_sorting_game():
    """
    Locates the fruit and animal boxes, then for each of the objects, locates them on screen and performs
    Drag-and-Drop to place them in box. (Drag-and-Drop is instantaneous with a linear trajectory for simple bot)
    :return: nothing
    """
    objects = ['apple', 'banana', 'beaver', 'cat', 'dog', 'monkey', 'strawberry', 'orange']

    fx, fy = find_center(find_image('fruits_box.png', True))
    ax, ay = find_center(find_image('animals_box.png', True))

    fruits = ['apple', 'orange', 'banana', 'strawberry']
    animals = ['beaver', 'cat', 'dog', 'monkey']

    for obj in objects:
        img = ''.join([obj, '.png'])
        x, y = find_center(find_image(img, False))
        pyautogui.moveTo(x, y, duration=0.05)

        if obj in fruits:
            pyautogui.dragTo(fx, fy, button='left')
        elif obj in animals:
            pyautogui.dragTo(ax, ay, button='left')


def play_ball_game():
    """
    Locates the ball and uses Point-and-Click action to move and click on it
    :return: nothing
    """
    click_start_button()
    timeout = time.time() + 10
    while time.time() < timeout:
        location = find_image('ball.png', True)
        click_image(location)


def click_start_button():
    location = find_image('start_btn.png', True)
    click_image(location)


def main():
    pyautogui.MINIMUM_DURATION = 0
    time.sleep(1)
    # Type something into the input box
    location = find_image('input_box.png', False)
    click_image(location)
    type_word('hello world')
    # Click start_time button to begin recording
    click_start_button()
    # Play the ball clicking game
    play_ball_game()
    # Play the drag-and-drop sorting game
    play_sorting_game()


if __name__ == '__main__':
    main()
