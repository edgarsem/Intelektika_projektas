import torch, random
import numpy as np
from collections import deque
from main import Game
from pygame.math import Vector2
from model import Linear_QNet, QTrainer

class Agent:
    
    def __init__(self):
        self.game_count = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen = 100_000)
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr = 0.001, gamma = self.gamma)
    
    def get_state(self, game):
        head = game.snek.body[0]
        
        point_l = (head.x - 1, head.y)
        point_r = (head.x + 1, head.y)
        point_u = (head.x, head.y - 1)
        point_d = (head.x, head.y + 1)
        
        dir_l = game.snek.direction == Vector2(-1, 0)
        dir_r = game.snek.direction == Vector2(1, 0)
        dir_u = game.snek.direction == Vector2(0, -1)
        dir_d = game.snek.direction == Vector2(0, 1)
        
        state = [
            (dir_r and game.gameover_collision_check(point_r)) or 
            (dir_l and game.gameover_collision_check(point_l)) or 
            (dir_u and game.gameover_collision_check(point_u)) or 
            (dir_d and game.gameover_collision_check(point_d)),

            (dir_u and game.gameover_collision_check(point_r)) or 
            (dir_d and game.gameover_collision_check(point_l)) or 
            (dir_l and game.gameover_collision_check(point_u)) or 
            (dir_r and game.gameover_collision_check(point_d)),

            (dir_d and game.gameover_collision_check(point_r)) or 
            (dir_u and game.gameover_collision_check(point_l)) or 
            (dir_r and game.gameover_collision_check(point_u)) or 
            (dir_l and game.gameover_collision_check(point_d)),
            
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            game.fruit.pos.x < game.snek.body[0].x,
            game.fruit.pos.x > game.snek.body[0].x,
            game.fruit.pos.y < game.snek.body[0].y,
            game.fruit.pos.y > game.snek.body[0].y,
            ]
        
        return np.array(state, dtype = int)
        
        
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def train_long_memory(self):
        if len(self.memory) > 1000:
            small_sample = random.sample(self.memory, 1000)
        else:
            small_sample = self.memory 
            
        states, actions, rewards, next_states, dones = zip(*small_sample)
        self.trainer.train_move(states, actions, rewards, next_states, dones)
        
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_move(state, action, reward, next_state, done)
    
    def get_action(self, state):
        self.epsilon = 80 - self.game_count
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state_0 = torch.tensor(state, dtype = torch.float)
            prediction = self.model(state_0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
            
        return final_move
    
def train():
    record = 0
    agent = Agent()
    main_game = Game()
    while True:
        old_state = agent.get_state(main_game)
        
        final_move = agent.get_action(old_state)
        
        reward, done, cur_score = main_game.event_loop(final_move)

        new_state = agent.get_state(main_game)
        
        agent.train_short_memory(old_state, final_move, reward, new_state, done)
        
        agent.remember(old_state, final_move, reward, new_state, done)
        
        if done:
            main_game.gameover()
            agent.game_count += 1
            agent.train_long_memory()
            
            if cur_score > record:
                record = cur_score
                agent.model.save()
                
            print('Game: ', agent.game_count, ' | Score: ', cur_score, ' | Record: ', record)

           
train()