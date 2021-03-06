#!/usr/bin/env python
"""
Created on Tue Dec  1 11:14:18 2015

@author: lauren
"""

fps                 = 10        #at most  this many frames per second
back_image          = 'back2_800_600.bmp'   #must have this file in same dir.
display_cols        = 800
display_rows        = 600
wall_thickness      = 5         #thickness in pixels
wall_color          = 'black'
food_color          = 'purple'
trace_color         = 'blue'
trace_arc           = 10        #in degrees, shows on both sides of r.azi
trace_decrease      = -17       #negative, subtracts from robot size to make a smaller trace
trace_width         = 1
leave_trace         = 0         #default mode is not to leave traces

color_of_nothing    = 'white'
sim_version         = 'FrustrationRobot2000'

r_image          = 'robo2.bmp'  #must have this file in same dir.
r_edge           = 51       #edge of square surrounding robot (in pixels)
r_init_azi       = 0        #azimuth, in degrees (up is 0)
r_init_x         = 30       #must be >= wall_thickness
r_init_y         = 30

r_init_fwd_speed = 5        #pixels per simulation cycle
r_init_spin_speed= 3        #degrees per simulation cycle
r_transparency   = 0       #0 is totally transp., 255 totally opaque
r_visual_range   = 100      #measured from robot center
r_visual_angle   = 30       #in degrees, must divide 90 exactly!
r_visual_granularity = 5    #must be < wall_thickness for walls to be detected correctly!

user_input       = 0.0        #amount of influence of user control the human has on the system



list_obstacles = []
blocked_nodes = []
debug_path  = []
path = None

#import everything
import os, pygame
from pygame.locals import *
import math
import random
import time
import numpy


main_dir = os.path.split(os.path.abspath(__file__))[0]
screen = pygame.display.set_mode((display_cols, display_rows))
list_walls= []



class Obstacle(pygame.Rect):       #for now just colored rectangles
    def __init__(self, x_topleft, y_topleft, width, height, color):
        self.x_topleft  = x_topleft
        self.y_topleft  = y_topleft
        
        self.width      = width
        self.height     = height
        self.color      = pygame.Color(color)
        self.rect       = pygame.Rect(x_topleft, y_topleft, width, height)
        
        self.r          = width
        
        self.x          = self.rect.center[0]
        self.y          = self.rect.center[1]
        
        self.force      = 0.0
        self.theta      = 0.0
        
    def nodes(self):
        nodes = []
        buff  = 15
        
        for y in range(self.y_topleft -buff, self.y_topleft + self.height + buff):
            for x in range(self.x_topleft-buff, self.x_topleft + self.width + buff ):
                nodes.append((int(x), int(y)))
        return nodes
        

''' Changes alpha for surfaces with per-pixel alpha; only for small surfaces!
    Sets alpha for WHITE pixels to new_alpha.
    The alpha value is an integer from 0 to 255, 0 is fully transparent and
    255 is fully opaque. '''
def change_alpha_for_white(surface,new_alpha):
    size = surface.get_size()
    if size[0]>300 or size[1]>300:
        print 'change_alpha_for_white-> size = ', size, ' IMAGE TOO LARGE!'
        return surface
    for y in xrange(size[1]):
	for x in xrange(size[0]):
	    r,g,b,a = surface.get_at((x,y))
	    if r==255 and g==255 and b==255:
                surface.set_at((x,y),(r,g,b,new_alpha))
    return surface

''' Changes alpha for surfaces with per-pixel alpha; only for small surfaces!
    Sets alpha for pixels with alpha == 0 to new_alpha. It is needed b/c
    transform.smoothscale pads image with alpha=0. '''
def change_alpha_for_alpha(surface,new_alpha):
    size = surface.get_size()
    for y in xrange(size[1]):
	for x in xrange(size[0]):
	    r,g,b,a = surface.get_at((x,y))
	    if a<200:
                surface.set_at((x,y),(r,g,b,new_alpha))
    return surface

                        
