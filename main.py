from random import randint

import pyxel


class Figure:
    def __init__(self, u, v, w, h, field_arr=None, preview_figure=None, img=0):
        self.u = u
        self.v = v
        self.w = w
        self.h = h
        self.preview_figure = preview_figure
        self.field_arr = field_arr
        self.img = img
        if field_arr is not None:
            self.max_height = len(field_arr)
            self.max_width = 0
            for i in field_arr:
                if len(i) > self.max_width:
                    self.max_width = len(i)

    def draw(self, x, y):
        pyxel.blt(x, y, self.img, self.u, self.v, self.w, self.h, 12)


class FigureStorage:
    def __init__(self, figure_list):
        self.figure_list = figure_list

    def get_rand_figure(self):
        return self.figure_list[randint(0, len(self.figure_list) - 1)]


class FigureManager:
    def __init__(self, figure_storage, field):
        self.figure_storage = figure_storage
        self.state_machine = self.StateMachine()
        self.figure_offer = self.FigureOffer(self.figure_storage, self.state_machine, field)
        self.field = field

    def update(self):
        self.figure_offer.update()
        # self.field.update()

    def draw(self):
        self.figure_offer.draw()
        self.field.draw()

    class StateMachine:
        def __init__(self):
            self.figure_dragging = False

        def get_figure_dragging_state(self):
            return self.figure_dragging

        def set_figure_dragging_state(self, state):
            self.figure_dragging = state

    class FigureOffer:
        def __init__(self, figure_storage, state_machine, field):
            self.offer_list = [None, None, None]
            self.figure_storage = figure_storage
            self.state_machine = state_machine
            self.field = field
            self.active_figure = None
            self.active_figure_place = 0

        def need_to_generate(self):
            for v in self.offer_list:
                if v is not None:
                    return False
            return True

        def generate(self):
            self.offer_list[0] = self.figure_storage.get_rand_figure()
            self.offer_list[1] = self.figure_storage.get_rand_figure()
            self.offer_list[2] = self.figure_storage.get_rand_figure()

        def pick_up_figure(self, offer_list_id):
            print("pick up")
            self.active_figure = self.offer_list[offer_list_id]
            self.offer_list[offer_list_id] = None
            self.active_figure_place = offer_list_id
            self.state_machine.set_figure_dragging_state(True)

        def drop_figure(self):
            print("drop")
            self.state_machine.set_figure_dragging_state(False)
            if 0 <= pyxel.mouse_x < 41 and 0 <= pyxel.mouse_y < 41:
                if self.field.addFigure(self.active_figure):
                    return
                # FIXME:
                # print("fix me")

            self.offer_list[self.active_figure_place] = self.active_figure
            self.active_figure = None

        def update(self):
            print(self.state_machine.get_figure_dragging_state())
            if self.need_to_generate() is True:
                self.generate()

            if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                print(pyxel.mouse_x, pyxel.mouse_y)
                if self.state_machine.get_figure_dragging_state() is False:
                    if 3 < pyxel.mouse_x < 14 and 43 < pyxel.mouse_y < 60:
                        self.pick_up_figure(0)
                    elif 15 < pyxel.mouse_x < 26 and 43 < pyxel.mouse_y < 60:
                        self.pick_up_figure(1)
                    elif 26 < pyxel.mouse_x < 37 and 43 < pyxel.mouse_y < 60:
                        self.pick_up_figure(2)

            if pyxel.btnr(pyxel.MOUSE_LEFT_BUTTON):
                if self.state_machine.get_figure_dragging_state():
                    self.drop_figure()

            if pyxel.btnp(pyxel.MOUSE_RIGHT_BUTTON):
                if self.state_machine.get_figure_dragging_state():
                    self.drop_figure()

        def draw(self):
            if self.offer_list[0] is not None:
                if self.offer_list[0].preview_figure is not None:
                    self.offer_list[0].preview_figure.draw(4, 44)
            if self.offer_list[1] is not None:
                if self.offer_list[1].preview_figure is not None:
                    self.offer_list[1].preview_figure.draw(16, 44)
            if self.offer_list[2] is not None:
                if self.offer_list[2].preview_figure is not None:
                    self.offer_list[2].preview_figure.draw(27, 44)

            if self.state_machine.get_figure_dragging_state():
                self.active_figure.draw(pyxel.mouse_x, pyxel.mouse_y)


