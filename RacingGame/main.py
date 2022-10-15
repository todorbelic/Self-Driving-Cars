import copy
import random

import numpy as np
import pygame
import math
from utils import scale_image, blit_rotate_center

from neuralNetwork.layers.dense import Dense
from neuralNetwork.layers.tanh import Tanh

GRASS = scale_image(pygame.image.load("images/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("images/track1.png"), 1.5)
CAR = scale_image(pygame.image.load("images/purple-car.png"), 0.3)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing game")

FPS = 30
POPULATION = 20


class Car:
    IMG = CAR
    START_POS = (915, 120)

    def __init__(self, max_velocity, rotation_velocity, neural_network=None):
        self.img = self.IMG
        self.max_velocity = max_velocity
        self.vel = 0
        self.rotation_velocity = rotation_velocity
        self.angle = -90
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.rotated_image = None
        self.alive = True
        self.neural_network = neural_network
        self.radars = []
        self.fitness = 0

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_velocity
        elif right:
            self.angle -= self.rotation_velocity

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_velocity)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        self.x -= math.sin(radians) * self.vel
        self.y -= math.cos(radians) * self.vel

    def draw(self, win):
        self.rotated_image, topLeft, center = blit_rotate_center(win, self.img, (self.x, self.y), self.angle)
        self.radars.clear()
        for angle in (-60, -30, 0, 30, 60):
            self.radar(angle, center, win)
        self.collision(center)

    def radar(self, angle, center, win):
        length = 0
        x = int(center[0])
        y = int(center[1])
        while not TRACK.get_at((x, y)) == pygame.Color(0, 0, 0, 255) and length <= 100:
            length += 1
            x = int(center[0] - math.sin(math.radians(self.angle + angle)) * length)
            y = int(center[1] - math.cos(math.radians(self.angle + angle)) * length)
            try:
                TRACK.get_at((x, y))
            except IndexError:
                break
        distance = math.sqrt((x - center[0]) ** 2 + (y - center[1]) ** 2)
        distance /= 100
        self.radars.append(distance)
        pygame.draw.line(win, (255, 255, 255, 255), center, (x, y), 1)
        pygame.draw.circle(win, (255, 0, 0, 0), (x, y), 3)

    def collision(self, center):
        length = 12
        collision_point_right = [int(center[0] - math.sin(math.radians(self.angle + 18)) * length),
                                 int(center[1] - math.cos(math.radians(self.angle + 18)) * length)]
        collision_point_left = [int(center[0] - math.sin(math.radians(self.angle - 18)) * length),
                                int(center[1] - math.cos(math.radians(self.angle - 18)) * length)]

        if TRACK.get_at(collision_point_right) == pygame.Color(0, 0, 0, 255) \
                or TRACK.get_at(collision_point_left) == pygame.Color(139, 195, 74, 255):
            self.alive = False

    def mutate(self, mutation_rate):
        for layer in self.neural_network:
            if isinstance(layer, Dense):
                layer.mutate(mutation_rate)


def draw(win, imgs, cars):
    for img, pos in imgs:
        win.blit(img, pos)
    for car in cars:
        if car.alive:
            car.draw(win)
    pygame.display.update()


def next_generation(cars):
    normalize_fitness(cars)
    new_cars = []
    for i in range(POPULATION):
        new_cars.append(pick_one(cars))
    cars.clear()
    cars = new_cars
    return cars


def normalize_fitness(cars):
    sum = 0
    for car in cars:
        sum += car.fitness
    for car in cars:
        car.fitness /= sum


def pick_one(cars):
    index = 0
    r = random.random()
    while r > 0:
        r = r - cars[index].fitness
        index += 1
    index -= 1
    car = cars[index]
    child = Car(4, 4, copy.deepcopy(car.neural_network))
    child.mutate(0.1)
    return child


run = True
clock = pygame.time.Clock()
images = [(TRACK, (0, 0))]
cars = []

for i in range(POPULATION):
    network = [
        Dense(5, 6),
        Tanh(),
        Dense(6, 3),
        Tanh()
    ]
    cars.append(Car(4, 4, network))
i = 0
while run:
    clock.tick(FPS)  # 60 fps

    draw(WIN, images, cars)
    for event in pygame.event.get():  # svi eventovi
        if event.type == pygame.QUIT:
            run = False
            break
    keys = pygame.key.get_pressed()
    moved = False
    i = 0
    for car in cars:
        output = np.reshape(car.radars, (5, 1))
        if car.alive:
            car.fitness += 1
        if not car.alive:
            i += 1
        for layer in car.neural_network:
            output = layer.forward(output)
        car.move_forward()
        if 0.5 < output[1][0] > output[2][0] and car.alive:
            car.rotate(left=True)
        if 0.5 < output[2][0] > output[1][0] and car.alive:
            car.rotate(right=True)
        """if keys[pygame.K_a]:
            car.rotate(left=True)
        if keys[pygame.K_d]:
            car.rotate(right=True)
        if keys[pygame.K_w]:
            moved = True
            car.move_forward()
        if not moved:
            car.reduce_speed()"""
        if i == POPULATION:
            cars = next_generation(cars)

pygame.quit()
