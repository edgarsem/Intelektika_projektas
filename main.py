import pygame, sys, random, pygame_menu
from pygame.math import Vector2
import numpy as np

pygame.init()
CELL_SIZE = 20
CELL_NUMBER = 34

game_font = pygame.font.Font('snekAssets/pixel_font.ttf', 25)


class Snek:
    def __init__(self, screen):
        self.screen = screen
        self.body = [Vector2(5, 7), Vector2(4, 7), Vector2(3, 7)]
        self.direction = Vector2(1, 0)
        self.new_block = False
        
    def draw_snek(self):
        for block in self.body:
            x_pox = int(block.x * CELL_SIZE)
            y_pos = int(block.y * CELL_SIZE)
            block_rect = pygame.Rect(x_pox, y_pos, CELL_SIZE, CELL_SIZE)
            if block == self.body[0]:
                pygame.draw.rect(self.screen, (255, 255, 255), block_rect)
            else:
                pygame.draw.rect(self.screen, (0, 255, 0), block_rect)
            
    def move_snek(self):
        if self.new_block == True:
            body_change = self.body[:]
            body_change.insert(0, body_change[0] + self.direction)
            self.body = body_change[:]
            self.new_block = False
        else:
            body_change = self.body[:-1]
            body_change.insert(0, body_change[0] + self.direction)
            self.body = body_change[:]
            
    def add_block(self):
        self.new_block = True
        
    def reset(self):
        self.body = [Vector2(5, 7), Vector2(4, 7), Vector2(3, 7)]
        self.direction = Vector2(1, 0)
            
            

class Fruit:
    def __init__(self, screen):
        self.screen = screen
        self.position_generator()
    
    def position_generator(self):
        self.x = random.randint(0, CELL_NUMBER - 1)
        self.y = random.randint(0, CELL_NUMBER - 1)
        self.pos = Vector2(self.x, self.y)
        
    def draw_fruit(self):
        fruit_rect = pygame.Rect(int (self.pos.x * CELL_SIZE), int (self.pos.y * CELL_SIZE), CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(self.screen, (255, 0, 0), fruit_rect)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((CELL_SIZE * CELL_NUMBER, CELL_SIZE * CELL_NUMBER))
        self.score = 0
        self.frame_iteration = 0
        self.snek = Snek(self.screen)
        self.fruit = Fruit(self.screen)
        self.clock = pygame.time.Clock()
        
    def event_loop(self, action):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
        
                
        return self.update(action) 
                
                              
    def update(self, action):

        clock_wise = [Vector2(1, 0), Vector2(0, 1), Vector2(-1, 0), Vector2(0, -1)] # right, down, left, up
        index = clock_wise.index(self.snek.direction)
        
        if np.array_equal(action, [1, 0, 0]):
            new_direction = clock_wise[index]
        elif np.array_equal(action, [0, 1, 0]):
            next_index = (index + 1) % 4
            new_direction = clock_wise[next_index]
        else:
            next_index = (index - 1) % 4
            new_direction = clock_wise[next_index]
            
        self.snek.direction = new_direction
        
        self.snek.move_snek()
        
        self.reward = 0
        game_over = False
        
        if self.gameover_collision_check() or self.iteration_check():
            self.reward = -10
            game_over = True
            return self.reward, game_over, self.score
        
        
        self.fruit_collision_check()
        self.draw_components()
        self.clock.tick(80)
        
        return self.reward, game_over, self.score
        
        
    def draw_components(self):
        self.screen.fill((0, 0, 0))
        self.fruit.draw_fruit()
        self.snek.draw_snek()
        self.draw_score()
        pygame.display.flip()
                    
    def fruit_collision_check(self):
        if self.fruit.pos == self.snek.body[0]:
            self.fruit.position_generator()
            self.snek.add_block()
            self.score += 1
            self.reward = 10
        for block in self.snek.body[1:]:
            if block == self.fruit.pos:
                self.fruit.position_generator()
    
    def iteration_check(self):
        if self.frame_iteration > 100 * len(self.snek.body):
            return True
         
    def draw_score(self):
        score_text = 'Score: ' + str(self.score)
        score_surface = game_font.render(score_text, False, (255, 255, 255))
        score_x = CELL_SIZE * 3
        score_y = CELL_SIZE
        score_rect = score_surface.get_rect(center = (score_x, score_y))
        self.screen.blit(score_surface, score_rect)
    
    def gameover_collision_check(self, point = None):
        if point is None:
            point = self.snek.body[0]
        
        if not 0 <= self.snek.body[0].x < CELL_NUMBER or not 0 <= self.snek.body[0].y < CELL_NUMBER:
            return True
        
        for block in self.snek.body[1:]:
            if block == self.snek.body[0]:
                return True
            
        return False
                
    def gameover(self):
        self.frame_iteration = 0
        self.score = 0
        self.snek.reset()
        self.fruit.position_generator()
    
        
        
  

