import pygame
import os
import random
import esper
from enum import Enum

pygame.init()

#GLOBAL CONSTANTS
#TODO: Configuration file, maybe?
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900 
TILE_WIDTH = 30
TILE_HEIGHT = 30
ROWS = SCREEN_HEIGHT // TILE_HEIGHT
COLUMNS = SCREEN_WIDTH // TILE_WIDTH
TERRAIN_SCROLL_SPEED = 1
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30
PLAYER_SPEED = 1
MAX_FPS = 60
BACKGROUND_COLOR = (0, 0, 0)
BOMB_WIDTH = 30
BOMB_HEIGHT = 30
#In frames
TERRAIN_SCROLL_DELAY = 20


win = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("River Run AI")





#Position Component
class Position:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

#Velocity Component
class Velocity:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

#Player-Specific Component
class Player:
    def __init__(self, lives=1, fuel=100, max=100, fuel_rate=0.5, defuel_rate=0.05):
        self.lives = lives
        self.fuel = fuel
        self.max = max
        self.fuel_rate = fuel_rate
        self.defuel_rate = defuel_rate

#Render Component
class Renderable:
    def __init__(self, sprite):
        self.sprite = sprite
        self.width = sprite.get_width()
        self.height = sprite.get_height()

class RenderSystem(esper.Processor):
    def __init__(self, window, clear_color):
        super().__init__()
        self.window = window
        self.clear_color = clear_color
    def process(self):
        #Render everything . . .
        self.window.fill(self.clear_color)
        #Render the Terrain . . .
        for ent, terrain in self.world.get_component(Terrain):
            #By Row
            for i in range(terrain.scroll_pos, terrain.scroll_pos + ROWS):
                #By Column
                for j in range(0, terrain.terrain_width):
                    if(terrain.tile_matrix[i % terrain.terrain_height][j].tile_type == Tiles.LAND):
                        #Land is GREEN
                        pygame.draw.rect(self.window,
                                        (0,255,0),
                                        (j * TILE_WIDTH,
                                        (i % terrain.terrain_height) * TILE_HEIGHT,
                                        TILE_WIDTH,
                                        TILE_HEIGHT))
                    elif(terrain.tile_matrix[i % terrain.terrain_height][j].tile_type == Tiles.WATER):
                        #Water is WET, err I mean BLUE
                        pygame.draw.rect(self.window,
                                        (0,0,255),
                                        (j * TILE_WIDTH,
                                        (i % terrain.terrain_height) * TILE_HEIGHT,
                                        TILE_WIDTH,
                                        TILE_HEIGHT))
        #Render the Entities . . .
        for ent, (pos, render) in self.world.get_components(Position, Renderable):
            self.window.blit(render.sprite, (pos.x * TILE_WIDTH, pos.y * TILE_HEIGHT))
        pygame.display.flip()

#Collision Component
class Collider:
    def __init__(self):
        pass

class ColliderSystem(esper.Processor):
    def __init__(self):
        super().__init__()
    def process(self):
        for ent, (pos, col) in self.world.get_components(Position, Collider):
            #Collision
            pass

#Fuelstrip Component
class Fuelstrip:
    def __init__(self):
        None
        #Stateless component, essentially functions as a flag.

#Refueling System
class RefuelingSystem(esper.Processor):
    def __init__(self):
        super().__init__()
    def process(self):
        #Refueling strip's components
        for ent_1, (ref, col_1) in self.world.get_components(Fuelstrip, Collider):
            #Player's components
            for ent_2, (play, fuel, col_2) in self.world.get_components(Player, Collider):
                #AABB Collision
                if(col_1.rect.contains(col_2.rect)):
                    #TODO: Refuel
                    continue


#Movement System
class MovementSystem(esper.Processor):
    def __init__(self):
        super().__init__()
    def process(self):
        for ent, (vel, pos) in self.world.get_components(Velocity, Position):
            pos.x += vel.x
            pos.y += vel.y
            vel.x = 0
            vel.y = 0

class Bullet:
    None

#Collision System
class BulletSystem(esper.Processor):
    def __init__(self):
        super().__init__()
    def process(self):
        for ent_1, (pos_1, lives, col_1) in self.world.get_components(Player, Collider):
            for ent_2, (pos_2, col_2) in self.world.get_components(Bullet, Collider):
                if ent_1 != ent_2:
                    #TODO: Bullet Collision
                    pass


class Boat:
    None

class Plane:
    None

class EnemySystem(esper.Processor):
    def __init__(self):
        super().__init__()
    def process(self):
        pass
        #TODO: Update Enemies

