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
            self.max_width = len(field_arr)
            self.max_height = 0
            for i in field_arr:
                if len(i) > self.max_height:
                    self.max_height = len(i)

    def draw(self, x, y):
        pyxel.blt(x, y, self.img, self.u, self.v, self.w, self.h, 12)


class FigureStorage:
    def __init__(self, figure_list):
        self.figure_list = figure_list

    def get_rand_figure(self):
        return self.figure_list[randint(0, len(self.figure_list) - 1)]


class Field:
    def __init__(self, size, first_cell_x, first_cell_y, cell_size, separator_size, cell):
        self.field = [[0 for _ in range(size)] for _ in range(size)]
        self.first_cell_x = first_cell_x
        self.first_cell_y = first_cell_y
        self.cell_size = cell_size
        self.separator_size = separator_size
        self.cell = cell
        self.score = 0
        self.state_machine = self.StateMachine(20)

    class StateMachine:
        def __init__(self, counter):
            self.combo_text = False
            self.__counter = counter
            self.__counter_limit = counter
            self.__combo_count = 0

        def get_combo_text_state(self):
            return self.combo_text

        def get_combo_count(self):
            return self.__combo_count

        def set_combo_text_state(self, state, combo_count):
            self.combo_text = state
            self.__combo_count = combo_count

        def get_counter(self):
            return self.__counter

        def update_counter(self):
            if self.__counter == 0:
                self.__counter = self.__counter_limit
                self.combo_text = False
            else:
                self.__counter -= 1

    def addFigure(self, figure):
        add_x = (pyxel.mouse_x - self.first_cell_x) // (self.cell_size + self.separator_size)
        add_y = (pyxel.mouse_y - self.first_cell_y) // (self.cell_size + self.separator_size)

        if figure.max_width > len(self.field) - add_x:
            return False
        if figure.max_height > len(self.field) - add_y:
            return False

        # validate adding
        for i in range(figure.max_width):
            for j in range(figure.max_height):
                if figure.field_arr[i][j] == 1 and self.field[add_x + i][add_y + j] == 1:
                    return False

        # add figure
        for i in range(figure.max_width):
            for j in range(figure.max_height):
                if figure.field_arr[i][j] == 1:
                    self.field[add_x + i][add_y + j] = 1

        return True

    def update(self):
        removed_lines_count = 0
        rows_filled = [True for _ in range(len(self.field))]

        # check and remove cols
        for width_index in range(len(self.field)):
            col_filled = True
            for height_index in range(len(self.field[width_index])):
                if self.field[width_index][height_index] == 0:
                    col_filled = False
                    rows_filled[height_index] = False
            if col_filled:
                removed_lines_count += 1
                for height_index in range(len(self.field[width_index])):
                    self.field[width_index][height_index] = 0
            else:
                continue

        # remove rows
        for filled_index in range(len(rows_filled)):
            if rows_filled[filled_index]:
                removed_lines_count += 1
                for width_index in range(len(self.field)):
                    print(width_index)
                    self.field[width_index][filled_index] = 0

        self.state_machine.update_counter()

        if removed_lines_count > 1:
            self.score += 3 * removed_lines_count
            self.state_machine.set_combo_text_state(True, removed_lines_count)
        elif removed_lines_count == 1:
            self.score += 1

    def draw(self):
        for i in range(len(self.field)):
            for j in range(len(self.field)):
                if self.field[i][j]:
                    self.cell.draw(self.first_cell_x + (i * (self.cell_size + self.separator_size)),
                                   self.first_cell_y + (j * (self.cell_size + self.separator_size)))

        if self.state_machine.get_combo_text_state():
            s = "COMBO X{0}".format(self.state_machine.get_combo_count())
            pyxel.text(5, 18, s, 1)
            pyxel.text(4, 18, s, 7)