class Goal(pygame.sprite.Sprite):
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        #Sprites must have an image and a rectangle
        self.image          = image
        self.image_original = self.image    #unchanging copy, for rotations
        self.rect           = image.get_rect()
        
        self.x = 300
        self.y = 400
        self.rect.center = (self.x, self.y) # set starting position
        
        if self.inObstacle():
            self.getNew()
        
    def getNew(self):
        self.x = random.randint(60,display_cols-60)
        self.y = random.randint(60,display_rows-60)
        self.rect.center = (self.x, self.y) # set starting position
        
        while self.inObstacle():
             self.x = random.randint(60,display_cols-60)
             self.y = random.randint(60,display_rows-60)
             self.rect.center = (self.x, self.y) # set starting position
                
        
    def inObstacle(self):
        for ob in list_rect_obstacles: 
            if ob.colliderect(self.rect):
                return True
        return False
        
class Wall(pygame.Rect):       #for now just colored rectangles
    def __init__(self, x_topleft, y_topleft, width, height, color):
        self.x_topleft  = x_topleft
        self.y_topleft  = y_topleft
        self.width      = width
        self.height     = height
        self.color      = pygame.Color(color)
        self.rect       = pygame.Rect(x_topleft, y_topleft, width, height)
        
        
#Create list of obstacles (walls+others)
#First 2 args are x and y of top-left corner, next two width and height, next color
w01 = Obstacle(0,0,display_cols,wall_thickness, wall_color)                          #top wall
list_obstacles.append(w01)
w02 = Obstacle(display_cols-wall_thickness,0,wall_thickness,display_rows,wall_color) #right wall
list_obstacles.append(w02)
w03 = Obstacle(0,display_rows-wall_thickness,display_cols,wall_thickness,wall_color) #bottom wall
list_obstacles.append(w03)
w04 = Obstacle(0,0,wall_thickness,display_rows, wall_color)                          #left wall
list_obstacles.append(w04)
#w05 = Obstacle(display_cols/2,display_rows/2,wall_thickness,display_rows/2,wall_color)
#list_obstacles.append(w05)
#w06 = Obstacle(display_cols/6,display_rows/2,display_rows/4,wall_thickness,wall_color)
#list_obstacles.append(w06)
    
obs = random.randint(20,50)
for i in range(1,obs):
    x = random.randint(30,display_cols)
    y = random.randint(30,display_rows)
 
    r = random.randint(20,50)
    obstacle = Obstacle(x,y,r,r,food_color)
    list_obstacles.append(obstacle)



list_rect_obstacles = []
for ob in list_obstacles:
    list_rect_obstacles.append(ob.rect)
    


class Robot(pygame.sprite.Sprite):
    def __init__(self, image, x, y, azimuth, fwd_speed, spin_speed,\
                 visual_range, visual_angle, goal):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        #Sprites must have an image and a rectangle
        self.image          = image
        self.image_original = self.image    #unchanging copy, for rotations
        self.rect           = image.get_rect()
        self.rect_original  = self.rect     #unchanging copy, for rotations
        self.x = x # created because self.rect.center does not hold
        self.y = y # decimal values but these do
        self.rect.center = (self.x, self.y) # set starting position
        self.fwd_speed      = fwd_speed
        self.spin_speed     = spin_speed
        self.azi            = azimuth       #in degrees
        self.collided       = False
        self.opmode         = 0             #0=tele, 1=(random)walk 2=auto
        self.spin_angle_left= 0             #relative angle left to spin
        
        self._d = {'w':-1, 's':1, 'a':1, 'd':-1, 'N':0} 
        
        self.speed          = 0.0
        self.Vg             = 10.0
        self.Vo             = 0.0
        
        
        self.rotspeed       = 5.0
        self.bearing        = 0.0
        self.direction       = 'N'
        self.maxAccel       = 10.0
        
        self.goal           = goal 
        self.spin_angle_left = 0.0
        self.found_goal     = 0
        
        self.path           = None
        self.obsWarn        = False
        
        self.userInf        = 0.0
        
        self.infl_obst           = []
        
        
        
        ## LET'S TRY TO FIX VELOCITY
        self.Vo  = 0.0
        self.Va  = 0.0
        self.Vg  = 0.0
        self.Vu  = 0.0

        
        #these are the parameters of the range-sensing system
        self.visual_range   = visual_range
        self.visual_angle   = visual_angle
        self.nr_sensors     = 2*90/self.visual_angle+1
        self.retina         = list([self.visual_range, pygame.Color(color_of_nothing)]\
                                   for i in range(self.nr_sensors))

    def printRetina(self):
        """Prints the content of the retina list"""
        for s in self.retina:
            if (s[0] == self.visual_range): #this really means >=, since sense() func. caps distances
                                            #to visual_range
                print '>'+str(self.visual_range)
            else:       #obstacle detected
                print s
        print '\n'

    def update(self):
        """All sprites have an update() method. This function is
        typically called once per frame. IMPORTANT: All actions in
        here execute AFTER the ones called directly in the event loop.
        """
        if   (self.opmode == 0): self.test()     #teleop mode   
        elif (self.opmode == 1): self.mode_1_auto()
        else:
            print 'ERROR! Undefined operation mode!'
            
        
            
