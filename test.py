from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Rectangle, Color
from kivy.clock import Clock
from kivy.vector import Vector
from random import randint

class Snake(Widget):
    def __init__(self, size):
        super(Snake, self).__init__()
        self.size = size
        self.snake_block = Rectangle()
        self.food_block = Rectangle()
        self.create_snake()
        self.create_food()
        self.direction = Vector(1, 0)
        self.bind(pos=self.update_snake)
        Clock.schedule_interval(self.move_snake, 1.0/15.0)

    def create_snake(self):
        with self.canvas:
            Color(1, 1, 0)
            self.snake_block = Rectangle(pos=(300, 300), size=(self.size, self.size))

def create_food(self):
    with self.canvas:
        Color(1, 0, 0)
        self.food_block = Rectangle(pos=(randint(0, 600-self.size), randint(0, 600-self.size)), size=(self.size, self.size))
        
def update_snake(self, *args):
    self.snake_block.pos = self.pos

def move_snake(self, dt):
    self.pos = Vector(*self.pos) + self.direction
    if self.food_block.collide_widget(self):
        self.create_food()

def on_touch_down(self, touch):
    if touch.x < self.width/2:
        self.direction = Vector(-1, 0)
    else:
        self.direction = Vector(1, 0)

class SnakeApp(App):
    def build(self):
        return Snake(20)

if __name__ == '__main__':
    SnakeApp().run()
