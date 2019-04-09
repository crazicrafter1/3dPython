import pygame
import math
import random
import json
import operations as op

pi = math.pi

def rotate2d(pos,rad): x,y = pos; s,c = math.sin(rad), math.cos(rad); return x*c-y*s,y*c+x*s

class GameObject:
    #def __init__(self, name, pos, faces):
    def __init__(self, gameObject):
        self.name = gameObject["name"]
        self.isRigid = gameObject["isRigid"]
        self.pos = gameObject["pos"]
        #print(self.pos)
        self.faces = []
        if self.isRigid:
            self.velocity = [0,0,0]
            self.useGravity = True
            self.useFriction = True
            self.friction = .4
            self.isKinematic = False
            #self.mass = 1 # really no examples of mass used in SM 64
            
            
        if "faces" in gameObject:
            self.faces = gameObject["faces"]
            
##            for face in self.faces:
##                f = face["verts"]
##                for vert in f:
##                    vert[0]+=1;vert[1]+=1;vert[2]+=1

            
##        self.name = name
##        self.pos = pos
##        self.faces = faces
##        for face in faces:
##            f = face["verts"]
##            for vert in f:
##                vert[0]+=1;vert[1]+=1;vert[2]+=1
        
    def getRawVerts(self):
        v = []
        for face in self.faces:
            for vert in face["verts"]:
                v.append(vert)
        return v

    def getRawFaces(self):
        r_faces = []
        for face in self.faces:
            r_faces.append(face["verts"])
        return r_faces

gameObjects = []
with open("objects.json") as file:
    f = json.load(file)
    for gameObject in f:
        #print(gameObject["pos"][2])
        gameObjects.append(GameObject(gameObject)) #["name"], mod["pos"], mod["faces"]))

##objects = []
##with open("objects.json") as file:
##    f = json.load(file)
##    #for mod in f:
##    #    if "faces" in mod:#####
##    #        objects.append(model(mod["name"], mod["pos"], mod["faces"]))

    
def get3dVert(vertex, caster, gameObjectPos):
    # WAS - FOR x,y,z
    v = [vertex[0]-caster.pos[0]+gameObjectPos[0], vertex[1]-caster.pos[1]+gameObjectPos[1], vertex[2]-caster.pos[2]+gameObjectPos[2]]

##    print("vertex", vertex,
##          "caster", caster.pos,
##          "gameObjectPos", gameObjectPos,
##          "3dvert:", v)
    
    v[0], v[2] = rotate2d((v[0],v[2]), caster.ry)
    v[1], v[2] = rotate2d((v[1],v[2]), caster.rx)

    return v

def get2dVert(vertex, display):
    
    # vertex z is 0 in for unknown reason
    # possibly position of camera not added to vert, so 0,0,0 vert would
    # return err
    if vertex[2]==0:
        f = 0
    else:
        f = 200/vertex[2]

    v = [(vertex[0]*f)+display.cx,
         (display.h-(vertex[1]*f)+display.cy)-display.h]

    return v

minZ = .1

##colors = [
##        int(math.random()*255), 
##
##    ]

class Renderer:
    def __init__(self, w, h):
        #self.objects = []
        pygame.event.get(); pygame.mouse.get_rel()
        self.currentInterval = 0
    
        self.w = w; self.h = h
        self.cx = w//2; self.cy = h//2

        self.display = pygame.display.set_mode((w,h))
        
##        with open("objects.json") as file:
##            f = json.load(file)
##            for mod in f:
##                if "faces" in mod:#####
##                    self.objects.append(model(mod["name"], mod["pos"], mod["faces"]))

    def render(self, clock, delta, caster):
        # clear screen before draw
        self.display.fill((255,255,255))
        
        #verts = [obj.getRawVerts() for obj in self.objects]
        for gameObject in gameObjects:
            if gameObject.faces:
                
                for face in gameObject.getRawFaces():
                    verts3d = [get3dVert(vert, caster, gameObject.pos) for vert in face]
                    #for vt in verts3d: print(vt[2])
                    
                    i=0
                    while i<len(verts3d):
                        
                        # if clipping
                        if verts3d[i][2] < 0:
                            sides=[]

                            # left vert
                            left = verts3d[i-1]

                            # right vert
                            right = verts3d[(i+1) % len(verts3d)]

                            # if left vert is not clipping
                            if left[2]>=minZ:
                                sides += [getZ(verts3d[i],left,minZ)]

                            # if right vert is not clipping
                            if right[2]>=minZ:
                                sides += [getZ(verts3d[i],right,minZ)]
                            verts3d = verts3d[:i]+sides+verts3d[i+1:]
                            i+=len(sides)-1;
                        i+=1

                    #print(verts3d)

                    if verts3d:
                        verts2d=[]
                        for vert in verts3d:
                            verts2d.append(get2dVert(vert,self))
                        #verts2d = [get2dVert(vert, self) for vert in verts3d]

                        #verts2d.append(verts2d[0])

                    #print(verts2d)

                    try:
                        pygame.draw.polygon(self.display, (0, 127, 50), verts2d)
                    except: pass

        self.currentInterval+=delta
        if self.currentInterval>=1:
            self.currentInterval=0
            pygame.display.set_caption("3dTriEngine | %.00f fps" % (clock.get_fps()))

        pygame.display.flip()

    def lockMouse(self):
        pygame.mouse.set_visible(0); pygame.event.set_grab(1)
        
    def unlockMouse(self):
        pygame.mouse.set_visible(1); pygame.event.set_grab(0)

    def addObject(self, gameObject):
        self.objects.append(gameObject)