#    def mode_0_tele(self):
#        self.sense()   
#        dtheta = 0 
#        if self.collided:
#                print 'update-->self.opmode==0 THAT HURT!'
#                self.collided = False
#                self.speed = 0.0
#        
#        if self.direction == 'w':
#            R =0.8
#            if self.speed >-self.maxAccel:
#                self.speed -= 1
#        elif self.direction == 's':
#            R = 0.8
#            if self.speed < self.maxAccel:
#                self.speed += 1
#        elif self.direction == 'd' or self.direction == 'a':
#            R = 0.1
#            dtheta = self.rotspeed*self._d[self.direction]
#        else :
#            R = 1
#            self.speed = -5
#        
#        dx,dy = self.potentialField()*R
#        
#        angle = math.atan2(dx,dy)* 180/math.pi + 180
#        if angle  >= 360:         #keep theta between -360..360
#            angle -= 360
#        if angle <= -360:
#            angle += 360
#
#        self.spin_angle_left = int(angle) - self.bearing
#          
#         
#        if self.spin_angle_left >=180.0:
#            self.spin_angle_left = self.spin_angle_left - 360.0
#        if self.spin_angle_left <=-180.0:
#            self.spin_anlge_left = self.spin_angle_left + 360.0
#
#        if self.spin_angle_left != 0:     #must finish SPIN
#            if math.fabs(self.spin_angle_left) <= self.rotspeed:
#                dtheta += (sign(self.spin_angle_left))
#            else:
#                dtheta += (sign(self.spin_angle_left)*(self.rotspeed))*R
#                
#
#        movex = self.speed*math.sin(self.bearing*math.pi/180)
#        movey = self.speed*math.cos(self.bearing*math.pi/180)
#        self.move(movex,movey,dtheta)
        
        
    def mode_1_auto(self):
        self.sense() 
        self.printRetina()
        dtheta = 0 
        global user_input
        if user_input > 1:
            user_input = 1

        if self.collided:
                print 'update-->self.opmode==0 THAT HURT!'
                self.collided = False
                self.speed = 0.0
        
        if self.direction == 'w':
            U =1-user_input
            if self.speed >-self.maxAccel:
                self.speed -= 1
        elif self.direction == 's':
            U = 1-user_input
            if self.speed < self.maxAccel:
                self.speed += 1
        elif self.direction == 'd' or self.direction == 'a':
            U = 0.1
            dtheta = self.rotspeed*self._d[self.direction]
        else :
            U = 1
            
        
        dx,dy = self.potentialField()*U
        
        angle = math.atan2(dx,dy)* 180/math.pi + 180
        if angle  >= 360:         #keep theta between -360..360
            angle -= 360
        if angle <= -360:
            angle += 360

        self.spin_angle_left = int(angle) - self.bearing
          
         
        if self.spin_angle_left >=180.0:
            self.spin_angle_left = self.spin_angle_left - 360.0
        if self.spin_angle_left <=-180.0:
            self.spin_anlge_left = self.spin_angle_left + 360.0

        if self.spin_angle_left != 0:     #must finish SPIN
            if math.fabs(self.spin_angle_left) <= self.rotspeed:
                dtheta += int(sign(self.spin_angle_left))
            else:
                dtheta += int(sign(self.spin_angle_left)*(self.rotspeed))
        print self.spin_angle_left        
        if self.obsWarn :

            if self.spin_angle_left != 0:
                if self.speed < 0 :
                    self.speed += 2
                    
            elif self.speed < -2 :
                 self.speed += 4
            else :
                self.speed = -2
               
                if self.obsDist < 30:
                    if self.speed < 0 :
                        self.speed += 1
                    else :
                        self.speed = 0
                        
                         
        else :
            if self.spin_angle_left > 45.0 or self.spin_angle_left < -45.0:
                if self.speed < 0 :
                    self.speed += 1
            elif self.speed >-self.maxAccel :
                self.speed -= 1
                    
                    
                    
        print self.speed
        movex = self.speed*math.sin(self.bearing*math.pi/180)
        movey = self.speed*math.cos(self.bearing*math.pi/180)
        self.move(movex,movey,dtheta)
        
    def test(self):
        self.sense() 
        global user_input
        if user_input > 1:
            user_input = 1
        
        if self.collided:
                print 'update-->self.opmode==0 THAT HURT!'
                self.collided = False
                self.speed = 0.0
