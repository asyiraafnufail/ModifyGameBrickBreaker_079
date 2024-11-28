# UNTUK PERUBAHAN CODE SILAHKAN BACA FILE README.MD 


import tkinter as tk


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


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 8
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='white')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
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


class Brick(GameObject):
    # Hapus warna yang berbeda untuk hits yang berbeda
    COLORS = '#800000'

    def __init__(self, canvas, x, y):
        self.width = 75
        self.height = 20
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=self.COLORS, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        # Langsung hapus brick saat dipukul
        self.delete()


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.score = 0
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#000000',
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle
        
        self.create_bricks()

        self.hud = None
        self.score_text = None
        self.game_over_text = None
        self.is_game_over = False
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-30) if not self.is_game_over else None)
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(30) if not self.is_game_over else None)
        self.canvas.bind('<space>', self.handle_space_key)

    def create_bricks(self):
        for x in range(5, self.width - 5, 75):
            # Hapus parameter hits, sekarang semua brick langsung hancur
            self.add_brick(x + 37.5, 50)
            self.add_brick(x + 37.5, 70)
            self.add_brick(x + 37.5, 90)

    def setup_game(self):
        self.add_ball()
        self.update_lives_text()
        self.update_score_text()
        self.text = self.draw_text(300, 200,
                                   'Press Space to start')

    def handle_space_key(self, event):
        if self.is_game_over:
            # Restart the game if it's already game over
            self.reset_game()
        elif self.text:
            # Start the game if it hasn't started yet
            self.start_game()

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y):
        brick = Brick(self.canvas, x, y)
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

    def update_score_text(self):
        text = 'Score: %s' % self.score
        if self.score_text is None:
            self.score_text = self.draw_text(550, 20, text, 15)
        else:
            self.canvas.itemconfig(self.score_text, text=text)

    def start_game(self):
        self.canvas.delete(self.text)
        self.text = None
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0: 
            self.ball.speed = None
            self.draw_text(300, 200, 'You win! You the Breaker of Bricks.')
            self.score += 100  # Bonus points for clearing all bricks
            self.update_score_text()
        elif self.ball.get_position()[3] >= self.height: 
            self.ball.speed = None
            self.lives -= 1
            if self.lives <= 0:
                self.game_over()
            else:
                # Restart the round after 1 second
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def game_over(self):
        self.is_game_over = True
        self.ball.speed = None
        
        # Clear any existing game over text
        if self.game_over_text:
            self.canvas.delete(self.game_over_text)
        
        # Draw game over text with score
        self.game_over_text = self.draw_text(300, 200, f'Game Over!\nYour Score: {self.score}\nPress Space to Restart', 25)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        
        # Track initial number of bricks before collision
        initial_brick_count = len(self.canvas.find_withtag('brick'))
        
        self.ball.collide(objects)
        
        # Calculate bricks destroyed
        current_brick_count = len(self.canvas.find_withtag('brick'))
        bricks_destroyed = initial_brick_count - current_brick_count
        
        # Add score for destroyed bricks
        if bricks_destroyed > 0:
            self.score += bricks_destroyed * 10
            self.update_score_text()

    def reset_game(self):
        # Clear game over text
        if self.game_over_text:
            self.canvas.delete(self.game_over_text)
            self.game_over_text = None

        # Clear all existing items
        self.canvas.delete('all')
        
        # Reset game state
        self.lives = 3
        self.score = 0
        self.is_game_over = False
        
        # Recreate paddle and bricks
        self.items = {}
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle
        
        # Recreate bricks
        self.create_bricks()
        
        # Reset HUD and score text
        self.hud = None
        self.score_text = None
        
        # Set up the game again
        self.setup_game()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Break those Bricks!')
    game = Game(root)
    root.mainloop()