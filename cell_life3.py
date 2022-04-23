from random import random, randint, choice
import pygame as pg
import matplotlib.pyplot as plt


class App:
    def __init__(self):
        pg.init()
        self.res = self.width, self.height = (1600, 900)
        self.screen = pg.display.set_mode(self.res, pg.SCALED)
        self.clock = pg.time.Clock()
        self.TILE = 20
        self.cols, self.rows = self.width // self.TILE, self.height // self.TILE

        self.colors = [pg.Color('red'), pg.Color('green'), pg.Color('blue')]

        self.colors_counter = set(tuple(color) for color in self.colors)
        self.step_for_color_cells = 70

        self.grid = [Cell(self.screen, self.colors, self.get_rect(col, row), self.TILE, randint(1, 100)) for row in range(self.rows)
                     for col in range(self.cols) if random() < 0.02]
        self.avg_strength = sum([cell.strength for cell in self.grid]) // len(self.grid)

        self.FPS = 100

        self.font = pg.font.Font(None, 20)

        self.shoots = []

        self.counter = []

    def get_rect(self, x, y):
        return x * self.TILE + 1, y * self.TILE + 1, self.TILE - 1, self.TILE - 1

    def update(self):
        self.screen.fill(pg.Color('black'))
        for cell in self.grid:
            self.shoot(cell)
            dx, dy = self.cell_movement_logic_kernel(cell)
            self.if_out_of_screen([cell.pos[0] + dx, cell.pos[1] + dy, self.TILE, self.TILE], cell)

            cell.tick_x -= 1
            cell.tick_y -= 1
            cell.count_for_collision -= 1
            cell.check_tick()

        for shoot in self.shoots:
            shoot.pos[0] += shoot.direction[0]
            shoot.pos[1] += shoot.direction[1]
            if shoot.pos[0] > self.width or shoot.pos[1] > self.height :
                self.shoots.remove(shoot) # Удаляем выстрелы вылетевшие за поле

        collision = self.check_collision()

        if len(collision) > 1:
            if collision[0].gender + collision[1].gender == 1:
                for cell in collision:
                    cell.count_for_collision = 250
                self.cell_born(collision[0], collision[1])
            else:
                print('fight')
                if collision[0].strength > collision[1].strength:
                    self.grid.remove(collision[0])
                elif collision[0].strength < collision[1].strength:
                    self.grid.remove(collision[1])
        self.check_shoot_collision()

    def shoot(self, cell):
        if cell.is_shooter and cell.shoot_delay == 2000:
            if randint(1, 2000) > 1950:  # выстрел
                b = True
                while b:
                    x = choice([-1, 0, 1])
                    y = choice([-1, 0, 1])
                    if not (x == 0 and y == 0):
                        b = False
                self.shoots.append(Shoot(self.screen, [cell.center[0], cell.center[1]], [x, y], cell))
                cell.shoot_delay = randint(-1000, 0)
        else:
            if cell.is_shooter:
                cell.shoot_delay += 1

    def cell_movement_logic_kernel(self, cell):
        if cell.rand_x < 1 / (2 * cell.div):
            dx = 1
        elif 1 / (2 * cell.div) <= cell.rand_x <= 1 / cell.div:
            dx = -1
        else:
            dx = 0
        if cell.rand_y < 1 / (2 * cell.div):
            dy = 1
        elif 1 / (2 * cell.div) <= cell.rand_y <= 1 / cell.div:
            dy = -1
        else:
            dy = 0
        return dx, dy


    def if_out_of_screen(self, pos, cell):
        if pos[0] > self.width:
            pos[0] = 0
        if pos[0] < 0:
            pos[0] = self.width
        if pos[1] > self.height:
            pos[1] = 0
        if pos[1] < 0:
            pos[1] = self.height
        cell.pos = tuple(pos)
        cell.center = cell.calc_center()

    def check_collision(self):
        collision_list = []
        for cell in self.grid:
            if cell in collision_list:
                continue
            else:
                for cell2 in self.grid:
                    if cell is not cell2:
                        if cell.center[0] in cell2.x_range:  #[cell2.center[0] - self.TILE // 2, cell2.center[0], cell2.center[0] + self.TILE // 2]:
                            if cell.center[1] in cell2.y_range:  #[cell2.center[1] - self.TILE // 2, cell2.center[1], cell2.center[1] + self.TILE // 2]:
                                collision_list.append(cell)
                                collision_list.append(cell2)
                                break
        return [elem for elem in collision_list if elem.count_for_collision <= 0]  # возвращаем только те клетки, которым можно скрещиваться

    def check_shoot_collision(self):
        for cell in self.grid:
            for shoot in self.shoots:
                if cell != shoot.cell:
                    if cell.reflect:
                        side = 0
                        if shoot.pos[0] in cell.x_range:
                            if shoot.pos[1] == cell.down_y:
                                side = 'DOWN'
                            if shoot.pos[1] == cell.up_y:
                                side = 'UP'
                        if shoot.pos[1] in cell.y_range:
                            if shoot.pos[0] == cell.right_x:
                                side = 'RIGHT'
                            if shoot.pos[0] == cell.left_x:
                                side = 'LEFT'
                        if side:
                            shoot.change_direction(side)
                            break
                    # if shoot.pos[0] in range(cell.center[0] - self.TILE // 2, cell.center[0] + self.TILE // 2 + 1) and \
                    #         shoot.pos[1] in range(cell.center[1] - self.TILE // 2, cell.center[1] + self.TILE // 2 + 1):
                    if shoot.pos[0] in cell.x_range and shoot.pos[1] in cell.y_range:
                        print('kill')
                        try:
                            self.grid.remove(cell)
                        except Exception as ex:
                            print(ex)
                        if not shoot.level:
                            self.shoots.remove(shoot)

    def cell_born(self, cell_1, cell_2):
        color1 = cell_1.color
        color2 = cell_2.color

        print('family')

        born_color = pg.Color((color1[0] + color2[0]) // 2, (color1[1] + color2[1]) // 2,
                              (color1[2] + color2[2]) // 2)
        strength = max(cell_1.strength, cell_2.strength)
        self.grid.append(Cell(self.screen, [born_color], cell_1.pos, self.TILE, strength))
        self.colors_counter.add(tuple(born_color))

    def draw(self):
        [cell.draw_cell() for cell in self.grid]
        self.step_for_color_cells = 70
        for color in self.colors_counter:
            CellColor(self.screen).draw_cell(self.step_for_color_cells, pg.Color(color))
            self.step_for_color_cells += 15

        [shoot.draw() for shoot in self.shoots]

        # plt.plot(self.counter)
        # plt.show()

        pg.display.flip()

    def run(self):
        paused = True
        while True:
            self.draw()
            self.update()
            text = self.font.render(f'{len([y for y in self.grid])}', True, pg.Color('white'))
            self.screen.blit(text, [10, 10])
            text = self.font.render(f'{len(self.colors_counter)}', True, pg.Color('white'))
            self.screen.blit(text, [50, 10])

            avg_strength = sum([cell.strength for cell in self.grid]) / len(self.grid)
            text = self.font.render(f'{avg_strength:.2f}', True, pg.Color('white'))
            self.screen.blit(text, (10, 40))

            [exit() for i in pg.event.get() if i.type == pg.QUIT]
            keys = pg.key.get_pressed()
            if keys[pg.K_p] and paused:
                paused = not paused
                while True:
                    if keys[pg.K_p] and not paused:
                        paused = not paused
                        break

            self.clock.tick(self.FPS)
            pg.display.set_caption(f'Game of Life. FPS: {self.clock.get_fps(): .1f}')


class Cell:
    def __init__(self, screen, color, pos, tile, strength=randint(1, 100)):
        self.color = choice(color)
        self.screen = screen
        self.pos = pos
        self.TILE = tile
        self.center = [self.pos[0] + self.TILE // 2, self.pos[1] + self.TILE // 2]
        self.period = 40
        self.div = randint(1, 10)
        self.rand_x = random() # Граница определяющая приращение - в плюс или в минус
        self.rand_y = random()
        self.tick_x = randint(1, self.period) # Количество эпох с границей rand_x
        self.tick_y = randint(1, self.period)

        self.count_for_collision = 250 # Время отдыха до следующего скрещивания

        self.gender = 1 if random() > 0.5 else 0  # choice([0, 1])

        self.font = pg.font.Font(None, 10)
        self.letter = 'm' if self.gender == 1 else 'f'
        self.gender_text = self.font.render(self.letter, False, pg.Color('white'))

        self.strength = strength

        self.is_shooter = 1 if random() < 0.7 else 0
        self.shoot_delay = randint(-1000, 2000)

        self.x_range = range(self.pos[0], self.pos[0] + self.TILE)
        self.y_range = range(self.pos[1], self.pos[1] + self.TILE)
        self.right_x = self.pos[0] + self.TILE
        self.left_x = self.pos[0]
        self.up_y = self.pos[1]
        self.down_y = self.pos[1] + self.TILE

        self.reflect = choice([0, 1])

        # self.SIDES = {'UP': self.UP, 'DOWN': self.DOWN, 'RIGHT': self.RIGHT, 'LEFT': self.DOWN}

    def draw_cell(self):
        pg.draw.rect(self.screen, self.color, self.pos)
        if self.count_for_collision <= 0: self.screen.blit(self.gender_text, [self.pos[0], self.pos[1]])

    def check_tick(self):
        if self.tick_x == 0:
            self.rand_x = random()
            self.tick_x = randint(1, self.period)
        if self.tick_y == 0:
            self.rand_y = random()
            self.tick_y = randint(1, self.period)

            self.x_range = range(self.pos[0], self.pos[0] + self.TILE)
            self.y_range = range(self.pos[1], self.pos[1] + self.TILE)
            self.right_x = self.pos[0] + self.TILE
            self.left_x = self.pos[0]
            self.up_y = self.pos[1]
            self.down_y = self.pos[1] + self.TILE

    def calc_center(self):
        return [self.pos[0] + self.TILE // 2, self.pos[1] + self.TILE // 2]

class Shoot():
    def __init__(self, screen, pos, direction, cell):
        self.screen = screen
        self.pos = pos
        self.direction = direction

        self.cell = cell

        self.level = 1 if random() > 0.7 else 0  # сквозная или нет
        self.color = pg.Color('red') if self.level else pg.Color('yellow')

    def draw(self):
        # выпускаем три точки для видимости очереди выстрелов
        pg.draw.circle(self.screen, self.color, self.pos, 1)
        pg.draw.circle(self.screen, self.color, [self.pos[0] - 2 * self.direction[0], self.pos[1] - 2 * self.direction[1]], 1)
        pg.draw.circle(self.screen, self.color, [self.pos[0] - 4 * self.direction[0], self.pos[1] - 4 * self.direction[1]], 1)

    def change_direction(self, side):
        if side == 'UP':
            self.direction[1] *= -1
        if side == 'DOWN':
            self.direction[1] *= -1
        if side == 'RIGHT':
            self.direction[0] *= -1
        if side == 'LEFT':
            self.direction[0] *= -1


class CellColor:
    def __init__(self, screen):
        self.screen = screen

    def draw_cell(self, x, color):
        pg.draw.circle(self.screen, color, (x, 16), 5)


if __name__ == '__main__':
    app = App()
    app.run()

