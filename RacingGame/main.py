import pygame
import math
from utils import scale_image, blit_rotate_center

GRASS = scale_image(pygame.image.load("images/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("images/track1.png"), 1.5)
CAR = scale_image(pygame.image.load("images/purple-car.png"), 0.3)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing game")


FPS = 60


class Car:
    IMG = CAR
    START_POS = (180, 200)

    def __init__(self, max_velocity, rotation_velocity):
        self.img = self.IMG
        self.max_velocity = max_velocity
        self.vel = 0
        self.rotation_velocity = rotation_velocity
        self.angle = -90
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.rotated_image = None
        self.alive = True

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
        #for angle in (-60, -30, 0, 30, 60):
            #self.radar(angle, center, win)
        self.collision(center)

    def radar(self, angle, center, win):
        length = 0
        x = int(center[0])
        y = int(center[1])
        while not TRACK.get_at((x, y)) == pygame.Color(0, 0, 0, 255) and length < 100:
            length += 1
            x = int(center[0] - math.sin(math.radians(self.angle + angle)) * length)
            y = int(center[1] - math.cos(math.radians(self.angle + angle)) * length)
            try:
                TRACK.get_at((x, y))
            except IndexError:
                break
        pygame.draw.line(win, (255, 255, 255, 255), center, (x, y), 1)
        pygame.draw.circle(win, (255, 0, 0, 0), (x, y), 3)

    def collision(self, center):
        length = 12
        collision_point_right = [int(center[0] - math.sin(math.radians(self.angle + 18)) * length),
                                 int(center[1] - math.cos(math.radians(self.angle + 18)) * length)]
        collision_point_left = [int(center[0] - math.sin(math.radians(self.angle - 18)) * length),
                                int(center[1] - math.cos(math.radians(self.angle - 18)) * length)]

        # Die on Collision
        if TRACK.get_at(collision_point_right) == pygame.Color(0, 0, 0, 255) \
                or TRACK.get_at(collision_point_left) == pygame.Color(0, 0, 0, 255):
            self.stop()

        # Draw Collision Points
        pygame.draw.circle(WIN, (0, 255, 255, 0), collision_point_right, 2)
        pygame.draw.circle(WIN, (0, 255, 255, 0), collision_point_left, 2)


    def reduce_speed(self):
        self.vel = max(0, int(self.vel - self.acceleration / 2))
        self.move()

    def stop(self):
        self.vel = 0
        self.move()


def draw(win, imgs, cars):
    for img, pos in imgs:
        win.blit(img, pos)
    for car in cars:
        car.draw(win)
    pygame.display.update()


run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0))]
cars = []
#car = Car(3, 3)
for i in range(1):
    cars.append(Car(3, 3))
i = 0
while run:
    clock.tick(60)  # 60 fps


    draw(WIN, images, cars)
    for event in pygame.event.get():  # all events in pygame
        if event.type == pygame.QUIT:
            run = False
            break
    keys = pygame.key.get_pressed()
    moved = False
    for car in cars:
        """if random.random() < 0.1:
            car.rotate(left=True)
        elif 0.3 < random.random() < 0.4:
            car.rotate(right=True)

        car.move_forward()"""

        if keys[pygame.K_a]:
            car.rotate(left=True)
        if keys[pygame.K_d]:
            car.rotate(right=True)
        if keys[pygame.K_w]:
            moved = True
            car.move_forward()
        if not moved:
            car.reduce_speed()

pygame.quit()
