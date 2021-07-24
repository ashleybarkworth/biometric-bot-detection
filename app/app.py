import random
import time
from random import randint
import tkinter as tk
import logger
import argparse

# GUI Background colour
bg = 'SlateGray1'

# GUI screen width, height, and upper left corner (x,y) coordinates
canvas_width = 1100
canvas_height = 800
x_coord = 200
y_coord = 100

# Image folder containing objects for ball and sorting games
img_folder = 'img/'

# Either human, simple (Simple Bot), or advanced (Advanced Bot)
user_type = None


class MainApp(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.title('MainApp')
        self.geometry('{}x{}+{}+{}'.format(canvas_width, canvas_height, x_coord, y_coord))
        self.configure(bg=bg)
        self._mainCanvas = None
        self._allCanvases = dict()
        self.switch_canvas(StartUpPage)

    def switch_canvas(self, canvas_class):
        """
        Used to switch between different 'screens' of the GUI
        :param canvas_class: The canvas (scene) to switch to
        :return: nothing
        """
        if self._mainCanvas:
            self._mainCanvas.pack_forget()

        canvas = self._allCanvases.get(canvas_class, False)

        if not canvas:
            canvas = canvas_class(self)
            self._allCanvases[canvas_class] = canvas

        canvas.pack()
        self._mainCanvas = canvas


class StartUpPage(tk.Canvas):

    def start(self):
        self.master.switch_canvas(Keyboard)

    def __init__(self, master, *args, **kwargs):
        tk.Canvas.__init__(self, master, bg=bg, highlightthickness=3, highlightbackground=bg,
                           width=canvas_width, height=canvas_height, *args, **kwargs)
        tk.Frame(self)
        tk.Label(self, text='Bot or Not?', bg=bg, font='Verdana 60').pack(pady=50, fill=tk.Y)

        instructions = 'INSTRUCTIONS: Complete three activities using your mouse and/or\n keyboard. After playing, ' \
                       'your mouse and keyboard activity data are saved to 2 CSV files. '

        tk.Label(self, text=instructions, bg=bg, width=80, font='Verdana 14 bold').pack()

        tk.Label(self, text='Click the button to begin', bg=bg, pady=20, font='Verdana 16 italic').pack()

        tk.Button(self, text='START', command=self.start, width=10, height=2, font='Verdana 16').pack()

        self.pack()


class EndPage(tk.Canvas):

    def __init__(self, master, *args, **kwargs):
        tk.Canvas.__init__(self, master, width=canvas_width, height=canvas_height, *args, **kwargs)
        tk.Frame(self)
        tk.Label(self, text='Thanks for playing! This window will close shortly.', bg=bg,
                 font='Verdana 24 bold').pack(fill=tk.X)
        self.pack(expand=tk.YES)
        self.after(4000, self.master.destroy)


class Keyboard(tk.Frame):

    def end(self):
        if self.capture_started:
            time.sleep(2)
            # Stop logging key data and switch to ball game
            logger.stop_key_logging()
            self.master.switch_canvas(BallGame)
        else:
            # Display error message for 2 second
            self.error.config(fg='red')
            self.error.after(2000, lambda color=bg: self.error.config(fg=color))

    def start(self):
        self.capture_started = True
        logger.start_key_logging(user_type)

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=3, highlightbackground=bg,
                                width=canvas_width, height=canvas_height)

        instructions = 'Press \'Capture\' and type the following word 10 times'
        tk.Label(self, text=instructions, font='Verdana 14 bold', fg='orange2', bg=bg).pack(fill=tk.X, pady=(10, 0))
        self.master.configure(bg=bg)

        # Error message shown if user clicks "Done" before "Capture"
        error_msg = 'Please press \'Capture\' and type the word first.'
        self.error = tk.Label(self, text=error_msg, font='Verdana 14 bold', fg=bg, bg=bg)
        self.error.pack(pady=(0, 5))

        tk.Label(self, text='123CAPabc!', bg=bg, font='Verdana 14 italic').pack(fill=tk.X)
        self.entry = tk.Text(self, height=10, width=40, padx=40, pady=40, highlightbackground=bg)
        self.entry.pack(fill=tk.Y)

        def test(e):
            text = e.widget.get("1.0", "end-1c")
            word_count = len(text.split())
            if word_count > 10:
                self.end()

        self.entry.bind('<KeyRelease>', test)

        # Indicates whether key logger has started capturing
        self.capture_started = False

        tk.Button(self, text='Capture', bg='lightgoldenrod', font='Verdana 16', command=self.start).pack(side=tk.LEFT,
                                                                                                         anchor=tk.E,
                                                                                                         pady=10)
        self.configure(bg=bg)

        tk.Button(self, text='Done', bg='lightgoldenrod', font='Verdana 16', command=self.end).pack(side=tk.RIGHT,
                                                                                                    anchor=tk.W,
                                                                                                    pady=10)
        self.configure(bg=bg)

        self.pack()


