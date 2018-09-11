import pygame
import os
import random
import esper

pygame.init()

#GLOBAL CONSTANTS
#TODO: Configuration file, maybe?
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
TILE_WIDTH = 30
TILE_HEIGHT = 30
TERRAIN_SCROLL_SPEED = 1
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 30
PLAYER_SPEED = 3
FPS = 60
BACKGROUND_COLOR = (55, 55, 255)

win = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("River Run AI")





#Position Component
class Position:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

#Velocity Component
class Velocity:
    def __init__(self, x=0.0, y=0.0):
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
        for ent, (pos, render) in self.world.get_components(Position, Renderable):
            self.window.blit(render.sprite, (pos.x - render.width / 2, pos.y - render.height / 2))
        pygame.display.flip()

#Collision Component
class Collider:
    def __init__(self, rect):
        self.rect = rect

class ColliderSystem(esper.Processor):
    def __init__(self):
        super().__init__()
    def process(self):
        for ent, (pos, col) in self.world.get_components(Position, Collider):
            col.rect.center(pos.x, pos.y)

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
            for ent_2, (play, fuel, col_2) in self.world.get_components(Player, Fuel, Collider):
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
                    if col_1.rect.contains(col_2.rect):
                        #TODO: Handle Collision
                        continue


class Boat:
    None

class Plane:
    None

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

class Terrain:
    def __init__(self, scroll_speed = TERRAIN_SCROLL_SPEED, terrain_tile_width = SCREEN_WIDTH):
        self.tileMatrix = []
        self.terrain_tile_width = terrain_tile_width
        self.initialized = False

class TerrainTile:

    def __init__(self, x, y, color, width, is_land):
        self.rect = pygame.Rect(x, y, width, width)
        self.color = color
        self.width = width
        self.is_land = is_land

class TerrainSystem(esper.Processor):
    def __init__(self):
        super().__init__()
    def process(self):
        for ent, (terrain) in self.world.get_component(Terrain):
            if not (terrain.initialized):
                for i in range(0, terrain.terrain_tile_width + 1):
                    terrain.tileMatrix.append([])
                self.generate_initial_terrain(terrain)

    def generate_initial_terrain(self, terrain):
        x = 0
        y = SCREEN_HEIGHT - TILE_HEIGHT
        row = 0

        #build terrain from bottom up with one extra row off screen
        for i in range(terrain.terrain_tile_width**2 + terrain.terrain_tile_width):
            if x < (3 * TILE_WIDTH) or x > (SCREEN_WIDTH - (4 * TILE_WIDTH)): #3 tiles of land on each side
                terrain.tileMatrix[row].append(TerrainTile(x, y, (0,random.randint(200,255),0), TILE_WIDTH, True))
            else:
                terrain.tileMatrix[row].append(TerrainTile(x, y, (0,0,random.randint(200,255)), TILE_WIDTH, False))

            x += TILE_WIDTH
            if x == SCREEN_WIDTH:
                row += 1
                x = 0
                y -= TILE_HEIGHT

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