#class that spawns in objects, draws objects, moves enemies, and contains all objects
class Spawner:
    def __init__(self, max_heli, max_jet, max_boat, max_bomb, max_fuel):
        self.max_heli = max_heli
        self.max_jet = max_jet
        self.max_boat = max_boat
        self.max_bomb = max_bomb
        self.max_fuel = max_fuel
        self.heliCount = 0
        self.jetCount = 0
        self.boatCount = 0
        self.bombCount = 0
        self.fuelCount = 0

class SpawnSystem(esper.Processor):
    def __init__(self):
        super().__init__()
    def process(self):
        for ent, spawn in self.world.get_components(Spawner):
            if spawn.bombCount < spawn.BOMB_CAP: #if bombs have not reached their spawn limit
                bomb = self.world.create_entity(Bomb)
                spawn.bombCount += 1
            if spawn.boatCount < spawn.BOAT_CAP: #if boats have not reached their spawn limit
                boat = self.world.create_entity(Boat)
                spawn.boatCount += 1
            if spawn.fuelCount < spawn.FUEL_CAP:
                fuelstrip = self.world.create_entity(Fuelstrip)
                spawn.fuelCount += 1

""" class Bomb:
    def __init__(self, width = BOMB_WIDTH, height = BOMB_HEIGHT):
        self.width = width
        self.height = height

class BombSystem:
    def __init__(self):
        super().__init__()
    def process(self):
        for ent, (bomb, col_1) in self.world.get_components(Bomb, Collider):
            for ent, (player, col_2) in self.world.get_components(Player, Collider):
                if (col_1.rect.contains(col_2.rect)):
                    print("Collision!") """
    


