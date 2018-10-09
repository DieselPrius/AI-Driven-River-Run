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
#Width in pixels of each tile
TILE_WIDTH = 30
TILE_HEIGHT = 30
#Number of tiles in a column.
ROWS = SCREEN_HEIGHT // TILE_HEIGHT
#Number of tiles in a row.
COLUMNS = SCREEN_WIDTH // TILE_WIDTH
#Player speed, in tiles per action.
PLAYER_SPEED = 1
#Maximum frames to process per second.
MAX_FPS = 60
#Background color to render for empty space.
BACKGROUND_COLOR = (0, 0, 0)
#Bomb width, in pixels.
BOMB_WIDTH = 30
#Bomb height, in pixels.
BOMB_HEIGHT = 30
#Frames to wait between scrolls, in frames
TERRAIN_SCROLL_DELAY = 30
PLAYER_START_POS_X = 14
PLAYER_START_POS_Y = 29

BOAT_WIDTH = 3
BOAT_HEIGHT = 2
BOAT_START_VELOCITY_X = 1
BOAT_START_VELOCITY_Y = 0


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
    def __init__(self, lives=3, fuel=100, max=100, fuel_rate=0.5, defuel_rate=0.05):
        self.lives = lives
        self.fuel = fuel
        self.max = max
        self.fuel_rate = fuel_rate
        self.defuel_rate = defuel_rate

    def kill(self):
        self.lives -= 1
        if(self.lives == 0):
            print("GAME OVER") #load title screen etc
        world.get_processor(TerrainSystem).clearTerrain() #clear terrain
        for ent,_ in world.get_component(Position): #clear all enemy entities
            if(ent != player): #dont delete player
                world.delete_entity(ent,True) #clear all enemy entities
        world.get_processor(TerrainSystem).generate_initial_terrain(world.component_for_entity(terrain,Terrain)) #re-intialize terrain
        world.component_for_entity(player,Position).x = PLAYER_START_POS_X #change player position
        world.component_for_entity(player,Position).y = PLAYER_START_POS_Y #change player position


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
        for _, terrain in self.world.get_component(Terrain):
            #By Column
            for x in range(0, terrain.terrain_width):
                #By Row
                row = 0
                for y in range( (terrain.scroll_pos - (terrain.terrain_height // 2)) , terrain.scroll_pos):
                    #print("y -----------------------------> " + str((terrain.scroll_pos - (terrain.terrain_height // 2))) + ", " + str(terrain.scroll_pos))
                    if(terrain.tile_matrix[x][y].tile_type == Tiles.LAND):
                        #Land is GREEN
                        pygame.draw.rect(self.window,
                                        (0,255,0),
                                        (x * TILE_WIDTH,
                                        row * TILE_HEIGHT,
                                        TILE_WIDTH,
                                        TILE_HEIGHT))
                    elif(terrain.tile_matrix[x][y].tile_type == Tiles.WATER):
                        #Water is WET, err I mean BLUE
                        pygame.draw.rect(self.window,
                                        (0,0,255),
                                        (x * TILE_WIDTH,
                                         row * TILE_HEIGHT,
                                        TILE_WIDTH,
                                        TILE_HEIGHT))
                    row += 1

        #Render the Entities . . .
        for ent, (pos, render) in self.world.get_components(Position, Renderable):
            self.window.blit(render.sprite, (pos.x * TILE_WIDTH, pos.y * TILE_HEIGHT))
        pygame.display.flip()


#Collision Component
class Collider:
    #width and height are in tiles, not pixels
    def __init__(self, width=1, height=1):
        self.width = width * TILE_WIDTH
        self.height = height * TILE_HEIGHT
        #self.collider_class = collider_class

    # player_collider = world.component_for_entity(player, Collider).colliderToRect(player_pos)
    def colliderToRect(self, posComp):
        return pygame.Rect(posComp.x * TILE_WIDTH, posComp.y * TILE_HEIGHT, self.width, self.height)



class ColliderSystem(esper.Processor):
    def __init__(self):
        super().__init__()

    def process(self):
        #check for player-land collisions
        if( self.checkForLandCollision(world.component_for_entity(player, Position), world.component_for_entity(player, Collider)) ):
            print("player hit land")
            self.world.component_for_entity(player,Player).kill()

        #check for player-enemy collisions
        if(self.checkPlayerEnemyCollisions()):
            print("player hit enemy")
            self.world.component_for_entity(player,Player).kill()

    #returns true if the player hits land, otherwise false
    def checkPlayerEnemyCollisions(self):
        collisionDetected = False
        player_pos        = self.world.component_for_entity(player,Position)
        player_collider   = self.world.component_for_entity(player,Collider)
        for ent, (_, pos, col) in self.world.get_components(Enemy, Position, Collider):      
            if(self.checkCollision(player_pos, player_collider, pos, col)):
                collisionDetected = True
                break
        return collisionDetected     

    #returns true if entity one is colliding with entity two
    def checkCollision(self, entOnePos, entOneCollider, entTwoPos, entTwoCollider):
        entOneRect = entOneCollider.colliderToRect(entOnePos)
        entTwoRect = entTwoCollider.colliderToRect(entTwoPos)
        #pygame.draw.rect(win,(0,0,0),entTwoRect)
        #pygame.display.flip()
        return entOneRect.colliderect(entTwoRect)


    #checks for ON-SCREEN COLLISIONS only
    def checkForLandCollision(self,positionComponent, colliderComponent):
        landTileRects = []
        #create a collider for all on-screen land tiles ...
        for _, terrain in world.get_component(Terrain):
            for x in range(terrain.terrain_width): #for each column
                row = 0 #row is the on-screen row number
                #for each row that is currently on the screen ...
                for y in range((terrain.scroll_pos - (terrain.terrain_height // 2)) , terrain.scroll_pos):
                    if(terrain.tile_matrix[x][y].tile_type == Tiles.LAND): #if tile is land create a Rect for it
                        landTileRects.append(pygame.Rect(x*TILE_WIDTH, row*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT))
                    row += 1

        #create a pygame Rect out the two components
        other = colliderComponent.colliderToRect(positionComponent)

        collisionDetected = False
        for landTile in landTileRects: #for each land tile rect
            if landTile.colliderect(other): #check if the 'other' collider is hitting a land tile
                collisionDetected = True
                break
        
        return collisionDetected
    
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
        self.movementDelay = TERRAIN_SCROLL_DELAY
        self.currentDelay = 0

    def process(self):
        self.currentDelay += 1
        if(self.currentDelay >= self.movementDelay): #move everything every movementDelay number of frames
            self.currentDelay = 0
            self.movePlayer()
            self.moveBoats()
            #TODO: WRITE OTHER ENEMY MOVEMENT FUNCTIONS
            #self.moveJets()
            #self.moveHelit()
            #etc.
            
    def movePlayer(self):
        for ent, (p, vel, pos) in self.world.get_components(Player, Velocity, Position):
            pos.x += vel.x
            pos.y += vel.y
            vel.x = 0
            vel.y = 0

    def moveBoats(self):
        for ent, (boat, vel, pos, col, rend) in self.world.get_components(Boat, Velocity, Position, Collider, Renderable):
            if(pos.y >= 0): #don't move boats left/right until they are on screen
                if(self.world.get_processor(ColliderSystem).checkForLandCollision(Position(pos.x + vel.x,pos.y),col)): #if boat will hit land at its next location
                    vel.x = -vel.x #change direction
                    rend.sprite = pygame.transform.flip(rend.sprite, True, False) #flip image
                pos.x += vel.x #change position based on velocity

class Bullet:
    None

class Enemy:
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
    def __init__(self):
        self.enemy_type_count = 7
        self.initial_spawn_attempts = 5
        self.chunks_required_to_increase_spawn_attempts = 2 #spawn attempts will after this many new chunks have been generated
        self.chunk_generation_count = 0 #how many times a new chunck has been generated
        self.spawn_attempts = 5

#TODO: Implement this system.
#This system is currently not added to the world, and thus is never processed.
class SpawnSystem(esper.Processor):
    def __init__(self):
        super().__init__()
    def process(self):
        None

    def spawnEnemies(self):
        the_spawner = self.world.component_for_entity(spawner,Spawner)
        the_spawner.chunk_generation_count += 1
        the_spawner.spawn_attempts = (the_spawner.chunk_generation_count // the_spawner.chunks_required_to_increase_spawn_attempts) + the_spawner.initial_spawn_attempts

        for i in range(the_spawner.spawn_attempts):
            the_terrain = self.world.component_for_entity(terrain,Terrain)
            randomX = random.randint(0, the_terrain.terrain_width)
            randomY = random.randint(-(the_terrain.terrain_height // 2), -1)

            randomNumber = random.randint(1,the_spawner.enemy_type_count)

            if(randomNumber == 1):
                self.spawnBoat(randomX, randomY)
            elif(randomNumber == 2):
                self.spawnHeli(randomX, randomY)
            elif(randomNumber == 3):
                self.spawnJet(randomX, randomY)
            elif(randomNumber == 4):
                self.spawnBomb(randomX, randomY)
            elif(randomNumber == 5):
                self.spawnEnhancedHeli(randomX, randomY)
            elif(randomNumber == 6):
                self.spawnEnhancedJet(randomX, randomY)
            elif(randomNumber == 7):
                self.spawnTurretBoat(randomX, randomY)


    def spawnBoat(self, xpos, ypos):
        #if boat will not spawn on land at this rand x,y position
        if(not self.CheckForNewChunkLandCollision(Position(xpos,ypos),Collider(BOAT_WIDTH,BOAT_HEIGHT))):
            world.create_entity(
                Enemy(), #all enemies must have this component for enemy-player collisions to work
                Boat(), #usefull for the moveBoat function
                Position(xpos, ypos),
                Velocity(BOAT_START_VELOCITY_X,BOAT_START_VELOCITY_Y),
                Renderable(pygame.image.load("./Boat2.png")),
                Collider(BOAT_WIDTH,BOAT_HEIGHT)
            )

    def spawnHeli(self, xpos, ypos):
        print("spawnHeli()")

    def spawnJet(self, xpos, ypos):
        print("spawnJet()")

    def spawnBomb(self, xpos, ypos):
        print("spawnBomb()")
    
    def spawnEnhancedHeli(self, xpos, ypos):
        print("spawnEnhancedHeli()")

    def spawnEnhancedJet(self, xpos, ypos):
        print("spawnEnhancedJet()")

    def spawnTurretBoat(self, xpos, ypos):
        print("spawnTurretBoat()")

    def spawnFuelStrips(self):
        print("spawnFuelStrips()")

    #returns true if the an entity will spawn in on land, this checks for OFF-SCREEN LAND COLLISIONS
    def CheckForNewChunkLandCollision(self, positionComponent, colliderComponent):
        landTileRects = []
        #create a collider for all land tiles in the newly created chunck ...
        for _, terrain in world.get_component(Terrain):
            for x in range(terrain.terrain_width): #for each column
                for y in range(0, terrain.terrain_height // 2): #for each row in the new chunck
                    if(terrain.tile_matrix[x][y].tile_type == Tiles.LAND): #if tile is land create a Rect for it
                        landTileRects.append(pygame.Rect(x*TILE_WIDTH, (y-(terrain.terrain_height // 2))*TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT))
        other = colliderComponent.colliderToRect(positionComponent)
        collisionDetected = False
        for landTile in landTileRects: #for each land tile rect
            if landTile.colliderect(other): #check if the 'other' collider is hitting a land tile
                collisionDetected = True
                break
        return collisionDetected

    

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
        #Frames per scroll
        self.scroll_delay = scroll_delay
        #Width in tiles
        self.terrain_width = terrain_width
        #Height in tiles
        self.terrain_height = terrain_height

        self.scroll_pos = terrain_height - 1

        self.initialized = False


#Enum for terrain tile types
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
        #Cellular Automata Parameters
        self.carving_center = carving_center
        self.generation_steps = generation_steps
        self.neighbors_for_murder = neighbors_for_murder
        self.neighbors_for_rebirth = neighbors_for_rebirth
        self.start_alive_prob = start_alive_prob
        #Frames since last scroll
        self.current_delay = 0

    def process(self):
        for _, (terrain) in self.world.get_component(Terrain):
            if not (terrain.initialized):
                #Initialized terrain to WIDTHxHEIGHT water tiles
                for i in range(0, terrain.terrain_width):
                    terrain.tile_matrix.append([])
                    for j in range(0, terrain.terrain_height):
                        terrain.tile_matrix[i].append(TerrainTile(Tiles.WATER))
                #Then actually put it some effort and make it decent
                self.generate_initial_terrain(terrain)
                terrain.initialized = True
            else:
                self.scroll(terrain)


    #Populates terrain with land on sides of screen
    def generate_initial_terrain(self, terrain):
        for y in range(terrain.terrain_height //2 ,terrain.terrain_height):
            for x in range(0, 3):
                terrain.tile_matrix[x][y].tile_type = Tiles.LAND
            for x in range(terrain.terrain_width -3, terrain.terrain_width):
                terrain.tile_matrix[x][y].tile_type = Tiles.LAND
        self.generate_chunk(terrain,self.generate_noise())
        
    

    def clearTerrain(self):
        for _, (terrain) in self.world.get_component(Terrain):
            for x in range(COLUMNS):
                for y in range(terrain.terrain_height):
                    terrain.tile_matrix[x][y].tile_type = Tiles.WATER
            terrain.scroll_pos = terrain.terrain_height - 1

            

    #TODO: Fix
    #Should create a six tile wide path near the center of the screen, allowing the player to always
    #Have somewhere to be
    def carve(self, row, terrain):
        for i in range(-3,4): #carve a six wide path
            terrain.tile_matrix[self.carving_center + i][row].tile_type = Tiles.WATER

        self.carving_center += random.randint(-1,1)
        if(self.carving_center >= (terrain.terrain_width - 4)):
            self.carving_center = terrain.terrain_width - 5
        elif(self.carving_center <= 4):
            self.carving_center = 5

    #Scrolls and regenerates the terrain every ROWS rows
    def scroll(self, terrain):
        self.current_delay += 1
        if(self.current_delay >= terrain.scroll_delay):
            #print(terrain.scroll_pos)
            terrain.scroll_pos -= 1
            self.current_delay = 0
            for _, (pos) in self.world.get_component(Position):
                pos.y += 1
            player_pos = self.world.component_for_entity(player,Position)
            player_pos.y -= 1

        if(terrain.scroll_pos == ((terrain.terrain_height // 2) - 1)):
            #print("scroll_pos = " + str(terrain.scroll_pos) + "   ((terrain.terrain_height // 2) - 1) = " + str(((terrain.terrain_height // 2) - 1)))
            #copy upper terrain down
            for x in range(terrain.terrain_width):
                for y in range(terrain.terrain_height // 2): #0 to 29
                    terrain.tile_matrix[x][y + (terrain.terrain_height // 2)].tile_type = terrain.tile_matrix[x][y].tile_type
            
            #load new chunck into upper terrain
            self.generate_chunk(terrain, self.generate_noise())
            #update scroll position
            terrain.scroll_pos = terrain.terrain_height - 1


    #Populates the chunk using the generated noise map
    def generate_chunk(self, terrain, noise_map):
        for x in range(0,terrain.terrain_height // 2): #0 to 29
            for y in range(0,terrain.terrain_width): #0 to 29
                terrain.tile_matrix[x][y].tile_type = noise_map[y][x]
        for y in range((terrain.terrain_height // 2) - 1, -1, -1): #29 to 0 
                self.carve(y,terrain)
   
        #spawn in enemies in the new chunk
        self.world.get_processor(SpawnSystem).spawnEnemies()

    #Initializes the noise map lists and then simulates the automata
    def generate_noise(self):
        noise_map = []
        for i in range(0, COLUMNS):
            noise_map.append([])
        for x in noise_map:
            for y in range(0, ROWS):
                x.append(Tiles.WATER)

        noise_map = self.initialize_map(noise_map)

        for i in range(self.generation_steps):
            noise_map = self.sim_step(noise_map)

        return noise_map

    #Steps through the simulation, counting, killing, and rebirthing neighboring cells
    #for every cell in the noise map.
    def sim_step(self, old_noise_map):
        new_noise_map = []
        for _ in range(0, COLUMNS):
            new_noise_map.append([])
        for x in new_noise_map:
            for y in range(0, ROWS):
                x.append(Tiles.WATER)

        for x in range(0, COLUMNS):
            for y in range(0, ROWS):
                neighbors = self.count_live_neighbors(old_noise_map, x, y)
                if(old_noise_map[x][y] == Tiles.LAND):
                    if(neighbors < self.neighbors_for_murder):
                        new_noise_map[x][y] = Tiles.WATER
                    else:
                        new_noise_map[x][y] = Tiles.LAND
                else:
                    if(neighbors > self.neighbors_for_rebirth):
                        new_noise_map[x][y] = Tiles.LAND
                    else:
                        new_noise_map[x][y] = Tiles.WATER

        return new_noise_map

    #TODO: Check to see if actual behavior matches intended behavior.
    #Simply counts the number of nearby cells that are alive.
    #Counts cells over the edge as alive, leading to more land on the sides.
    def count_live_neighbors(self, noise_map, x, y):
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                neighbor_x = x + i
                neighbor_y = y + j

                if(i == 0 and j == 0): #don't do anything if you are looking at the cell whose neighbors you want to count
                    pass
                elif(neighbor_x < 0 or neighbor_x >= COLUMNS): #if cell has no above neighbors or below neighbors count those non-existance neighbors as dead
                    count += 0
                elif(neighbor_y < 0 or neighbor_y >= ROWS): #if cell has no right/left neighbors, count them as living
                    count += 1
                elif(noise_map[neighbor_x][neighbor_y] == Tiles.LAND): #if neighbor is alive, increase living neighbor count
                    count += 1

        return count

    #Randomly decides if each cell starts as alive or dead
    def initialize_map(self, noise_map):
        for x in range(0, COLUMNS):
            for y in range(0, ROWS):
                if(random.random() < self.start_alive_prob):
                    noise_map[x][y] = Tiles.LAND
        
        return noise_map

#TODO: Refactor enemies to use new tile system. Also refactor into components and systems.
#TODOCONT: Logic goes in systems, state in components.


world = esper.World()

#Create the player entity. Has a position, velocity, collider, it can be rendered,
#and it has special player logic and state.
player = world.create_entity(
    Position(14, 27),
    Player(3, 100, 100, 0.5, 0.05),
    Velocity(0,0),
    Renderable(pygame.image.load("./plane.png")),
    Collider(1,1)
)

#manually spawn a boat for testing
world.create_entity(
    Enemy(),
    Boat(),
    Position(3,5),
    Velocity(1,0),
    Renderable(pygame.image.load("./Boat2.png")),
    Collider(3,2)
)


#Create the terrain entity. Simply has Terrain component.
terrain = world.create_entity(
    Terrain()
)

spawner = world.create_entity(
    Spawner()
)

#Creates the systems. The render system requires as inputs the pygame Surface
#(window) that it is rendering to, and a background color to display where nothing else
#is rendered.
render_system = RenderSystem(win, BACKGROUND_COLOR)
collider_system = ColliderSystem()
movement_system = MovementSystem()
terrain_system = TerrainSystem()
spawn_system = SpawnSystem()

#Adds the systems to the world. The priority argument is optional, higher values are
#higher priority. Defaults to 0.
world.add_processor(render_system)
world.add_processor(collider_system, 1)
world.add_processor(movement_system, 2)
world.add_processor(spawn_system, 3)
world.add_processor(terrain_system, 4)



#Is the game running?
run = True
#The clock object tracks time.
clock = pygame.time.Clock()


#Main Game Loop
while run:

    #================================= LISTEN FOR EVENTS ========================================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            #We're no longer running. Closes the game at the end of the current frame.
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pass
                #TODO: Fire Bullet
            if event.key == pygame.K_LEFT:
                #Move the player left.
                if(world.component_for_entity(player,Position).x - 1 >= 0):
                    world.component_for_entity(player, Velocity).x = -PLAYER_SPEED
            if event.key == pygame.K_RIGHT:
                #Move the player right.
                if(world.component_for_entity(player,Position).x + 1 <= (COLUMNS - 1)):
                    world.component_for_entity(player, Velocity).x = PLAYER_SPEED
            if event.key == pygame.K_UP:
                #Move the player up.
                if(world.component_for_entity(player,Position).y - 1 >= 0):
                    world.component_for_entity(player, Velocity).y = -PLAYER_SPEED
            if event.key == pygame.K_DOWN:
                #Move the player down.
                if(world.component_for_entity(player,Position).y + 1 <  ROWS):
                    world.component_for_entity(player, Velocity).y = PLAYER_SPEED
    world.process()
    #Pauses the thread if the frame was quick to process, effectively limiting the framerate.
    clock.tick(MAX_FPS)

#If we're no longer running, quit() pygame to free its resources.
pygame.quit()

