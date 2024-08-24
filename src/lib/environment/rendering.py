import pyglet
from pyglet import shapes

WHITE = [255, 255, 255, 255]
GREEN = [0, 255, 0, 123]
BLUE = [0, 0, 128, 255]
BLACK = [0, 0, 0, 255]
RED = [255, 0, 0, 123]
LIGHT = [255, 150, 150, 123]


class PygletWindow:

    def __init__(self, width, height):
        self.active = True
        self.display_surface = pyglet.window.Window(width=width, height=height)
        self.top = height
        self.main_batch = pyglet.graphics.Batch()
        self.items = []

        pyglet.gl.glLineWidth(3)

        # make OpenGL context current
        self.display_surface.switch_to()
        self.reset()

    def text(self, text, x, y, font_size=20, color=BLACK):
        y = self.translate(y)
        label = pyglet.text.Label(
            text, font_size=font_size,
            x=x, y=y, anchor_x='left', anchor_y='top',
            batch=self.main_batch,
            color=color)
        self.items.append(label)

    def translate(self, y):
        y = self.top - y
        return y

    def rectangle(self, x, y, dx, dy, color=BLACK):
        y = self.translate(y)
        rectangle_1 = shapes.Rectangle(
            x, y, dx, dy,
            color=color,
            batch=self.main_batch)
        rectangle_2 = shapes.Rectangle(
            x + 1, y + 1, dx - 1, dy - 1,
            color=WHITE,
            batch=self.main_batch)
        self.items.append(rectangle_1)
        self.items.append(rectangle_2)

    def line(self, x, y, dx, dy, color=BLACK):
        y = self.translate(y)
        dy = self.translate(dy)
        line = shapes.Line(
            x, y, dx, dy,
            width=2,
            color=color,
            batch=self.main_batch)
        self.items.append(line)

    def reset(self):
        pyglet.clock.tick()
        self.display_surface.dispatch_events()
        pyglet.gl.glClearColor(1, 1, 1, 1)
        from pyglet.gl import glClear
        glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
        self.main_batch = pyglet.graphics.Batch()

    def update(self):
        """Draw the current state on screen"""
        self.main_batch.draw()
        self.display_surface.flip()
        self.items = []

    def close(self):
        self.display_surface.close()