class Terrain:
    def __init__(self,
        scroll_delay = TERRAIN_SCROLL_DELAY,
        terrain_width = (SCREEN_WIDTH // TILE_WIDTH),
        terrain_height = ((SCREEN_HEIGHT // TILE_HEIGHT) * 2),
        ):
        self.tile_matrix = []
        self.scroll_delay = scroll_delay
        self.terrain_width = terrain_width
        self.terrain_height = terrain_height

        self.scroll_pos = TILE_HEIGHT

        self.initialized = False

class Tiles(Enum):
    WATER = 0
    LAND = 1

class TerrainTile:

    def __init__(self, tile_type):
        self.tile_type = tile_type

class TerrainSystem(esper.Processor):
    def __init__(self,
        carving_center = (SCREEN_WIDTH // TILE_WIDTH // 2),
        generation_steps = 6,
        neighbors_for_murder = 4,
        neighbors_for_rebirth = 3,
        start_alive_prob = 0.35):
        super().__init__()
        self.carving_center = carving_center
        self.generation_steps = generation_steps
        self.neighbors_for_murder = neighbors_for_murder
        self.neighbors_for_rebirth = neighbors_for_rebirth
        self.start_alive_prob = start_alive_prob
        self.current_delay = 0
    def process(self):
        for ent, (terrain) in self.world.get_component(Terrain):
            if not (terrain.initialized):
                #Initialized terrain to HEIGHTxWIDTH water tiles
                for i in range(0, terrain.terrain_height):
                    terrain.tile_matrix.append([])
                    for j in range(0, terrain.terrain_width):
                        terrain.tile_matrix[i].append(TerrainTile(Tiles.WATER))
                #Then actually put it some effort and make it decent
                self.generate_initial_terrain(terrain)
                terrain.initialized = True
            else:
                self.scroll(terrain)

    def generate_initial_terrain(self, terrain):
        for i in range(0, terrain.terrain_height):
            for j in range(0, 3):
                terrain.tile_matrix[i][j].tile_type = Tiles.LAND
            for j in range(terrain.terrain_width -3, terrain.terrain_width):
                terrain.tile_matrix[i][j].tile_type = Tiles.LAND
         
    def carve(self, row, terrain):
        for i in range(-3,4): #carve a six wide path
            terrain.tile_matrix[row][self.carving_center + i].tile_type = Tiles.WATER

        self.carving_center += random.randint(-1,1)
        if(self.carving_center >= (terrain.terrain_width - 4)):
            self.carving_center = terrain.terrain_width - 5
        elif(self.carving_center <= 4):
            self.carving_center = 5

    def scroll(self, terrain):
        self.current_delay += 1
        if(self.current_delay >= terrain.scroll_delay):
            terrain.scroll_pos -= 1
            self.current_delay = 0
        if(terrain.scroll_pos < 0):
            terrain.scroll_pos = terrain.terrain_height - 1

        if(terrain.scroll_pos == ROWS or terrain.scroll_pos == 0):
            self.generate_chunk(terrain, self.generate_noise())

    def generate_chunk(self, terrain, noise_map):
        for i in range(0, len(noise_map)):
            for j in range(0, len(noise_map[i])):
                terrain.tile_matrix[i + ROWS % terrain.terrain_height][j] = noise_map[i][j]
            self.carve(i + ROWS % terrain.terrain_height, terrain)

    def generate_noise(self):
        noise_map = []
        for i in range(0, ROWS):
            noise_map.append([])
        for x in noise_map:
            for i in range(0, COLUMNS):
                x.append(Tiles.WATER)

        noise_map = self.initialize_map(noise_map)

        for i in range(self.generation_steps):
            noise_map = self.sim_step(noise_map)

        return noise_map

    def sim_step(self, old_noise_map):
        new_noise_map = []
        for i in range(0, ROWS):
            new_noise_map.append([])
        for x in new_noise_map:
            for i in range(0, COLUMNS):
                x.append(Tiles.WATER)

        for i in range(0, ROWS):
            for j in range(0, COLUMNS):
                neighbors = self.count_live_neighbors(old_noise_map, i, j)
                if(old_noise_map[i][j] == Tiles.LAND):
                    if(neighbors < self.neighbors_for_murder):
                        new_noise_map[i][j] = Tiles.WATER
                    else:
                        new_noise_map[i][j] = Tiles.LAND
                else:
                    if(neighbors > self.neighbors_for_rebirth):
                        new_noise_map[i][j] = Tiles.LAND
                    else:
                        new_noise_map[i][j] = Tiles.WATER

        return new_noise_map

    def count_live_neighbors(self, noise_map, x, y):
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                neighbor_x = x + i
                neighbor_y = y + j

                if(i == 0 and j == 0): #don't do anything if you are looking at the cell whose neighbors you want to count
                    dummy = 1
                elif(neighbor_x < 0 or neighbor_x >= ROWS): #if cell has no above neighbors or below neighbors count those non-existance neighbors as dead
                    count += 0
                elif(neighbor_y < 0 or neighbor_y >= COLUMNS): #if cell has no right/left neighbors, count them as living
                    count += 1
                elif(noise_map[neighbor_x][neighbor_y] == Tiles.LAND): #if neighbor is alive, increase living neighbor count
                    count += 1

        return count

    def initialize_map(self, noise_map):
        for x in range(0, ROWS):
            for y in range(0, COLUMNS):
                if(random.random() < self.start_alive_prob): #randomly make cell alive
                    noise_map[x][y] = Tiles.LAND
        
        return noise_map

        
""" class SpawnManager:
    #object spawn caps
    HELICOPTER_CAP = 5
    JET_CAP = 5
    BOAT_CAP = 5
    BOMB_CAP = 5
    FUEL_CAP = 1
    
    #object spawn probabilities, will be used later
    HELICOPTER_PROB = 0
    JET_PROB = 0
    BOAT_PROB = 0
    BOMB_PROB = 100
    FUEL_PROB = 0
    
    #current count of objects
    heliCount = 0
    jetCount = 0
    boatCount = 0
    bombCount = 0
    fuelCount = 0
    
    #list of enemies spawned in objects
    objects = []

    #desc: function to update enemy counts after an enemy is despawned
    #pre:
    #post: one of the enemy counts is changed
    def decreaseObjectCount(self, objectType):
        if objectType == "bomb":
            self.bombCount -= 1
        elif objectType == "helicopter":
            self.heliCount -= 1
        elif objectType == "jet":
            self.jetCount -= 1
        elif objectType == "boat":
            self.boatCount -= 1
        elif objectType == "fuel":
            self.fuelCount -= 1

    #desc: decides where, when, how many, and how often objects will be spawn onto the terrain
    #pre: terrain should be a TerrainManager object, spawnManager should be an SpawnManager object
    #post: A new random object is spawned in a random location, object counts are updated, object is appened to self.objects
    def spawnObjects(self, terrain, spawnManager):
        if self.bombCount < self.BOMB_CAP: #if bombs have not reached their spawn limit
            bomb = Bomb()
            self.objects.append(bomb.spawn(terrain, spawnManager))
            self.bombCount += 1
        if self.boatCount < self.BOAT_CAP: #if boats have not reached their spawn limit
            boat = Boat()
            self.objects.append(boat.spawn(terrain, spawnManager))
            self.boatCount += 1
        if self.fuelCount < self.FUEL_CAP:
            fuelstrip = Fuel()
            self.objects.append(fuelstrip.spawn(terrain, spawnManager))
            self.fuelCount += 1

    #desc: checks to see if an object has been hit by a player bullet
    #pre: bullets should be an array of Bullets
    #post: if an enemy is being hit by a bullet it is removed from self.objects via self.despawnObjects
    def detectEnemyBulletCollision(self, bullets):
        for bullet in bullets:
            for o in self.objects:
                if bullet.detectCollision(o): #if bullet is colliding with object
                    self.despawnObject(o)

    #desc: scrolls all enemies at the same pase as the terrain is scrolling 
    #pre: all enemies must have a scroll function
    #post: enemies are scrolled 
    def scrollObjects(self):
        for o in self.objects:
            o.scroll()

    #desc: draws all objects in self.objects
    #pre:
    #post: see desc
    def drawObjects(self):
        for object in self.objects:
            object.draw()

    #desc: moves all objects
    #pre:
    #post: see desc
    def moveObjects(self):
        for object in self.objects:
            move = getattr(object, "move", None) #checks if move method exists
            if move != None and callable(move): #if move is a method and exists
                if object.m_type == "boat":
                    object.move(terrain) #boat moves based on terrain
                else:
                    object.move()

    #desc: removes an object from self.objects
    #pre: object must have member m_type
    #post: object is removed from self.objects
    def despawnObject(self, object):
        for o in self.objects:
            if o == object:
                self.decreaseObjectCount(o.m_type)
                self.objects.remove(o)

    #desc: see name of function 
    #pre:
    #post: see name of function
    def despawnOffScreenObjects(self):
        for o in self.objects:
            if o.rect.top >= SCREEN_HEIGHT:
                self.despawnObject(o)

    #desc: checks to see if another sprite is colliding with an object
    #pre: other must be an object with a rect property
    #post: returns object type if an object is being collided with
    def detectCollision(self, other):
        for o in self.objects:
            if o.detectCollision(other):
                return o.m_type
        return False


class Bomb(pygame.sprite.Sprite):
    m_width = 30
    m_height = 30
    m_type = "bomb"

    #constructor
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, self.m_width, self.m_height)

    #moves the enemy
    def move(self):
        self.rect.y += 0
    
    #returns true if enemy is hitting other sprite 
    def detectCollision(self, other):
        return self.rect.colliderect(other.rect)
        
    #draws enemy
    def draw(self):
        pygame.draw.rect(win, (255,255,255), (self.rect.x, self.rect.y, self.rect.width, self.rect.height))

    #scroll the enemy at the same rate as the terrain
    def scroll(self):
        self.rect.y += TERRAIN_SCROLL_SPEED

    #desc: spawn in the enemy
    #pre: terrain is a TerrainManager object and enemyManager is an EnemyManager object
    #post: 
    def spawn(self, terrain, enemyManager):
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)  #random on screeen point
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height) #random on screen point

        #keep looping through until you find an x/y coordinate that will not spawn the bomb on top of land or on top of another enemy
        while terrain.checkForLandCollisions(self) or enemyManager.detectCollision(self):
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)

        return self


class Bullet(pygame.sprite.Sprite):
    m_width = 14
    m_height = 14

    #constructor
    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 5
        self.rect = pygame.Rect(player.rect.x + ((player.rect.width - self.m_width) // 2), player.rect.y - (self.m_height + 5), self.m_width, self.m_height)

    #move the bullet
    def move(self):
        self.rect.y -= self.speed

    def draw(self):
        pygame.draw.rect(win, (250,250,0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height))

    #true if bottom of sprite is off the screen
    def offScreen(self):
        return (self.rect.bottom <= 0)
        
    #is the bullet hitting something
    def detectCollision(self, enemy):
        return self.rect.colliderect(enemy.rect)


class Boat(pygame.sprite.Sprite):
    m_type = "boat"
    m_width = 50
    m_height = 30
    m_movement = 1 #movement modifier: boat moves right if positive, left if negative

    #constructor
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, self.m_width, self.m_height)
        self.image = pygame.image.load("Boat.png")

    #moves the boat back and forth
    def move(self, terrain):
        if(terrain.checkForLandCollisions(self)):
            self.m_movement = self.m_movement * -1 #change movement direction
            self.turn()
        self.rect.x += self.m_movement

    def scroll(self):
        self.rect.y += TERRAIN_SCROLL_SPEED

    def spawn(self, terrain, enemyManager):
        while terrain.checkForLandCollisions(self) or enemyManager.detectCollision(self):
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        return self

    def draw(self):
        win.blit(self.image, [self.rect.x - 30, self.rect.y - 40])

    def detectCollision(self, enemy):
        return self.rect.colliderect(enemy.rect)

    #flips the image horizontally
    def turn(self):
        self.image = pygame.transform.flip(self.image, True, False)


class FuelStrip(pygame.sprite.Sprite):
    m_type = "fuel"
    m_width = 30
    m_height = 60

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, self.m_width, self.m_height)

    def scroll(self):
        self.rect.y += TERRAIN_SCROLL_SPEED

    def spawn(self, terrain, spawnManager):
        while terrain.checkForLandCollisions(self) or spawnManager.detectCollision(self):
            self.rect.x = random.randint (0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randint( 0, SCREEN_HEIGHT - self.rect.height)
        return self

    def draw(self):
        pygame.draw.rect(win, (250, 0, 255), (self.rect.x, self.rect.y, self.m_width, self.m_height))

    def detectCollision(self, player):
        return self.rect.colliderect(player.rect)


class Player(pygame.sprite.Sprite):
    lives = 3
    fuel = 100
    MAX_FUEL = 100
    FUEL_RATE = 0.5
    DEFUEL_RATE = 0.05
    playerWidth = 30
    playerHeight = 30
    speed = TILE_WIDTH
    img = pygame.image.load(os.path.relpath("Plane1.png"))
    startPosX = (SCREEN_WIDTH * 0.5) - (PLAYER_WIDTH * 0.5) + 10
    startPosY = SCREEN_HEIGHT - PLAYER_HEIGHT
    color = (255,0,0)
    hudFont = pygame.font.SysFont("Times New Roman", 30)

    #constructor
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(self.startPosX, self.startPosY, self.playerWidth, self.playerHeight)
        
    def draw(self):
        #print("Drawing Player at " + str(self.x) + ", " + str(self.y))
        pygame.draw.rect(win, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height))
        text = self.hudFont.render(str(int(self.fuel)), False, (255, 0, 0))
        win.blit(text, (0, 0))
        #win.blit(self.img, (self.rect.x, self.rect.y))

    def kill(self):
        self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,255)) #just change color for now

    def shoot(self):
        return Bullet(self)

    def refuel(self):
        if self.fuel + self.FUEL_RATE <= self.MAX_FUEL:
            self.fuel += self.FUEL_RATE #refuel player at fuel_rate
        else:
            self.fuel += self.MAX_FUEL - self.fuel #top off player

    def defuel(self):
        if self.fuel - self.DEFUEL_RATE > 0:
            self.fuel -= self.DEFUEL_RATE #deduct the defuel rate
        else:
            player.kill() #Kill player since plane is out of fuel

    def moveLeft(self):
        if (self.rect.x - self.speed) >= 0: #keep player from going off screen
            self.rect.x -= self.speed
        
    def moveRight(self):
        if (self.rect.x + self.speed) <= (SCREEN_WIDTH - self.playerWidth): #keep player on screen
            self.rect.x += self.speed
        
    def moveForward(self):
        if self.rect.y - self.speed >= 0: #keep player on screen
            self.rect.y -= self.speed
        
    def moveBack(self):
        if (self.rect.y + self.speed) <= (SCREEN_HEIGHT - self.playerHeight): #keep player on screen
            self.rect.y += self.speed

"""

world = esper.World()

player = world.create_entity(
    Position(14, 27),
    Player(3, 100, 100, 0.5, 0.05),
    Velocity(0,0),
    Renderable(pygame.image.load("./plane.png")),
    Collider()
)

terrain = world.create_entity(
    Terrain()
)

render_system = RenderSystem(win, BACKGROUND_COLOR)
collider_system = ColliderSystem()
movement_system = MovementSystem()
terrain_system = TerrainSystem()

world.add_processor(render_system)
world.add_processor(collider_system, 1)
world.add_processor(movement_system, 2)
world.add_processor(terrain_system, 3)

run = True
clock = pygame.time.Clock()


#Main Game Loop
while run:

    #================================= LISTEN FOR EVENTS ========================================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pass
                #TODO: Fire Bullet
            if event.key == pygame.K_LEFT:
                world.component_for_entity(player, Velocity).x = -PLAYER_SPEED
            if event.key == pygame.K_RIGHT:
                world.component_for_entity(player, Velocity).x = PLAYER_SPEED
            if event.key == pygame.K_UP:
                world.component_for_entity(player, Velocity).y = -PLAYER_SPEED
            if event.key == pygame.K_DOWN:
                world.component_for_entity(player, Velocity).y = PLAYER_SPEED
    world.process()
    clock.tick(MAX_FPS)

pygame.quit()