#                
        dtheta1 = 0 
        dtheta = 0
                
        U = user_input
        if self.direction == 'w':
            if self.Vu >-self.maxAccel:
                self.Vu  -= 2*(U)
        elif self.direction == 's':
            if self.Vu  < self.maxAccel:
                self.Vu  += 2*(U)
        elif self.direction == 'd' or self.direction == 'a':
            dtheta1 = self.rotspeed*self._d[self.direction]*(U)
            self.Vu = 0
        else:
            self.Vu = 0
         
        if self.Vg > -self.maxAccel:
            self.Vg -= 2*(1-U)
            
        dx,dy = self.potentialField()
       # print dx, dy
        
        angle = math.atan2(dx,dy)* 180/math.pi + 180
        if angle  >= 360:         #keep theta between -360..360
            angle -= 360
        if angle <= -360:
            angle += 360
        if angle == NaN:
            angle = 0

        self.spin_angle_left = int(angle) - self.bearing
          
        if self.spin_angle_left >=180.0:
            self.spin_angle_left = self.spin_angle_left - 360.0
        if self.spin_angle_left <=-180.0:
            self.spin_angle_left = self.spin_angle_left + 360.0

        if self.spin_angle_left != 0:     #must finish SPIN
            if math.fabs(self.spin_angle_left) <= self.rotspeed:
                dtheta += int(sign(self.spin_angle_left)*(1-U))
            else:
                dtheta += int(sign(self.spin_angle_left)*(self.rotspeed)*(1-U))
        
        R = 1
        A =( math.fabs(math.cos( self.spin_angle_left*math.pi/180.0)))
        print 'A' + str( A)
        self.Vo = -self.Vg * R * (70/(self.retina[3][0]))
        print 'Vo' + str(self.Vo)
        Ob = 0
        for i in range(0,2):
            Ob += ((90/self.retina[i][0])*(i+1)*(.01)+ (90/self.retina[i+4][0])*(i+1)*(.01))*-self.Vg
        R2 = .1
        self.Vo += R2*Ob
        self.Va =int( (self.Vg + self.Vo)*(1-U))*A
        
        self.speed = self.Vu + self.Va
        print self.speed
    
            
            
    
        
        dx = self.speed*math.sin(self.bearing*math.pi/180)
        dy = self.speed*math.cos(self.bearing*math.pi/180)

        self.move(dx,dy,dtheta+dtheta1)

        
        

    def potentialField(self):
        RadiusOfInfluence   = 50.0
        Kobjs               = 5000
        Kgoal               = 1
        self.infl_obst = []
        for ob in list_obstacles:
            ob.dist = math.sqrt(math.pow(self.x - ob.x,2)+math.pow(self.y - ob.y,2))
            if ob.dist < (RadiusOfInfluence): 
                if ob.color != pygame.Color('black'):
                    self.infl_obst.append(ob)
        Distance = np.zeros((1,len(self.infl_obst)))
        V        = np.zeros((2,len(self.infl_obst)))
        count = 0
        if self.infl_obst != []:
            for ob in self.infl_obst:
                Distance[0][count] = ob.dist - ob.r
                V[0][count]     = ob.x - self.x
                V[1][count]     = ob.y - self.y
                count +=1
            
            rho = np.repeat(Distance,2,0)
            DrhoDx = -V/rho
            F = (1/rho - 1/RadiusOfInfluence)* 1/np.square(rho)*DrhoDx
            FObjects = Kobjs*numpy.sum(F) 
            
        else :
            FObjects = np.array((0,0))
            
        GoalError = np.array([self.goal.x - self.x, self.goal.y - self.y])
        normGoal = (math.sqrt(math.pow(GoalError[0],2)+math.pow(GoalError[1],2)))
        Fgoal = Kgoal * GoalError/normGoal
        Ftotal = Fgoal + FObjects
        normTotal = (math.sqrt(math.pow(Ftotal[0],2)+math.pow(Ftotal[1],2)))
        Magnitude = numpy.min((1,normTotal))
        Ftotal = Ftotal/normTotal * Magnitude
        return Ftotal
        
        
    
        
    def move(self,dx,dy,dtheta):
        self.spin(dtheta)
        previous_rect = self.rect           # in case undo is necessary       
        self.rect = self.rect.move(dx,dy)
        if self.rect.collidelist(list_rect_obstacles) != -1 or self.rect.collidelist(list_walls) != -1:#if collision exists
            print 'mode  -->I collided with wall(s)',\
                  self.rect.collidelistall(list_rect_obstacles)
            self.rect = previous_rect                   #undo the move
            self.collided = True
        else:                   #if there was no collision
            self.x,self.y = self.rect.center
            
            
      


    def spin(self,dtheta):
        self.bearing += dtheta
        if self.bearing >= 360:         #keep theta between -360..360
            self.bearing -= 360
        if self.bearing <= -360:
            self.bearing += 360
        original_rect = self.image_original.get_rect()
        rotated_image = pygame.transform.rotate(self.image_original, self.bearing)
        rotated_rect  = original_rect.copy()
        rotated_rect.center = rotated_image.get_rect().center
        self.image = rotated_image.subsurface(rotated_rect).copy()
        self.image = change_alpha_for_alpha(self.image, r_transparency)

    
    
    #this function's job is to place in self.retina the range sensed by each sensor
    def sense(self):
        self.obsWarn = False
        self.obsDist = 200.0
        n = (self.nr_sensors - 1)/2     #the "natural" sensor range is -n to +n
        granu = r_visual_granularity    #must be at least as large as the wall thickness!!
        for i in range(-n,n+1):         #sense with each of the 2n+1 range sensors
            ang = (self.bearing - i*self.visual_angle)*math.pi/180
            for distance in range(granu, self.visual_range+granu, granu):
                x = self.rect.center[0]-distance*math.sin(ang)  #endpoint coordinates
                y = self.rect.center[1]-distance*math.cos(ang)
                nr_collisions = 0
                count = -1          #needed to coordinate the two lists, to extract color after loop
                for ob in list_rect_obstacles:  #use the stripped-down list of rectangles for speed
                    count = count + 1
                    minDist = math.sqrt(math.pow(self.rect.center[0] - ob.center[0],2) + math.pow(self.rect.center[1] - ob.center[1],2))
                    if minDist < self.obsDist:
                        self.obsDist = minDist
        
                    if ob.collidepoint(x,y):
                        nr_collisions = 1
                        break       #breaks out of wall loop
                        
                for ob in list_walls:  #use the stripped-down list of rectangles for speed
                    if ob.collidepoint(x,y):
                        nr_collisions = 1
                        break       #breaks out of wall loop
                        
                if nr_collisions:   #non-zero collision
                    break           #breaks out of distance loop
                    
                dist = math.sqrt(math.pow(self.x -self.goal.x,2)+math.pow(self.y -self.goal.y,2))
                if dist < self.visual_range:
                    self.found_goal = 1
                else:
                    self.found_goal = 0
            #distance now has the min. between the visual range and the first collision
            self.retina[i+n][0] = distance
            if nr_collisions:       #nr_collisions is 1 if a collision has occurred
                if i == 0:
                    self.obsWarn = True
                self.retina[i+n][1] = list_obstacles[count].color #color comes form the larger list
            else:
                self.retina[i+n][1] = pygame.Color(color_of_nothing)
        
        #print 'sense -->retina is:\n', self.retina
        #self.printRetina()
          
    def draw_rays(self, target_surf):
        n = (self.nr_sensors - 1)/2 #the "natural" sensor range -n to +n
        for i in range(-n,n+1):     #draw the 2n+1 rays of the range sensors
            ang = (self.bearing - i*self.visual_angle)*math.pi/180
            x = self.rect.center[0]-self.retina[i+n][0]*math.sin(ang)
            y = self.rect.center[1]-self.retina[i+n][0]*math.cos(ang)
            #use aaline for smoother (but slower) lines
            pygame.draw.line(target_surf, (0,0,0), self.rect.center, (x,y))