class Manager:
    def __init__(self, figure_storage, field):
        self.figure_storage = figure_storage
        self.state_machine = self.StateMachine()
        self.figure_offer = self.FigureOffer(self.figure_storage, self.state_machine, field)
        self.field = field
        self.game_over = False

    def update(self):
        self.figure_offer.update()
        if self.if_can_insert() is False:
            self.game_over = True
        # self.field.update()

    def draw(self):
        self.field.draw()
        self.figure_offer.draw()

        if self.game_over:
            pyxel.text(5, 18,  "GAME OVER", 1)
            pyxel.text(4, 18,  "GAME OVER", 7)

    def get_score(self):
        return self.field.score

    def if_can_insert(self):
        can_insert = False
        if self.figure_offer.storage is not None:
            can_insert = can_insert or self.if_can_insert_figure(self.figure_offer.storage)
        else:
            return True

        if self.figure_offer.offer_list[0] is not None:
            can_insert = can_insert or self.if_can_insert_figure(self.figure_offer.offer_list[0])
        if self.figure_offer.offer_list[1] is not None:
            can_insert = can_insert or self.if_can_insert_figure(self.figure_offer.offer_list[1])
        if self.figure_offer.offer_list[2] is not None:
            can_insert = can_insert or self.if_can_insert_figure(self.figure_offer.offer_list[2])

        return can_insert

    def if_can_insert_figure(self, figure):
        for i in range(len(self.field.field)):
            for j in range(len(self.field.field)):
                if figure.max_width > len(self.field.field) - i:
                    break
                if figure.max_height > len(self.field.field) - j:
                    break
                can_insert = True
                for fi in range(len(figure.field_arr)):
                    for fj in range(len(figure.field_arr[fi])):
                        if figure.field_arr[fi][fj] == 1 and self.field.field[i + fi][j + fj] == 1:
                            can_insert = False
                            break
                    if can_insert is False:
                        break
                if can_insert is True:
                    return True

        return False

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
            self.storage = None

        def need_to_generate(self):
            for v in self.offer_list:
                if v is not None:
                    return False
            return True

        def generate(self):
            if self.state_machine.get_figure_dragging_state() is False:
                self.offer_list[0] = self.figure_storage.get_rand_figure()
                self.offer_list[1] = self.figure_storage.get_rand_figure()
                self.offer_list[2] = self.figure_storage.get_rand_figure()

        def pick_up_figure(self, offer_list_id):
            print("pick up")
            if offer_list_id == -1:
                if self.storage is not None:
                    self.active_figure = self.storage
                    self.storage = None
                    self.active_figure_place = -1
                    self.state_machine.set_figure_dragging_state(True)
            else:
                print(self.offer_list[offer_list_id])
                if self.offer_list[offer_list_id] is not None:
                    self.active_figure = self.offer_list[offer_list_id]
                    self.offer_list[offer_list_id] = None
                    self.active_figure_place = offer_list_id
                    self.state_machine.set_figure_dragging_state(True)

        def drop_figure(self):
            print("drop")
            self.state_machine.set_figure_dragging_state(False)
            if 0 <= pyxel.mouse_x < 41 and 0 <= pyxel.mouse_y < 41:
                if self.field.addFigure(self.active_figure):
                    # TODO: check
                    return
                # FIXME:
                # print("fix me")
            elif 15 < pyxel.mouse_x < 26 and 59 < pyxel.mouse_y < 76:
                if self.storage is None:
                    self.storage = self.active_figure
                    return

            if self.active_figure_place == -1:
                self.storage = self.active_figure
            else:
                self.offer_list[self.active_figure_place] = self.active_figure
            self.active_figure = None

        def update(self):
            # print(self.state_machine.get_figure_dragging_state())
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
                    elif 15 < pyxel.mouse_x < 26 and 59 < pyxel.mouse_y < 76:
                        self.pick_up_figure(-1)

            if pyxel.btnr(pyxel.MOUSE_LEFT_BUTTON):
                if self.state_machine.get_figure_dragging_state():
                    self.drop_figure()

            if pyxel.btnp(pyxel.MOUSE_RIGHT_BUTTON):
                if self.state_machine.get_figure_dragging_state():
                    self.drop_figure()

            self.field.update()

        def draw(self):
            if self.storage is not None:
                self.storage.preview_figure.draw(16, 60)

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


class App:
    # x >>>>>>>>>>>
    # y
    # v
    # v
    # v
    # v
    def __init__(self):
        temp_figure_list = [Figure(0, 0, 13, 13, [[1, 1, 1], [1, 1, 1], [1, 1, 1]], Figure(13, 0, 10, 10)),
                            Figure(24, 0, 9, 9, [[1, 1], [1, 1]], Figure(33, 0, 7, 7)),
                            Figure(40, 0, 13, 13, [[1, 1, 1], [0, 0, 1], [0, 0, 1]], Figure(56, 0, 10, 10)),
                            Figure(72, 0, 13, 13, [[0, 0, 1], [0, 0, 1], [1, 1, 1]], Figure(88, 0, 10, 10)),
                            Figure(0, 16, 9, 9, [[1, 1], [0, 1]], Figure(9, 16, 7, 7)),
                            Figure(16, 16, 9, 9, [[0, 1], [1, 1]], Figure(25, 16, 7, 7)),
                            Figure(32, 16, 5, 9, [[1, 1]], Figure(40, 16, 4, 7)),
                            Figure(48, 16, 5, 13, [[1, 1, 1]], Figure(56, 16, 4, 10)),
                            Figure(64, 16, 5, 17, [[1, 1, 1, 1]], Figure(72, 16, 4, 13)),
                            Figure(0, 24, 5, 21, [[1, 1, 1, 1, 1]], Figure(8, 24, 4, 16)),
                            Figure(16, 25, 5, 5, [[1]], Figure(16, 32, 4, 4))]
        # temp_figure_list = [Figure(0, 0, 13, 13, [[1, 1, 1], [1, 1, 1], [1, 1, 1]], Figure(13, 0, 10, 10)),
        #                     Figure(0, 24, 5, 21, [[1, 1, 1, 1, 1]], Figure(8, 24, 4, 16))]

        self.figure_storage = FigureStorage(temp_figure_list)
        self.field = Field(10, 0, 0, 3, 1, Figure(24, 24, 5, 5, [[1]]))
        self.manager = Manager(self.figure_storage, self.field)
        self.score = 0

        # pyxel.init(41, 76, caption="Wood Block Puzzle")
        pyxel.init(41, 90, caption="Wood Block Puzzle")
        pyxel.mouse(True)

        pyxel.load("assets/assets.pyxres")

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        self.manager.update()

    def draw(self):
        pyxel.cls(0)

        # draw playfield
        pyxel.blt(0, 0, 0, 0, 64, 41, 76)
        # pyxel.blt(0, 0, 0, 0, 64, 41, 90)

        # draw offers of new figure
        self.manager.draw()

        # draw score
        s = "SCORE {:>4}".format(self.manager.get_score())
        pyxel.text(1, 80, s, 1)
        pyxel.text(0, 80, s, 7)


App()
