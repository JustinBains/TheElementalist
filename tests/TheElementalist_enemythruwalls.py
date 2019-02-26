import pygame
import math

pygame.init()

pygame.display.set_caption("The Elementalist")

width = 500
height = 500
playerSpeed = 5
enemySpeed = 2

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load("Player Sprites/idle1.png")
        self.rect = self.image.get_rect()

        self.x = 50
        self.y = 400
        self.rect.center = (self.x, self.y)

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= playerSpeed
        if keys[pygame.K_RIGHT] and self.x < width:
            self.x += playerSpeed

        self.rect.center = (self.x, self.y)


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load("Enemy Sprites/slime-idle-0.png")
        self.rect = self.image.get_rect()

        self.x = 50
        self.y = 400
        self.dx = 0
        self.dy = 0
        self.dz = 0
        self.speedX = 0
        self.speedY = 0
        self.rect.center = (self.x, self.y)

    def update(self):
        global player

        self.dx = player.x - self.x
        self.dy = player.y - self.y

        self.dz = math.sqrt(self.dx**2 + self.dy**2)

        if self.dz != 0:
            self.speedX = self.dx / self.dz * enemySpeed
            self.speedY = self.dy / self.dz * enemySpeed

        if self.x < player.x:
            self.x += self.speedX
            self.rect.center = (self.x, self.y)

        elif self.x > player.x:
            self.x -= -self.speedX
            self.rect.center = (self.x, self.y)

        if self.y < player.y:
            self.y += self.speedY
            self.rect.center = (self.x, self.y)

        elif self.y > player.y:
            self.y -= -self.speedY
            self.rect.center = (self.x, self.y)


def main():
    global player

    screen = pygame.display.set_mode((width, height))

    background = pygame.Surface(screen.get_size())
    background.fill((0, 0, 0))

    player = Player()
    enemy = Enemy()

    playerSprites = pygame.sprite.Group(player)
    enemySprites = pygame.sprite.Group(enemy)

    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        playerSprites.clear(screen, background)
        enemySprites.clear(screen, background)
        playerSprites.update()
        enemySprites.update()
        playerSprites.draw(screen)
        enemySprites.draw(screen)
        pygame.display.flip()


main()
