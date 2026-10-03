from dataclasses import dataclass
from Model.game.game_logic import Grid
from Model.game.ai_player import a_star
from time import sleep
import pygame

SCREEN_W, SCREEN_H = 800, 600
GRID_PIXEL_W, GRID_PIXEL_H = 500, 500
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

LEVELS = ['Model/game/levels/level1.txt', 'Model/game/levels/level2.txt', 'Model/game/levels/level3.txt']
SPRITES = {'player_win': 'Model/game/sprites/player3.jpeg', 'player': 'Model/game/sprites/player4.jpeg',
           'trap': 'Model/game/sprites/bear_trap.jpg', 'reward': 'Model/game/sprites/protein.jpg'}


class Game(object):
    def __init__(self, level, session=None):
        pygame.init()
        pygame.display.set_caption('18 Gym')
        self.level = level
        self.session = session

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font('freesansbold.ttf', 40)
        self.score = 0

        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        self.screen.fill((255, 255, 255))

        self.x_offset = (SCREEN_W - GRID_PIXEL_W) / 2
        self.y_offset = (SCREEN_H - GRID_PIXEL_H) / 2
        self.grid = Grid(LEVELS[self.level], GRID_PIXEL_W, GRID_PIXEL_H, SPRITES)
        self.original_grid = self.grid

        self.path = []
        self.best_path = []
        self.stop = False

    def run(self):
        self.best_path = a_star(self.grid)
        while not self.stop:
            # Check for events
            event_score = 0
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        event_score = self.grid.move_up()
                        self.path.append('UP')
                    if event.key == pygame.K_DOWN:
                        event_score = self.grid.move_down()
                        self.path.append('DOWN')
                    if event.key == pygame.K_LEFT:
                        event_score = self.grid.move_left()
                        self.path.append('LEFT')
                    if event.key == pygame.K_RIGHT:
                        event_score = self.grid.move_right()
                        self.path.append('RIGHT')
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            self.score += event_score

            # Draw on screen stuff
            self.screen.fill(WHITE)
            self.grid.draw(self.screen, self.x_offset, self.y_offset)

            self.display_score()
            self.check_score()

            self.clock.tick(60)
            pygame.display.update()
        pygame.display.quit()

    def run_ai(self):
        self.display_message("OPTIMAL SOLUTION:")
        moves = {'UP': self.grid.move_up, 'DOWN': self.grid.move_down, 'LEFT': self.grid.move_left,
                 'RIGHT': self.grid.move_right}
        path = a_star(self.grid)
        for move in path:
            # Check for events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            sleep(0.7)
            moves[move]()

            # Draw on screen stuff
            self.screen.fill(WHITE)
            self.grid.draw(self.screen, self.x_offset, self.y_offset)

            self.clock.tick(60)
            pygame.display.update()
        self.win()
        pygame.display.quit()

    def get_best_path(self):
        return a_star(self.original_grid)

    def check_score(self):
        if self.score < -800:
            self.game_over()
        if self.score > 100:
            self.win()

    def game_over(self):
        text = self.font.render('GAME OVER', True, RED)
        textRect = text.get_rect()
        textRect.center = (SCREEN_W // 2, SCREEN_H // 2)
        self.screen.blit(text, textRect)
        pygame.display.update()
        self.stop = True
        sleep(1.5)

    def win(self):
        text = self.font.render('YOU WON', True, RED)
        textRect = text.get_rect()
        textRect.center = (SCREEN_W // 2, SCREEN_H // 2)
        self.screen.blit(text, textRect)
        pygame.display.update()
        self.stop = True
        sleep(1)

    def display_message(self, message):
        text = self.font.render(message, True, RED)
        textRect = text.get_rect()
        textRect.center = (SCREEN_W // 2, SCREEN_H // 2)
        self.screen.blit(text, textRect)
        pygame.display.update()
        self.stop = True
        sleep(1)

    def display_score(self):
        text = self.font.render(f'Score: {self.score}', True, BLACK)
        textRect = text.get_rect()
        textRect.center = (SCREEN_W // 2, SCREEN_H // 20)
        self.screen.blit(text, textRect)
        pygame.display.update()

    def reset(self):
        self.stop = False
        self.score = 0
        self.grid = Grid(LEVELS[self.level], GRID_PIXEL_W, GRID_PIXEL_H, SPRITES)


@dataclass
class GameDAO(object):
    id: int = 0
    player_id: int = 0
    level: int = 0
    score: int = 0

    def __init__(self, game: Game):
        self.player_id = game.session['id']
        self.level = game.level
        self.score = game.score
