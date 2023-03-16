import pygame
import math
import time

pygame.init()

width,height=1200,600

root=pygame.display.set_mode((width,height))

pygame.mouse.set_visible(False)

GRID=100

gameover=False

clock=pygame.time.Clock()

MAP=[
    [1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,3,0,0,0,0,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,4,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,2,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,3,0,0,0,0,0,0,3,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1]
]

coords=[1.5,1.5]
angle=0
fov=math.pi/3
max_depth=10
number_of_rays=width//2
delta_angle=fov/number_of_rays

scale=width//number_of_rays

screen_distance=(width/2)/math.tan(fov/2)

move=0.060
rotate=0.050

objects={}
colors={1:(0,255,255),2:(0,0,255),3:(0,255,0),4:(255,0,255)}

def setup_map():
    for i in range(len(MAP)):
        for j in range(len(MAP[i])):
            if MAP[i][j]:
                objects[(j,i)]=MAP[i][j]
                # pygame.draw.rect(root,'white',[j*GRID,i*GRID,GRID,GRID],2)

    # pygame.draw.circle(root,'white',(coords[0]*GRID,coords[1]*GRID),5)

    pygame.draw.rect(root,(50,50,50),(0,height//2,width,height))
    pygame.draw.rect(root,(30,30,30),(0,0,width,height//2))

def movements():
    global angle
    mx=move*math.cos(angle)
    my=move*math.sin(angle)
    dx,dy=0,0

    mouse_x,mouse_y=pygame.mouse.get_pos()

    pressed=pygame.key.get_pressed()
    if pressed[pygame.K_w]:
        dx+=mx
        dy+=my
    if pressed[pygame.K_s]:
        dx+=-mx
        dy+=-my
    if pressed[pygame.K_a]:
        dx+=my
        dy+=-mx
    if pressed[pygame.K_d]:
        dx+=-my
        dy+=mx

    if (int(coords[0]+dx),int(coords[1])) not in objects:
        coords[0]+=dx
    if (int(coords[0]),int(coords[1]+dy)) not in objects:
        coords[1]+=dy

    if mouse_x<100 or mouse_x>width-100:
        pygame.mouse.set_pos([width//2,height//2])
    rel=pygame.mouse.get_rel()[0]
    rel=max(-40,min(40,rel))
    angle+=rel*0.002

def raycast():

    ray_angle=(angle-(fov/2))+0.000001
    color=0

    for ray in range(number_of_rays):

        sin_angle=math.sin(ray_angle)
        cos_angle=math.cos(ray_angle)

        #vertical
        x_vertical,dx=(int(coords[0])+1,1) if cos_angle>0 else (int(coords[0])-0.000001,-1)
        depth_vertical=(x_vertical-coords[0])/cos_angle

        y_vertical=(depth_vertical*sin_angle)+coords[1]

        delta_depth=dx/cos_angle
        dy=delta_depth*sin_angle

        for i in range(max_depth):
            tile_vertical=(int(x_vertical),int(y_vertical))
            if tile_vertical in objects:
                break
            x_vertical+=dx
            y_vertical+=dy
            depth_vertical+=delta_depth

        #horizontal
        y_horizontal,dy=(int(coords[1])+1,1) if sin_angle>0 else (int(coords[1])-0.000001,-1)
        depth_horizontal=(y_horizontal-coords[1])/sin_angle

        x_horizontal=(depth_horizontal*cos_angle)+coords[0]

        delta_depth=dy/sin_angle
        dx=delta_depth*cos_angle

        for i in range(max_depth):
            tile_horizontal=(int(x_horizontal),int(y_horizontal))
            if tile_horizontal in objects:
                break
            x_horizontal+=dx
            y_horizontal+=dy
            depth_horizontal+=delta_depth

        if depth_horizontal<depth_vertical:
            depth=depth_horizontal
            color=objects[tile_horizontal]
            side=0
        elif depth_vertical<depth_horizontal:
            depth=depth_vertical
            color=objects[tile_vertical]
            side=1

        # pygame.draw.line(root,(255,0,0),(GRID*coords[0],GRID*coords[1]),((GRID*coords[0])+(GRID*depth*cos_angle),(GRID*coords[1])+(GRID*depth*sin_angle)),2)

        #remove fish-eye effect
        depth=depth*(math.cos(angle-ray_angle))

        #projection
        projection_height=screen_distance/(depth+0.000001)

        #draw walls
        if side==0:
            pygame.draw.rect(root,colors[color],(ray*scale,(height//2)-projection_height//2,scale,projection_height))
        else:
            pygame.draw.rect(root,list(map(lambda x:x//2,colors[color])),(ray*scale,(height//2)-projection_height//2,scale,projection_height))


        ray_angle+=delta_angle

while not gameover:
    root.fill('black')

    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            gameover=True
        if i.type == pygame.KEYUP:
            if i.key==pygame.K_q:
                gameover=True

    setup_map()
    raycast()
    movements()

    pygame.display.set_caption(str(clock.get_fps()//1))

    clock.tick(60)
    pygame.display.update()
