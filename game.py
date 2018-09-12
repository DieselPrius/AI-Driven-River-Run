import pygame
import os
import random
pygame.init()

#GLOBAL CONSTANTS
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 900
TILE_WIDTH = 30
TILE_HEIGHT = 30
TERRAIN_SCROLL_SPEED = 1

win = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption("River Run AI")




#class that spawns in objects, draws objects, moves enemies, and contains all objects
class SpawnManager:
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
        if self.jetCount < self.JET_CAP: #if jets have not reached their spawn limit
            jet = Jet()
            self.objects.append(jet.spawn(terrain, spawnManager))
            self.jetCount += 1
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
                elif object.m_type == "jet":
                    object.move(terrain) #jet moves based on terrain
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

    #desc: Despawns objects when they move off the screen vertically or horizontally. 
    #pre:
    #post: see name of function
    def despawnOffScreenObjects(self):
        for o in self.objects:
            if o.rect.top >= SCREEN_HEIGHT or o.rect.right >= SCREEN_WIDTH or o.rect.left < -30:
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




class Fuel(pygame.sprite.Sprite):
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




class Jet(pygame.sprite.Sprite):
    m_type = "jet"
    m_width = 30
    m_height = 30
    image = pygame.image.load(os.path.relpath("Jet.png"))

    #constructor
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 2
        self.rect = pygame.Rect(0, 0, self.m_width, self.m_height)

    #moves the jet down towards the bottom of the screen
    def move(self, terrain):
        self.rect.y += self.speed

    def scroll(self):
        self.rect.y += TERRAIN_SCROLL_SPEED

    def spawn(self, terrain, enemyManager):
        while terrain.checkForLandCollisions(self) or enemyManager.detectCollision(self):
            self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
            self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        return self

    def draw(self):
        win.blit(self.image, [self.rect.x - 30, self.rect.y - 30])
        
    def detectCollision(self, enemy):
        return self.rect.colliderect(enemy.rect)

    def offScreen(self):
        return (self.rect.bottom > SCREEN_HEIGHT)




class Player(pygame.sprite.Sprite):
    lives = 3
    fuel = 100
    MAX_FUEL = 100
    FUEL_RATE = 0.5
    DEFUEL_RATE = 0.05
    playerWidth = 30
    playerHeight = 30
    speed = 3
    img = pygame.image.load(os.path.relpath("Plane1.png"))
    startPosX = (SCREEN_WIDTH * 0.5) - (playerWidth * 0.5) + 10
    startPosY = SCREEN_HEIGHT - playerHeight
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





class TerrainTile(pygame.sprite.Sprite):

    def __init__(self, x, y, color, width, isLand):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(x, y, width, width)
        self.color = color
        self.width = width
        self.isLand = isLand #true if terrain tile is land

    def draw(self):
        pygame.draw.rect(win, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.width))

    def setY(self, y):
        self.rect.y = y

    def getY(self):
        return self.rect.y




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
    pygame.display.update()
    


  
player = Player()
terrain = TerrainManager()
spawnManager = SpawnManager()
run = True
bullets = [] #a list for all bullets on screen

#the main game loop
while run:
    

    #================================= LISTEN FOR EVENTS ========================================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False 
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullets.append(player.shoot()) 
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.moveLeft()
    if keys[pygame.K_RIGHT]:
        player.moveRight()
    if keys[pygame.K_UP]:
        player.moveForward()
    if keys[pygame.K_DOWN]:
        player.moveBack()

    #==========================================================================================================


    #================================= SPAWN OBJECTS =========================================================
    spawnManager.spawnObjects(terrain, spawnManager)
    #=========================================================================================================


    #================================== TELL EVERYTHING THAT NEEDS TO MOVE TO MOVE HERE =======================
    terrain.scroll()
    spawnManager.scrollObjects()
    for bullet in bullets:
        bullet.move()
    spawnManager.moveObjects()

    #==========================================================================================================


    #================================== DESPAWN OFF SCREEN ENTITIES ===========================================
    for bullet in bullets:
        if bullet.offScreen():
            bullets.remove(bullet)
    spawnManager.despawnOffScreenObjects()

    #==========================================================================================================


    #================================== DETECT COLLISIONS =====================================================
    if terrain.checkForLandCollisions(player):  #if the player hits land
        player.kill()
    objtype = spawnManager.detectCollision(player) #returns object.m_type the player collided with
    if objtype == "fuel": #Player collided with fuel strip
        player.refuel()
    elif objtype != False: #Everything else other than the fuel strip currently kills player
        player.kill()

    spawnManager.detectEnemyBulletCollision(bullets)
    
    #==========================================================================================================

    #================================= DEFUEL PLANE ===========================================================
    player.defuel()

    DrawEverything() #redraws everything to the screen


pygame.quit()

