import os
import pygame
import random

class Color:
    def __init__(self):
        self.walls =  (90, 90, 120)
        self.red = (200, 50, 50)
        self.white = (220, 220, 220)
        self.background = (50, 50, 70)
        self.stripes = (60,60,80)

    def get_random_tetris_color(self):
        tetris_colors = [(3, 65, 255), (114, 203, 59), (255, 213, 0), (255, 151, 28), (255, 50, 19)]
        return random.choice(tetris_colors)

    def is_legal(self, color):
        for color_channel in color:
            if not(0 <= color_channel <= 255):
                return False
        return True
colors = Color()

class GameController:
    def __init__(self):
        self.current_score = 0
        self.highscore = 0
        self.window = Window()
        self.overview = Overview()
        self.next_block = Block("random", self.window.grid)
        self.active_block = None; self.draw_new_block()
        self.old_blocks = []

    def update_high_score(self):
        if self.current_score > self.highscore:
            self.highscore = self.current_score

    def restart(self):
        self.update_high_score()
        self.current_score = 0
        self.window.grid.reset()

    def start_collide(self):
        for y in [1,2]:
            for x in [5,6,7,8]:
                if not self.window.grid[y][x].is_empty():
                    return True
        return False

    def draw_new_block(self):
        self.current_score += self.window.grid.check_and_handle_full_rows()
        self.update_high_score()
        if self.start_collide():
            self.restart()
        if self.active_block:
            self.active_block.clear_projection()
        self.active_block = self.next_block
        self.active_block.activate()
        self.next_block = Block("random", self.window.grid)
        print("SCORE: ", self.current_score)

    def rotate(self):
        self.active_block.rotate()

    def move(self, direction):
        self.active_block.move(direction)

    def tick(self, fps):
        self.window.clock.tick(fps)

    def end_of_frame_update(self):
        self.window.screen.fill(colors.stripes)
        self.window.grid.draw_all(self.window.screen)
        self.overview.update_display(self.window.screen, self.current_score, self.highscore,
                                     self.next_block, self.window.grid)
        pygame.display.update()

    def at_bottom(self):
        return self.active_block.at_bottom()

    def move_to_bottom(self):
        while not self.at_bottom():
            self.move("down")
        self.draw_new_block()


class Window:
    def __init__(self):
        self.grid = Grid()
        self.screen = None
        self.clock = None
        self._init()

    def _init(self):
        self.screen = pygame.display.set_mode((self.grid.W+300, self.grid.H))
        self.clock = pygame.time.Clock()
        os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # Hide the pygame loading screen
        pygame.font.init()
        pygame.init()


class Grid:
    def __init__(self):
        self.H = 770
        self.W = (4*self.H)//7
        self.HA = (20+2) # 20 cells plus bottom wall
        self.WA = (10+2) # 10 cells plus left and right wall
        self.TS = self.H//self.HA
        self.cells = None; self.reset()

    def reset(self):
        self.cells = [[None for _ in range(self.WA)] for _ in range(self.HA)]

        # assign cells as empty or wall
        for y in range(self.HA):
            for x in range(self.WA):
                if (x in [0, self.WA-1]) or (y in [0, self.HA-1]):
                    self.cells[y][x] = Cell(x, y, x*self.TS, y*self.TS, "wall", colors.walls, self.TS)
                else:
                    self.cells[y][x] = Cell(x, y, x*self.TS, y*self.TS, "empty", colors.background, self.TS)

        # Assign neighbours to each cell
        for y in range(self.HA):
            for x in range(self.WA):
                current_cell = self.cells[y][x]
                # Left
                if x == 0: current_cell.neighbours[0] = None
                else: current_cell.neighbours[0] = self.cells[y][x-1]
                # Right
                if x == 11: current_cell.neighbours[1] = None
                else: current_cell.neighbours[1] = self.cells[y][x+1]
                # Up
                if y == 0: current_cell.neighbours[2] = None
                else: current_cell.neighbours[2] = self.cells[y-1][x]
                # Down
                if y == 21: current_cell.neighbours[3] = None
                else: current_cell.neighbours[3] = self.cells[y+1][x]

    def __getitem__(self, idx):
        return self.cells[idx]

    def draw_all(self, screen):

        def draw_outliners():
            if cell.get_neighbour("left") and not cell.get_neighbour("left").outline:
                pygame.draw.rect(screen, colors.white, (cell.py_x, cell.py_y, 1, self.TS))
            if cell.get_neighbour("right") and not cell.get_neighbour("right").outline:
                pygame.draw.rect(screen, colors.white, (cell.py_x+self.TS-1, cell.py_y, 1, self.TS))
            if cell.get_neighbour("up") and not cell.get_neighbour("up").outline:
                pygame.draw.rect(screen, colors.white, (cell.py_x, cell.py_y, self.TS, 1))
            if cell.get_neighbour("down") and not cell.get_neighbour("down").outline:
                pygame.draw.rect(screen, colors.white, (cell.py_x, cell.py_y+self.TS-1, self.TS, 1))

        for y in range(self.HA):
            for x in range(self.WA):
                cell = self.cells[y][x]
                pygame.draw.rect(screen, cell.color, (cell.py_x, cell.py_y, self.TS - 1, self.TS - 1))
                if cell.type == "block":
                    dark = [0,0,0]
                    light = [255,255,255]
                    for i, channel in enumerate(cell.color):
                        darker = channel - 10
                        lighter = channel + 10
                        if darker > 0:
                            dark[i] = darker

                        if lighter < 255:
                            light[i] = lighter

                    pygame.draw.rect(screen, dark, (cell.py_x+3, cell.py_y+3, self.TS-6, self.TS-6))
                    pygame.draw.rect(screen, light, (cell.py_x+3, cell.py_y+3, self.TS-6, self.TS-6), 2)


                if cell.outline:
                    draw_outliners()

    def check_and_handle_full_rows(self):
        score = 0
        def is_full(row):
            for cell in row:
                if cell.is_empty():
                    return False
            return True

        def clear_row(row_index):
            for i in range(1,11):
                self.cells[row_index][i].outline = False
                self.cells[row_index][i].adjust("empty", colors.background)

        def move_rows_down_by_one(start_row_index):
            for y in range(start_row_index, 0, -1):
                for x in range(1, 11):
                    self.cells[y+1][x].adjust(self.cells[y][x].type, self.cells[y][x].color)
            # top row must be empty
            for x in range(1, 11):
                self.cells[1][x].adjust("empty", colors.background)

        i = 20
        while i > 0:
            if is_full(self.cells[i]):
                clear_row(i)
                move_rows_down_by_one(i-1)
                score += 1
            else:
                i -= 1

        return score


