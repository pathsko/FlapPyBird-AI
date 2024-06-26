import asyncio
import os
import random
import sys
import time
from copy import copy, deepcopy

import pygame
from pygame.locals import K_ESCAPE, K_SPACE, K_UP, KEYDOWN, QUIT

from .entities import (
    Background,
    Floor,
    GameOver,
    Pipes,
    Player,
    PlayerMode,
    Score,
    WelcomeMessage,
)
from .utils import GameConfig, Images, Sounds, Window


class Flappy:
    def __init__(self):

        pygame.init()
        pygame.display.set_caption("Flappy Bird")
        window = Window(288, 512)
        screen = pygame.display.set_mode((window.width, window.height))
        images = Images()

        self.config = GameConfig(
            screen=screen,
            clock=pygame.time.Clock(),
            fps=30,
            window=window,
            images=images,
            sounds=Sounds(),
            mode="normal",
        )

    async def start(self, args=None):
        mode = "ia"
        if len(args) < 2:
            mode = "normal"
        elif len(args) == 2 and args[1] == "-ia":
            mode = "ia"
        elif args[2] == "-train":
            mode = "train"
            if len(args) > 3 and args[3] == "-verbose":
                mode = "train-verbose"

        self.config.mode = mode
        if self.config.mode != "train" and self.config.mode != "train-verbose":
            while True:

                self.background = Background(self.config)
                self.floor = Floor(self.config)

                self.player = Player(self.config)
                self.welcome_message = WelcomeMessage(self.config)
                self.game_over_message = GameOver(self.config)
                self.pipes = Pipes(self.config)
                self.score = Score(self.config)

                await self.splash()
                await self.play()
                await self.game_over()
        else:
            await self.train()

    async def splash(self, mute=None):
        """Shows welcome splash screen animation of flappy bird"""

        self.player.set_mode(PlayerMode.SHM, mute)

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    return

            self.background.tick()
            self.floor.tick()
            self.player.tick()
            self.welcome_message.tick()

            pygame.display.update()
            await asyncio.sleep(0)
            self.config.tick()

    def check_quit_event(self, event):
        if event.type == QUIT or (
            event.type == KEYDOWN and event.key == K_ESCAPE
        ):
            pygame.quit()
            sys.exit()

    def is_tap_event(self, event):
        m_left, _, _ = pygame.mouse.get_pressed()
        space_or_up = event.type == KEYDOWN and (
            event.key == K_SPACE or event.key == K_UP
        )
        screen_tap = event.type == pygame.FINGERDOWN
        return m_left or space_or_up or screen_tap

    async def play(self):
        self.score.reset()
        self.player.set_mode(PlayerMode.NORMAL)

        while True:
            if self.player.collided(self.pipes, self.floor):
                return

            for i, pipe in enumerate(self.pipes.upper):
                if self.player.crossed(pipe):
                    self.score.add()

            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.config.mode == "normal" and self.is_tap_event(event):
                    self.player.flap()

            if self.config.mode == "ia":
                self.player.ia_action(self.pipes)
            self.background.tick()

            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            # self.player.distance_to_pipes(self.pipes)
            pygame.display.update()

            await asyncio.sleep(0)
            self.config.tick()

    async def game_over(self, mute=None):
        """crashes the player down and shows gameover image"""

        self.player.set_mode(PlayerMode.CRASH, mute)
        self.pipes.stop()
        self.floor.stop()

        while True:
            for event in pygame.event.get():
                self.check_quit_event(event)
                if self.is_tap_event(event):
                    if self.player.y + self.player.h >= self.floor.y - 1:
                        return

            self.background.tick()
            self.floor.tick()
            self.pipes.tick()
            self.score.tick()
            self.player.tick()
            self.game_over_message.tick()

            self.config.tick()
            pygame.display.update()
            await asyncio.sleep(0)

    async def train(self):
        self.config.fps = 10000000

        npob = 100
        nGenerations = 10
        k = 5
        cProb = 50
        mProb = 50
        pob = []
        for _ in range(npob):
            s = [round(random.uniform(-1, 1), 4) for _ in range(5)]
            await self.evaluate_sol(s)
            s = [s, self.score.score]
            pob.append(s)

        it = 1
        elite = [[[], 0]]
        while it <= nGenerations:
            print(f"Generation {it}")
            pob = self.geneticOperators(population=pob, k=k, cProb=50, mProb=50)

            for i in range(len(pob)):
                await self.evaluate_sol(pob[i][0])
                pob[i][1] = self.score.score
            for s in pob:
                if s[1] > elite[0][1]:
                    elite[0] = deepcopy(s)
            f = open(f"./results/generation{it}.txt", "w")
            f.write(str(elite[0]))
            f.close()
            if it == nGenerations:
                f = open(f"./results/finalsol.txt", "w")
                f.write(str(elite[0]))
                f.close()

            it += 1
            print(f"Best individual's fitness so far: {elite[0][1]}")
        print(f"Best weights: {elite[0]}")

    async def evaluate_sol(self, sol):
        self.background = Background(self.config)
        self.floor = Floor(self.config)

        self.player = Player(self.config)
        self.welcome_message = WelcomeMessage(self.config)
        self.game_over_message = GameOver(self.config)
        self.pipes = Pipes(self.config)
        self.score = Score(self.config)
        mute = None
        if self.config.mode == "train" or self.config.mode == "train-verbose":
            mute = 0

        # await self.splash(mute)

        self.player.perceptron.weights = sol
        self.score.reset()
        self.player.set_mode(PlayerMode.NORMAL, 0)
        while True:

            if self.player.collided(self.pipes, self.floor):
                return

            for i, pipe in enumerate(self.pipes.upper):
                if self.player.crossed(pipe):
                    self.score.add(0)
            for event in pygame.event.get():

                self.check_quit_event(event)
            #     if self.is_tap_event(event):
            self.player.ia_action(self.pipes, 0)

            self.background.tick()

            self.floor.tick()
            self.pipes.tick()
            self.score.tick()

            self.player.tick()
            self.player.distance_to_pipes(self.pipes)
            if self.config.mode == 'train-verbose':
                pygame.display.update()

            await asyncio.sleep(0)
            self.config.tick()

    def geneticOperators(self, population, k, cProb, mProb):
        new_population = []
        # tournament
        for _ in range(len(population)):
            tournament = random.sample(population, k)
            winner = max(tournament, key=lambda x: x[1])

            new_population.append(deepcopy(winner))
        # crossover operator
        for i in range(0, len(new_population), 2):

            if random.randint(1, 100) <= cProb:
                parent1, parent2 = (
                    new_population[i][0],
                    new_population[i + 1][0],
                )

                # Esto es lo que hay que cambiar
                cross_point = random.randint(1, len(parent1) - 1)
                # cross_point = 5
                child1 = parent1[:cross_point] + parent2[cross_point:]
                child2 = parent2[:cross_point] + parent1[cross_point:]

                new_population[i][0] = deepcopy(child1)
                new_population[i + 1][0] = deepcopy(child2)
        # mutation operator
        for i in range(len(new_population)):
            if random.randint(1, 100) <= mProb:
                j = random.randint(0, len(new_population[0][0]) - 1)
                sum = 0.1
                if random.random() <= 0.5:
                    sum = -1 * sum
                else:
                    sum = 1 * sum

                new_population[i][0][j] += sum
                new_population[i][0][j] = round(new_population[i][0][j], 4)
        return new_population
