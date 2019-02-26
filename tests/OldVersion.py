import pygame
import random
# Global constants

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Screen dimensions
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# These constants define our platform types:
#   Name of file
#   X location of sprite
#   Y location of sprite
#   Width of sprite
#   Height of sprite
PLAT = (190, 10, 65, 26)
PLAT_1 = (0, 0, 96, 30)
PLAT_2 = (96, 0, 32, 33)
PLAT_BIG_TOP = (0, 32, 96, 32)
PLAT_BIG_MIDDLE = (0, 64, 96, 32)
PLAT_BIG_BOTT = (0, 96, 96, 32)

wall_list = pygame.sprite.Group()  # holds all walls/platforms`
base_bullet_timer = 500  # milliseconds
base_damage = 15
infusion_counter = 0
max_health = 100 + infusion_counter


class Player(pygame.sprite.Sprite):  # Player class takes pygame.sprite.Sprite as the object
    """ This class represents the bar at the bottom that the player
        controls. """

    # -- Methods
    def __init__(self):
        """ Constructor function """

        # Call the parent's constructor
        super().__init__()

        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk. insert sprite here
        self.width = 37
        self.height = 50

        self.hitbox = [self.width, self.height]
        self.image = pygame.image.load("Player Sprites/adventurer-idle-2-00.png")

        # player direction
        self.playerFacing = 1
        self.left = True
        self.right = False
        self.idle = True
        self.isMelee = False
        self.isJump = False

        # Set a reference to the image rect.
        self.rect = self.image.get_rect()

        # Set speed vector of player
        self.speedX = 0
        self.speedY = 0

        # List of sprites we can bump against
        self.level = None

        # deletes melee sprite after 100 ms
        self.last_melee = pygame.time.get_ticks()
        self.melee_timer = 100

        # changes the cool down of bullets
        self.last_bullet = pygame.time.get_ticks()
        self.bullet_timer = base_bullet_timer

        # players gold counter
        self.gold = 0

        # initializes the items variables tODO purchasable from the shop
        self.luminous_leviathan = 0  # implemented in melee
        self.infusion = False  # implemented in mainloop(after kills)
        self.appetite = 0  # implemented in mainloop (after kills)
        self.mastery = 0  # implemented in global constants
        self.shoes = 0  # implemented in player.go_left/go_right
        self.spring_heels = 0  # implemented in player.jump
        self.the_economist = 0  # cannot be implemented until isaac is done

        # players health
        self.health = max_health

        # firing modes
        self.normal = True
        self.repeater = False  # chance to shoot 2 bullets
        self.big_bullet = False

        # sets damage variables for melee/ranged attacks
        self.damage = base_damage
        if self.normal:
            self.ranged_damage = self.damage * 2  # 30
        elif self.repeater:
            self.ranged_damage = self.damage * 1.5  # 22.5 should be 45
        elif self.big_bullet:
            self.ranged_damage = self.damage * 5  # 75

        self.runAnim = [pygame.image.load('Player Sprites/adventurer-run-00.png'),
                        pygame.image.load('Player Sprites/adventurer-run-01.png'),
                        pygame.image.load('Player Sprites/adventurer-run-02.png'),
                        pygame.image.load('Player Sprites/adventurer-run-03.png'),
                        pygame.image.load('Player Sprites/adventurer-run-04.png'),
                        pygame.image.load('Player Sprites/adventurer-run-05.png')
                        ]
        self.idleAnim = [pygame.image.load('Player Sprites/adventurer-idle-2-00.png'),
                         pygame.image.load('Player Sprites/adventurer-idle-2-01.png'),
                         pygame.image.load('Player Sprites/adventurer-idle-2-02.png'),
                         pygame.image.load('Player Sprites/adventurer-idle-2-03.png')
                         ]
        self.meleeAnim = [pygame.image.load('Player Sprites/adventurer-attack2-00.png'),
                          pygame.image.load('Player Sprites/adventurer-attack2-01.png'),
                          pygame.image.load('Player Sprites/adventurer-attack2-02.png'),
                          pygame.image.load('Player Sprites/adventurer-attack2-03.png'),
                          pygame.image.load('Player Sprites/adventurer-attack2-04.png'),
                          pygame.image.load('Player Sprites/adventurer-attack2-05.png')
                          ]
        self.jumpAnim = [pygame.image.load('Player Sprites/adventurer-jump-00.png'),
                         pygame.image.load('Player Sprites/adventurer-jump-01.png'),
                         pygame.image.load('Player Sprites/adventurer-jump-02.png'),
                         pygame.image.load('Player Sprites/adventurer-jump-03.png'),
                         pygame.image.load('Player Sprites/adventurer-fall-00.png'),
                         pygame.image.load('Player Sprites/adventurer-fall-01.png')
                         ]
        self.runCount = 0
        self.idleCount = 0
        self.meleeCount = 0
        self.jumpCount = 0

    def update(self):
        """ Move the player. """
        # Gravity
        self.calc_grav()

        # Move left/right
        self.rect.x += self.speedX

        # See if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.speedX > 0:
                self.rect.right = block.rect.left
            elif self.speedX < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right

        # Move up/down
        self.rect.y += self.speedY

        # Check and see if we hit anything
        block_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # Reset our position based on the top/bottom of the object.
            if self.speedY > 0:
                self.rect.bottom = block.rect.top
            elif self.speedY < 0:
                self.rect.top = block.rect.bottom

            # Stop our vertical movement
            self.speedY = 0

        self.animation()

    def calc_grav(self):  # perhaps create global gravity function
        """ Calculate effect of gravity. """
        if self.speedY == 0:
            self.speedY = 1
        else:
            self.speedY += .5 * 0.95 ** self.spring_heels  # was .35

        # See if we are on the ground.
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.speedY >= 0:
            self.speedY = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):
        """ Called when user hits 'jump' button. """
        self.isJump = True
        self.idle = False
        self.right = False
        self.left = False

        # move down a bit and see if there is a platform below us.
        # Move down 2 pixels because it doesn't work well if we only move down
        # 1 when working with a platform moving down.
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speedY = -10

    # Player-controlled movement:
    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.left = True
        self.right = False
        self.idle = False
        Player.left = True
        Player.right = False
        Player.idle = False
        self.playerFacing = -1

        self.speedX = -6 * (1 + 0.05 * self.shoes)

    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.left = False
        self.right = True
        self.idle = False
        Player.left = False
        Player.right = True
        Player.idle = False
        self.playerFacing = 1

        self.speedX = 6 * (1 + 0.05 * self.shoes)

    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.left = False
        self.right = False
        self.idle = True
        Player.left = False
        Player.right = False
        Player.idle = True

        self.speedX = 0

    def shoot(self):
        nowS = pygame.time.get_ticks()
        """ normal firing mode """
        if self.normal:  # shoots 1 bullet
            self.bullet_timer = base_bullet_timer

            if nowS - self.last_bullet >= self.bullet_timer:
                self.last_bullet = pygame.time.get_ticks()
                bullet = PlayerProjectile(self.rect.centerx, self.rect.centery)
                active_sprite_list.add(bullet)
                bullets_list.add(bullet)

        """ Repeater firing mode """
        if self.repeater:  # shoots 2 bullets
            self.bullet_timer = base_bullet_timer * 1.25
            if nowS - self.last_bullet >= self.bullet_timer:
                self.last_bullet = pygame.time.get_ticks()
                bullet = PlayerProjectile(self.rect.centerx, self.rect.centery)
                active_sprite_list.add(bullet)
                bullets_list.add(bullet)

                active_sprite_list.add(bullet)
                bullets_list.add(bullet)

        """ big bullet firing mode """
        if self.big_bullet:
            self.bullet_timer = base_bullet_timer * 2.5

            if nowS - self.last_bullet >= self.bullet_timer:
                self.last_bullet = pygame.time.get_ticks()
                bullet = PlayerProjectile(self.rect.centerx, self.rect.centery)
                active_sprite_list.add(bullet)
                bullets_list.add(bullet)

    def animation(self):
        if self.runCount + 1 >= 60:
            self.runCount = 0
        if self.idleCount + 1 >= 40:
            self.idleCount = 0
        if self.meleeCount + 1 >= 30:
            self.meleeCount = 0
            self.isMelee = False
            self.idle = True
        if self.jumpCount + 1 >= 60:
            self.jumpCount = 0
            self.isJump = False

        if self.right:
            self.image = self.runAnim[self.runCount//10]
            self.runCount += 1
        elif self.left:
            self.image = pygame.transform.flip(self.runAnim[self.runCount//10], True, False)
            self.runCount += 1
        elif self.idle:
            if self.playerFacing == 1:
                self.image = self.idleAnim[self.idleCount//10]
            else:
                self.image = pygame.transform.flip(self.idleAnim[self.idleCount//10], True, False)
            self.idleCount += 1
        elif self.isMelee:
            if self.playerFacing == 1:
                self.image = self.meleeAnim[self.meleeCount//5]
            else:
                self.image = pygame.transform.flip(self.meleeAnim[self.meleeCount//5], True, False)
            self.meleeCount += 1
        elif self.isJump:
            if self.playerFacing == 1:
                self.image = self.jumpAnim[self.jumpCount//10]
            else:
                self.image = pygame.transform.flip(self.jumpAnim[self.jumpCount//10], True, False)
            self.jumpCount += 1


class PlayerProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        if player.normal:
            self.side = 10
            self.speed = 8
        if player.repeater:
            self.side = 5
            self.speed = 15
        if player.big_bullet:
            self.side = 15
            self.speed = 5

        self.image = pygame.Surface([self.side, self.side])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()

        self.rect.bottom = y
        self.rect.centerx = x

        # find direction
        self.direction = player.playerFacing
        self.vel = self.speed * self.direction

    def update(self):
        self.rect.centerx += self.vel


def melee_attack():
    player.idle = False
    player.isMelee = True
    print("yyeeeeet")
    length = 60 * 1.10 ** player.luminous_leviathan

    for E in range(len(enemy_list)):

        if player.playerFacing == -1:
            print("left melee")
            if enemy[E].rect.x <= player.rect.x - length:
                print(E, enemy[E].health)
                enemy[E].health -= player.damage
                if enemy[i].health <= 0:
                    enemy_list.remove(enemy[i])
                    enemy[i].dead = True
                    if player.appetite != 0 and player.health < 100 - player.appetite * 5:
                        player.health += player.appetite * 5

        if player.playerFacing == 1:
            print("right melee")
            if enemy[E].rect.x >= player.rect.x + length:
                print("right melee hit")
                enemy[E].health -= player.damage
                if enemy[i].health <= 0:
                    enemy_list.remove(enemy[i])
                    enemy[i].dead = True
                    if player.appetite != 0 and player.health < 100 - player.appetite * 5:
                        player.health += player.appetite * 5


class Waves():
    def __init__(self):
        self.waveNum = 1
        self.enemy_choose = 0
        self.enemy_choice = []
        self.spawnNum = 3
        self.spawnStatus = True
        self.deathCounter = 0

    def update(self):
        if self.spawnStatus:
            self.spawnEnemy()

        for i in range(len(enemy)):
            if self.deathCounter == len(enemy):
                self.spawnStatus = True
                self.waveNum += 1
                int(self.spawnNum * 1.5)
            else:
                if enemy[i].dead:
                    self.deathCounter += 1
                else:
                    pass

    def spawnEnemy(self):
        # this number will be the random number generator when the spawn algorithm is good
        for i in range(self.spawnNum):
            self.enemy_choose = random.randint(0, 2)
            self.enemy_choice = [Slime(), Mimic(), TotemEnemy()]
            enemy.append((self.enemy_choice[self.enemy_choose]))
            enemy_list.add((self.enemy_choice[self.enemy_choose]))

        self.spawnStatus = False


class Slime(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load("Enemy Sprites/Slime/slime-idle-0.png")
        self.rect = self.image.get_rect()

        enemyWall = pygame.sprite.groupcollide(enemy_list, wall_list, False, False)

        while(True):
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = random.randint(0, SCREEN_HEIGHT)
            enemyWall = pygame.sprite.groupcollide(enemy_list, wall_list, False, False)
            if enemyWall and (self.y >= SCREEN_HEIGHT - self.rect.height / 2):
                pass
            else:
                break

        self.speedX = 2
        self.speedY = 0
        self.rect.center = (self.x, self.y)
        self.isJump = False
        self.health = 100
        self.dead = False

        self.level = None

    def update(self):

        if not self.isJump:
            self.gravity()

        if self.x < player.rect.centerx:
            self.x += self.speedX
            self.rect.center = (self.x, self.y)

        elif self.x > player.rect.centerx:
            self.x -= self.speedX
            self.rect.center = (self.x, self.y)

        self.y += self.speedY

        self.collide()

    def gravity(self):
        if self.y >= SCREEN_HEIGHT - self.rect.height:
            self.speedY = 0
        else:
            self.speedY += 0.500

    def jump(self):
        self.isJump = True

        platform_hit_list = pygame.sprite.spritecollide(self, wall_list, False)

        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.speedY = -10
            self.speedX = 0

    def collide(self):
        enemyWall = pygame.sprite.groupcollide(enemy_list, wall_list, False, False)

        if enemyWall:
            self.jump()
        else:
            self.speedX = 2
            self.isJump = False


class Mimic(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load("Enemy Sprites/Mimic/mimic-attack-00.png")
        self.rect = self.image.get_rect()

        enemyWall = pygame.sprite.groupcollide(enemy_list, wall_list, False, False)

        while True:
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = random.randint(0, SCREEN_HEIGHT)
            enemyWall = pygame.sprite.groupcollide(enemy_list, wall_list, False, False)
            if enemyWall and (self.y >= SCREEN_HEIGHT - self.rect.height / 2):
                pass
            else:
                break

        self.speedX = 2
        self.speedY = 0
        self.rect.center = (self.x, self.y)
        self.isJump = False
        self.health = 100
        self.dead = False

        self.level = None

    def update(self):

        self.gravity()

        if self.x < player.rect.centerx:
            self.x += self.speedX
            self.rect.center = (self.x, self.y)

        elif self.x > player.rect.centerx:
            self.x -= self.speedX
            self.rect.center = (self.x, self.y)

        self.y += self.speedY

        self.collide()

    def gravity(self):
        if self.y >= SCREEN_HEIGHT - self.rect.height:
            self.speedY = 0
        else:
            self.speedY += 0.500

    def collide(self):
        enemyWall = pygame.sprite.groupcollide(enemy_list, wall_list, False, False)


class TotemEnemy(pygame.sprite.Sprite):  # turret enemy
    """ shoots bullets in left, right, and upward directions """

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        # self.sorcererAttack =

        self.image = pygame.image.load("Enemy Sprites/Turret/sorcerer attack_Animation 1_0.png")
        self.image.set_colorkey((44, 72, 48))
        self.image = pygame.transform.scale(self.image, (55, 65))
        self.rect = self.image.get_rect()

        enemyWall = pygame.sprite.groupcollide(enemy_list, wall_list, False, False)

        while True:
            self.x = random.randint(0, SCREEN_WIDTH)
            self.y = random.randint(0, SCREEN_HEIGHT)
            enemyWall = pygame.sprite.groupcollide(enemy_list, wall_list, False, False)
            if enemyWall and (self.y >= SCREEN_HEIGHT - self.rect.height / 2):
                pass
            else:
                break

        self.speedX = 1
        self.speedY = 0
        self.rect.center = (self.x, self.y)
        self.isJump = False
        self.health = 50
        self.dead = False
        self.damage = 12

        self.timer = 1000
        self.now = pygame.time.get_ticks()
        self.lastAttack = 0

        self.level = None

    def update(self):

        self.gravity()
        self.rect.y += self.speedY
        self.rect.x += self.speedX
        self.attack()
        self.collide()

    def attack(self):
        if self.now - self.lastAttack >= self.timer:
            self.lastAttack = pygame.time.get_ticks()
            for direction in range(3):
                tb1 = TotemBullet(self.rect.centerx, self.rect.centery, 0)
                tb2 = TotemBullet(self.rect.centerx, self.rect.centery, 1)
                tb3 = TotemBullet(self.rect.centerx, self.rect.centery, 2)
                enemy_bullets.add(tb1)
                enemy_bullets.add(tb2)
                enemy_bullets.add(tb3)

    def gravity(self):
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.speedY = 0
        else:
            self.speedY += 0.500

    def collide(self):
        enemy_wall_totem = pygame.sprite.groupcollide(enemy_list, wall_list, False, False)

        if enemy_wall_totem:
            self.speedY = 0
            self.speedX = 0


class TotemBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, velX, velY):
        super().__init__()

        self.image = pygame.Surface([8, 8])
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()

        self.rect.centery = y
        self.rect.centerx = x

        # find direction
        self.velX = velX
        self.velY = velY

        self.image = pygame.Surface([8, 8])
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()

        self.rect.bottom = y
        self.rect.centerx = x

        def update(self):
            self.rect.centerx += self.velX

    def update(self):
        self.rect.centerx += self.velX
        self.rect.centery += self.velY


class SpriteSheet(object):
    """ Class used to grab images out of a sprite sheet. """
    # This points to our sprite sheet image
    sprite_sheet = None

    def __init__(self, file_name):
        """ Constructor. Pass in the file name of the sprite sheet. """

        # Load the sprite sheet.
        self.sprite_sheet = pygame.image.load("Platforms.png").convert()

    def get_image(self, x, y, width, height):
        """ Grab a single image out of a larger spritesheet
            Pass in the x, y location of the sprite
            and the width and height of the sprite. """

        # Create a new blank image
        image = pygame.Surface([width, height]).convert()

        # Copy the sprite from the large sheet onto the smaller image
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))

        # Assuming black works as the transparent color
        image.set_colorkey(BLACK)

        # Return the image
        return image


class Platform(pygame.sprite.Sprite):
    """ Platform the user can jump on """

    def __init__(self, sprite_sheet_data):
        """ Platform constructor. Assumes constructed with user passing in
            an array of 5 numbers like what's defined at the top of this
            code. """
        super().__init__()

        sprite_sheet = SpriteSheet("png")
        # Grab the image for this platform
        self.image = sprite_sheet.get_image(sprite_sheet_data[0],
                                            sprite_sheet_data[1],
                                            sprite_sheet_data[2],
                                            sprite_sheet_data[3])

        self.rect = self.image.get_rect()


class MovingPlatform(Platform):
    """ This is a fancier platform that can actually move. """
    change_x = 0
    change_y = 0

    boundary_top = 0
    boundary_bottom = 0
    boundary_left = 0
    boundary_right = 0

    level = None
    player = None

    def update(self):
        """ Move the platform.
            If the player is in the way, it will shove the player
            out of the way. This does NOT handle what happens if a
            platform shoves a player into another object. Make sure
            moving platforms have clearance to push the player around
            or add code to handle what happens if they don't. """

        # Move left/right
        self.rect.x += self.change_x

        # See if we hit the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            # We did hit the player. Shove the player around and
            # assume he/she won't hit anything else.

            # If we are moving right, set our right side
            # to the left side of the item we hit
            if self.change_x < 0:
                self.player.rect.right = self.rect.left
            else:
                # Otherwise if we are moving left, do the opposite.
                self.player.rect.left = self.rect.right

        # Move up/down
        self.rect.y += self.change_y

        # Check and see if we the player
        hit = pygame.sprite.collide_rect(self, self.player)
        if hit:
            # We did hit the player. Shove the player around and
            # assume he/she won't hit anything else.

            # Reset our position based on the top/bottom of the object.
            if self.change_y < 0:
                self.player.rect.bottom = self.rect.top
            else:
                self.player.rect.top = self.rect.bottom

        # Check the boundaries and see if we need to reverse
        # direction.
        if self.rect.bottom > self.boundary_bottom or self.rect.top < self.boundary_top:
            self.change_y *= -1

        cur_pos = self.rect.x - self.level.world_shift
        if cur_pos < self.boundary_left or cur_pos > self.boundary_right:
            self.change_x *= -1


class Level(object):
    """ This is a generic super-class used to define a level.
        Create a child class for each level with level-specific
        info. """

    def __init__(self, player):
        """ Constructor. Pass in a handle to player. Needed for when moving platforms
            collide with the player. """
        self.platform_list = pygame.sprite.Group()
        self.enemy_list = pygame.sprite.Group()
        self.player = player

        # Background image
        self.background = None

        self.world_shift = 0
        self.level_limit = -1000

    # Update everything on this level
    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        enemy_list.update()

    def draw(self, screen):
        """ Draw everything on this level. """
        # screen.blit()

        # Draw the background
        screen.fill(BLACK)
        screen.blit(self.background, (self.world_shift // 3, -10))
        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        enemy_list.draw(screen)

    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll everything: """

        # Keep track of the shift amount
        self.world_shift += shift_x

        # Go through all the sprite lists and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x

        for enemy in enemy_list:
            enemy.rect.x += shift_x


# Create platforms for the level
class World(Level):
    """ Definition for level 1. """

    def __init__(self, player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, player)

        self.background = pygame.image.load("BackgroundLong.png").convert()
        self.background.set_colorkey(BLACK)
        self.level_limit = -2500

        # Array with width, height, x, and y of platform
        level = [[PLAT_1, 100, 700],
                 [PLAT, 100, 560],
                 [PLAT_1, 475, 500],
                 [PLAT_1, 600, 400],
                 [PLAT_1, 675, 400],
                 [PLAT_1, 700, 400],
                 [PLAT_1, 350, 300],
                 [PLAT_1, 375, 200],
                 [PLAT_1, 425, 300],
                 [PLAT_1, 500, 300],
                 [PLAT_2, 540, 200],
                 [PLAT_1, 575, 300],
                 [PLAT_2, 625, 200],
                 [PLAT_1, 650, 300],
                 [PLAT_1, 900, 300],
                 [PLAT_BIG_TOP, 1000, 300],
                 [PLAT_BIG_MIDDLE, 1000, 320],
                 [PLAT_BIG_MIDDLE, 1000, 340],
                 [PLAT_BIG_MIDDLE, 1000, 360],
                 [PLAT_BIG_MIDDLE, 1000, 380],
                 [PLAT_BIG_BOTT, 1000, 400],
                 [PLAT_BIG_TOP, 1075, 300],
                 [PLAT_BIG_MIDDLE, 1075, 320],
                 [PLAT_BIG_MIDDLE, 1075, 340],
                 [PLAT_BIG_MIDDLE, 1075, 360],
                 [PLAT_BIG_MIDDLE, 1075, 380],
                 [PLAT_BIG_MIDDLE, 1075, 400],
                 [PLAT_BIG_MIDDLE, 1075, 420],
                 [PLAT_BIG_BOTT, 1075, 440],
                 [PLAT_BIG_TOP, 1150, 300],
                 [PLAT_BIG_MIDDLE, 1150, 320],
                 [PLAT_BIG_MIDDLE, 1150, 340],
                 [PLAT_BIG_MIDDLE, 1150, 360],
                 [PLAT_BIG_MIDDLE, 1150, 380],
                 [PLAT_BIG_MIDDLE, 1150, 400],
                 [PLAT_BIG_MIDDLE, 1150, 420],
                 [PLAT_BIG_MIDDLE, 1150, 440],
                 [PLAT_BIG_MIDDLE, 1150, 460],
                 [PLAT_BIG_BOTT, 1150, 480],
                 [PLAT_BIG_TOP, 1225, 300],
                 [PLAT_BIG_MIDDLE, 1225, 320],
                 [PLAT_BIG_MIDDLE, 1225, 340],
                 [PLAT_BIG_MIDDLE, 1225, 360],
                 [PLAT_BIG_MIDDLE, 1225, 380],
                 [PLAT_BIG_MIDDLE, 1225, 400],
                 [PLAT_BIG_MIDDLE, 1225, 420],
                 [PLAT_BIG_MIDDLE, 1225, 440],
                 [PLAT_BIG_MIDDLE, 1225, 460],
                 [PLAT_BIG_MIDDLE, 1225, 480],
                 [PLAT_BIG_MIDDLE, 1225, 500],
                 [PLAT_BIG_MIDDLE, 1225, 520],
                 [PLAT_BIG_MIDDLE, 1225, 540],
                 [PLAT_BIG_BOTT, 1225, 560],
                 [PLAT_1, 1500, 200],
                 [PLAT_BIG_MIDDLE, 1625, 160],
                 [PLAT_BIG_MIDDLE, 1625, 180],
                 [PLAT_BIG_MIDDLE, 1625, 200],
                 [PLAT_BIG_MIDDLE, 1625, 220],
                 [PLAT_BIG_MIDDLE, 1625, 240],
                 [PLAT_BIG_MIDDLE, 1625, 260],
                 [PLAT_BIG_MIDDLE, 1625, 280],
                 [PLAT_BIG_MIDDLE, 1625, 300],
                 [PLAT_BIG_MIDDLE, 1625, 320],
                 [PLAT_BIG_MIDDLE, 1625, 340],
                 [PLAT_BIG_MIDDLE, 1625, 360],
                 [PLAT_BIG_MIDDLE, 1625, 380],
                 [PLAT_BIG_MIDDLE, 1625, 400],
                 [PLAT_BIG_MIDDLE, 1625, 420],
                 [PLAT_BIG_MIDDLE, 1625, 440],
                 [PLAT_BIG_MIDDLE, 1625, 460],
                 [PLAT_BIG_MIDDLE, 1625, 480],
                 [PLAT_BIG_MIDDLE, 1625, 500],
                 [PLAT_BIG_MIDDLE, 1625, 520],
                 [PLAT_BIG_MIDDLE, 1625, 540],
                 [PLAT_BIG_BOTT, 1625, 560],
                 [PLAT_BIG_TOP, 1700, 100],
                 [PLAT_BIG_MIDDLE, 1700, 120],
                 [PLAT_BIG_MIDDLE, 1700, 140],
                 [PLAT_BIG_MIDDLE, 1700, 160],
                 [PLAT_BIG_MIDDLE, 1700, 180],
                 [PLAT_BIG_MIDDLE, 1700, 200],
                 [PLAT_BIG_MIDDLE, 1700, 220],
                 [PLAT_BIG_MIDDLE, 1700, 240],
                 [PLAT_BIG_MIDDLE, 1700, 260],
                 [PLAT_BIG_MIDDLE, 1700, 280],
                 [PLAT_BIG_MIDDLE, 1700, 300],
                 [PLAT_BIG_MIDDLE, 1700, 320],
                 [PLAT_BIG_MIDDLE, 1700, 340],
                 [PLAT_BIG_MIDDLE, 1700, 360],
                 [PLAT_BIG_MIDDLE, 1700, 380],
                 [PLAT_BIG_MIDDLE, 1700, 400],
                 [PLAT_BIG_MIDDLE, 1700, 420],
                 [PLAT_BIG_MIDDLE, 1700, 440],
                 [PLAT_BIG_MIDDLE, 1700, 460],
                 [PLAT_BIG_MIDDLE, 1700, 480],
                 [PLAT_BIG_MIDDLE, 1700, 500],
                 [PLAT_BIG_MIDDLE, 1700, 520],
                 [PLAT_BIG_MIDDLE, 1700, 540],
                 [PLAT_BIG_BOTT, 1700, 560],
                 [PLAT_BIG_TOP, 1775, 100],
                 [PLAT_BIG_MIDDLE, 1775, 120],
                 [PLAT_BIG_MIDDLE, 1775, 140],
                 [PLAT_BIG_MIDDLE, 1775, 160],
                 [PLAT_BIG_MIDDLE, 1775, 180],
                 [PLAT_BIG_MIDDLE, 1775, 200],
                 [PLAT_BIG_MIDDLE, 1775, 220],
                 [PLAT_BIG_MIDDLE, 1775, 240],
                 [PLAT_BIG_MIDDLE, 1775, 260],
                 [PLAT_BIG_MIDDLE, 1775, 280],
                 [PLAT_BIG_MIDDLE, 1775, 300],
                 [PLAT_BIG_MIDDLE, 1775, 320],
                 [PLAT_BIG_MIDDLE, 1775, 340],
                 [PLAT_BIG_MIDDLE, 1775, 360],
                 [PLAT_BIG_MIDDLE, 1775, 380],
                 [PLAT_BIG_MIDDLE, 1775, 400],
                 [PLAT_BIG_MIDDLE, 1775, 420],
                 [PLAT_BIG_MIDDLE, 1775, 440],
                 [PLAT_BIG_MIDDLE, 1775, 460],
                 [PLAT_BIG_MIDDLE, 1775, 480],
                 [PLAT_BIG_MIDDLE, 1775, 500],
                 [PLAT_BIG_MIDDLE, 1775, 520],
                 [PLAT_BIG_MIDDLE, 1775, 540],
                 [PLAT_BIG_BOTT, 1775, 560],
                 [PLAT_1, 2000, 300],
                 [PLAT_BIG_TOP, 2100, 300],
                 [PLAT_BIG_MIDDLE, 2100, 320],
                 [PLAT_BIG_MIDDLE, 2100, 340],
                 [PLAT_BIG_MIDDLE, 2100, 360],
                 [PLAT_BIG_MIDDLE, 2100, 380],
                 [PLAT_BIG_MIDDLE, 2100, 400],
                 [PLAT_BIG_BOTT, 2100, 420],
                 [PLAT_BIG_TOP, 2175, 300],
                 [PLAT_BIG_MIDDLE, 2175, 320],
                 [PLAT_BIG_MIDDLE, 2175, 340],
                 [PLAT_BIG_MIDDLE, 2175, 360],
                 [PLAT_BIG_MIDDLE, 2175, 380],
                 [PLAT_BIG_MIDDLE, 2175, 400],
                 [PLAT_BIG_BOTT, 2175, 420],
                 [PLAT_BIG_TOP, 2250, 300],
                 [PLAT_BIG_MIDDLE, 2250, 320],
                 [PLAT_BIG_MIDDLE, 2250, 340],
                 [PLAT_BIG_MIDDLE, 2250, 360],
                 [PLAT_BIG_MIDDLE, 2250, 380],
                 [PLAT_BIG_MIDDLE, 2250, 400],
                 [PLAT_BIG_MIDDLE, 2250, 420],
                 [PLAT_BIG_MIDDLE, 2250, 440],
                 [PLAT_BIG_BOTT, 2250, 460],
                 [PLAT_BIG_TOP, 2325, 300],
                 [PLAT_BIG_MIDDLE, 2325, 320],
                 [PLAT_BIG_MIDDLE, 2325, 340],
                 [PLAT_BIG_MIDDLE, 2325, 360],
                 [PLAT_BIG_MIDDLE, 2325, 380],
                 [PLAT_BIG_MIDDLE, 2325, 400],
                 [PLAT_BIG_MIDDLE, 2325, 420],
                 [PLAT_BIG_MIDDLE, 2325, 440],
                 [PLAT_BIG_BOTT, 2325, 460],
                 [PLAT_BIG_TOP, 2400, 300],
                 [PLAT_BIG_MIDDLE, 2400, 320],
                 [PLAT_BIG_MIDDLE, 2400, 340],
                 [PLAT_BIG_MIDDLE, 2400, 360],
                 [PLAT_BIG_MIDDLE, 2400, 380],
                 [PLAT_BIG_MIDDLE, 2400, 400],
                 [PLAT_BIG_MIDDLE, 2400, 420],
                 [PLAT_BIG_MIDDLE, 2400, 440],
                 [PLAT_BIG_MIDDLE, 2400, 460],
                 [PLAT_BIG_MIDDLE, 2400, 480],
                 [PLAT_BIG_MIDDLE, 2400, 500],
                 [PLAT_BIG_MIDDLE, 2400, 520],
                 [PLAT_BIG_MIDDLE, 2400, 540],
                 [PLAT_BIG_BOTT, 2400, 560],
                 [PLAT_1, 2000, 200],
                 [PLAT_1, 2075, 200],
                 [PLAT_1, 2150, 200],
                 [PLAT_2, 2200, 100],
                 [PLAT_1, 2225, 200],
                 [PLAT_1, 2300, 200],
                 ]

        # Go through the array above and add platforms
        for platform in level:
            block = Platform(platform[0])
            block.rect.x = platform[1]
            block.rect.y = platform[2]
            block.player = self.player
            self.platform_list.add(block)
            wall_list.add(block)

        # Add a custom moving platform
        block = MovingPlatform(PLAT_1)
        block.rect.x = 1350
        block.rect.y = 300
        block.boundary_left = 1350
        block.boundary_right = 1500
        block.change_x = 1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)


""" Main Program """
pygame.init()

global enemyWall

# Set the height and width of the screen
size = [SCREEN_WIDTH, SCREEN_HEIGHT]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("The Elementalist")

# Create the player
player = Player()
enemy = []

# Create all the levels
level_list = []
level_list.append(World(player))

# initiates all the mouse controls
LMB = 1
MMB = 2
RMB = 3
MWU = 4
MWD = 5

# Set the current level
current_level_no = 0
current_level = level_list[current_level_no]

active_sprite_list = pygame.sprite.Group()
player.level = current_level

enemy_list = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
melee_list = pygame.sprite.Group()


Waves()  # spawn the next wave of enemies

bullets_list = pygame.sprite.Group()  # holds all bullets

player.rect.x = 340
player.rect.y = SCREEN_HEIGHT - player.rect.height
active_sprite_list.add(player)

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# size & initiate window
windowW = 1280
windowH = 720

# -------- Main Program Loop -----------
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                player.go_left()
            if event.key == pygame.K_d:
                player.go_right()
            if event.key == pygame.K_SPACE:
                player.jump()
            if event.key == pygame.K_k:  # event.key == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed() == LMB:
                player.shoot()
            if event.key == pygame.K_l:
                player.isMelee = True
                melee_attack()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a and player.speedX < 0:
                player.stop()
            if event.key == pygame.K_d and player.speedX > 0:
                player.stop()

    # Update the player.
    active_sprite_list.update()

    # Update items in the level
    current_level.update()

    # checks to see if bullet hits a wall
    hits_bullet = pygame.sprite.groupcollide(bullets_list, wall_list, True, False)
    hits_melee = pygame.sprite.groupcollide(active_sprite_list, enemy_list, False, False)

    for i in range(len(enemy)):
        if not enemy[i].dead:
            enemyHit = pygame.sprite.spritecollide(enemy[i], bullets_list, True)
            if enemyHit:
                enemy[i].health -= player.ranged_damage
                print(i, enemy[i].health)
                if enemy[i].health <= 0:
                    enemy_list.remove(enemy[i])
                    enemy[i].dead = True
                    if player.infusion:
                        infusion_counter += 1
                    if player.appetite != 0 and player.health < 100 - player.appetite * 5:
                        player.health += player.appetite * 5

    # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
    current_level.draw(screen)
    active_sprite_list.draw(screen)
    melee_list.draw(screen)
    bullets_list.draw(screen)
    enemy_bullets.draw(screen)
    Waves().update()
    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

    # If the player gets near the right side, shift the world left (-x)
    if player.rect.right >= SCREEN_WIDTH * 0.85:
        diff = player.rect.right - SCREEN_WIDTH * 0.85
        player.rect.right = SCREEN_WIDTH * 0.85
        current_level.shift_world(-diff)

    # If the player gets near the left side, shift the world right (+x)
    if player.rect.left <= SCREEN_WIDTH * 0.15:
        diff = (SCREEN_WIDTH * 0.15) - player.rect.left
        player.rect.left = SCREEN_WIDTH * 0.15
        current_level.shift_world(diff)

    # Limit to 60 frames per second
    clock.tick(60)

    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
pygame.quit()