##class Player:
##    def __init__(self): #, pos=[1,1,1]):
##        #self.pos = pos
##        self.ry = 0; self.rx = 0               #####
##        self.camera = Camera(self)
##        self.gameObject = gameObjects[0]
##
##    def events(self, event):
##        if event.type == pygame.MOUSEMOTION:
##            x,y = event.rel; x/=200; y/=200
##            #self.rx-=y;
##            self.ry+=x
##            
##        self.camera.events(event)
##        
##    def move(self, delta, key):
##        speed = delta * 5
##
##        x,y = speed*math.sin(self.ry), speed*math.cos(self.ry)
##        
##        if key[pygame.K_w]: self.pos[0]+=x; self.pos[2]+=y
##        if key[pygame.K_s]: self.pos[0]-=x; self.pos[2]-=y
##        if key[pygame.K_a]: self.pos[0]-=y; self.pos[2]+=x
##        if key[pygame.K_d]: self.pos[0]+=y; self.pos[2]-=x
##        
##        if key[pygame.K_SPACE]: self.pos[1]+=speed
##        if key[pygame.K_LSHIFT]: self.pos[1]-=speed
##
##        self.gameObject
##
##        # Modify position of "Player" GameObject in GameObjects
##        # 

class Camera:
    def __init__(self):
        self.mode = 0 #0:first; 1:third; 2:third_extended
        self.gameObject = gameObjects[0]
        
        self.pos = [self.gameObject.pos[0],
                    self.gameObject.pos[1],
                    self.gameObject.pos[2]]
        
        #self.parent = parent #gameObjects[0]
        self.rx = 0; self.ry = 0

    def update(self):
        self.rx = op.clamp(self.rx, -pi/2, pi/2)
        self.pos = [self.gameObject.pos[0],
                    self.gameObject.pos[1],
                    self.gameObject.pos[2]]
        
        print(self.gameObject.pos)
        if self.mode == 1: #third person:
            # beta = ry
            d = 3
            self.pos[0] -= d * (math.cos(self.ry)*math.cos(self.ry))
            self.pos[1] -= d * (math.sin(self.rx)*math.cos(self.ry))
            self.pos[2] -= d * (math.sin(self.ry))

        elif self.mode == 2: #third person extended
            d = 5
            self.pos[0] += d * (math.cos(self.ry)*math.cos(self.ry))
            self.pos[1] += d * (math.sin(self.rx)*math.cos(self.ry))
            self.pos[2] += d * (math.sin(self.ry))

        
    def events(self, event):
        if event.type == pygame.MOUSEMOTION:
            x,y = event.rel; x/=200; y/=200
            self.rx-=y; #self.ry+=x
            self.ry+=x
            
        # clamp rx rotation [-pi/2,pi/2]

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F5:
                
                self.mode = (self.mode+1)%3
        
    def move(self, delta, key):
        speed = delta * 5

##        x,y = speed*math.sin(self.ry), speed*math.cos(self.ry)
##        
##        if key[pygame.K_w]: self.x+=x; self.z+=y
##        if key[pygame.K_s]: self.x-=x; self.z-=y
##        if key[pygame.K_a]: self.x-=y; self.z+=x
##        if key[pygame.K_d]: self.x+=y; self.z-=x
##        
##        if key[pygame.K_SPACE]: self.y+=speed
##        if key[pygame.K_LSHIFT]: self.y-=speed
        
        x,y = speed*math.sin(self.ry), speed*math.cos(self.ry)
        
        if key[pygame.K_w]: self.gameObject.pos[0]+=x; self.gameObject.pos[2]+=y
        if key[pygame.K_s]: self.gameObject.pos[0]-=x; self.gameObject.pos[2]-=y
        if key[pygame.K_a]: self.gameObject.pos[0]-=y; self.gameObject.pos[2]+=x
        if key[pygame.K_d]: self.gameObject.pos[0]+=y; self.gameObject.pos[2]-=x
        
        if key[pygame.K_SPACE]: self.gameObject.pos[1]+=speed
        if key[pygame.K_LSHIFT]: self.gameObject.pos[1]-=speed



def getZ(A, B, newZ):
    if B[2]==A[2] or newZ<A[2] or newZ>B[2]: return None
    dx,dy,dz = B[0]-A[0],B[1]-A[1],B[2]-A[2]
    i=(newZ-A[2])/dz
    return A[0]+dx*i,A[1]+dy*i,newZ
