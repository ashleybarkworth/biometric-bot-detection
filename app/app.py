from random import randint
import tkinter as tk
import logger

bg = 'light sky blue'
canvas_width = 1100
canvas_height = 800
x_coord = 300
y_coord = 100

img_folder = 'app/img/'


class MainApp(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.title("MainApp")
        self.geometry("{}x{}+{}+{}".format(canvas_width, canvas_height, x_coord, y_coord))
        self.configure(bg=bg)
        self._mainCanvas = None
        self._allCanvases = dict()
        self.switch_canvas(StartUpPage)

    def switch_canvas(self, canvas_class):
        """
        Used to switch between different 'screens' in the img
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
        logger.start_recording()
        self.master.switch_canvas(BallGame)

    def __init__(self, master, *args, **kwargs):
        tk.Canvas.__init__(self, master, bg=bg, highlightthickness=3, highlightbackground=bg,
                           width=canvas_width, height=canvas_height, *args, **kwargs)
        tk.Frame(self)
        tk.Label(self, text="Bot or Not?", bg=bg, font="Verdana 60").pack(pady=50, fill="y")

        instructions = 'INSTRUCTIONS: Complete three activities using your mouse and/or\n keyboard. After playing, ' \
                       'please close the windows to save your \nmouse and keyboard activity data in events.csv. '

        tk.Label(self, text=instructions, bg=bg, width=50, font="Verdana 14 bold").pack()

        tk.Label(self, text="Click the button to begin", bg=bg, pady=20, font="Verdana 16 italic").pack()

        tk.Button(self, text="START", command=self.start, width=10, height=2, font='Verdana 16').pack()

        tk.Text(self, height=2, width=30).pack(pady=20)

        self.pack()


class EndPage(tk.Canvas):

    def __init__(self, master, *args, **kwargs):
        tk.Canvas.__init__(self, master, width=canvas_width, height=canvas_height, *args, **kwargs)
        tk.Frame(self)
        tk.Label(self, text="Thanks for playing! This window will close shortly.", bg=bg, font="Verdana 24 bold").pack(fill=tk.X)
        self.pack(expand=tk.YES)
        self.after(4000, self.master.destroy)


class BallGame(tk.Frame):

    def end(self):
        pass

    def on_click(self, event=None):
        # Hide both ball and spiky
        self.canvas.itemconfigure(self.ball, state='hidden')
        self.canvas.itemconfigure(self.spiky, state='hidden')

        # Choose random location for next object to appear
        x = randint(85, canvas_width - 85)
        y = randint(50, canvas_height - 180)

        # Choose either ball or spiky to appear randomly
        k = randint(0, 1)
        if k == 0:
            self.canvas.coords(self.ball, x, y)
            self.canvas.itemconfigure(self.ball, state='normal')
        else:
            self.canvas.coords(self.spiky, x, y)
            self.canvas.itemconfigure(self.spiky, state='normal')

        # Show another object after 2.5 seconds
        self.master.after(2200, self.on_click)

    def countdown(self, count):
        if count == 0:
            self.master.switch_canvas(SortingGame)
        self.time_label['text'] = count
        if count > 0:
            self.master.after(1000, self.countdown, count - 1)

    def start_game(self):
        self.start_btn.destroy()
        self.countdown(10)
        self.on_click(self)

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=3, highlightbackground=bg,
                                width=canvas_width, height=canvas_height)

        instructions = 'INSTRUCTIONS: For 40 seconds, click on the ball but avoid clicking on the spiky ball.'
        tk.Label(self, text=instructions, bg=bg, width=200, font="Verdana 14 bold").pack(pady=20)

        self.start_btn = tk.Button(self, text="START", command=self.start_game, width=10, height=2, font='Verdana 16')
        self.start_btn.pack()
        self.configure(bg=bg)

        # Create and hide ball
        self.ball_img = tk.PhotoImage(file=img_folder + 'ball.png')
        self.ball = self.canvas.create_image(canvas_width / 2, canvas_height / 2, image=self.ball_img, tags='ball')
        self.canvas.itemconfigure(self.ball, state='hidden')

        # Create and hide spiky ball
        self.spiky_img = tk.PhotoImage(file=img_folder + 'spiky.png')
        self.spiky = self.canvas.create_image(canvas_width / 3, canvas_height / 2, image=self.spiky_img, tags='spiky')
        self.canvas.itemconfigure(self.spiky, state='hidden')

        self.canvas.tag_bind('ball', '<Button-1>', self.on_click)
        self.canvas.tag_bind('spiky', '<Button-1>', self.on_click)

        self.time_label = tk.Label(self, bg=bg, font="Verdana 24")
        self.time_label.pack(side=tk.BOTTOM, pady=(0, 20))

        self.canvas.pack()


class SortingGame(tk.Frame):

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=3, highlightbackground=bg,
                                width=canvas_width, height=canvas_height)

        instructions = "INSTRUCTIONS: Sort the following items into the boxes below"
        tk.Label(self, text=instructions, bg=bg, width=200, font="Verdana 14 bold").pack(pady=20)
        self.configure(bg=bg)

        # Number of moves made
        self.moves = 0

        # Number of correct sorts
        self.correct = 0

        # Boxes
        box_width, box_height = 480, 270
        padding = 25
        mid = canvas_width / 2
        y2 = canvas_height - y_coord - padding
        y1 = y2 - box_height
        self.canvas.create_text((padding + box_width / 2, y1 - 20), text="FRUITS", font="Verdana 18 bold")
        self.fruit_box = self.canvas.create_rectangle(mid - padding - box_width, y1, mid - padding, y2, fill='white',
                                                      outline='black', tags='fruit_box')

        self.canvas.create_text((mid + padding + box_width / 2, y1 - 20), text="ANIMALS", font="Verdana 18 bold")
        self.animal_box = self.canvas.create_rectangle(mid + padding, y1, mid + padding + box_width, y2, fill='white',
                                                       outline='black', tags='animals_box')

        # Create draggable objects
        self._drag_data = {"x": 0, "y": 0, "item": None}

        # 1/8, 3/8, 5/8, 7/8
        x_positions = [(canvas_width * (i / 8)) for i in range(1, 8, 2)]
        x_positions = [item for item in x_positions for repetitions in range(2)]
        # random.shuffle(x_positions)

        y_positions = ([0, 1] * 4)
        y_positions = [80 + (i * 160) for i in y_positions]
        # random.shuffle(y_positions)

        # Fruits
        self.banana_img = tk.PhotoImage(file=img_folder + 'bananas.png')
        self.banana_token = self.create_image_token(x_positions[0], y_positions[0], self.banana_img)

        self.apple_img = tk.PhotoImage(file=img_folder + 'apple.png')
        self.apple_token = self.create_image_token(x_positions[1], y_positions[1], self.apple_img)

        self.orange_img = tk.PhotoImage(file=img_folder + 'orange.png')
        self.orange_token = self.create_image_token(x_positions[2], y_positions[2], self.orange_img)

        self.strawberry_img = tk.PhotoImage(file=img_folder + 'strawberry.png')
        self.strawberry_token = self.create_image_token(x_positions[3], y_positions[3], self.strawberry_img)

        # Animals
        self.dog_img = tk.PhotoImage(file=img_folder + 'dog.png')
        self.dog_token = self.create_image_token(x_positions[4], y_positions[4], self.dog_img)

        self.cat_img = tk.PhotoImage(file=img_folder + 'cat.png')
        self.cat_token = self.create_image_token(x_positions[5], y_positions[5], self.cat_img)

        self.beaver_img = tk.PhotoImage(file=img_folder + 'beaver.png')
        self.beaver_token = self.create_image_token(x_positions[6], y_positions[6], self.beaver_img)

        self.monkey_img = tk.PhotoImage(file=img_folder + 'monkey.png')
        self.monkey_token = self.create_image_token(x_positions[7], y_positions[7], self.monkey_img)

        self.canvas.tag_bind("token", "<ButtonPress-1>", self.drag_start)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.drag_stop)
        self.canvas.tag_bind("token", "<B1-Motion>", self.drag)

        self.correct_label = tk.Label(self, bg=bg, font="Verdana 18 bold", text='Correct: ' + str(self.correct))
        self.correct_label.pack(side=tk.BOTTOM, pady=(0, 20))

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
        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def drag_stop(self, event):
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0
        self.moves += 1

        self.correct = self.num_correct_fruits() + self.num_correct_animals()

        self.correct_label['text'] = 'Correct: ' + str(self.correct)

        if self.correct == 8 or self.moves == 16:
            self.master.switch_canvas(EndPage)

    def drag(self, event):
        # Compute how much the mouse has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        # Move the object the appropriate amount
        self.canvas.move(self._drag_data["item"], delta_x, delta_y)
        # Record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y


def main():
    app = MainApp()
    app.mainloop()


if __name__ == '__main__':
    main()