class BallGame(tk.Frame):

    def end(self):
        pass

    def on_click(self, event=None):
        self.ball_count += 1
        if self.ball_count > 10:
            self.master.switch_canvas(SortingGame)
        else:
            # Hide ball
            self.canvas.itemconfigure(self.ball, state='hidden')

            # Choose random location for next object to appear
            x = randint(85, canvas_width - 85)
            y = randint(50, canvas_height - 180)

            # Move ball to new location
            self.canvas.coords(self.ball, x, y)
            self.canvas.itemconfigure(self.ball, state='normal')

    def start_game(self):
        logger.start_mouse_logging(user_type)
        self.start_btn.pack_forget()
        self.on_click(self)

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=3, highlightbackground=bg,
                                width=canvas_width, height=canvas_height)
        self.master.geometry('{}x{}+{}+{}'.format(canvas_width, canvas_height, x_coord, y_coord))

        instructions = 'INSTRUCTIONS: Click on the ball 10 times.'
        tk.Label(self, text=instructions, bg=bg, width=200, font='Verdana 14 bold').pack(pady=20)

        # Tracks number of times that the ball appears
        self.ball_count = 0

        self.start_btn = tk.Button(self, text='START', command=self.start_game, width=10, height=2, font='Verdana 16')
        self.start_btn.pack()
        self.configure(bg=bg)

        # Create and hide ball
        self.ball_img = tk.PhotoImage(file=img_folder + 'ball.png')
        self.ball = self.canvas.create_image(canvas_width / 2, canvas_height / 2, image=self.ball_img, tags='ball')
        self.canvas.itemconfigure(self.ball, state='hidden')
        self.canvas.tag_bind('ball', '<Button-1>', self.on_click)

        self.canvas.pack()


