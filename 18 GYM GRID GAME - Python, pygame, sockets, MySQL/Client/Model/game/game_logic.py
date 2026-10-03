import math
import pygame

EMPTY = 0
TRAP = 1
PLAYER = 2
REWARD = 3


class Cell(object):
    def __init__(self, x, y, elem):
        self.x, self.y = x, y
        self.visible = False
        if elem == '.':
            self.elem = EMPTY
        if elem == 'x':
            self.elem = TRAP
        if elem == 'r':
            self.elem = REWARD
        if elem == 'p':
            self.elem = PLAYER
            self.visible = True


class Grid(object):
    def __init__(self, filename, pixel_w, pixel_h, sprites):
        # Initialize grid
        self.h = None
        self.w = None
        self.data = {}
        self.player_pos = (0, 0)
        self.reward_pos = (0, 0)
        
        # Load grid from text file
        self.load_file(filename)
        
        # Grid/image dimensions
        self.pixel_w = pixel_w
        self.pixel_h = pixel_h
        self.xscale = pixel_w / self.w
        self.yscale = pixel_h / self.h
        self.img_pos = (self.xscale / 1.05, self.yscale / 1.05)

        # Load images
        player_img = pygame.image.load(sprites['player']).convert_alpha()
        self.player_img = pygame.transform.scale(player_img, self.img_pos)
        player_win_img = pygame.image.load(sprites['player_win']).convert_alpha()
        self.player_win_img = pygame.transform.scale(player_win_img, self.img_pos)
        trap_img = pygame.image.load(sprites['trap']).convert_alpha()
        self.trap_img = pygame.transform.scale(trap_img, self.img_pos)
        reward_img = pygame.image.load(sprites['reward']).convert_alpha()
        self.reward_img = pygame.transform.scale(reward_img, self.img_pos)

    def draw(self, screen, x_offset, y_offset):
        from math import dist
        color = (0, 0, 0)
        for x in range(self.h):
            for y in range(self.w):
                bx = x * self.xscale
                by = y * self.yscale

                # Draw the basic rectangle
                cell = pygame.Rect(bx + x_offset, by + y_offset, self.xscale, self.yscale)
                pygame.draw.rect(screen, color, cell, 1)

                # Make nearby cells visited (euclidean distance)
                player_x, player_y = self.player_pos
                eudlician_dist = dist([player_x, player_y], [x, y])
                if eudlician_dist <= 1.5:
                    self.data[x][y].visible = True

                # Draw the sprites
                current = self.data[x][y]
                if current.elem == PLAYER:
                    if self.player_pos == self.reward_pos:
                        img_rect = self.player_img.get_rect(center=cell.center)
                        screen.blit(self.player_win_img, img_rect)
                    else:
                        img_rect = self.player_img.get_rect(center=cell.center)
                        screen.blit(self.player_img, img_rect)
                if current.elem == TRAP and current.visible:
                    img_rect = self.trap_img.get_rect(center=cell.center)
                    screen.blit(self.trap_img, img_rect)
                if current.elem == REWARD and current.visible:
                    img_rect = self.reward_img.get_rect(center=cell.center)
                    screen.blit(self.reward_img, img_rect)

    def move_up(self):
        x, y = self.player_pos
        score = -50
        try:
            if self.data[x][y - 1].elem == TRAP:
                score = -1000
            if self.data[x][y - 1].elem == REWARD:
                score = 1000

            self.data[x][y - 1].elem = PLAYER
            self.data[x][y].elem = EMPTY

            self.player_pos = (x, y - 1)

            return score
        except:
            print("Can't move up")
            return 0

    def move_down(self):
        x, y = self.player_pos
        score = -50
        try:
            if self.data[x][y + 1].elem == TRAP:
                score = -1000
            if self.data[x][y + 1].elem == REWARD:
                score = 1000

            self.data[x][y + 1].elem = PLAYER
            self.data[x][y].elem = EMPTY

            self.player_pos = (x, y + 1)

            return score
        except:
            print("Can't move down")
            return 0

    def move_left(self):
        x, y = self.player_pos
        score = -50
        try:
            if self.data[x - 1][y].elem == TRAP:
                score = -1000
            if self.data[x - 1][y].elem == REWARD:
                score = 1000

            self.data[x - 1][y].elem = PLAYER
            self.data[x][y].elem = EMPTY

            self.player_pos = (x - 1, y)

            return score
        except:
            print("Can't move left")
            return 0

    def move_right(self):
        x, y = self.player_pos
        score = -50
        try:
            if self.data[x + 1][y].elem == TRAP:
                score = -1000
            if self.data[x + 1][y].elem == REWARD:
                score = 1000

            self.data[x + 1][y].elem = PLAYER
            self.data[x][y].elem = EMPTY

            self.player_pos = (x + 1, y)

            return score
        except:
            print("Can't move right")
            return 0

    def get_successors(self, pos):
        x, y = pos
        successors = []

        try:
            if self.data[x][y + 1].elem != TRAP:
                successors.append(((x, y + 1), 'DOWN', 1))
        except:
            pass
        try:
            if self.data[x][y - 1].elem != TRAP:
                successors.append(((x, y - 1), 'UP', 1))
        except:
            pass
        try:
            if self.data[x + 1][y].elem != TRAP:
                successors.append(((x + 1, y), 'RIGHT', 1))
        except:
            pass
        try:
            if self.data[x - 1][y].elem != TRAP:
                successors.append(((x - 1, y), 'LEFT', 1))
        except:
            pass

        return successors

    def manhattan_heuristic(self, pos):
        x, y = pos
        x_reward, y_reward = self.reward_pos  # type: ignore

        return abs(x_reward - x) + abs(y_reward - y)

    # Text file -> grid
    def load_file(self, filename):
        with open(filename) as f:
            lines = [l.strip() for l in f.readlines()]
            self.h = len(lines)
            self.w = len(lines[0])

            self.data = {}
            for x in range(self.h):
                self.data[x] = {}

            for x in range(self.h):
                for y in range(self.w):
                    current = lines[x][y]
                    self.data[x][y] = Cell(x, y, current)
                    if current == 'p':
                        self.player_pos = (x, y)
                    if current == 'r':
                        self.reward_pos = (x, y)

    def pixel_to_grid(self, pixel_x, pixel_y):
        return math.floor((pixel_x / self.pixel_w) * self.w), math.floor((pixel_y / self.pixel_h) * self.h)

    def grid_to_pixel(self, grid_x, grid_y):
        return grid_x / self.w * self.pixel_w, grid_y / self.h * self.pixel_h