class Field:
    def __init__(self, size, first_cell_x, first_cell_y, cell_size, separator_size, cell):
        self.field = [[None for _ in range(size)] for _ in range(size)]
        self.first_cell_x = first_cell_x
        self.first_cell_y = first_cell_y
        self.cell_size = cell_size
        self.separator_size = separator_size
        self.cell = cell
        #
        # for i in range(size):
        #     for j in range(size):
        #         self.field[i][j] = self.Cell(self.first_cell_x + (i * (self.cell_size + self.separator_size)),
        #                                      self.first_cell_y + (j * (self.cell_size + self.separator_size)), cell_size)

    # class Cell:
    #     def __init__(self, x, y, size):
    #         self.x = x
    #         self.y = y

    def addFigure(self, figure):
        add_x = (pyxel.mouse_x - self.first_cell_x) // (self.cell_size + self.separator_size)
        add_y = (pyxel.mouse_y - self.first_cell_y) // (self.cell_size + self.separator_size)

        if figure.max_width > len(self.field) - add_x:
            return False
        if figure.max_height > len(self.field) - add_y:
            return False

        for i in range(figure.max_width):
            for j in range(figure.max_height):
                if figure.field_arr[j][i] == 1 and self.field[add_x + i][add_y + j] == 1:
                    return False

        for i in range(figure.max_width):
            for j in range(figure.max_height):
                if figure.field_arr[j][i] == 1:
                    self.field[add_x + i][add_y + j] = 1

        print(add_x, add_y)
        # if figure.max_height
        # FIXME:
        return True

    def draw(self):
        for i in range(len(self.field)):
            for j in range(len(self.field)):
                if self.field[i][j]:
                    self.cell.draw(self.first_cell_x + (i * (self.cell_size + self.separator_size)),
                                   self.first_cell_y + (j * (self.cell_size + self.separator_size)))


class App:
    def __init__(self):
        temp_figure_list = [Figure(0, 0, 13, 13, [[1, 1, 1], [1, 1, 1], [1, 1, 1]], Figure(13, 0, 10, 10)),
                            Figure(24, 0, 9, 9, [[1, 1], [1, 1]], Figure(33, 0, 7, 7)),
                            Figure(40, 0, 13, 13, [[1, 0, 0], [1, 0, 0], [1, 1, 1]], Figure(56, 0, 10, 10)),
                            Figure(72, 0, 13, 13, [[0, 0, 1], [0, 0, 1], [1, 1, 1]], Figure(88, 0, 10, 10)),
                            Figure(0, 16, 9, 9, [[1, 0], [1, 1]], Figure(9, 16, 7, 7)),
                            Figure(16, 16, 9, 9, [[0, 1], [1, 1]], Figure(25, 16, 7, 7)),
                            Figure(32, 16, 5, 9, [[1], [1]], Figure(40, 16, 4, 7)),
                            Figure(48, 16, 5, 13, [[1], [1], [1]], Figure(56, 16, 4, 10)),
                            Figure(64, 16, 5, 17, [[1], [1], [1], [1]], Figure(72, 16, 4, 13)),
                            Figure(0, 24, 5, 21, [[1], [1], [1], [1], [1]], Figure(8, 24, 4, 16)),
                            Figure(16, 25, 5, 5, [[1]], Figure(16, 32, 4, 4))]

        self.figure_storage = FigureStorage(temp_figure_list)
        self.field = Field(10, 0, 0, 3, 1, Figure(24, 24, 5, 5, [[1]]))
        self.figure_manager = FigureManager(self.figure_storage, self.field)

        pyxel.init(41, 76, caption="Wood Block Puzzle")
        pyxel.mouse(True)

        pyxel.load("my_resource.pyxres")

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        self.figure_manager.update()
        # if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON,)

    def draw(self):
        pyxel.cls(12)

        # draw playfield
        pyxel.blt(0, 0, 0, 0, 64, 41, 76)

        # draw offers of new figure
        self.figure_manager.draw()


App()