class SortingGame(tk.Frame):

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=3, highlightbackground=bg,
                                width=canvas_width, height=canvas_height)

        instructions = 'INSTRUCTIONS: Sort the following items into the boxes below'
        tk.Label(self, text=instructions, bg=bg, width=200, font='Verdana 14 bold').pack(pady=10)
        self.configure(bg=bg)

        # Number of correct sorts
        self.correct = 0

        # Boxes
        box_width, box_height = 480, 255
        x_padding, y_padding = 25, 40
        mid = canvas_width / 2

        # Coordinates for box and box label positions
        y2 = canvas_height - y_coord - y_padding
        x1 = mid - x_padding
        y1 = y2 - box_height
        x2 = mid + x_padding

        # [(lx, ly), (bx1, by1, bx2, by2)]
        # (lx, ly) are (x,y) coordinates for box's label
        # (bx1, by1, bx2, by2) are (x,y) coordinates for box's upper left (bx1, by1) and bottom right (bx2, by2) corner
        pos1 = [(x_padding + (box_width / 2), y1 - 20), (x1 - box_width, y2 - box_height, x1, y2)]
        pos2 = [(x2 + (box_width / 2), y1 - 20), (x2, y2 - box_height, x2 + box_width, y2)]
        # Shuffle positions
        positions = [pos1, pos2]
        # random.shuffle(positions)

        self.canvas.create_text(*positions[0][0], text='FRUITS', font='Verdana 18 bold')
        self.fruit_box = self.canvas.create_rectangle(*positions[0][1], fill='white', outline='black', tags='fruit_box')

        self.canvas.create_text(*positions[1][0], text='ANIMALS', font='Verdana 18 bold')
        self.animal_box = self.canvas.create_rectangle(*positions[1][1], fill='white', outline='black', tags='animals_box')

        # Create draggable objects
        self._drag_data = {'x': 0, 'y': 0, 'item': None}

        # x coordinate for image objects (1/8, 3/8, 5/8, 7/8)
        x_positions = [(canvas_width * (i / 8)) for i in range(1, 8, 2)]

        # y coordinates for image objects
        y_positions = [80, 240]

        # (x,y) position coordinates
        positions = [(i, j) for i in x_positions for j in y_positions]
        # Randomize where each object is placed
        random.shuffle(positions)

        # Fruits
        self.banana_img = tk.PhotoImage(file=img_folder + 'bananas.png')
        self.banana_token = self.create_image_token(positions[0][0], positions[0][1], self.banana_img)

        self.apple_img = tk.PhotoImage(file=img_folder + 'apple.png')
        self.apple_token = self.create_image_token(positions[1][0], positions[1][1], self.apple_img)

        self.orange_img = tk.PhotoImage(file=img_folder + 'orange.png')
        self.orange_token = self.create_image_token(positions[2][0], positions[2][1], self.orange_img)

        self.strawberry_img = tk.PhotoImage(file=img_folder + 'strawberry.png')
        self.strawberry_token = self.create_image_token(positions[3][0], positions[3][1], self.strawberry_img)

        # Animals
        self.dog_img = tk.PhotoImage(file=img_folder + 'dog.png')
        self.dog_token = self.create_image_token(positions[4][0], positions[4][1], self.dog_img)

        self.cat_img = tk.PhotoImage(file=img_folder + 'cat.png')
        self.cat_token = self.create_image_token(positions[5][0], positions[5][1], self.cat_img)

        self.beaver_img = tk.PhotoImage(file=img_folder + 'beaver.png')
        self.beaver_token = self.create_image_token(positions[6][0], positions[6][1], self.beaver_img)

        self.monkey_img = tk.PhotoImage(file=img_folder + 'monkey.png')
        self.monkey_token = self.create_image_token(positions[7][0], positions[7][1], self.monkey_img)

        self.correct_label = tk.Label(self, bg=bg, font='Verdana 18 bold', text='Correct: ' + str(self.correct))
        self.correct_label.pack(side=tk.BOTTOM, pady=(0, 20))

        self.canvas.tag_bind('token', '<ButtonPress-1>', self.drag_start)
        self.canvas.tag_bind('token', '<ButtonRelease-1>', self.drag_stop)
        self.canvas.tag_bind('token', '<B1-Motion>', self.drag)

        self.canvas.pack()

    def create_image_token(self, x, y, img):
        return self.canvas.create_image(x, y, image=img, tags='token')

    def is_correct(self, obj, box) -> bool:
        x, y = self.canvas.coords(obj)
        x1, y1, x2, y2 = self.canvas.coords(box)

        return x1 <= x <= x2 and y1 <= y <= y2

    def num_correct_fruits(self) -> int:
        # Returns True if all fruits have been placed in correct box, False otherwise
        return sum([self.is_correct(self.banana_token, self.fruit_box),
                    self.is_correct(self.apple_token, self.fruit_box),
                    self.is_correct(self.orange_token, self.fruit_box),
                    self.is_correct(self.strawberry_token, self.fruit_box)])

    def num_correct_animals(self) -> int:
        # Returns True if all animals have been placed in correct box, False otherwise
        return sum([self.is_correct(self.dog_token, self.animal_box),
                    self.is_correct(self.cat_token, self.animal_box),
                    self.is_correct(self.beaver_token, self.animal_box),
                    self.is_correct(self.monkey_token, self.animal_box)])

    def drag_start(self, event):
        self._drag_data['item'] = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data['x'] = event.x
        self._drag_data['y'] = event.y

    def drag_stop(self, event):
        self._drag_data['item'] = None
        self._drag_data['x'] = 0
        self._drag_data['y'] = 0

        self.correct = self.num_correct_fruits() + self.num_correct_animals()

        self.correct_label['text'] = 'Correct: ' + str(self.correct)

        if self.correct == 8:
            time.sleep(2)
            logger.stop_mouse_logging()
            self.master.switch_canvas(EndPage)

    def drag(self, event):
        # Compute how much the mouse has moved
        delta_x = event.x - self._drag_data['x']
        delta_y = event.y - self._drag_data['y']
        # Move the object the appropriate amount
        self.canvas.move(self._drag_data['item'], delta_x, delta_y)
        # Record the new position
        self._drag_data['x'] = event.x
        self._drag_data['y'] = event.y


def main():
    global user_type

    parser = argparse.ArgumentParser()
    parser.add_argument('userType', default='human')
    args = parser.parse_args()
    user_type = args.userType

    app = MainApp()
    app.mainloop()


if __name__ == '__main__':
    main()
