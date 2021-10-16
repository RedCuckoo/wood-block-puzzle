from random import randint

import pyxel


class Figure:
    def __init__(self, u, v, w, h, preview_figure=None):
        self.u = u
        self.v = v
        self.w = w
        self.h = h
        self.preview_figure = preview_figure

    def draw(self, x, y, img = 0):
        pyxel.blt(x, y, img, self.u, self.v, self.w, self.h, 12)


class FigureStorage:
    def __init__(self, figure_list):
        self.figure_list = figure_list

    def get_rand_figure(self):
        return self.figure_list[randint(0, len(self.figure_list) - 1)]


class FigureOffer:
    def __init__(self, figure_storage):
        self.offer_list = [None, None, None]
        self.figure_storage = figure_storage

    def need_to_generate(self):
        for v in self.offer_list:
            if v is not None:
                return False
        return True

    def generate(self):
        self.offer_list[0] = self.figure_storage.get_rand_figure().preview_figure
        self.offer_list[1] = self.figure_storage.get_rand_figure().preview_figure
        self.offer_list[2] = self.figure_storage.get_rand_figure().preview_figure

    def update(self):
        if self.need_to_generate() is True:
            self.generate()

    def draw(self):
        if self.offer_list[0] is not None:
            self.offer_list[0].draw(4, 44)
        if self.offer_list[1] is not None:
            self.offer_list[1].draw(16, 44)
        if self.offer_list[2] is not None:
            self.offer_list[2].draw(27, 44)

class App:
    def __init__(self):
        temp_figure_list = []
        temp_figure_list.append(Figure(0, 0, 13, 13, Figure(13, 0, 10, 10)))
        temp_figure_list.append(Figure(24, 0, 9, 9, Figure(33, 0, 7, 7)))
        temp_figure_list.append(Figure(40, 0, 13, 13, Figure(56, 0, 10, 10)))
        temp_figure_list.append(Figure(72, 0, 13, 13, Figure(88, 0, 10, 10)))
        temp_figure_list.append(Figure(0, 16, 9, 9, Figure(9, 16, 7, 7)))
        temp_figure_list.append(Figure(16, 16, 9, 9, Figure(25, 16, 7, 7)))
        temp_figure_list.append(Figure(32, 16, 5, 9, Figure(40, 16, 4, 7)))
        temp_figure_list.append(Figure(48, 16, 5, 13, Figure(56, 16, 4, 10)))
        temp_figure_list.append(Figure(64, 16, 5, 17, Figure(72, 16, 4, 13)))
        temp_figure_list.append(Figure(0, 24, 5, 21, Figure(8, 24, 4, 16)))
        temp_figure_list.append(Figure(16, 25, 5, 5, Figure(16, 32, 4, 4)))

        self.figure_storage = FigureStorage(temp_figure_list)
        self.figure_offer = FigureOffer(self.figure_storage)

        pyxel.init(41, 76, caption="Wood Block Puzzle")
        pyxel.mouse(True)

        pyxel.load("my_resource.pyxres")

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        self.figure_offer.update()
        if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON,)

    def draw(self):
        pyxel.cls(12)

        # draw playfield
        pyxel.blt(0, 0, 0, 0, 64, 41, 76)

        # draw offers of new figure
        self.figure_offer.draw()


App()
