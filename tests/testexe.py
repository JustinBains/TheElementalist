import pygame as pg
import random
import math

pg.init()


enemy_wall = None
invisible_wall = None

carnage = 0
hunger = 0
wind_boots = 0
cloud_boots = 0
fortitude = 0
savagery = 0
spark = False


def _carnage():
    global carnage
    # when the player buys this item from the shop a counter increases
    carnage += 1
    return carnage


def _hunger():
    global hunger

    hunger += 1
    return hunger


def _wind_boots():
    global wind_boots

    wind_boots += 1
    return wind_boots


def _cloud_boots():
    global cloud_boots

    cloud_boots += 1
    return cloud_boots


def _fortitude():
    global fortitude

    fortitude += 1
    return fortitude


def _savagery():
    global savagery

    savagery += 1
    return savagery


def _spark():
    global spark

    spark = True
    return spark


class Player(pg.sprite.Sprite):  # Player class takes pg.sprite.Sprite as the object
    """ This class represents the bar at the bottom that the player
        controls. """

    # -- Methods
    def __init__(self):
        """ Constructor function """
        # Call the parent's constructor
        super().__init__()

        self.image = pg.image.load("Player Sprites/adventurer-idle-2-00.png")

        # player direction and actions for animations
        self.playerFacing = 1
        self.left = True
        self.right = False
        self.idle = True
        self.isMelee = False
        self.isJump = False
        self.cast = True

        # Set a reference to the image rect.
        self.rect = self.image.get_rect()

        # Set speed vector of player
        self.vel = 6
        self.speedX = 0
        self.speedY = 0

        # List of sprites we can bump against
        self.level = None

        # deletes melee sprite after 100 ms
        self.last_melee = pg.time.get_ticks()
        self.melee_timer = 100

        # changes the cool down of bullets
        self.last_bullet = pg.time.get_ticks()
        self.bullet_timer = base_bullet_timer

        # 4 different elements. 1 = Air, 2 = Earth, 3 = Fire, 4 = Water
        self.element = 0

        # players gold counter
        self.gold = 0

        # initializes all the player items and attribtues
        global carnage
        global wind_boots
        global cloud_boots
        global fortitude
        global savagery
        self.carnage = _carnage()  # + attack AOE, used within melee
        self.waterHeal = 0  # heal after kills
        self.wind_boots = _wind_boots()  # + movement speed
        self.cloud_boots = _cloud_boots()  # + jump height

        # players health
        self.base_health = 100
        self.health = self.base_health + fortitude

        # changes the damage/size of the projectile the player shoots
        self.normal = True
        self.big_bullet = False

        # sets damage variables for melee/ranged attacks
        self.base_damage = 15
        self.damage = self.base_damage + savagery
        if self.normal:
            self.ranged_damage = self.damage * 2  # 30
        elif self.big_bullet:
            self.ranged_damage = self.damage * 3  # 75

        # intializes all of the animations .png's in a list
        self.runAnim = [pg.image.load('Player Sprites/adventurer-run-00.png'),
                        pg.image.load('Player Sprites/adventurer-run-01.png'),
                        pg.image.load('Player Sprites/adventurer-run-02.png'),
                        pg.image.load('Player Sprites/adventurer-run-03.png'),
                        pg.image.load('Player Sprites/adventurer-run-04.png'),
                        pg.image.load('Player Sprites/adventurer-run-05.png')]
        self.idleAnim = [pg.image.load('Player Sprites/adventurer-idle-2-00.png'),
                         pg.image.load('Player Sprites/adventurer-idle-2-01.png'),
                         pg.image.load('Player Sprites/adventurer-idle-2-02.png'),
                         pg.image.load('Player Sprites/adventurer-idle-2-03.png')]
        self.meleeAnim = [pg.image.load('Player Sprites/adventurer-attack2-00.png'),
                          pg.image.load('Player Sprites/adventurer-attack2-01.png'),
                          pg.image.load('Player Sprites/adventurer-attack2-02.png'),
                          pg.image.load('Player Sprites/adventurer-attack2-03.png'),
                          pg.image.load('Player Sprites/adventurer-attack2-04.png'),
                          pg.image.load('Player Sprites/adventurer-attack2-05.png')]
        self.jumpAnim = [pg.image.load('Player Sprites/adventurer-jump-00.png'),
                         pg.image.load('Player Sprites/adventurer-jump-01.png'),
                         pg.image.load('Player Sprites/adventurer-jump-02.png'),
                         pg.image.load('Player Sprites/adventurer-jump-03.png'),
                         pg.image.load('Player Sprites/adventurer-fall-00.png'),
                         pg.image.load('Player Sprites/adventurer-fall-01.png'),
                         pg.image.load('Player Sprites/adventurer-fall-00.png')]
        self.cast_ani = [pg.image.load("Player Sprites/adventurer-cast-02.png"),
                         pg.image.load("Player Sprites/adventurer-cast-01.png"),
                         pg.image.load("Player Sprites/adventurer-cast-00.png"),
                         pg.image.load("Player Sprites/adventurer-cast-03.png"),
                         pg.image.load("Player Sprites/adventurer-cast-loop-00.png"),
                         pg.image.load("Player Sprites/adventurer-cast-loop-01.png"),
                         pg.image.load("Player Sprites/adventurer-cast-loop-02.png"),
                         pg.image.load("Player Sprites/adventurer-cast-loop-03.png"),]
        # initializes the index of the array for animations
        self.runCount = 0
        self.idleCount = 0
        self.meleeCount = 0
        self.jumpCount = 0
        self.castCount = 0

    def update(self):
        """ Move the player. """
        # Gravity
        self.calc_grav()

        # Move left/rights
        self.rect.x += self.speedX

        # checks if the player collides with any platform
        self.collision()

        # calls the health bar
        health_bar()

        # When player is not moving play idle animation
        if self.speedX == 0:
            self.idle = True
            self.left = False
            self.right = False

        # animates everything that has occurred in the update function
        self.animation()

    def collision(self):
        # See if we hit anything
        block_hit_list = pg.sprite.spritecollide(self, self.level.platform_list, False)
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
        block_hit_list = pg.sprite.spritecollide(self, self.level.platform_list, False)
        for block in block_hit_list:
            # Reset our position based on the top/bottom of the object.
            if self.speedY > 0:
                self.rect.bottom = block.rect.top
            elif self.speedY < 0:
                self.rect.top = block.rect.bottom

            # Stop our vertical movement
            self.speedY = 0

    def calc_grav(self):  # perhaps create global gravity function
        """ Calculate effect of gravity. """
        if self.speedY == 0:
            self.speedY = 1
        else:
            self.speedY += .5 * 0.95 ** self.cloud_boots  # was .35

        # See if we are on the ground.
        if self.rect.y >= screen_h - self.rect.height and self.speedY >= 0:
            self.speedY = 0
            self.rect.y = screen_h - self.rect.height

    # Player-controlled movement:
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
        platform_hit_list = pg.sprite.spritecollide(self, self.level.platform_list, False)
        self.rect.y -= 2

        # If it is ok to jump, set our speed upwards
        if len(platform_hit_list) > 0 or self.rect.bottom >= screen_h:
            self.speedY = -10

    def go_left(self):
        """ Called when the user hits the left arrow. """
        self.left = True
        self.right = False
        self.idle = False
        self.cast = False
        Player.left = True
        Player.right = False
        Player.idle = False
        self.playerFacing = -1

        self.speedX = -self.vel * (1 + 0.05 * self.wind_boots)

    def go_right(self):
        """ Called when the user hits the right arrow. """
        self.left = False
        self.right = True
        self.idle = False
        self.cast = False
        Player.left = False
        Player.right = True
        Player.idle = False
        self.playerFacing = 1

        self.speedX = self.vel * (1 + 0.05 * self.wind_boots)

    def stop(self):
        """ Called when the user lets off the keyboard. """
        self.left = False
        self.right = False
        self.idle = True
        self.cast = False
        Player.left = False
        Player.right = False
        Player.idle = True

        self.speedX = 0

    def shoot(self):
        now_s = pg.time.get_ticks()
        """ normal firing mode """
        self.cast = True
        self.idle = False

        if player.playerFacing == 1:
            self.direction = "R"
        else:
            self.direction = "L"

        # shoots 1 bullet
        self.bullet_timer = base_bullet_timer
        # subtracts the current timer from the last shot to determine if the projectile cooldown is achieved
        if now_s - self.last_bullet >= self.bullet_timer:
            # resets the cooldown to the current time so player can't
            self.last_bullet = pg.time.get_ticks()

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
        if self.jumpCount + 1 >= 35:
            self.jumpCount = 0
            self.isJump = False
            if self.playerFacing == 1:
                self.right = True
            else:
                self.left = True
        if self.castCount + 1 >= 24:
            self.castCount = 0
            self.cast = False

        if self.right:
            self.image = self.runAnim[self.runCount // 10]
            self.runCount += 1
        elif self.left:
            self.image = pg.transform.flip(self.runAnim[self.runCount // 10], True, False)
            self.runCount += 1
        elif self.idle and self.cast == False and self.isMelee == False:
            if self.playerFacing == 1:
                self.image = self.idleAnim[self.idleCount // 10]
            else:
                self.image = pg.transform.flip(self.idleAnim[self.idleCount // 10], True, False)
            self.idleCount += 1
        elif self.isMelee:
            if self.playerFacing == 1:
                self.image = self.meleeAnim[self.meleeCount // 5]
            else:
                self.image = pg.transform.flip(self.meleeAnim[self.meleeCount // 5], True, False)
            self.meleeCount += 1
        elif self.cast:
            if self.playerFacing == 1:
                self.image = self.cast_ani[self.castCount // 4]
            else:
                self.image = pg.transform.flip(self.cast_ani[self.castCount // 4], True, False)
            self.castCount += 1
        if self.isJump:
            if self.playerFacing == 1:
                self.image = self.jumpAnim[self.jumpCount // 5]
            else:
                self.image = pg.transform.flip(self.jumpAnim[self.jumpCount // 5], True, False)
            self.jumpCount += 1


class PlayerProjectile(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.side = 10
        self.speed = 8

        if player.big_bullet:
            self.side = 15
            self.speed = 5

        self.image = pg.image.load("Projectile/water-projectile-move-00.png")
        self.rect = self.image.get_rect()

        self.projCount = 0

        self.rect.bottom = y + 7
        self.rect.centerx = x

        # find direction
        self.direction = player.playerFacing
        self.vel = self.speed * self.direction

    def update(self):
        self.rect.centerx += self.vel

        if self.projCount + 1 >= 40:
            self.projCount = 0

        if player.direction == "L":
            self.image = projAnim[self.projCount // 10]
            self.projCount += 1
        elif player.direction == "R":
            self.image = pg.transform.flip(projAnim[self.projCount // 10], True, False)
            self.projCount += 1


def melee_attack():
    """ when the player attacks checks if enemies are within a range to deal damage to"""
    player.idle = False
    player.isMelee = True
    player.isJump = False
    length = 60 * 1.10 ** player.carnage
    meleeHeight = 10 * 1.10 ** player.carnage
    player.animation()
    for i in range(len(enemy)):
        if player.playerFacing == -1:
            if player.rect.centerx >= enemy[
                i].rect.centerx > player.rect.centerx - length and player.rect.top - meleeHeight <= enemy[
                    i].rect.centery <= player.rect.bottom + meleeHeight:
                print(i, enemy[i].health)
                enemy[i].health -= player.damage
                if enemy[i].health <= 0:
                    enemy_list.remove(enemy[i])
                    enemy[i].dead = True
                    player.gold += 10
                    if player.waterHeal != 0 and player.health < 100 - player.waterHeal * 5:
                        player.health += player.waterHeal * 5

        if player.playerFacing == 1:
            if player.rect.centerx + length >= enemy[
                i].rect.centerx > player.rect.centerx and player.rect.top - meleeHeight <= enemy[
                    i].rect.centery <= player.rect.bottom + meleeHeight:
                print(i, enemy[i].health)
                enemy[i].health -= player.damage
                if enemy[i].health <= 0:
                    enemy_list.remove(enemy[i])
                    enemy[i].dead = True
                    player.gold += 10
                    if player.waterHeal != 0 and player.health + 5 < player.base_health:
                        player.health += player.waterHeal * 5


def health_bar():
    # adds health bars as a sprite so it will stay in place on the screen
    remaining_health = GreenHealth()
    lost_health = RedHealth()
    health_bars_list2.add(lost_health)
    health_bars_list1.add(remaining_health)


class GreenHealth(pg.sprite.Sprite):
    """ Displays the player health in top left corner"""
    def __init__(self):
        super().__init__()

        self.width = 316
        self.height = 8
        self.image = pg.Surface((self.width, self.height))
        self.image.fill(green)
        self.rect = self.image.get_rect()
        self.rect.x = 34
        self.rect.y = 26
        self.d_health = 0

    def update(self):
        self.d_health = player.health / player.base_health * self.width
        self.image = pg.Surface((self.d_health, self.height))
        self.image.fill(green)


class RedHealth(pg.sprite.Sprite):
    """ background for the health so it is easier to see players health """
    def __init__(self):
        super().__init__()

        self.width = 320
        self.height = 10
        self.image = pg.Surface((self.width, self.height))
        self.image.fill(black)
        self.rect = self.image.get_rect()
        self.rect.x = 32
        self.rect.y = 25

    def update(self):
        self.image = pg.Surface((self.width, self.height))
        self.image.fill(black)


class Waves:
    """ spawns a specific number of enemies per wave """
    def __init__(self):
        self.waveNum = 0
        self.enemy_choose = 0
        self.enemy_choice = []
        self.spawnNum = 2
        self.spawnStatus = True
        self.waveNext = True
        self.deathCounter = 0
        self.bossCounter = 0

    def update(self):
        global waveNext
        if self.spawnStatus and self.waveNext:  # checks if enemies can spawn and if the next wave should spawn
            self.spawn_enemy()  # calls the spawner class
            self.spawnStatus = False  # disables enemy spawns
            self.waveNext = False  # disables next wave
            for i in range(len(enemy)):
                enemy[i].alreadyDead = False

        for i in range(len(enemy)):
            if self.deathCounter == len(enemy):
                self.spawnStatus = True
                self.waveNum += 1
                self.spawnNum += 1
                self.deathCounter = 0
                game_wave()
            else:
                if enemy[i].dead and not enemy[i].alreadyDead:  # adds to the death counter
                    self.deathCounter += 1
                    enemy[i].alreadyDead = True

    def spawn_enemy(self):
        """ Chooses which enemy to spawn """
        # if the wave is divisible by 5 it is not wave 0, a Boss will spawn
        if self.waveNum % 5 == 0 and self.waveNum != 0:
            self.enemy_choice = Boss()
            enemy.append(self.enemy_choice)
            enemy_list.add(self.enemy_choice)

        for i in range(self.spawnNum):
            self.enemy_choose = random.randint(5, 8)  # chooses a random number between 0 to 8
            # a number from 1 to 8 is chosen and normal enemies and flying
            self.enemy_choice = [NormalEnemy(), NormalEnemy(), NormalEnemy(), FlyingEnemy(), FlyingEnemy(),
                                 HomingTurret(), WaterSpirits(), FireSpirits(), WindSpirits()]
            enemy.append((self.enemy_choice[self.enemy_choose]))
            enemy_list.add((self.enemy_choice[self.enemy_choose]))

        if self.waveNum % 6 == 0 and self.waveNum != 0:  # adds 500 gold for beating a boss / passing 5 waves
            player.gold += 500


class NormalEnemy(pg.sprite.Sprite):
    """ Enemies that melee attack, and jump"""
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        # chooses a random sprite from 3 waves
        self.sprite = random.randint(0, 2)
        if self.sprite == 0:
            self.image = pg.image.load("Enemy Sprites/Slime/slime-idle-0.png")
        elif self.sprite == 1:
            self.image = pg.image.load("Enemy Sprites/Goblin/goblin-idle-00.png")
        else:
            self.image = pg.image.load("Enemy Sprites/Kobold/kobold-idle-00.png")

        # gathers the rect from the chosen sprite
        self.rect = self.image.get_rect()

        # checks if the enemy can spawn in a valid position
        while True:
            self.rect.x = random.randint(250, 1550)
            self.rect.y = random.randint(0, screen_h - 250)
            enemy_wall = pg.sprite.groupcollide(enemy_list, wall_list, False, False)
            if enemy_wall and (self.rect.y >= screen_h - self.rect.height / 2):
                pass
            else:
                break

        # initializes the move and attack animation for all 3 sprites
        if self.sprite == 0:
            self.enemy_move = [pg.image.load("Enemy Sprites/Slime/slime-move-0.png"),
                               pg.image.load("Enemy Sprites/Slime/slime-move-1.png"),
                               pg.image.load("Enemy Sprites/Slime/slime-move-2.png"),
                               pg.image.load("Enemy Sprites/Slime/slime-move-3.png")]

            self.enemy_att = [pg.image.load("Enemy Sprites/Slime/slime-attack-0.png"),
                              pg.image.load("Enemy Sprites/Slime/slime-attack-1.png"),
                              pg.image.load("Enemy Sprites/Slime/slime-attack-2.png"),
                              pg.image.load("Enemy Sprites/Slime/slime-attack-3.png")]
        elif self.sprite == 1:
            self.enemy_move = [pg.image.load("Enemy Sprites/Goblin/goblin-run-00.png"),
                               pg.image.load("Enemy Sprites/Goblin/goblin-run-01.png"),
                               pg.image.load("Enemy Sprites/Goblin/goblin-run-02.png"),
                               pg.image.load("Enemy Sprites/Goblin/goblin-run-03.png"),
                               pg.image.load("Enemy Sprites/Goblin/goblin-run-04.png"),
                               pg.image.load("Enemy Sprites/Goblin/goblin-run-05.png")]

            self.enemy_att = [pg.image.load("Enemy Sprites/Goblin/goblin-attack-00.png"),
                              pg.image.load("Enemy Sprites/Goblin/goblin-attack-01.png"),
                              pg.image.load("Enemy Sprites/Goblin/goblin-attack-02.png"),
                              pg.image.load("Enemy Sprites/Goblin/goblin-attack-03.png"),
                              pg.image.load("Enemy Sprites/Goblin/goblin-attack-04.png")]
        else:
            self.enemy_move = [pg.image.load("Enemy Sprites/Kobold/kobold-run-00.png"),
                               pg.image.load("Enemy Sprites/Kobold/kobold-run-01.png"),
                               pg.image.load("Enemy Sprites/Kobold/kobold-run-02.png"),
                               pg.image.load("Enemy Sprites/Kobold/kobold-run-03.png"),
                               pg.image.load("Enemy Sprites/Kobold/kobold-run-04.png"),
                               pg.image.load("Enemy Sprites/Kobold/kobold-run-05.png")]

            self.enemy_att = [pg.image.load("Enemy Sprites/Kobold/kobold-attack-00.png"),
                              pg.image.load("Enemy Sprites/Kobold/kobold-attack-01.png"),
                              pg.image.load("Enemy Sprites/Kobold/kobold-attack-02.png"),
                              pg.image.load("Enemy Sprites/Kobold/kobold-attack-03.png"),
                              pg.image.load("Enemy Sprites/Kobold/kobold-attack-04.png")]

        # intiializes all the 'normal enemy' attributes
        self.moveCount = 0
        self.attackCount = 0
        self.left = False
        self.right = False
        self.speedXChoose = random.uniform(1.45, 2)  # chooses the players speed
        self.speedX = self.speedXChoose
        self.speedY = 0
        self.isJump = False
        self.isAttack = False
        self.health = 60
        self.damage = 7
        self.dead = False
        self.alreadyDead = False
        self.idle = True

        self.attackAnim = False
        self.idle = True

        # initializes attack variables
        self.now = pg.time.get_ticks()
        self.lastAttack = 0
        self.timerChooser = random.randint(0, 5)
        self.CD = 500 + 115 * self.timerChooser

        self.level = None

    def update(self):
        # adds gravity if the enemy is not jumping
        if not self.isJump:
            self.gravity()

        # enemy moves towards player
        if self.rect.x < player.rect.centerx:
            self.rect.x += self.speedX
            self.enemyFacing = 1
            self.right = True
            self.left = False
            self.idle = False
            self.isJump = False
        elif self.rect.x > player.rect.centerx:
            self.rect.x -= self.speedX
            self.enemyFacing = -1
            self.right = False
            self.left = True
            self.idle = False
            self.isJump = False
        else:
            self.right = False
            self.left = False
            self.idle = True
            self.isJump = False
            self.rect.x += 0

        # if the enemy is near the player and the timer returns true
        if pg.time.get_ticks() - self.lastAttack >= self.CD and (
                self.rect.left - 10 <= player.rect.centerx <= self.rect.right + 10):
            self.lastAttack = pg.time.get_ticks()
            self.attack()
            self.isAttack = True

        self.rect.y += self.speedY

        # checks all animation booleans and animates
        self.animation()

    def gravity(self):
        # if the enemy is above the floor the enemy will fall
        if self.rect.y >= screen_h - self.rect.height:
            self.speedY = 0
        else:
            self.speedY += 0.5

    def jump(self):
        # sets enemy Y velocity to negative so they will move upwards
        self.isJump = True

        platform_hit_list = pg.sprite.spritecollide(self, wall_list, False)

        if len(platform_hit_list) > 0 or self.rect.bottom >= screen_h:
            self.speedY = -10
            self.speedX = 0

    def attack(self):
        # checks if the enemy can attack left
        if (self.rect.left <= player.rect.centerx <= self.rect.centerx) and (
                self.rect.top - 10 <= player.rect.centery <= self.rect.bottom + 10):
            if player.health - self.damage <= 0:
                game_end()
            player.health -= self.damage
            print(player.health)
            self.Attackright = False
            self.Attackleft = True
        # checks if the enemy can attack to the right
        if self.rect.centerx <= player.rect.centerx <= self.rect.right + 5 and (
                self.rect.top - 10 <= player.rect.centery <= self.rect.bottom + 10):
            if player.health - self.damage <= 0:  # if the players health is <= 0 they will die
                game_end()
            player.health -= self.damage
            print(player.health)
            self.Attackright = True
            self.Attackleft = False

    def animation(self):
        """ animates all things that happen in update """
        if self.moveCount + 1 >= 40:
            self.moveCount = 0
        if self.attackCount + 1 >= 40:
            self.attackCount = 0
            self.isAttack = False

        if self.isAttack:
            if self.enemyFacing == -1:
                self.image = self.enemy_att[self.attackCount // 10]
            else:
                self.image = pg.transform.flip(self.enemy_att[self.attackCount // 10], True, False)
            self.attackCount += 1
        if self.left:
            self.image = self.enemy_move[self.moveCount // 10]
            self.moveCount += 1
        elif self.right:
            self.image = pg.transform.flip(self.enemy_move[self.moveCount // 10], True, False)
            self.moveCount += 1


class HomingTurret(pg.sprite.Sprite):  # turret enemy
    """ shoots homing projectiles, and doesnt move """

    def __init__(self):
        global enemy_wall

        pg.sprite.Sprite.__init__(self)

        self.image = pg.image.load("Enemy Sprites/Earth Wisp/earth-attack-00.png")
        self.rect = self.image.get_rect()

        enemy_wall = pg.sprite.groupcollide(enemy_list, wall_list, False, False)

        # checks if the enemy can spawn in a valid location
        while True:
            self.rect.x = random.randint(250, 1050)
            self.rect.y = random.randint(0, screen_h - 100)
            enemy_wall = pg.sprite.groupcollide(enemy_list, wall_list, False, False)
            if enemy_wall and (self.rect.y >= screen_h - self.rect.height / 2):
                pass
            else:
                break

        # initializes all the animations
        self.idleearth = [
            pg.image.load("Enemy Sprites/Earth Wisp/earth-idle-00.png"),
            pg.image.load("Enemy Sprites/Earth Wisp/earth-idle-01.png"),
            pg.image.load("Enemy Sprites/Earth Wisp/earth-idle-02.png"),
            pg.image.load("Enemy Sprites/Earth Wisp/earth-idle-03.png"),
        ]
        self.shootearth = [
            pg.image.load("Enemy Sprites/Earth Wisp/earth-attack-00.png"),
            pg.image.load("Enemy Sprites/Earth Wisp/earth-attack-01.png"),
            pg.image.load("Enemy Sprites/Earth Wisp/earth-attack-02.png"),
            pg.image.load("Enemy Sprites/Earth Wisp/earth-attack-03.png"),
            pg.image.load("Enemy Sprites/Earth Wisp/earth-attack-04.png"),
            pg.image.load("Enemy Sprites/Earth Wisp/earth-attack-05.png"),
            pg.image.load("Enemy Sprites/Earth Wisp/earth-attack-06.png"),
            pg.image.load("Enemy Sprites/Earth Wisp/earth-attack-07.png"),
            pg.image.load("Enemy Sprites/Earth Wisp/earth-attack-08.png"),
            pg.image.load("Enemy Sprites/Earth Wisp/earth-attack-09.png"),
        ]

        # initializes animation variables
        self.idleCount = 0
        self.shootCount = 0
        self.shoot = False
        self.idle = True

        # initializes movement variables
        self.speedXChoose = 0
        self.speedX = self.speedXChoose
        self.speedY = 0
        self.isJump = False
        self.health = 50
        self.dead = False
        self.damage = 5

        # initializes timer / cooldown variables
        self.now = pg.time.get_ticks()
        self.lastAttack = 0
        self.timerChooser = random.randint(0, 5)
        self.timer = 2500 + 250 * self.timerChooser

        self.level = None

    def update(self):
        # applies gravity
        self.gravity()

        # moves towards player
        self.rect.y += self.speedY
        self.rect.x += self.speedX

        self.idle = True

        # attacks if timer returns true
        self.now = pg.time.get_ticks()
        if self.now - self.lastAttack >= self.timer and (
                self.rect.centerx + 500 >= player.rect.centerx or self.rect.centerx - 500 <= player.rect.centerx):
            self.lastAttack = pg.time.get_ticks()
            self.attack()

        pg.sprite.groupcollide(enemy_list, wall_list, False, False)
        self.collide()

        # animates the enemy
        self.animation()

    def attack(self):
        #
        hb = HomingBullet(self.rect.centerx, self.rect.top - 20, player.rect.centerx, player.rect.centery)
        enemy_homing_bullets_list.add(hb)

    def gravity(self):
        if self.rect.y >= screen_h - self.rect.top:
            self.speedY = 0
        else:
            self.speedY += 0.500

        """ Calculate effect of gravity. """
        if self.speedY == 0:
            self.speedY = 1
        else:
            self.speedY += .5

        # See if we are on the ground.
        if self.rect.bottom >= screen_h - self.rect.top and self.speedY > 0:
            self.speedY = 0
            self.rect.bottom = screen_h - self.rect.top

    def collide(self):
        enemy_wall_totem = pg.sprite.groupcollide(enemy_list, wall_list, False, False)
        if self.rect.y >= screen_h - self.rect.top:
            self.speedY = 0

    def animation(self):
        # animates the enemy
        self.shoot = True

        if self.idleCount + 1 >= 60:
            self.idleCount = 0
        if self.shootCount + 1 >= 45:
            self.shootCount = 0
            self.shoot = False

        if self.shoot:
            self.image = self.shootearth[self.shootCount // 5]
            self.shootCount += 1
        if self.idle:
            self.image = self.idleearth[self.idleCount // 15]
            self.idleCount += 1


class HomingBullet(pg.sprite.Sprite):
    """ shoots a bullet that homes in onto the player's last location """
    def __init__(self, x, y, initPX, initPY):
        super().__init__()

        self.image = pg.image.load("Projectile/earth-projectile-move-00.png")
        self.rect = self.image.get_rect()  # gets the rect for the image

        # finds x and y position from the homing turret enemy class
        self.y = y
        self.x = x
        self.rect.center = (self.x, self.y)

        # sets the velocity
        self.vel = 2.5

        # initializes the variable to home the bullet
        self.destX = initPX
        self.destY = initPY
        self.dx = 0
        self.dy = 0
        self.dz = 0

    def update(self):
        # finds if the last position of the player
        if player.rect.x > 0:
            self.dx = self.destX - self.x
            self.dy = self.destY - self.y

        # finds the hypotenuse of the right angle triangle formed by the x and y vectors
        self.dz = math.sqrt(self.dx ** 2 + self.dy ** 2)

        # Finding the speedX
        if self.dz != 0:
            self.speedX = self.dx / self.dz * self.vel
            self.speedY = self.dy / self.dz * self.vel

        # moves projectiles towards the player if the projectile has not reached its target
        self.x += self.speedX
        self.rect.center = (self.x, self.y)
        # moves the bullet towards the y position of the target
        self.y += self.speedY
        self.rect.center = (self.x, self.y)

        # checks to see if any collision has occured, and deals damage occordingly
        pg.sprite.groupcollide(enemy_homing_bullets_list, wall_list, True, False)
        enemy_bullet_hit = pg.sprite.groupcollide(enemy_homing_bullets_list, active_sprite_list, True, False)
        if enemy_bullet_hit:
            if player.health - HomingTurret().damage <= 0:
                game_end()
            player.health -= HomingTurret().damage
            print(player.health)

        # kills the projectiles in case it hits nothing
        if self.dz <= 2:
            self.kill()

        pg.sprite.groupcollide(enemy_bullets_list, wall_list, True, False)


class WaterSpirits(pg.sprite.Sprite):
    def __init__(self):
        global enemy_wall
        global sprite_choice

        pg.sprite.Sprite.__init__(self)

        self.image = pg.image.load("Enemy Sprites/Water Wisp/water-idle-00.png")

        self.rect = self.image.get_rect()

        enemy_wall = pg.sprite.groupcollide(enemy_list, wall_list, False, False)

        # checks for valid spawn location
        while True:
            self.rect.x = random.randint(250, 2500)  # spawns it within the 2 invisible walls to stop projectiles moving infinitly
            self.rect.y = random.randint(550, screen_h - 100)  # spawns it a y range where the player can still hit it
            enemy_wall = pg.sprite.groupcollide(enemy_list, wall_list, False, False)
            if enemy_wall and (self.rect.y >= screen_h - self.rect.height - 100 / 2):
                pass
            else:
                break

        # initializes the enemy animations
        self.movewater = [pg.image.load("Enemy Sprites/Water Wisp/water-move-00.png"),
                          pg.image.load("Enemy Sprites/Water Wisp/water-move-01.png"),
                          pg.image.load("Enemy Sprites/Water Wisp/water-move-02.png"),
                          pg.image.load("Enemy Sprites/Water Wisp/water-move-03.png")]
        self.shootwater = [pg.image.load("Enemy Sprites/Water Wisp/water-attack-00.png"),
                           pg.image.load("Enemy Sprites/Water Wisp/water-attack-01.png"),
                           pg.image.load("Enemy Sprites/Water Wisp/water-attack-02.png"),
                           pg.image.load("Enemy Sprites/Water Wisp/water-attack-03.png"),
                           pg.image.load("Enemy Sprites/Water Wisp/water-attack-04.png"),
                           pg.image.load("Enemy Sprites/Water Wisp/water-attack-05.png"),
                           pg.image.load("Enemy Sprites/Water Wisp/water-attack-06.png"),
                           pg.image.load("Enemy Sprites/Water Wisp/water-attack-07.png"),
                           pg.image.load("Enemy Sprites/Water Wisp/water-attack-08.png"),
                           pg.image.load("Enemy Sprites/Water Wisp/water-attack-09.png")]
        self.moveCount = 0
        self.shootCount = 0

        # initializes the enemy movement variables
        self.facing = "R"
        self.left = False
        self.right = False
        self.shoot = False
        self.speedXChoose = random.uniform(2, 2)
        self.speedX = self.speedXChoose
        self.speedY = 0
        self.health = 100
        self.dead = False
        self.damage = 7
        self.idle = True

        # initializes enemy attack variables
        self.now = pg.time.get_ticks()
        self.lastAttack = 0
        self.timerChooser = random.randint(0, 5)
        self.timer = 1500 + 75 * self.timerChooser

        self.level = None

    def update(self):
        # ensures the enemy cannot go through platforms
        block_hit_list = pg.sprite.spritecollide(self, wall_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the object we hit
            if self.speedX > 0:
                self.rect.right = block.rect.left
            elif self.speedX < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right

        # enemy moves towards the player
        if self.rect.x < player.rect.centerx:
            self.rect.x += self.speedX
            self.right = True
            self.left = False
            self.facing = "R"
        elif self.rect.x > player.rect.centerx:
            self.rect.x -= self.speedX
            self.left = True
            self.right = False
            self.facing = "L"

        # gets current time
        self.now = pg.time.get_ticks()
        if self.now - self.lastAttack >= self.timer:
            self.lastAttack = pg.time.get_ticks()  # resets attack timer
            self.shoot = True

        self.rect.y += self.speedY

        self.animation(self.rect.centerx, self.rect.centery - 3)

    def animation(self, x, y):
        # resets the counter for animations
        if self.moveCount + 1 >= 60:
            self.moveCount = 0
        if self.shootCount + 1 >= 45:
            self.shootCount = 0
            self.shoot = False
        if self.shootCount + 1 == 30:
            # calls the shoot class for the specific enemy and adds it to a sprite group so it can be drawn
            sp = WaterShoot(x, y)
            enemy_bullets_list.add(sp)
            enemy_spirit_bullets_list.add(sp)

        if self.shoot:
            if self.facing == "L":
                self.image = self.shootwater[self.shootCount // 5]
            else:
                self.image = pg.transform.flip(self.shootwater[self.shootCount // 5], True, False)
            self.shootCount += 1

        elif self.left:
            self.image = self.movewater[self.moveCount // 15]
        elif self.right:
            self.image = pg.transform.flip(self.movewater[self.moveCount // 15], True, False)


class WaterShoot(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        global sprite_choice

        # sets the image of the rect to the sprite
        self.image = pg.image.load("Projectile/water-projectile-move-00.png")
        self.rect = self.image.get_rect()

        # initializes projectile animation
        self.Proj_water = [pg.image.load("Projectile/water-projectile-move-00.png"),
                           pg.image.load("Projectile/water-projectile-move-01.png"),
                           pg.image.load("Projectile/water-projectile-move-02.png"),
                           pg.image.load("Projectile/water-projectile-move-03.png")]
        self.AttCount = 0

        # initializes movement variables
        self.rect.x = x
        self.rect.y = y

        if self.rect.centerx < player.rect.centerx:
            self.direction = 1
        else:
            self.direction = -1

        self.vel = 3.5
        self.speedX = self.vel * self.direction

    def update(self):
        # moves the projectile in the direction originally shot
        self.rect.x += self.speedX

        # checks for collision, and damages the player if collide
        pg.sprite.groupcollide(enemy_spirit_bullets_list, wall_list, True, False)
        enemy_bullet_hit = pg.sprite.groupcollide(enemy_spirit_bullets_list, active_sprite_list, True, False)
        if enemy_bullet_hit:
            if player.health - WaterSpirits().damage <= 0:
                game_end()
            player.health -= WaterSpirits().damage

        pg.sprite.groupcollide(enemy_bullets_list, wall_list, True, False)

        self.animation()

    def animation(self):
        # animates the projectiles
        if self.AttCount + 1 >= 40:
            self.AttCount = 0

        if self.direction == -1:
            self.image = self.Proj_water[self.AttCount // 10]
            self.AttCount += 1

        else:
            self.image = pg.transform.flip(self.Proj_water[self.AttCount // 10], True, False)
            self.AttCount += 1


class FireSpirits(pg.sprite.Sprite):

    def __init__(self):
        global enemy_wall
        pg.sprite.Sprite.__init__(self)

        # gets the rect of the image
        self.image = pg.image.load("Enemy Sprites/Fire Wisp/fire-idle-00.png")
        self.rect = self.image.get_rect()

        enemy_wall = pg.sprite.groupcollide(enemy_list, wall_list, False, False)

        # checks for valid spawn location
        while True:
            self.rect.x = random.randint(250, 2500)  # spawns it within the 2 invisible walls to stop projectiles moving infinitly
            self.rect.y = random.randint(550, screen_h - 100)  # spawns it a y range where the player can still hit it
            enemy_wall = pg.sprite.groupcollide(enemy_list, wall_list, False, False)
            if enemy_wall and (self.rect.y >= screen_h - self.rect.height - 100 / 2):
                pass
            else:
                break

        # initializes the animation
        self.movefire = [pg.image.load("Enemy Sprites/Fire Wisp/fire-move-00.png"),
                         pg.image.load("Enemy Sprites/Fire Wisp/fire-move-01.png"),
                         pg.image.load("Enemy Sprites/Fire Wisp/fire-move-02.png"),
                         pg.image.load("Enemy Sprites/Fire Wisp/fire-move-03.png")]
        self.shootfire = [pg.image.load("Enemy Sprites/Fire Wisp/fire-attack-00.png"),
                          pg.image.load("Enemy Sprites/Fire Wisp/fire-attack-01.png"),
                          pg.image.load("Enemy Sprites/Fire Wisp/fire-attack-02.png"),
                          pg.image.load("Enemy Sprites/Fire Wisp/fire-attack-03.png"),
                          pg.image.load("Enemy Sprites/Fire Wisp/fire-attack-04.png"),
                          pg.image.load("Enemy Sprites/Fire Wisp/fire-attack-05.png"),
                          pg.image.load("Enemy Sprites/Fire Wisp/fire-attack-06.png"),
                          pg.image.load("Enemy Sprites/Fire Wisp/fire-attack-07.png"),
                          pg.image.load("Enemy Sprites/Fire Wisp/fire-attack-08.png"),
                          pg.image.load("Enemy Sprites/Fire Wisp/fire-attack-09.png")]
        self.moveCount = 0
        self.shootCount = 0

        # initializes the movement variables
        self.facing = "R"
        self.left = False
        self.right = False
        self.shoot = False
        self.speedXChoose = random.uniform(2, 2)
        self.speedX = self.speedXChoose
        self.speedY = 0
        self.health = 100
        self.dead = False
        self.damage = 7

        # initializes the attack variables
        self.now = pg.time.get_ticks()
        self.lastAttack = 0
        self.timerChooser = random.randint(0, 5)
        self.timer = 1500 + 75 * self.timerChooser

        self.level = None

    def update(self):
        # ensures the enemy cannot go through platforms
        block_hit_list = pg.sprite.spritecollide(self, wall_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the object we hit
            if self.speedX > 0:
                self.rect.right = block.rect.left
            elif self.speedX < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right

        # moves enemy toward the player
        if self.rect.x < player.rect.centerx:
            self.rect.x += self.speedX
            self.right = True
            self.left = False
            self.facing = "R"
        if self.rect.x > player.rect.centerx:
            self.rect.x -= self.speedX
            self.left = True
            self.right = False
            self.facing = "L"
        self.rect.y += self.speedY

        # gets current time and checks if it is ok to shoot
        self.now = pg.time.get_ticks()
        if self.now - self.lastAttack >= self.timer:
            self.lastAttack = pg.time.get_ticks()
            self.shoot = True

        self.animation(self.rect.centerx, self.rect.centery - 3)

    def gravity(self):
        if self.rect.y >= screen_h - self.rect.height:
            self.speedY = 0
        else:
            self.speedY += 0.500

    def animation(self, x, y):
        # resets all animation variables
        if self.moveCount + 1 >= 60:
            self.moveCount = 0
        if self.shootCount + 1 >= 45:
            self.shootCount = 0
            self.shoot = False
        if self.shootCount + 1 == 30:
            # calls the shoot class for the specific enemy and adds it to a sprite group so it can be drawn
            sp = FireShoot(x, y)
            enemy_bullets_list.add(sp)
            enemy_spirit_bullets_list.add(sp)

        if self.shoot:
            if self.facing == "L":
                self.image = self.shootfire[self.shootCount // 5]
            else:
                self.image = pg.transform.flip(self.shootfire[self.shootCount // 5], True, False)
            self.shootCount += 1

        elif self.left:
            self.image = self.movefire[self.moveCount // 15]
            self.moveCount += 1

        elif self.right:
            self.image = pg.transform.flip(self.movefire[self.moveCount // 15], True, False)
            self.moveCount += 1


class FireShoot(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # gets the rect of the image
        self.image = pg.image.load("Projectile/fire-projectile-move-00.png")
        self.rect = self.image.get_rect()

        # initializes the animations
        self.Proj_fire = [pg.image.load("Projectile/fire-projectile-move-00.png"),
                          pg.image.load("Projectile/fire-projectile-move-01.png"),
                          pg.image.load("Projectile/fire-projectile-move-02.png"),
                          pg.image.load("Projectile/fire-projectile-move-03.png")]
        self.AttCount = 0

        # initializes the spawn location of the projectile
        self.rect.x = x
        self.rect.y = y

        # gets direction the projectile should be fired in
        if self.rect.centerx < player.rect.centerx:
            self.direction = 1
        else:
            self.direction = -1
        self.vel = 3.5
        self.speedX = self.vel * self.direction

    def update(self):
        # continues moving in the correct direction
        self.rect.x += self.speedX

        # checks if any other sprite group is hit and deals damage if it is the player sprite
        pg.sprite.groupcollide(enemy_spirit_bullets_list, wall_list, True, False)
        enemy_bullet_hit = pg.sprite.groupcollide(enemy_spirit_bullets_list, active_sprite_list, True, False)
        if enemy_bullet_hit:
            if enemy_bullet_hit:
                if player.health - FireSpirits().damage <= 0:
                    game_end()
            player.health -= FireSpirits().damage
        pg.sprite.groupcollide(enemy_bullets_list, wall_list, True, False)

        self.animation()

    def animation(self):
        # animates the projectile
        if self.AttCount + 1 >= 40:
            self.AttCount = 0

        if self.direction == -1:
            self.image = self.Proj_fire[self.AttCount // 10]
            self.AttCount += 1
        else:
            self.image = pg.transform.flip(self.Proj_fire[self.AttCount // 10], True, False)
            self.AttCount += 1


class WindSpirits(pg.sprite.Sprite):

    def __init__(self):
        global enemy_wall
        pg.sprite.Sprite.__init__(self)

        # gets the rect of the image
        self.image = pg.image.load("Enemy Sprites/Wind Wisp/wind-idle-00.png")
        self.rect = self.image.get_rect()

        # checks for valid spawn location
        while True:
            self.rect.x = random.randint(250, 2500)  # spawns it within the 2 invisible walls to stop projectiles moving infinitly
            self.rect.y = random.randint(550, screen_h - 100)  # spawns it a y range where the player can still hit it
            enemy_wall = pg.sprite.groupcollide(enemy_list, wall_list, False, False)
            if enemy_wall and (self.rect.y >= screen_h - self.rect.height - 100 / 2):
                pass
            else:
                break

        # initializes the animation
        self.movewind = [pg.image.load("Enemy Sprites/Wind Wisp/wind-move-00.png"),
                         pg.image.load("Enemy Sprites/Wind Wisp/wind-move-01.png"),
                         pg.image.load("Enemy Sprites/Wind Wisp/wind-move-02.png"),
                         pg.image.load("Enemy Sprites/Wind Wisp/wind-move-03.png")]
        self.shootwind = [pg.image.load("Enemy Sprites/Wind Wisp/wind-attack-00.png"),
                          pg.image.load("Enemy Sprites/Wind Wisp/wind-attack-01.png"),
                          pg.image.load("Enemy Sprites/Wind Wisp/wind-attack-02.png"),
                          pg.image.load("Enemy Sprites/Wind Wisp/wind-attack-03.png"),
                          pg.image.load("Enemy Sprites/Wind Wisp/wind-attack-04.png"),
                          pg.image.load("Enemy Sprites/Wind Wisp/wind-attack-05.png"),
                          pg.image.load("Enemy Sprites/Wind Wisp/wind-attack-06.png"),
                          pg.image.load("Enemy Sprites/Wind Wisp/wind-attack-07.png"),
                          pg.image.load("Enemy Sprites/Wind Wisp/wind-attack-08.png"),
                          pg.image.load("Enemy Sprites/Wind Wisp/wind-attack-09.png")]
        self.moveCount = 0
        self.shootCount = 0

        # initializes the movement variables
        self.facing = "R"
        self.left = False
        self.right = False
        self.shoot = False
        self.speedXChoose = random.uniform(2, 2)
        self.speedX = self.speedXChoose
        self.speedY = 0
        self.health = 100
        self.dead = False
        self.damage = 7

        # initializes the attack variables
        self.now = pg.time.get_ticks()
        self.lastAttack = 0
        self.timerChooser = random.randint(0, 5)
        self.timer = 1500 + 75 * self.timerChooser

        self.level = None

    def update(self):
        # ensures the enemy cannot go through platforms
        block_hit_list = pg.sprite.spritecollide(self, wall_list, False)
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the object we hit
            if self.speedX > 0:
                self.rect.right = block.rect.left
            elif self.speedX < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right

        # moves the enemy towards the player
        if self.rect.x < player.rect.centerx:
            self.rect.x += self.speedX
            self.enemyFacing = 1
            self.facing = "R"
            self.right = True
            self.left = False
            self.idle = False
            self.isJump = False
        elif self.rect.x > player.rect.centerx:
            self.rect.x -= self.speedX
            self.enemyFacing = -1
            self.facing = "L"
            self.right = False
            self.left = True
            self.idle = False
            self.isJump = False

        # checks if it is ok to shoot
        self.now = pg.time.get_ticks()
        if self.now - self.lastAttack >= self.timer:
            self.lastAttack = pg.time.get_ticks()
            self.shoot = True

        self.rect.y += self.speedY

        # See if we hit anything
        self.animation(self.rect.centerx, self.rect.centery - 3)

    def gravity(self):
        if self.rect.y >= screen_h - self.rect.height:
            self.speedY = 0
        else:
            self.speedY += 0.500

    def animation(self, x, y):
        # animates the enemy
        if self.moveCount + 1 >= 60:
            self.moveCount = 0
        if self.shootCount + 1 >= 45:
            self.shootCount = 0
            self.shoot = False
        if self.shootCount + 1 == 30:
            # calls the shoot class for the specific enemy and adds it to a sprite group so it can be drawn
            sp = WindShoot(x, y)
            enemy_bullets_list.add(sp)
            enemy_spirit_bullets_list.add(sp)

        if self.shoot:
            if self.facing == "L":
                self.image = self.shootwind[self.shootCount // 5]
            else:
                self.image = pg.transform.flip(self.shootwind[self.shootCount // 5], True, False)
            self.shootCount += 1

        elif self.left:
            self.image = self.movewind[self.moveCount // 15]
            self.moveCount += 1

        elif self.right:
            self.image = pg.transform.flip(self.movewind[self.moveCount // 15], True, False)
            self.moveCount += 1


class WindShoot(pg.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        # initializes the projectile sprite, and animation
        self.image = pg.image.load("Projectile/wind-projectile-move-00.png")
        self.rect = self.image.get_rect()
        self.Proj_wind = [pg.image.load("Projectile/wind-projectile-move-00.png"),
                          pg.image.load("Projectile/wind-projectile-move-01.png"),
                          pg.image.load("Projectile/wind-projectile-move-02.png"),
                          pg.image.load("Projectile/wind-projectile-move-03.png")]
        self.AttCount = 0

        # sets spawn location on the enemy that shot it out
        self.rect.x = x
        self.rect.y = y

        # sets speed and direction of the projectile
        if self.rect.centerx < player.rect.centerx:
            self.direction = 1
        else:
            self.direction = -1
        self.vel = 3.5
        self.speedX = self.vel * self.direction

    def update(self):
        # moves the projectile in the correct direction
        self.rect.x += self.speedX

        # checks for collisions and deals damage occordingly
        pg.sprite.groupcollide(enemy_spirit_bullets_list, wall_list, True, False)
        enemy_bullet_hit = pg.sprite.groupcollide(enemy_spirit_bullets_list, active_sprite_list, True, False)
        if enemy_bullet_hit:
            if player.health - WindSpirits().damage <= 0:
                game_end()
            player.health -= WindSpirits().damage
            print(player.health)

        pg.sprite.groupcollide(enemy_bullets_list, wall_list, True, False)

        self.animation()

    def animation(self):
        # animates the projectile
        if self.AttCount + 1 >= 40:
            self.AttCount = 0

        if self.direction == -1:
            self.image = self.Proj_wind[self.AttCount // 10]
            self.AttCount += 1
        else:
            self.image = pg.transform.flip(self.Proj_wind[self.AttCount // 10], True, False)
            self.AttCount += 1


class FlyingEnemy(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pg.image.load("Enemy Sprites/Oculothorax/oculothorax-idle-00.png")
        self.rect = self.image.get_rect()

        # checks for valid spawn location
        while True:
            self.rect.x = random.randint(250, 2850)  # spawns it within the 2 invisible walls to stop projectiles moving infinitly
            self.rect.y = random.randint(0, screen_h - 200)  # spawns it a y range where the player can still hit it
            enemy_wall = pg.sprite.groupcollide(enemy_list, wall_list, False, False)
            if enemy_wall and (self.rect.y >= screen_h - self.rect.height / 2):
                pass
            else:
                break

        # initializes the animations
        self.move = [pg.image.load("Enemy Sprites/Oculothorax/oculothorax-move-00.png"),
                     pg.image.load("Enemy Sprites/Oculothorax/oculothorax-move-01.png"),
                     pg.image.load("Enemy Sprites/Oculothorax/oculothorax-move-02.png"),
                     pg.image.load("Enemy Sprites/Oculothorax/oculothorax-move-03.png")]
        self.attack_ani = [pg.image.load("Enemy Sprites/Oculothorax/oculothorax-attack-00.png"),
                           pg.image.load("Enemy Sprites/Oculothorax/oculothorax-attack-01.png"),
                           pg.image.load("Enemy Sprites/Oculothorax/oculothorax-attack-02.png"),
                           pg.image.load("Enemy Sprites/Oculothorax/oculothorax-attack-03.png"),
                           pg.image.load("Enemy Sprites/Oculothorax/oculothorax-attack-04.png"),
                           pg.image.load("Enemy Sprites/Oculothorax/oculothorax-attack-05.png"),
                           pg.image.load("Enemy Sprites/Oculothorax/oculothorax-attack-06.png"),
                           pg.image.load("Enemy Sprites/Oculothorax/oculothorax-attack-07.png"),
                           pg.image.load("Enemy Sprites/Oculothorax/oculothorax-attack-08.png")]
        self.moveCount = 0
        self.attackCount = 0

        # initializes the movement variables
        self.left = False
        self.right = False
        self.dx = 0
        self.dy = 0
        self.dz = 0
        self.speedX = 0
        self.speedY = 0
        self.health = 20
        self.damage = 3
        self.Attackleft = False
        self.Attackright = False
        self.dead = False
        self.speedXChoose = random.uniform(2, 3)
        self.vel = self.speedXChoose

        # initializes attack variables
        self.now = pg.time.get_ticks()
        self.lastAttack = 0
        self.ChooseTimer = random.randint(0, 5)
        self.CD = 650 + 35 * self.ChooseTimer

    def update(self):
        global player

        # finds position of the player
        self.dx = player.rect.centerx - self.rect.x
        self.dy = player.rect.centery - self.rect.y

        # finds straight line to players position
        self.dz = math.sqrt(self.dx ** 2 + self.dy ** 2)

        # checks if it is ok to attack, and ifi the player is within attacking range
        self.now = pg.time.get_ticks()
        if pg.time.get_ticks() - self.lastAttack >= self.CD and (
                self.rect.left - 10 <= player.rect.centerx <= self.rect.right + 10):
            self.lastAttack = pg.time.get_ticks()
            self.attack()
            self.isAttack = True

        # ensures the enemy is not on the player, and creates a speed vector to move on
        if self.dz != 0:
            self.speedX = self.dx / self.dz * self.vel
            self.speedY = self.dy / self.dz * self.vel

        # moves the enemy towards the player
        if self.rect.x < player.rect.centerx:
            self.rect.x += self.speedX
            self.right = True
            self.left = False
        elif self.rect.x > player.rect.centerx:
            self.rect.x -= -self.speedX
            self.right = False
            self.left = True

        if self.rect.y < player.rect.centery:
            self.rect.y += self.speedY
        elif self.rect.y > player.rect.centery:
            self.rect.y -= -self.speedY

        self.animation()

    def attack(self):
        # facing left; checks if the player is within the range of the enemy's attack
        if (self.rect.left <= player.rect.centerx <= self.rect.centerx) and (
                self.rect.top - 10 <= player.rect.centery <= self.rect.bottom + 10):
            if player.health - self.damage <= 0:
                game_end()
            player.health -= self.damage
            self.Attackright = False
            self.Attackleft = True
        # facing right; checks if the player is within the range of the enemy's attack
        if self.rect.centerx <= player.rect.centerx <= self.rect.right + 5 and (
                self.rect.top - 10 <= player.rect.centery <= self.rect.bottom + 10):
            player.health -= self.damage
            self.Attackright = True
            self.Attackleft = False

    def animation(self):
        # animates
        if self.moveCount + 1 >= 40:
            self.moveCount = 0

        if self.attackCount + 1 >= 40:
            self.attackCount = 0

        if self.left:
            self.image = self.move[self.moveCount // 10]
            self.moveCount += 1

        elif self.right:
            self.image = pg.transform.flip(self.move[self.moveCount // 10], True, False)
            self.moveCount += 1

        elif self.left:
            self.image = self.move[self.moveCount // 10]
            self.moveCount += 1

        elif self.right:
            self.image = pg.transform.flip(self.move[self.moveCount // 10], True, False)
            self.moveCount += 1


class Boss(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)

        # chooses a between 2 boss enemies
        self.sprite = random.randint(0, 1)
        if self.sprite == 0:
            self.image = pg.image.load("Enemy Sprites/Minotaur/minotaur-idle-00.png")
        elif self.sprite == 1:
            self.image = pg.image.load("Enemy Sprites/Ogre/ogre-idle-00.png")

        # gets the appropriate rect from the image
        self.rect = self.image.get_rect()

        # checks for valid spawn location
        while True:
            self.rect.x = random.randint(100, 1550)  # spawns it within the 2 invisible walls to stop projectiles moving infinitly
            self.rect.y = random.randint(0, screen_h - 100)  # spawns it a y range where the player can still hit it
            enemy_wall = pg.sprite.groupcollide(enemy_list, wall_list, False, False)
            if enemy_wall and (self.rect.y >= screen_h - self.rect.height / 2):
                pass
            else:
                break

        # initializes the animation for the chosen boss
        if self.sprite == 0:
            self.enemy_move = [pg.image.load("Enemy Sprites/Minotaur/minotaur-run-00.png"),
                               pg.image.load("Enemy Sprites/Minotaur/minotaur-run-01.png"),
                               pg.image.load("Enemy Sprites/Minotaur/minotaur-run-02.png"),
                               pg.image.load("Enemy Sprites/Minotaur/minotaur-run-03.png"),
                               pg.image.load("Enemy Sprites/Minotaur/minotaur-run-04.png"),
                               pg.image.load("Enemy Sprites/Minotaur/minotaur-run-05.png"),
                               ]
            self.enemy_att = [pg.image.load("Enemy Sprites/Minotaur/minotaur-attack2-00.png"),
                              pg.image.load("Enemy Sprites/Minotaur/minotaur-attack2-01.png"),
                              pg.image.load("Enemy Sprites/Minotaur/minotaur-attack2-02.png"),
                              pg.image.load("Enemy Sprites/Minotaur/minotaur-attack2-03.png"),
                              pg.image.load("Enemy Sprites/Minotaur/minotaur-attack2-04.png"),
                              pg.image.load("Enemy Sprites/Minotaur/minotaur-attack2-05.png"),
                              pg.image.load("Enemy Sprites/Minotaur/minotaur-attack2-06.png"),
                              pg.image.load("Enemy Sprites/Minotaur/minotaur-attack2-07.png"),
                              pg.image.load("Enemy Sprites/Minotaur/minotaur-attack2-08.png"),
                              ]
        else:
            self.enemy_move = [pg.image.load("Enemy Sprites/Ogre/ogre-run-00.png"),
                               pg.image.load("Enemy Sprites/Ogre/ogre-run-01.png"),
                               pg.image.load("Enemy Sprites/Ogre/ogre-run-02.png"),
                               pg.image.load("Enemy Sprites/Ogre/ogre-run-03.png"),
                               pg.image.load("Enemy Sprites/Ogre/ogre-run-04.png"),
                               pg.image.load("Enemy Sprites/Ogre/ogre-run-05.png"),
                               ]
            self.enemy_att = [pg.image.load("Enemy Sprites/Ogre/ogre-attack2-00.png"),
                              pg.image.load("Enemy Sprites/Ogre/ogre-attack2-01.png"),
                              pg.image.load("Enemy Sprites/Ogre/ogre-attack2-02.png"),
                              pg.image.load("Enemy Sprites/Ogre/ogre-attack2-03.png"),
                              pg.image.load("Enemy Sprites/Ogre/ogre-attack2-04.png"),
                              pg.image.load("Enemy Sprites/Ogre/ogre-attack2-05.png"),
                              pg.image.load("Enemy Sprites/Ogre/ogre-attack2-06.png"),
                              ]

        # initializes the movement and health attributes of the boss
        self.moveCount = 0
        self.attackCount = 0
        self.left = False
        self.right = False
        self.speedXChoose = random.uniform(1.15, 1.35)
        self.speedX = self.speedXChoose
        self.speedY = 0
        self.isJump = False
        self.isAttack = False
        self.health = 500
        self.damage = 25
        self.dead = False
        self.alreadyDead = False
        self.idle = True

        self.attackAnim = False
        self.idle = True

        # initializes the attack variables
        self.now = pg.time.get_ticks()
        self.lastAttack = 0
        self.timerChooser = random.randint(0, 5)
        self.CD = 3500 + 115 * self.timerChooser

        self.level = None

    def update(self):
        if not self.isJump:
            self.gravity()

        # moves towarrds the player
        if self.rect.x < player.rect.centerx:
            self.rect.x += self.speedX
            self.enemyFacing = 1
            self.right = True
            self.left = False
            self.idle = False
            self.isJump = False
        elif self.rect.x > player.rect.centerx:
            self.rect.x -= self.speedX
            self.enemyFacing = -1
            self.right = False
            self.left = True
            self.idle = False
            self.isJump = False
        else:
            self.right = False
            self.left = False
            self.idle = True
            self.isJump = False
            self.rect.x += 0

        # checks if it is ok to attack
        if pg.time.get_ticks() - self.lastAttack >= self.CD and (
                self.rect.left - 10 <= player.rect.centerx <= self.rect.right + 10):
            self.lastAttack = pg.time.get_ticks()
            self.attack()
            self.isAttack = True

        self.rect.y += self.speedY

        self.animation()

    def gravity(self):
        if self.rect.y >= screen_h - self.rect.height:
            self.speedY = 0
        else:
            self.speedY += 0.5

    def jump(self):
        self.isJump = True

        platform_hit_list = pg.sprite.spritecollide(self, wall_list, False)

        if len(platform_hit_list) > 0 or self.rect.bottom >= screen_h:
            self.speedY = -10
            self.speedX = 0

    def attack(self):
        # left attack doesnt work
        if (self.rect.left <= player.rect.centerx <= self.rect.centerx) and (
                self.rect.top - 10 <= player.rect.centery <= self.rect.bottom + 10):
            if player.health - self.damage <= 0:
                game_end()
            player.health -= self.damage
            print(player.health)
            self.Attackright = False
            self.Attackleft = True
        # right attack too long
        if self.rect.centerx <= player.rect.centerx <= self.rect.right + 5 and (
                self.rect.top - 10 <= player.rect.centery <= self.rect.bottom + 10):
            if player.health - self.damage <= 0:
                game_end()
            player.health -= self.damage
            print(player.health)
            self.Attackright = True
            self.Attackleft = False

    def animation(self):
        if self.moveCount + 1 >= 40:
            self.moveCount = 0

        if self.attackCount + 1 >= 40:
            self.attackCount = 0
            self.isAttack = False

        if self.isAttack:
            if self.enemyFacing == -1:
                self.image = self.enemy_att[self.attackCount // 10]
            else:
                self.image = pg.transform.flip(self.enemy_att[self.attackCount // 10], True, False)
            self.attackCount += 1
        if self.left:
            self.image = self.enemy_move[self.moveCount // 10]
            self.moveCount += 1
        elif self.right:
            self.image = pg.transform.flip(self.enemy_move[self.moveCount // 10], True, False)
            self.moveCount += 1


# TODO unused param <file_name> in class
# TODO nothing is converted with <convert()> in function <get_image()>
class SpriteSheet(object):
    """ Class used to grab images out of a sprite sheet. """
    # This points to our sprite sheet image
    sprite_sheet = None

    def __init__(self, file_name):
        """ Constructor. Pass in the file name of the sprite sheet. """

        # Load the sprite sheet.
        self.sprite_sheet = pg.image.load("Platforms.png").convert()

    def get_image(self, x, y, width, height):
        """ Grab a single image out of a larger sprite sheet
            Pass in the x, y location of the sprite
            and the width and height of the sprite. """

        # Create a new blank image
        image = pg.Surface([width, height]).convert()

        # Copy the sprite from the large sheet onto the smaller image
        image.blit(self.sprite_sheet, (0, 0), (x, y, width, height))

        # Assuming black works as the transparent color
        image.set_colorkey(black)

        # Return the image
        return image


class Wall(pg.sprite.Sprite):
    """
    Walls can't be passed by player.
    """

    def __init__(self, width, height):
        # Init.
        pg.sprite.Sprite.__init__(self)

        self.height = height
        self.width = width
        self.image = pg.Surface([width, height])
        self.image.set_colorkey(black)
        self.image.fill(black)
        self.rect = self.image.get_rect()


class Platform(pg.sprite.Sprite):
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
        hit = pg.sprite.collide_rect(self, self.player)
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
        hit = pg.sprite.collide_rect(self, self.player)
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

    def __init__(self, _player):
        """ Constructor. Pass in a handle to player. Needed for when moving platforms
            collide with the player. """
        self.platform_list = pg.sprite.Group()
        self.wall_list = pg.sprite.Group()
        self.player = _player

        # Background image
        self.background = None

        self.world_shift = 0
        self.level_limit = -1000

    # Update everything on this level
    def update(self):
        """ Update everything in this level."""
        self.platform_list.update()
        enemy_list.update()
        enemy_spirit_bullets_list.update()
        enemy_homing_bullets_list.update()
        health_bars_list1.update()
        health_bars_list2.update()

    def draw(self, _screen):
        """ Draw everything on this level. """
        # Draw the background
        screen.fill(black)
        screen.blit(self.background, (-1000 + self.world_shift // 3, -10))
        # Draw all the sprite lists that we have
        self.platform_list.draw(screen)
        enemy_list.draw(screen)
        enemy_spirit_bullets_list.draw(screen)
        enemy_homing_bullets_list.draw(screen)
        health_bars_list2.draw(screen)
        health_bars_list1.draw(screen)
        self.wall_list.update()

    def shift_world(self, shift_x):
        """ When the user moves left/right and we need to scroll everything: """

        # Keep track of the shift amount
        self.world_shift += shift_x

        # Go through all the sprite lists and shift
        for platform in self.platform_list:
            platform.rect.x += shift_x

        for e in enemy_list:
            e.rect.x += shift_x
        for n in enemy_spirit_bullets_list:
            n.rect.x += shift_x
        for j in enemy_homing_bullets_list:
            j.rect.x += shift_x
            j.rect.y += shift_x

        for wall in self.wall_list:
            wall.rect.x += shift_x


# Create platforms for the level
class World(Level):
    """ Definition for level 1. """

    def __init__(self, _player):
        """ Create level 1. """

        # Call the parent constructor
        Level.__init__(self, _player)

        self.background = pg.image.load("BackgroundLong.png").convert()
        self.background.set_colorkey(black)
        self.level_limit = -2500

        # Array with width, height, x, and y of platform
        level = [[PLAT_BIG_TOP, -450, 640],
                 [PLAT_BIG_MIDDLE, -450, 660],
                 [PLAT_BIG_MIDDLE, -450, 680],
                 [PLAT_BIG_MIDDLE, -450, 700],
                 [PLAT_BIG_TOP, -375, 640],
                 [PLAT_BIG_MIDDLE, -375, 660],
                 [PLAT_BIG_MIDDLE, -375, 680],
                 [PLAT_BIG_MIDDLE, -375, 700],
                 [PLAT_BIG_TOP, -300, 640],
                 [PLAT_BIG_MIDDLE, -300, 660],
                 [PLAT_BIG_MIDDLE, -300, 680],
                 [PLAT_BIG_MIDDLE, -300, 700],
                 [PLAT_BIG_TOP, -225, 640],
                 [PLAT_BIG_MIDDLE, -225, 660],
                 [PLAT_BIG_MIDDLE, -225, 680],
                 [PLAT_BIG_MIDDLE, -225, 700],
                 [PLAT_BIG_TOP, -150, 640],
                 [PLAT_BIG_MIDDLE, -150, 660],
                 [PLAT_BIG_MIDDLE, -150, 680],
                 [PLAT_BIG_MIDDLE, -150, 700],
                 [PLAT_BIG_TOP, -75, 640],
                 [PLAT_BIG_MIDDLE, -75, 660],
                 [PLAT_BIG_MIDDLE, -75, 680],
                 [PLAT_BIG_MIDDLE, -75, 700],
                 [PLAT_BIG_TOP, -75, 640],
                 [PLAT_BIG_MIDDLE, -75, 660],
                 [PLAT_BIG_MIDDLE, -75, 680],
                 [PLAT_BIG_MIDDLE, -75, 700],
                 [PLAT_BIG_TOP, 0, 640],
                 [PLAT_BIG_MIDDLE, 0, 660],
                 [PLAT_BIG_MIDDLE, 0, 680],
                 [PLAT_BIG_MIDDLE, 0, 700],
                 [PLAT_BIG_TOP, 75, 640],
                 [PLAT_BIG_MIDDLE, 75, 660],
                 [PLAT_BIG_MIDDLE, 75, 680],
                 [PLAT_BIG_MIDDLE, 75, 700],
                 [PLAT_BIG_TOP, 150, 640],
                 [PLAT_BIG_MIDDLE, 150, 660],
                 [PLAT_BIG_MIDDLE, 150, 680],
                 [PLAT_BIG_MIDDLE, 150, 700],
                 [PLAT_BIG_TOP, 225, 640],
                 [PLAT_BIG_MIDDLE, 225, 660],
                 [PLAT_BIG_MIDDLE, 225, 680],
                 [PLAT_BIG_MIDDLE, 225, 700],
                 [PLAT_1, 300, 700],
                 [PLAT_1, 375, 700],
                 [PLAT_1, 450, 700],
                 [PLAT_1, 525, 700],
                 [PLAT_1, 600, 700],
                 [PLAT_1, 675, 700],
                 [PLAT_1, 750, 700],
                 [PLAT_1, 825, 700],
                 [PLAT_1, 900, 700],
                 [PLAT_1, 975, 700],
                 [PLAT_1, 1050, 700],
                 [PLAT_1, 1125, 700],
                 [PLAT_1, 1200, 700],
                 [PLAT_1, 1275, 700],
                 [PLAT_1, 1350, 700],
                 [PLAT_1, 1425, 700],
                 [PLAT_1, 1500, 700],
                 [PLAT_1, 1575, 700],
                 [PLAT_1, 1650, 700],
                 [PLAT_1, 1725, 700],
                 [PLAT_1, 1800, 700],
                 [PLAT_1, 1875, 700],
                 [PLAT_1, 1950, 700],
                 [PLAT_BIG_TOP, 2025, 640],
                 [PLAT_BIG_MIDDLE, 2025, 660],
                 [PLAT_BIG_MIDDLE, 2025, 680],
                 [PLAT_BIG_MIDDLE, 2025, 700],
                 [PLAT_BIG_TOP, 2100, 640],
                 [PLAT_BIG_MIDDLE, 2100, 660],
                 [PLAT_BIG_MIDDLE, 2100, 680],
                 [PLAT_BIG_MIDDLE, 2100, 700],
                 [PLAT_BIG_TOP, 2175, 640],
                 [PLAT_BIG_MIDDLE, 2175, 660],
                 [PLAT_BIG_MIDDLE, 2175, 680],
                 [PLAT_BIG_MIDDLE, 2175, 700],
                 [PLAT_BIG_TOP, 2250, 640],
                 [PLAT_BIG_MIDDLE, 2250, 660],
                 [PLAT_BIG_MIDDLE, 2250, 680],
                 [PLAT_BIG_MIDDLE, 2250, 700],
                 [PLAT_BIG_TOP, 2325, 640],
                 [PLAT_BIG_MIDDLE, 2325, 660],
                 [PLAT_BIG_MIDDLE, 2325, 680],
                 [PLAT_BIG_MIDDLE, 2325, 700],
                 [PLAT_BIG_TOP, 2400, 640],
                 [PLAT_BIG_MIDDLE, 2400, 660],
                 [PLAT_BIG_MIDDLE, 2400, 680],
                 [PLAT_BIG_MIDDLE, 2400, 700],
                 [PLAT_BIG_TOP, 2475, 640],
                 [PLAT_BIG_MIDDLE, 2475, 660],
                 [PLAT_BIG_MIDDLE, 2475, 680],
                 [PLAT_BIG_MIDDLE, 2475, 700],
                 [PLAT_BIG_TOP, 2550, 640],
                 [PLAT_BIG_MIDDLE, 2550, 660],
                 [PLAT_BIG_MIDDLE, 2550, 680],
                 [PLAT_BIG_MIDDLE, 2550, 700],
                 [PLAT_BIG_TOP, 2625, 640],
                 [PLAT_BIG_MIDDLE, 2625, 660],
                 [PLAT_BIG_MIDDLE, 2625, 680],
                 [PLAT_BIG_MIDDLE, 2625, 700],
                 [PLAT_BIG_TOP, 2700, 640],
                 [PLAT_BIG_MIDDLE, 2700, 660],
                 [PLAT_BIG_MIDDLE, 2700, 680],
                 [PLAT_BIG_MIDDLE, 2700, 700],
                 [PLAT_BIG_TOP, 2775, 640],
                 [PLAT_BIG_MIDDLE, 2775, 660],
                 [PLAT_BIG_MIDDLE, 2775, 680],
                 [PLAT_BIG_MIDDLE, 2775, 700],
                 [PLAT_BIG_TOP, 2850, 640],
                 [PLAT_BIG_MIDDLE, 2850, 660],
                 [PLAT_BIG_MIDDLE, 2850, 680],
                 [PLAT_BIG_MIDDLE, 2850, 700],
                 [PLAT_BIG_TOP, 2925, 640],
                 [PLAT_BIG_MIDDLE, 2925, 660],
                 [PLAT_BIG_MIDDLE, 2925, 680],
                 [PLAT_BIG_MIDDLE, 2925, 700],
                 [PLAT_1, 500, 600],
                 [PLAT_1, 650, 550],
                 [PLAT_1, 800, 500],
                 [PLAT_1, 1200, 500],
                 [PLAT_1, 1350, 550],
                 [PLAT_1, 1500, 600],
                 [PLAT_2, 1632, 600],
                 [PLAT_1, 1700, 600],
                 [PLAT_1, 1850, 550]]

        invisibleWall = [[1, 60, 320, 655],
                         [1, 60, 2025, 655]]

        borderWall = [[100, 720, 0, 0],
                     [100, 720, 2425, 0]]

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
        block.rect.x = 950
        block.rect.y = 500
        block.boundary_left = 900
        block.boundary_right = 1100
        block.change_x = 1
        block.player = self.player
        block.level = self
        self.platform_list.add(block)
        wall_list.add(block)

        for Walls in invisibleWall:
            block = Wall(Walls[0], Walls[1])
            block.rect.x = (Walls[2])
            block.rect.y = (Walls[3])
            self.wall_list.add(block)
            invisible_wall_list.add(block)

        for border in borderWall:
            block = Wall(border[0], border[1])
            block.rect.x = (border[2])
            block.rect.y = (border[3])
            self.platform_list.add(block)
            wall_list.add(block)


""" all the variables of the game """
# RGB colors
white = [255, 255, 255]
black = [0, 0, 0]

grey = [145, 145, 145]
red = [200, 0, 0]
green = [0, 200, 0]
blue = [32, 137, 188]
orange = [255, 140, 0]
brown = [140, 70, 20]
purple = [140, 40, 230]

grey2 = [200, 200, 200]
red2 = [255, 0, 0]
green2 = [0, 255, 0]
blue2 = [55, 159, 210]
orange2 = [255, 170, 0]
brown2 = [170, 100, 60]
purple2 = [170, 80, 255]

# size & initiate screen
screen_w = 1280
screen_h = 720
screen = pg.display.set_mode((screen_w, screen_h))
pg.display.set_caption('The Elementalist')

# booleans for stages of game
start = False
run = False
end = False
pause = False
_objective = False
_controls = False
_shop = False
__items = False
__skills = False

# clock for frame rate
clock = pg.time.Clock()

# These constants define our platform types:
#   Name of file
#   X location of sprite
#   Y location of sprite
#   Width of sprite
#   Height of sprite
PLAT_1 = (0, 0, 96, 30)
PLAT_2 = (96, 0, 32, 33)
PLAT_BIG_TOP = (0, 32, 96, 32)
PLAT_BIG_MIDDLE = (0, 64, 96, 32)
PLAT_BIG_BOTT = (0, 96, 96, 32)
GROUND = (100, 35, 100, 40)

wall_list = pg.sprite.Group()  # holds all walls/platforms
invisible_wall_list = pg.sprite.Group()
base_bullet_timer = 500  # milliseconds
infusion_counter = 0

# Create the player
player = Player()
enemy = []

# Create all the levels
level_list = []
level_list.append(World(player))

# Set the current level
current_level_no = 0
current_level = level_list[current_level_no]

active_sprite_list = pg.sprite.Group()
player.level = current_level

enemy_list = pg.sprite.Group()
enemy_bullets_list = pg.sprite.Group()

# enemy bullets need multiple groups because of different damages
enemy_homing_bullets_list = pg.sprite.Group()
enemy_spirit_bullets_list = pg.sprite.Group()

# add all types of enemy bullets to a single list
enemy_bullets_list.add(enemy_spirit_bullets_list)
enemy_bullets_list.add(enemy_homing_bullets_list)

waves = Waves()  # spawn the next wave of enemies

bullets_list = pg.sprite.Group()  # holds all bullets

health_bars_list1 = pg.sprite.Group()
health_bars_list2 = pg.sprite.Group()

player.rect.x = 340
player.rect.y = 600
active_sprite_list.add(player)


# function for creating text for buttons
def txt_object(msg, font):
    txt_surface = font.render(msg, True, black)
    return txt_surface, txt_surface.get_rect()


# function for creating plain text
def txt_plain(msg, f_size, x, y):
    options = pg.font.SysFont('freesansbold.ttf', f_size)
    txt_surface, txt_rect = txt_object(msg, options)
    txt_rect.center = (x, y)
    screen.blit(txt_surface, txt_rect)


# function for creating two-toned buttons & putting text on those buttons
def button(msg, f_size, x, y, w, h, c1, c2, action=None):
    mouse = pg.mouse.get_pos()
    click = pg.mouse.get_pressed()
    # print(click)
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pg.draw.rect(screen, c2, (x, y, w, h))
        if click[0] == 1 and action is not None:
            action()
    else:
        pg.draw.rect(screen, c1, (x, y, w, h))

    # create buttons
    txt_button = pg.font.SysFont('freesansbold.ttf', f_size)
    txt_surface, txt_rect = txt_object(msg, txt_button)
    txt_rect.center = ((x+(w/2)), (y+(h/2)))
    screen.blit(txt_surface, txt_rect)


# 1st & start stage of game - start menu
def game_start():
    # brings in global boolean variables
    global run
    global start
    global _objective
    global _controls
    global _wave

    start = True
    _objective = False
    _controls = False
    _wave = False

    while start:
        # quit game if screen is closed
        for e in pg.event.get():
            if e.type == pg.QUIT:
                quit()
                run = False

        # set frame rate & background
        clock.tick(60)
        screen.fill(white)

        # create title for start menu, titled 'The Elementalist'
        txt_plain('The Elementalist', 115, screen_w / 2, screen_h/2-screen_h/4)

        # create buttons for start menu, to start/quit game, etc
        button('START', 50, screen_w / 2 - 90, 300, 220, 80, green, green2, game_element)  # game() if pressed
        button('OBJECTIVES', 50, screen_w / 2 - 90, 390, 220, 80, blue, blue2, objective)  # objective() if pressed
        button('CONTROLS', 50, screen_w / 2 - 90, 480, 220, 80, grey, grey2, controls)  # controls() if pressed
        button('QUIT', 50, screen_w / 2 - 90, 570, 220, 80, red, red2, quit)  # quit() if pressed

        pg.display.update()


# 2nd & main stage of game - game
def game():
    global run
    global pause

    run = True
    pause = False

    while run:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                run = False
                quit()

            if e.type == pg.KEYDOWN:
                """when a key is pressed the function to control the players action is called"""
                if e.key == pg.K_a:
                    player.go_left()
                if e.key == pg.K_d:
                    player.go_right()
                if e.key in (pg.K_SPACE, pg.K_w):
                    player.jump()
                if e.key == pg.K_k:
                    player.shoot()
                if e.key == pg.K_l:
                    player.isMelee = True
                    melee_attack()
                if e.key == pg.K_p:
                    game_pause()

            if e.type == pg.KEYUP:
                """when a left or right movement key is released it stops the players movement"""
                if e.key == pg.K_a and player.speedX < 0:
                    player.stop()
                if e.key == pg.K_d and player.speedX > 0:
                    player.stop()

        # Update the player.
        active_sprite_list.update()

        # Update items in the level
        current_level.update()

        # checks to see if bullet hits a wall
        pg.sprite.groupcollide(bullets_list, wall_list, True, False)
        pg.sprite.groupcollide(active_sprite_list, enemy_list, False, False)

        for i in range(len(enemy)):
            """"""
            if hasattr(enemy[i], 'isJump'):
                if not enemy[i].isJump:
                    enemy_wall = pg.sprite.spritecollide(enemy[i], wall_list, False, False)
                    if enemy_wall:
                        enemy[i].speedY = 0
                    else:
                        enemy[i].isJump = False

                invisible_wall = pg.sprite.spritecollide(enemy[i], invisible_wall_list, False, False)
                if invisible_wall:
                    enemy[i].jump()
                else:
                    enemy[i].speedX = enemy[i].speedXChoose
                    enemy[i].isJump = False

        for i in range(len(enemy)):
            """if a player bullet hits an enemy the enemies health will decrease or the enemy will die and the 
            player will gain gold and will be healed if the player chose water"""
            if not enemy[i].dead:
                enemyHit = pg.sprite.spritecollide(enemy[i], bullets_list, True)
                if enemyHit:
                    enemy[i].health -= player.ranged_damage
                    print(i, enemy[i].health)
                    if enemy[i].health <= 0:
                        enemy_list.remove(enemy[i])
                        enemy[i].dead = True
                        player.gold += 10
                        if player.waterHeal != 0:
                            if player.health + 5 >= player.base_health:
                                player.health = player.base_health
                            else:
                                player.health += player.waterHeal * 5

        # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
        waves.update()
        current_level.draw(screen)
        active_sprite_list.draw(screen)
        bullets_list.draw(screen)
        enemy_bullets_list.draw(screen)
        # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

        # If the player gets near the right side, shift the world left (-x)
        if player.rect.right >= screen_w * 0.85:
            diff = player.rect.right - screen_w * 0.85
            player.rect.right = screen_w * 0.85
            current_level.shift_world(-diff)

        # If the player gets near the left side, shift the world right (+x)
        if player.rect.left <= screen_w * 0.15:
            diff = (screen_w * 0.15) - player.rect.left
            player.rect.left = screen_w * 0.15
            current_level.shift_world(diff)

        # Go ahead and update the screen with what we've drawn.
        pg.display.flip()


# 3rd & last stage of game - end menu # TODO make end menu
def game_end():
    global run

    run = True

    # to remove graphics present in previous stage - game
    screen.fill(red)
    pg.display.flip()

    while run:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                quit()
                run = False

        txt_plain('YOU DIED', 110, screen_w / 2, screen_h / 2 - screen_h / 3)

        button('QUIT', 50, screen_w / 2 - 110, 570, 220, 80, red, red2, quit)  # quit() if pressed

        pg.display.flip()
        clock.tick(60)


# intermediary paused stage of game - pause menu
def game_pause():
    global run
    global pause

    pause = True

    # to remove graphics present in previous stage - game
    screen.fill(white)
    pg.display.flip()

    # create text for pause menu, titled 'PAUSED'
    txt_plain('PAUSED', 90, screen_w / 2, screen_h / 2 - screen_h / 3)

    while pause:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                quit()
                run = False

        # create buttons for pause menu, to continue/quit game, etc
        button('CONTINUE', 50, screen_w / 2 - 110, 210, 220, 80, green, green2, game_unpause)
        button('SHOP', 50, screen_w / 2 - 110, 300, 220, 80, orange, orange2, shop)
        button('OBJECTIVES', 50, screen_w / 2 - 110, 390, 220, 80, blue, blue2, objective)  # objective() if pressed
        button('CONTROLS', 50, screen_w / 2 - 110, 480, 220, 80, grey, grey2, controls)  # controls() if pressed
        button('QUIT', 50, screen_w / 2 - 110, 570, 220, 80, red, red2, quit)  # quit() if pressedc

        txt_plain("Gold Coins: " + str(player.gold), 30, 150, 20)
        txt_plain("Health: " + str(player.health) + '/' + str(player.base_health), 30, 140, 40)
        txt_plain("Melee Damage: " + str(player.damage), 30, 155, 60)

        pg.display.update()
        clock.tick(60)


# change to intermediary paused stage of game, an parameter for button() function
def game_unpause():
    global pause
    pause = False
    game()


def game_wave():
    global run
    global _wave

    _wave = True
    waveComplete = "Wave " + str(waves.waveNum) + " Completed"

    screen.fill(white)
    pg.display.flip()

    while _wave:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                run = False
                quit()

        txt_plain(waveComplete, 90, screen_w / 2, screen_h / 2 - screen_h / 3)

        button('NEXT WAVE', 50, screen_w / 2 - 110, 210, 220, 80, green, green2, next_wave)
        button('SHOP', 50, screen_w / 2 - 110, 300, 220, 80, orange, orange2, shop)
        button('OBJECTIVES', 50, screen_w / 2 - 110, 390, 220, 80, blue, blue2, objective)
        button('CONTROLS', 50, screen_w / 2 - 110, 480, 220, 80, grey, grey2, controls)
        button('QUIT', 50, screen_w / 2 - 110, 570, 220, 80, red, red2, quit)

        txt_plain("Gold Coins: " + str(player.gold), 30, 150, 20)
        txt_plain("Health: " + str(player.health) + '/' + str(player.base_health), 30, 140, 40)
        txt_plain("Melee Damage: " + str(player.damage), 30, 155, 60)

        pg.display.update()


def next_wave():
    waves.waveNext = True
    game()


def game_element():
    global run
    global _element

    _element = True

    screen.fill(white)
    pg.display.flip()

    while _element:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                run = False
                quit()

        txt_plain('Choose an Element', 60, screen_w / 2, 290)

        button('AIR', 50, 140, 400, 220, 80, grey, grey2, air)
        txt_plain('+ MOVEMENT SPEED', 25, 250, 470)
        button('EARTH', 50, 400, 400, 220, 80, brown, brown2, earth)
        txt_plain('+ HEALTH', 25, 510, 470)
        button('FIRE', 50, 660, 400, 220, 80, red, red2, fire)
        txt_plain('+ DAMAGE', 25, 770, 470)
        button('WATER', 50, 920, 400, 220, 80, blue, blue2, water)
        txt_plain('LEECH HEALTH AFTER KILL', 20, 1030, 465)

        pg.display.update()


def air():
    global projAnim
    player.element = 1
    player.vel = 9
    projAnim = [pg.image.load("Projectile/wind-projectile-move-00.png"),
                pg.image.load("Projectile/wind-projectile-move-01.png"),
                pg.image.load("Projectile/wind-projectile-move-02.png"),
                pg.image.load("Projectile/wind-projectile-move-03.png")]
    game()


def earth():
    global projAnim
    player.element = 2
    player.base_health = 150
    player.health = 150
    projAnim = [pg.image.load("Projectile/earth-projectile-move-00.png"),
                pg.image.load("Projectile/earth-projectile-move-01.png"),
                pg.image.load("Projectile/earth-projectile-move-02.png"),
                pg.image.load("Projectile/earth-projectile-move-03.png")]
    game()


def fire():
    global projAnim
    player.element = 3
    player.base_damage = 25
    player.ranged_damage = 50
    projAnim = [pg.image.load("Projectile/fire-projectile-move-00.png"),
                pg.image.load("Projectile/fire-projectile-move-01.png"),
                pg.image.load("Projectile/fire-projectile-move-02.png"),
                pg.image.load("Projectile/fire-projectile-move-03.png")]
    game()


def water():
    global projAnim
    player.element = 4
    player.waterHeal = 1
    projAnim = [pg.image.load("Projectile/water-projectile-move-00.png"),
                pg.image.load("Projectile/water-projectile-move-01.png"),
                pg.image.load("Projectile/water-projectile-move-02.png"),
                pg.image.load("Projectile/water-projectile-move-03.png")]
    game()


# intermediary stage of menu - objectives
def objective():
    global run
    global pause
    global _wave
    global _objective

    _objective = True

    # to remove graphics present in previous stage - start menu
    screen.fill(white)
    pg.display.flip()

    while _objective:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                quit()
                run = False

        txt_plain('Objective', 60, screen_w / 2, 150)
        txt_plain('Defend yourself from enemies', 40, screen_w / 2, 300)
        txt_plain('Collect gold to upgrade your abilities', 40, screen_w / 2, 350)
        txt_plain('Survive as long as possible', 40, screen_w / 2, 400)

        if not pause and not _wave:  # call/return to game_start if pressed
            button('BACK', 40, 15, 15, 100, 50, grey, grey2, game_start)
        elif _wave and not pause:
            button('BACK', 40, 15, 15, 100, 50, grey, grey2, game_wave)
        else:  # call/return to game_pause if pressed and game is currently paused
            button('BACK', 40, 15, 15, 100, 50, grey, grey2, game_pause)

        pg.display.update()


# intermediary stage of menu - controls
def controls():
    global run
    global pause
    global _wave
    global _controls

    _controls = True

    # to remove graphics present in previous stage - start menu
    screen.fill(white)
    pg.display.flip()

    while _controls:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                quit()
                run = False

        txt_plain('Controls', 60, screen_w / 2, 150)
        txt_plain('A: Move Left', 40, screen_w / 2, 250)
        txt_plain('D: Move Right', 40, screen_w / 2, 300)
        txt_plain('SPACE: Jump', 40, screen_w / 2, 350)
        txt_plain('K: Ranged Attack', 40, screen_w / 2, 400)
        txt_plain('L: Melee Attack', 40, screen_w / 2, 450)
        # txt_plain('P: Pause Game', 40, screen_w / 2, 500)

        if not pause and not _wave:  # call/return to game_start if pressed
            button('BACK', 40, 15, 15, 100, 50, grey, grey2, game_start)
        elif _wave and not pause:
            button('BACK', 40, 15, 15, 100, 50, grey, grey2, game_wave)
        else:  # call/return to game_pause if pressed and game is currently paused
            button('BACK', 40, 15, 15, 100, 50, grey, grey2, game_pause)

            txt_plain('Everything costs 100 gold coins', 40, screen_w / 2, screen_h / 2 - screen_h / 3 + 70)

        pg.display.update()


# intermediary stage of menu - shop
def shop():
    global run
    global pause
    global _wave
    global _shop

    _shop = True

    # to remove graphics present in previous stage - pause
    screen.fill(white)
    pg.display.flip()

    while _shop:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                quit()
                run = False

        # create text for shop menu, titled 'SHOP'
        txt_plain('SHOP', 90, screen_w / 2, screen_h / 2 - screen_h / 3)

        # call/return to game_pause if pressed
        if _wave:
            button('BACK', 40, 15, 15, 100, 50, grey, grey2, game_wave)
        else:
            button('BACK', 40, 15, 15, 100, 50, grey, grey2, game_pause)

        button('ITEMS', 50, 220, 350, 220, 80, brown, brown2, items)  # item() if pressed
        button('SKILLS', 50, screen_w - 450, 350, 220, 80, purple, purple2, skills)  # skill() if pressed

        pg.display.update()
        clock.tick(60)


# intermediary stage of shop - items
# intermediary stage of shop - items
def items():
    global run
    global __items

    __items = True

    # to remove graphics present in previous stage - pause
    screen.fill(white)
    pg.display.flip()

    while __items:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                quit()
                run = False

        # create text for shop menu, titled 'SHOP'
        txt_plain('ITEMS', 90, screen_w / 2, screen_h / 2 - screen_h / 3)

        # call/return to game_pause if pressed
        button('BACK', 40, 15, 80, 100, 50, grey, grey2, shop)

        button('CARNAGE', 50, screen_w / 2 - 110, 250, 220, 90, brown, brown2, _carnage)
        txt_plain('+ AREA OF ATTACK', 25, screen_w / 2, 320)
        button('HUNGER', 50, screen_w / 2 - 110, 350, 220, 90, brown, brown2, _hunger)
        txt_plain('+ HEALTH AFTER KILL', 25, screen_w / 2, 420)
        button('WIND BOOTS', 40, screen_w / 2 - 110, 450, 220, 90, brown, brown2, _wind_boots)
        txt_plain('+ MOVEMENT SPEED', 25, screen_w / 2, 520)
        button('CLOUD BOOTS', 40, screen_w / 2 - 110, 550, 220, 90, brown, brown2, _cloud_boots)
        txt_plain('+ JUMP HEIGHT', 25, screen_w / 2, 620)

        pg.display.update()


# intermediary stage of shop - skills
# intermediary stage of shop - skills
def skills():
    global run
    global pause
    global _shop
    global __skills

    __skills = True

    # to remove graphics present in previous stage - pause
    screen.fill(white)
    pg.display.flip()

    while __skills:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                quit()
                run = False

        # create text for shop menu, titled 'SHOP'
        txt_plain('SKILLS', 90, screen_w / 2, screen_h / 2 - screen_h / 3)

        # call/return to game_pause if pressed
        button('BACK', 40, 15, 80, 100, 50, grey, grey2, shop)

        button('FORTITUDE', 50, screen_w / 2 - 110, 300, 220, 80, purple, purple2, _fortitude)
        txt_plain('+ MAX HEALTH', 25, screen_w / 2, 370)
        button('SAVAGERY', 50, screen_w / 2 - 110, 400, 220, 80, purple, purple2, _savagery)
        txt_plain('+ DAMAGE', 25, screen_w / 2, 470)
        button('SPARK', 50, screen_w / 2 - 110, 500, 220, 80, purple, purple2, _spark)
        txt_plain('LARGE PROJECTILE', 25, screen_w / 2, 570)

        pg.display.update()


# functions for item purchases from shop


""" main loop """
# calls game_start(), as it is the first stage of the game
game_start()

# to be IDLE friendly, exits program when code finishes
pg.quit()