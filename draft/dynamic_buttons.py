import pygame
import time

pygame.init()

pygame.display.set_caption('Hello Button')

display_width = 800
display_height = 600

black = (0,0,0)
white = (255,255,255)
bright_red = (255,0,0)
red = (139,0,0)
green = (0,128,0)
bright_green = (0,255,0)
bright_blue = (0,192,255)
blue = (0,0,139)

gameDisplay = pygame.display.set_mode((display_width, display_height))



is_running = True

def show_map(gameDisplay,road_map_img,x,y):
    gameDisplay.blit(road_map_img, (x,y))

class PygameButton(object):
    def __init__(self, gameDisplay):
        self.gameDisplay = gameDisplay
        self.fixed_button_dict = dict([("create button", (150,450,100,50,green,bright_green,self.add_button)), ("delete button", (550,450,100,50,red,bright_red,self.delete_button))])
        self.dynamic_button_dict = {}
        self.clock = pygame.time.Clock()
        self.click_on_dynamic_button = False
        self.clicked_button = None
        self.count = 0
    
    def add_button(self,unique_name,x,y):
        
        pygame.mouse.set_visible(True)

        while True:
            event = pygame.event.wait()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    mouse = event.pos
                    if not self.collide_with_fixed_button(mouse[0],mouse[1]) and not self.in_dynamic_button(mouse[0],mouse[1]):
                        self.dynamic_button_dict[str(self.count)] = (mouse[0],mouse[1],20,20,blue,bright_blue,self.print_pos)
                        print("add new button, id = %d" % (self.count))
                        self.count += 1
                    else:
                        print("clicked area collides with other button")
                    break


        return

    def collide_with_fixed_button(self,x0,y0):
        ret_val = False
        for key in self.fixed_button_dict:
            x,y,w,h,_,_,_ = self.fixed_button_dict[key]
            if x+w > x0 > x and y+h > y0 > y:
                ret_val = True
                break


        return ret_val

    def in_dynamic_button(self,x0,y0):
        ret_val = False
        for key in self.dynamic_button_dict:
            x,y,w,h,_,_,_ = self.dynamic_button_dict[key]
            if x+w > x0 > x and y+h > y0 > y:
                ret_val = True
                self.clicked_button = key
                break
        return ret_val

    def delete_button(self,unique_name,x,y):
        pygame.mouse.set_visible(True)
        '''
        while True:
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            if click[0] == 1:
                if self.click_on_dynamic_button:
                    del self.dynamic_button_dict[self.clicked_button]
                    self.clicked_button = None
                    self.click_on_dynamic_button = False
                break
            self.clock.tick(15)
        '''
        while True:
            event = pygame.event.wait()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    mouse = event.pos
                    if not self.collide_with_fixed_button(mouse[0],mouse[1]) and self.in_dynamic_button(mouse[0],mouse[1]):
                        del self.dynamic_button_dict[self.clicked_button]
                        self.clicked_button = None
                    break            
        return

    def text_objects(self,text, font):
        textSurface = font.render(text, True, black)
        return textSurface, textSurface.get_rect()

    def print_pos(self,unique_name,x,y):
        print("button pos\n: x == %d, y == %d" % (x,y))
        self.click_on_dynamic_button = True
        self.clicked_button = unique_name

    def button(self, uniquename, button_info):
        x,y,w,h,ic,ac,action = button_info
    
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        #print(click)

        if x+w > mouse[0] > x and y+h > mouse[1] > y:
            pygame.draw.rect(self.gameDisplay, ac, (x,y,w,h))

            if click[0] == 1 and action != None:
                action(uniquename,x,y)

        else:
            pygame.draw.rect(self.gameDisplay, ic, (x,y,w,h))

        smallText = pygame.font.SysFont("comicsansms",20)
        textSurf, textRect = self.text_objects(uniquename,smallText)
        textRect.center = ((x+w/2),(y+(h/2)))
        gameDisplay.blit(textSurf, textRect)

    def draw_buttons(self):
        for key in self.fixed_button_dict:
            self.button(key,self.fixed_button_dict[key])

        for key in self.dynamic_button_dict:
            self.button(key,self.dynamic_button_dict[key])
        return

road_map_img = carImg = pygame.image.load('road_map.png')

x =  10
y = 10

pygame_button = PygameButton(gameDisplay)
while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False

    pygame_button.gameDisplay.fill(white)
    show_map(pygame_button.gameDisplay,road_map_img,x,y)
    
    pygame_button.draw_buttons()
    
    pygame.display.update()
    pygame_button.clock.tick(15)

