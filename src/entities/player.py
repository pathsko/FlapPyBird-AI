from enum import Enum
from itertools import cycle

import pygame
import math
import random
import copy
import ast
from ..utils import GameConfig, clamp
from .entity import Entity
from .floor import Floor
from .pipe import Pipe, Pipes
from ..utils import Perceptron

class PlayerMode(Enum):
    SHM = "SHM"
    NORMAL = "NORMAL"
    CRASH = "CRASH"


class Player(Entity):
    def __init__(self, config: GameConfig) -> None:
        image = config.images.player[0]
        x = int(config.window.width * 0.2)
        y = int((config.window.height - image.get_height()) / 2)
        super().__init__(config, image, x, y)
        self.min_y = -2 * self.h
        self.max_y = config.window.viewport_height - self.h * 0.75
        self.img_idx = 0
        self.img_gen = cycle([0, 1, 2, 1])
        self.frame = 0
        self.crashed = False
        self.crash_entity = None
        self.set_mode(PlayerMode.SHM)
        if  config.mode=='ia' :
            def sigmoid(x):
                if x >= 0:
                    z = math.exp(-x)
                    return 1 / (1 + z)
                else:
                    z = math.exp(x)
                    return z / (1 + z)
            f = open('./results/finalsol.txt')
            weights = ast.literal_eval(f.read().strip())[0]
            f.close()
            self.perceptron = Perceptron(sigmoid,weights)

        if  config.mode=='train' or self.config.mode=='train-verbose':
            def sigmoid(x):
                if x >= 0:
                    z = math.exp(-x)
                    return 1 / (1 + z)
                else:
                    z = math.exp(x)
                    return z / (1 + z)
            
            self.perceptron = Perceptron(sigmoid,[round(random.uniform(-1, 1),4) for _ in range(4)]+[0])
    def __copy__(self):
        # Create a new instance
        new_player = Player(self.config)
        
        # Copy all attributes
        new_player.min_y = self.min_y
        new_player.max_y = self.max_y
        new_player.img_idx = self.img_idx
        new_player.img_gen = self.img_gen 
        new_player.frame = self.frame
        new_player.crashed = self.crashed
        new_player.crash_entity = self.crash_entity
        new_player.set_mode(PlayerMode.SHM)
        # Deep copy the perceptron if it exists
        if hasattr(self, 'perceptron'):
            new_player.perceptron = copy.deepcopy(self.perceptron)
        
        return new_player

    def set_mode(self, mode: PlayerMode,mute=None) -> None:
        self.mode = mode
        if mode == PlayerMode.NORMAL:
            self.reset_vals_normal()
            if mute==None:
                self.config.sounds.wing.play()
        elif mode == PlayerMode.SHM:
            self.reset_vals_shm()
        elif mode == PlayerMode.CRASH:
            self.stop_wings()
            if mute==None:
                self.config.sounds.hit.play()
            if self.crash_entity == "pipe":
                if mute==None:
                    self.config.sounds.die.play()
                
            self.reset_vals_crash()

    def reset_vals_normal(self) -> None:
        self.vel_y = -9  # player's velocity along Y axis
        self.max_vel_y = 10  # max vel along Y, max descend speed
        self.min_vel_y = -8  # min vel along Y, max ascend speed
        self.acc_y = 1  # players downward acceleration

        self.rot = 80  # player's current rotation
        self.vel_rot = -3  # player's rotation speed
        self.rot_min = -90  # player's min rotation angle
        self.rot_max = 20  # player's max rotation angle

        self.flap_acc = -9  # players speed on flapping
        self.flapped = False  # True when player flaps

    def reset_vals_shm(self) -> None:
        self.vel_y = 1  # player's velocity along Y axis
        self.max_vel_y = 4  # max vel along Y, max descend speed
        self.min_vel_y = -4  # min vel along Y, max ascend speed
        self.acc_y = 0.5  # players downward acceleration

        self.rot = 0  # player's current rotation
        self.vel_rot = 0  # player's rotation speed
        self.rot_min = 0  # player's min rotation angle
        self.rot_max = 0  # player's max rotation angle

        self.flap_acc = 0  # players speed on flapping
        self.flapped = False  # True when player flaps

    def reset_vals_crash(self) -> None:
        self.acc_y = 2
        self.vel_y = 7
        self.max_vel_y = 15
        self.vel_rot = -8

    def update_image(self):
        self.frame += 1
        if self.frame % 5 == 0:
            self.img_idx = next(self.img_gen)
            self.image = self.config.images.player[self.img_idx]
            self.w = self.image.get_width()
            self.h = self.image.get_height()

    def tick_shm(self) -> None:
        if self.vel_y >= self.max_vel_y or self.vel_y <= self.min_vel_y:
            self.acc_y *= -1
        self.vel_y += self.acc_y
        self.y += self.vel_y

    def tick_normal(self) -> None:
        if self.vel_y < self.max_vel_y and not self.flapped:
            self.vel_y += self.acc_y
        if self.flapped:
            self.flapped = False
        

        self.y = clamp(self.y + self.vel_y, self.min_y, self.max_y)
        self.rotate()

    def tick_crash(self) -> None:
        if self.min_y <= self.y <= self.max_y:
            self.y = clamp(self.y + self.vel_y, self.min_y, self.max_y)
            # rotate only when it's a pipe crash and bird is still falling
            if self.crash_entity != "floor":
                self.rotate()

        # player velocity change
        if self.vel_y < self.max_vel_y:
            self.vel_y += self.acc_y

    def rotate(self) -> None:
        self.rot = clamp(self.rot + self.vel_rot, self.rot_min, self.rot_max)

    def draw(self) -> None:
        self.update_image()
        if self.mode == PlayerMode.SHM:
            self.tick_shm()
        elif self.mode == PlayerMode.NORMAL:
            self.tick_normal()
        elif self.mode == PlayerMode.CRASH:
            self.tick_crash()

        self.draw_player()

    def draw_player(self) -> None:
        rotated_image = pygame.transform.rotate(self.image, self.rot)
        rotated_rect = rotated_image.get_rect(center=self.rect.center)
        self.config.screen.blit(rotated_image, rotated_rect)

    def stop_wings(self) -> None:
        self.img_gen = cycle([self.img_idx])

    def flap(self,mute=None) -> None:
        if self.y > self.min_y:
            self.vel_y = self.flap_acc
            self.flapped = True
            self.rot = 80
            if mute==None:
                self.config.sounds.wing.play()

    def crossed(self, pipe: Pipe) -> bool:
        return pipe.cx <= self.cx < pipe.cx - pipe.vel_x

    def collided(self, pipes: Pipes, floor: Floor) -> bool:
        """returns True if player collides with floor or pipes."""

        # if player crashes into ground
        if self.collide(floor):
            self.crashed = True
            self.crash_entity = "floor"
            return True

        for pipe in pipes.upper:
            if self.collide(pipe):
                self.crashed = True
                self.crash_entity = "pipe"
                return True
        for pipe in pipes.lower:
            if self.collide(pipe):
                self.crashed = True
                self.crash_entity = "pipe"
                return True
        return False
    
    def distance_to_pipes(self,pipes,verbose=False):
        top_pipe1 = pipes.upper[0]
        p_upp1 = [top_pipe1.x,top_pipe1.y+top_pipe1.h]
        botton_pipe1 = pipes.lower[0]
        p_bott1 = [botton_pipe1.x,botton_pipe1.y]
        top_d1 = ((p_upp1[0]-self.cx)**2+(p_upp1[1]-self.cy)**2)**0.5
        botton_d1 = ((p_bott1[0]-self.cx)**2+(p_bott1[1]-self.cy)**2)**0.5
        if verbose:
            print(f'Distance to top pipes {top_d1}')
            print(f'Distance to botton pipes {botton_d1}')

        
        pygame.draw.line(self.config.screen, (255, 0, 0), (self.cx,self.cy),(p_upp1[0],p_upp1[1]))
        pygame.draw.line(self.config.screen, (255, 0, 0), (self.cx,self.cy),(p_bott1[0],p_bott1[1]))


        top_d2 = -1
        botton_d2 = -1
        if len(pipes.upper)>1:
            top_pipe2 = pipes.upper[1]
            p_upp2 = [top_pipe2.x,top_pipe2.y+top_pipe2.h]
            botton_pipe2 = pipes.lower[1]
            p_bott2 = [botton_pipe2.x,botton_pipe2.y]
            top_d2 = ((p_upp2[0]-self.cx)**2+(p_upp2[1]-self.cy)**2)**0.5
            botton_d2 = ((p_bott2[0]-self.cx)**2+(p_bott2[1]-self.cy)**2)**0.5

            pygame.draw.line(self.config.screen, (255, 0, 0), (self.cx,self.cy),(p_upp2[0],p_upp2[1]))
            pygame.draw.line(self.config.screen, (255, 0, 0), (self.cx,self.cy),(p_bott2[0],p_bott2[1]))
        
        return [top_d1,botton_d1,top_d2,botton_d2]
        
    def ia_action(self,pipes,mute=None):
        ds = self.distance_to_pipes(pipes)
        p = self.perceptron.predict(ds)
        if p>0.5:
            self.flap(mute)
        

