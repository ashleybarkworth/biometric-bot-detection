from random import randrange, randint

import tkinter as tk

import logger

canvas_width = 900
canvas_height = 650
x_coord = 300
y_coord = 200


class MainApp(tk.Tk):

    def __init__(self):
        tk.Tk.__init__(self)
        self.title("MainApp")
        self.geometry("{}x{}+{}+{}".format(canvas_width, canvas_height, x_coord, y_coord))
        self._mainCanvas = None
        self._allCanvases = dict()
        self.switch_canvas(StartUpPage)

    def switch_canvas(self, canvas_class):

        if self._mainCanvas:
            self._mainCanvas.pack_forget()

        canvas = self._allCanvases.get(canvas_class, False)

        if not canvas:
            canvas = canvas_class(self)
            self._allCanvases[canvas_class] = canvas

        canvas.pack()
        self._mainCanvas = canvas


class StartUpPage(tk.Canvas):

    def begin(self):
        logger.start_recording()
        self.master.switch_canvas(BallGame)

    def __init__(self, master, *args, **kwargs):
        tk.Canvas.__init__(self, master, width=canvas_width, height=canvas_height, *args, **kwargs)
        tk.Frame(self)
        tk.Label(self, text="Click the button to start", font="none 24 bold").pack(fill="x")
        tk.Button(self, text="BEGIN", command=self.begin, width=10).pack()
        self.pack(expand=tk.YES)


class EndPage(tk.Canvas):

    def __init__(self, master, *args, **kwargs):
        tk.Canvas.__init__(self, master, width=canvas_width, height=canvas_height, *args, **kwargs)
        tk.Frame(self)
        tk.Label(self, text="Thanks for playing! Please close the window.", font="none 24 bold").pack(fill="x")
        self.pack(expand=tk.YES)


class BallGame(tk.Frame):

    def end(self):
        pass

    def on_click(self, event=None):
        self.ball_clicks += 1
        x_padding = 90
        y_padding = 120

        if self.ball_clicks >= 10:
            print('Ball popped')
            self.master.switch_canvas(SortingGame)
        else:
            x = randint(x_padding, canvas_width - x_padding)
            y = randint(y_padding, canvas_height - y_padding)
            self.canvas.coords(self.ball, x, y)

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.canvas = tk.Canvas(self, bg='#9ae7f5', width=canvas_width, height=canvas_height)

        self.ball_clicks = 0
        self.ball_label = self.canvas.create_text((450, 20), text="Click the Ball 10 Times", font="none 20 bold")
        self.ball_img = tk.PhotoImage(file="img/ball.png")
        self.ball = self.canvas.create_image(canvas_width / 2, canvas_height / 2, image=self.ball_img, tags='ball')
        self.canvas.tag_bind('ball', '<Button-1>', self.on_click)

        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)


class SortingGame(tk.Frame):

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.canvas = tk.Canvas(self, width=canvas_width, height=canvas_height)
        self.canvas.pack(fill="both", expand=True)

        self._drag_data = {"x": 0, "y": 0, "item": None}

        # Fruits
        self.banana_img = tk.PhotoImage(file="img/bananas.png")
        self.banana_token = self.create_image_token(100, 100, self.banana_img)

        self.apple_img = tk.PhotoImage(file="img/apple.png")
        self.apple_token = self.create_image_token(150, 100, self.apple_img)

        self.orange_img = tk.PhotoImage(file="img/orange.png")
        self.orange_token = self.create_image_token(300, 100, self.orange_img)

        # Animals
        self.dog_img = tk.PhotoImage(file="img/dog.png")
        self.dog_token = self.create_image_token(500, 100, self.dog_img)

        self.cat_img = tk.PhotoImage(file="img/cat.png")
        self.cat_token = self.create_image_token(600, 100, self.cat_img)

        self.beaver_img = tk.PhotoImage(file="img/beaver.png")
        self.beaver_token = self.create_image_token(750, 100, self.beaver_img)

        # Boxes
        fruit_label = self.canvas.create_text((200, 380), text="FRUITS")
        self.fruit_box = self.canvas.create_rectangle(50, 400, 350, 600, outline='black', tags='fruit_box')

        animal_label = self.canvas.create_text((700, 380), text="ANIMALS")
        self.animal_box = self.canvas.create_rectangle(550, 400, 850, 600, outline='black', tags='animals_box')

        self.canvas.tag_bind("token", "<ButtonPress-1>", self.drag_start)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.drag_stop)
        self.canvas.tag_bind("token", "<B1-Motion>", self.drag)

    def create_image_token(self, x, y, img):
        return self.canvas.create_image(x, y, image=img, tags='token')

    def correct_box(self, obj, box):
        x, y = self.canvas.coords(obj)
        x1, y1, x2, y2 = self.canvas.coords(box)

        return x1 <= x <= x2 and y1 <= y <= y2

    def fruits_correct(self):
        return self.correct_box(self.banana_token, self.fruit_box) \
               and self.correct_box(self.apple_token, self.fruit_box) \
               and self.correct_box(self.orange_token, self.fruit_box)

    def animals_correct(self):
        return self.correct_box(self.dog_token, self.animal_box) \
               and self.correct_box(self.cat_token, self.animal_box) \
               and self.correct_box(self.beaver_token, self.animal_box)

    def drag_start(self, event):
        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def drag_stop(self, event):
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

        if self.fruits_correct() and self.animals_correct():
            print('correct for both')
            self.master.switch_canvas(EndPage)

    def drag(self, event):
        # compute how much the mouse has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        # move the obj the appropriate amount
        self.canvas.move(self._drag_data["item"], delta_x, delta_y)
        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y


def main():
    app = MainApp()
    app.mainloop()


if __name__ == '__main__':
    main()
