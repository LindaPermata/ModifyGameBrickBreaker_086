# Jadi disini saya memodif
#Tampilan: Menggunakan warna pastel cerah (pink, ungu) untuk latar belakang, paddle, dan bricks.
#Kontrol: Paddle digerakkan dengan tombol panah kiri/kanan, dan game dimulai dengan tombol space.
#Game Mechanics: Menambahkan sistem nyawa, bola bergerak otomatis, dan menangani tabrakan dengan paddle dan bricks.
#Bricks: Bricks dengan ketahanan berbeda (3, 2, 1 hit) dan berubah warna saat hancur.
#HUD(Heads-Up Display): Menampilkan jumlah nyawa yang tersisa.

import tkinter as tk
import random

# Kelas dasar untuk objek permainan
class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)

# Kelas untuk bola yang bergerak
class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]  # arah pergerakan bola (horizontal, vertikal)
        self.speed = 5  # Kecepatan bola
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='white')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        # Pantulan bola di kiri atau kanan layar
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        # Pantulan bola di atas layar
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()
            if isinstance(game_object, PowerUp):
                game_object.activate(self)

# Kelas untuk paddle yang dikendalikan pemain
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FFB643')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)

# Kelas untuk brick yang bisa dihancurkan
class Brick(GameObject):
    COLORS = {1: '#FF77B4', 2: '#D7A3C2', 3: '#F4C1D7'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])

# Kelas untuk power-up yang memberikan efek tambahan
class PowerUp(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 20
        self.height = 20
        self.effect = random.choice(['expand', 'extra_ball'])  # Pilih efek acak
        item = canvas.create_oval(x - self.width / 2, y - self.height / 2,
                                  x + self.width / 2, y + self.height / 2,
                                  fill='yellow', tags='powerup')
        super(PowerUp, self).__init__(canvas, item)

    def activate(self, ball):
        if self.effect == 'expand':
            paddle_coords = ball.canvas.find_withtag('paddle')
            ball.canvas.coords(paddle_coords, -40, 20, 120, 40)
        elif self.effect == 'extra_ball':
            new_ball = Ball(ball.canvas, ball.get_position()[0] + 20, ball.get_position()[1] + 20)
            new_ball.update()

# Kelas utama untuk permainan
class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#D6D1F5',
                                width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle
        # Menambahkan brick dengan ketahanan yang berbeda
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-10))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(10))

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.text = self.draw_text(300, 200, 'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text,
                                       font=font)

    def update_lives_text(self):
        text = 'Lives: %s' % self.lives
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0: 
            self.ball.speed = None
            self.draw_text(300, 200, 'You win! You are the Breaker of Bricks!')
        elif self.ball.get_position()[3] >= self.height: 
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(300, 200, 'You Lose! Game Over!')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    game.mainloop()