class Cell:
    def __init__(self, x, y, X, Y, cell_type, color, TS):
        self.grid_x = x
        self.grid_y = y
        self.py_x = X
        self.py_y = Y
        self.type = None
        self.color = None
        self.TS = TS
        self.adjust(cell_type, color)
        self.neighbours = [None, None, None, None] # [left, right, up, down]
        self.outline = 0

    def adjust(self, cell_type, color):
        assert (cell_type in ["empty", "block", "wall"])
        assert colors.is_legal(color)
        self.type = cell_type
        self.color = color

    def get_neighbour(self, direction):
        if   direction == "left" : return self.neighbours[0]
        elif direction == "right": return self.neighbours[1]
        elif direction == "up"   : return self.neighbours[2]
        elif direction == "down" : return self.neighbours[3]

    def is_empty(self):
        return self.type == "empty"

    def is_wall(self):
        return self.type == "wall"

    def is_block(self):
        return self.type == "block"

    def __str__(self):
        return f"{self.type}: ({self.grid_x},{self.grid_y})"


class Block:
    def __init__(self, shape, grid):
        self.shape = shape
        self.relative_coords = []
        self.projections = [None for _ in range(8)]
        self.grid = grid
        self.control_cell = grid[1][5] # The block always starts in the middle of the second row
        self.cells = []
        self.color = colors.get_random_tetris_color()
        self.active = False
        self._init()

    def activate(self):
        self.active = True
        self.update_block_projection()

    def _init(self):
        """
            Shape explanation:

            ####   ##    ##   #    #      #   ##
                    ##  ##   ###   ###  ###   ##
             l      z   s     t    j     L    o
        """
        if self.shape == "random":
            self.shape = random.choice(["l", "z", "s", "t", "j", "L", "o"])

        if   self.shape == "l":
            self.relative_coords = [[-1, 0], [0, 0], [1, 0], [2, 0],None, None, None, None]
        elif self.shape == "z":
            self.relative_coords = [[-1, 0], [0, 0], None, None,None, [0, 1], [1, 1], None]
        elif self.shape == "s":
            self.relative_coords = [None, [0, 0], [1, 0], None,[-1, 1], [0, 1], None, None]
        elif self.shape == "t":
            self.relative_coords =  [None, [0, 0], None, None, [-1, 1], [0, 1], [1, 1], None]
        elif self.shape == "j":
            self.relative_coords = [None, [-1,0], [0,0], [1,0], None, [-1, 1], None, None]
        elif self.shape == "L":
            self.relative_coords = [None, [-1,0], [0,0], [1,0], None, None, None, [1, 1]]
        elif self.shape == "o":
            self.relative_coords = [None, [0, 0], [1, 0], None, None, [0, 1], [1, 1], None]

        self.update_block_cells()


    def clear_projection(self):
        for i, cell in enumerate(self.projections):
            if cell:
                cell.outline = False

    def update_block_projection(self):
        self.clear_projection()

        # find the bottom projection y-coordinate
        self.projections = self.cells.copy()
        while not self.will_collide("down", self.projections):
            for i, cell in enumerate(self.projections):
                if cell:
                    self.projections[i] = cell.get_neighbour("down")

        for i, cell in enumerate(self.projections):
            if cell:
                cell.outline = True

    def update_block_cells(self):

        # Clean up old cells and projections
        for cell in self.cells:
            if cell:
                cell.adjust("empty", colors.background)

        self.cells = [None for _ in range(8)]
        for i, relative_coord in enumerate(self.relative_coords):
            if relative_coord:
                x = self.control_cell.grid_x + relative_coord[0]
                y = self.control_cell.grid_y + relative_coord[1]
                self.cells[i] = self.grid[y][x]
                if self.active:
                    self.cells[i].adjust("block", self.color)

    def will_collide(self, direction, cells):
        moveable_cells = 0

        for cell in cells:
            if cell:
                neighbour = cell.get_neighbour(direction)
                if neighbour.is_empty() or (neighbour in cells):
                    moveable_cells += 1

        number_of_cells_in_block = sum(not cell for cell in cells)
        return moveable_cells != number_of_cells_in_block

    def move(self, direction):
        assert (direction in ["left", "right", "up", "down"])

        if self.will_collide(direction, self.cells): #return false if collision has occured, otherwise return true and move block
            return False
        else:
            self.control_cell = self.control_cell.get_neighbour(direction)
            self.update_block_cells()
            self.update_block_projection()
            return True

    def rotate(self):

        def will_collide():
            moveable_cells = 0

            for i in range(len(self.relative_coords)):
                if self.relative_coords[i]:
                    x, y = self.relative_coords[i][0], self.relative_coords[i][1]
                    x, y = -y, x
                    try: destination = self.grid[self.control_cell.grid_y + y][self.control_cell.grid_x + x]
                    except IndexError: continue # Index error in rotation, probably the l-shape lying flat at the bottom
                    if destination.is_empty() or (destination in self.cells):
                        moveable_cells += 1

            number_of_cells_in_block = sum(not cell for cell in self.cells)
            return moveable_cells != number_of_cells_in_block

        # No reason for o to rotate
        if self.shape == "o":
            return True

        if will_collide():
            return False

        for i in range(len(self.relative_coords)):
            if self.relative_coords[i]:
                x, y = self.relative_coords[i][0], self.relative_coords[i][1]
                self.relative_coords[i][0] = -y
                self.relative_coords[i][1] = x

        self.update_block_cells()
        self.update_block_projection()
        return True

    def at_bottom(self):
        for cell in self.cells:
            if cell:
                down_neighbour = cell.get_neighbour("down")
                if down_neighbour.is_wall():
                    return True
                elif down_neighbour.is_block() and (down_neighbour not in self.cells):
                    return True
        return False