#class that generates the terrain
class TerrainManager:
    tileMatrix = []
    scrollSpeed = TERRAIN_SCROLL_SPEED
    terrainTILE_WIDTH = SCREEN_WIDTH // TILE_WIDTH #width of terrain in tiles

    def __init__(self):
        for i in range(0,self.terrainTILE_WIDTH + 1):
            self.tileMatrix.append([])
        self.generateIntialTerrain()


    def generateIntialTerrain(self):
        x = 0
        y = SCREEN_HEIGHT - TILE_HEIGHT
        row = 0

        #build terrain from bottom up with one extra row off screen
        for i in range(self.terrainTILE_WIDTH**2 + self.terrainTILE_WIDTH):
            if x < (3 * TILE_WIDTH) or x > (SCREEN_WIDTH - (4 * TILE_WIDTH)): #3 tiles of land on each side
                self.tileMatrix[row].append(TerrainTile(x, y, (0,random.randint(200,255),0), TILE_WIDTH, True))
            else:
                self.tileMatrix[row].append(TerrainTile(x, y, (0,0,random.randint(200,255)), TILE_WIDTH, False))

            x += TILE_WIDTH
            if x == SCREEN_WIDTH:
                row += 1
                x = 0
                y -= TILE_HEIGHT

    #draws all tiles
    def draw(self):
        for i in range(0,len(self.tileMatrix)):
            for j in range(0,len(self.tileMatrix[i])):
                self.tileMatrix[i][j].draw()

    #scrolls the terrain down the screen
    def scroll(self):
        for i in range(0,len(self.tileMatrix)):
            for j in range(0,len(self.tileMatrix[i])):
                self.tileMatrix[i][j].setY(self.tileMatrix[i][j].getY() + self.scrollSpeed) #increase y pos of each tile by scrollSpeed

        if self.tileMatrix[-1][0].rect.top > 0: #if the top of the last terrain row enters the screen a new chunk must be generated
            self.generateChunk()

        if self.tileMatrix[0][0].rect.top >= SCREEN_HEIGHT: #delete terrain rows that are no longer on the screen
            self.tileMatrix.pop(0)


    #generates a chunk of terrain
    def generateChunk(self):
        for i in range(10):
            self.generateRow()

    #generates a random terrain row
    def generateRow(self):
        tempList = []
        numOfSideLandBlocks = random.randint(1,3)
        islandWidth = random.randint(0,3)

        for i in range(0, SCREEN_WIDTH // TILE_WIDTH):
            if i < numOfSideLandBlocks: #generate left side land mass 
                tempList.append(TerrainTile(i*TILE_WIDTH, self.tileMatrix[-1][0].rect.y - TILE_HEIGHT, (0,random.randint(200,255),0), TILE_WIDTH, True))
            elif (i >= ((SCREEN_WIDTH//TILE_WIDTH) - numOfSideLandBlocks)): #generate right side land mass
                tempList.append(TerrainTile(i*TILE_WIDTH, self.tileMatrix[-1][0].rect.y - TILE_HEIGHT, (0,random.randint(200,255),0), TILE_WIDTH, True))
            elif islandWidth > 0 and i >= ((SCREEN_WIDTH // TILE_WIDTH)//2) - islandWidth and i <= ((SCREEN_WIDTH // TILE_WIDTH)//2) + islandWidth: #generate middle land mass
                tempList.append(TerrainTile(i*TILE_WIDTH, self.tileMatrix[-1][0].rect.y - TILE_HEIGHT, (0,random.randint(200,255),0), TILE_WIDTH, True))
            else: #generate water
                tempList.append(TerrainTile(i*TILE_WIDTH, self.tileMatrix[-1][0].rect.y - TILE_HEIGHT, (0,0,random.randint(200,255)), TILE_WIDTH, False))
            
        self.tileMatrix.append(tempList)


    
    #desc: checks to see if another object is colliding with land
    #pre: other must have a rect property
    #post: returns true if "other" sprite is colliding with land
    def checkForLandCollisions(self, other):
        collisionDetected = False
        for r in range(len(self.tileMatrix)):
            for c in range(len(self.tileMatrix[r])):
                if self.tileMatrix[r][c].isLand and self.tileMatrix[r][c].rect.colliderect(other.rect): #for each tile, if tile is land and is colliding with other
                    collisionDetected = True
                    break
        
        return collisionDetected


#put all your draw calls here
def DrawEverything():
    terrain.draw()
    player.draw()
    spawnManager.drawObjects()
    for bullet in bullets:
        bullet.draw()
    pygame.display.update() """
    

clock = pygame.time.Clock()
world = esper.World()
player = world.create_entity(
    Position(((SCREEN_WIDTH * 0.5) - (PLAYER_WIDTH * 0.5) + 10), (SCREEN_HEIGHT - PLAYER_HEIGHT)),
    Player(3, 100, 100, 0.5, 0.05),
    Velocity(0,0),
    Renderable(pygame.image.load("plane2.png"))
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

#Main Game Loop
while run:
    

    #================================= LISTEN FOR EVENTS ========================================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                world.create_entity(
                    Bullet(),
                    Position(
                        world.component_for_entity(player, Position)
                    )
                )
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        world.component_for_entity(player, Velocity).x = -PLAYER_SPEED
    if keys[pygame.K_RIGHT]:
        world.component_for_entity(player, Velocity).x = PLAYER_SPEED
    if keys[pygame.K_UP]:
        world.component_for_entity(player, Velocity).y = -PLAYER_SPEED
    if keys[pygame.K_DOWN]:
        world.component_for_entity(player, Velocity).y = PLAYER_SPEED

    world.process()
    clock.tick(FPS)
    #==========================================================================================================


    # #================================= SPAWN OBJECTS =========================================================
    # spawnManager.spawnObjects(terrain, spawnManager)
    # #=========================================================================================================


    # #================================== TELL EVERYTHING THAT NEEDS TO MOVE TO MOVE HERE =======================
    # terrain.scroll()
    # spawnManager.scrollObjects()
    # for bullet in bullets:
    #     bullet.move()
    # spawnManager.moveObjects()

    # #==========================================================================================================


    # #================================== DESPAWN OFF SCREEN ENTITIES ===========================================
    # for bullet in bullets:
    #     if bullet.offScreen():
    #         bullets.remove(bullet)
    # spawnManager.despawnOffScreenObjects()

    # #==========================================================================================================


    # #================================== DETECT COLLISIONS =====================================================
    # if terrain.checkForLandCollisions(player):  #if the player hits land
    #     player.kill()
    # objtype = spawnManager.detectCollision(player) #returns object.m_type the player collided with
    # if objtype == "fuel": #Player collided with fuel strip
    #     player.refuel()
    # elif objtype != False: #Everything else other than the fuel strip currently kills player
    #     player.kill()

    # spawnManager.detectEnemyBulletCollision(bullets)
    
    # #==========================================================================================================

    # #================================= DEFUEL PLANE ===========================================================
    # player.defuel()

    #DrawEverything() #redraws everything to the screen


pygame.quit()