########end of Robot class########

def load_image(name):
    path = os.path.join(main_dir, name)
    temp_image = pygame.image.load(path).convert_alpha()  #need this if using ppalpha
    return change_alpha_for_white(temp_image, r_transparency)  
    


###########################################
###########################################
def main():
    global leave_trace, list_traces, user_input
    if r_visual_granularity > wall_thickness:
        print 'PARAMETER ERROR: r_visual_granularity exceeds wall_thickness!'
        print 'This can cause wall detection errors!'
    if r_init_x<wall_thickness or r_init_y<wall_thickness:
        print 'PARAMETER ERROR: starting position overlaps wall!'
        print 'Check r_init_x|y_topleft and wall_thickness'
    pygame.init()           #also calls display.init()   
    startTime = time.time()
    caption = (sim_version + ' \tmode: teleoperation  ' )
    pygame.display.set_caption(caption+ str(startTime))
    r_sprite = load_image(r_image)
    g_sprite = load_image('goal.bmp')
    background  = load_image(back_image)


    #prepare simulation objects
    clock = pygame.time.Clock()
    screen.blit(background, (0, 0))
    goal = Goal(g_sprite)
    r = Robot(r_sprite, r_init_x, r_init_y,r_init_azi, r_init_fwd_speed,\
              r_init_spin_speed, r_visual_range, r_visual_angle,goal)

    robotSprite = pygame.sprite.Group(r)
    goalSprite = pygame.sprite.Group(goal)

    #display the environment once, right before event loop
    
    count = -1
    for ob in list_obstacles:
        count = count + 1
        s = pygame.display.get_surface()
        s.fill(ob.color, list_rect_obstacles[count])
    r.draw_rays(screen) 
    pygame.display.flip() 
    

    going = True
    time_down = 0.0
    time_elapsed = 0.0
    T = -1
    
    while going:
        clock.tick(fps)      #at most that many fps

        #Event loop################################

        for event in pygame.event.get():
            if event == QUIT:
                going = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    going = False
                    
                    
                time_down = pygame.time.get_ticks()
                    
                if event.key == K_w:
                    T = 1
                    r.direction = 'w'
                elif event.key == K_d:
                    T = 1
                    r.direction = 'd'
                elif event.key == K_a:
                    T = 1
                    r.direction = 'a'
                elif event.key == K_s:
                    T = 1
                    r.direction = 's'
                    
               
                if event.key == K_SPACE:
                    r.opmode = 0            #teleop mode
                    caption = sim_version + ' \tmode: teleoperation  '
                if event.key == K_1:
                    r.opmode = 1            #autonomous navigation mode
                    caption = (sim_version + ' \tmode: autonomous  ')  
                
               
            elif event.type == KEYUP:
                time_elapsed = (pygame.time.get_ticks() - time_down)/1000.0                
                
                if event.key == K_w:
                    T = -1
                    r.direction = 'N'
                elif event.key == K_d:
                    T = -1
                    r.direction = 'N'
                elif event.key == K_a:
                    T = -1
                    r.direction = 'N'
                elif event.key == K_s:
                    T = -1
                    r.direction = 'N'
            
        user_input += T*0.1

        if user_input > 1.0:
            user_input = 1.0
        elif user_input < 0.0:
            user_input = 0.0
                
        pygame.display.set_caption(caption + str(time.time() - startTime))
     
        # Find if goal reached 
        if pygame.sprite.spritecollide(r, goalSprite, False) != []:
            print 'You made it to the goal'
            goal.getNew()
            startTime = time.time()
            
        if r.speed > 0.0:
            r.speed -= 0.5
        elif r.speed < 0.0:
            r.speed += 0.5
 
        
        robotSprite.update()
        goalSprite.update()
        screen.blit(background, (0, 0))  #redraws the entire bkgrnd.
        #screen.fill((255,255,255)) # white background
        #screen.blit(red_block, (100,100))
        count = -1
        
        for ob in list_obstacles:
            count = count + 1
            s = pygame.display.get_surface()
            s.fill(ob.color,list_rect_obstacles[count])
        count = -1
        for ob in list_walls:
            count = count + 1
            s = pygame.display.get_surface()
            s.fill(ob.color, list_walls[count])

        r.draw_rays(screen) 
        robotSprite.draw(screen)
        goalSprite.draw(screen)
        
       
        #pygame.display.update()
        pygame.display.flip()   #all changes are drawn at once (double buffer)
        #pygame.time.delay(100)
    pygame.quit()               #also calls display.quit()


if __name__ == '__main__':
    main()