class Pane:
    def __init__(self, start_x, start_y, W, H):
        self.x = start_x
        self.y = start_y
        self.w = W
        self.h = H
        self.edge_thickness = None
        self.edge_color = None


class Overview:
    def __init__(self):
        self.current_score = Pane(480, 50, 300, 100)
        self.high_score = Pane(480, 300, 300, 100)
        self.next_block = Pane(480, 550, 300, 100)
        self.myfont = pygame.font.SysFont("Courier New", 100)


    def update_display(self, screen, score, high_score, next_block, grid):
        # Current score
        x, y, w, h = self.current_score.x, self.current_score.y, self.current_score.w, self.current_score.h
        screen.blit(self.myfont.render(f"{score}", True, colors.white), (x, y))
        pygame.draw.rect(screen, colors.white, (x, y, w, h), 2)

        # High score
        x, y, w, h = self.high_score.x, self.high_score.y, self.high_score.w, self.high_score.h
        screen.blit(self.myfont.render(f"{high_score}", True, colors.white), (x, y))
        pygame.draw.rect(screen, colors.white, (x, y, w, h), 2)

        # Next block
        x, y, w, h, color = self.next_block.x, self.next_block.y, self.next_block.w, self.next_block.h, next_block.color

        for cell in next_block.cells:
            if cell:
                pygame.draw.rect(screen, color, (cell.py_x + x - 100, cell.py_y + y - 15, cell.TS - 1, cell.TS - 1))
                dark = [0,0,0]
                light = [255,255,255]
                for i, channel in enumerate(color):
                    darker = channel - 10
                    lighter = channel + 10
                    if darker > 0:
                        dark[i] = darker

                    if lighter < 255:
                        light[i] = lighter

                pygame.draw.rect(screen, dark, (cell.py_x+2 + x - 100, cell.py_y+2 + y - 15, cell.TS-6, cell.TS-6))
                pygame.draw.rect(screen, light, (cell.py_x+2 + x - 100, cell.py_y+2 + y - 15, cell.TS-6, cell.TS-6), 2)

        pygame.draw.rect(screen, colors.white, (x, y, w, h), 2)







