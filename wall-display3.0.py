# ***************************************************************************
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU General Public License as published by  *
# *   the Free Software Foundation; either version 2 of the License, or     *
# *   (at your option) any later version.                                   *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU General Public License for more details.                          *
# *                                                                         *
# *   You should have received a copy of the GNU General Public License     *
# *   along with this program; if not, write to the                         *
# *   Free Software Foundation, Inc.,                                       *
# *   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
# ***************************************************************************
"""
import pygame
import sys
import os
import csv

# ******************************************
# Helper functions - Verbose messages and fatal
# ******************************************
def verbose_clean(scr) :
    global verbln
    verbln = 0
    backgnd = pygame.Surface(screen.get_size()).convert()
    backgnd.fill((0,0,0))
    scr.blit(backgnd,(0,0))

# Print menu[0]["menuimg"] again
def update_menu(scr,menu) :
    img = menu[0]["menuimg"]
    scr.blit(img,(0,0))

def verbose(scr,msg) :
    global verbln
    f32 = pygame.font.Font(None, 32)
    font_height = f32.get_height()
    left_margin = 10
    surf_msg = f32.render(msg, 0, (50,50,50))
    scr.blit(surf_msg,(left_margin,verbln))
    verbln = verbln + font_height;
    pygame.display.flip()

# Prints a message and exits with status value
def fatal(status,msg) :
        sys.stderr.write('FATAL: '+msg+'\n')
        sys.exit(status)

# ******************************************
# Load menu info
# ******************************************
def load_menu_data(dirname) :
    fn = os.path.join(dirname,"menu.data")
    menu_entries = []
    with open(fn,'rb') as csvfile :
        linha = csv.reader(csvfile, delimiter=':')
        for row in linha :
            if len(row) > 1 :
                if int(row[2]) == 1 :
                    d = {}
                    d["id"] = int(row[0].strip())
                    d["dir"] = row[1].strip()
                    d["menu"] = row[3]
                    d["desc"] = row[4]
                    menu_entries.append(d)
    return menu_entries

def load_menu(dirname) :
    verbose(screen,"Reading menu info...")
    menu = load_menu_data("menu-data")
    verbose(screen,"Reading menu info... [Done]")
    def read_images (menu_item) :
        verbose(screen,"Reading image files for menu entry: " + 
                menu_item["menu"])
        img_list = read_jpg_files(menu_item["dir"])
        verbose(screen,"Reading image files for menu entry: " + 
                menu_item["menu"] + "[Done]")
        menu_item["imgs"] = img_list
        return menu_item
    menu = map(read_images,menu)
    menu_list = map(lambda x : (x["id"],x["menu"]),menu)
    def add_menu_img (menu_list,menu_item) :
        menu_img = pygame.Surface( (menu_width,menu_heigh) ).convert()
        menu_background_color=(0,0,0)
        menu_img.fill(menu_background_color)
        menu_fontname="gillsansmt"
        f  = pygame.font.SysFont(menu_fontname,20,bold=False)
        fh = f.get_height()
        left_margin = 10
        vertical_padding = 40
        ln = vertical_padding
        for (i,name) in menu_list :
            if i == menu_item["id"] : font_color = (255,255,255)
            else :                    font_color = (150,150,150)
            surf_msg = f.render(name,0, font_color)
            menu_img.blit(surf_msg,(left_margin,ln))
            ln = ln + fh + vertical_padding
        menu_item["menuimg"] = menu_img
        return menu_item
    return map(lambda x : add_menu_img(menu_list,x),menu)
        
# ******************************************
# Load images functions
# ******************************************
def img_to_back(i) :
    back = pygame.Surface(i.get_size())
    back = back.convert()
    back.blit(i,(0,0))
    return back

# Returns a list of tuples ("filename.jpg", pygame.image, pygame.back_img)
def read_jpg_files(dirname) :
        print "listing dir: ["+dirname+"]"
	fn_lst = os.listdir(dirname)
	fn_lst = sorted(fn_lst)
	img_list = []
	for fn in fn_lst :
		try :
			img = pygame.image.load(os.path.join(dirname,fn))
			back = img_to_back(img)
			img_list.append((fn,img,back))
		except:
			print "Warning could not open file "+fn
	return img_list

# ******************************************
# Fading in/out
# ******************************************
def fade_out(scr,img) :
    backgnd = pygame.Surface(scr.get_size()).convert()
    for i in range(250,-1,-25) :
        backgnd.fill((0,0,0))
        img.set_alpha(i)
        scr.blit(img, (menu_width,0))
        pygame.display.flip()
	pygame.time.delay(20)

def fade_in(scr,img) :
    backgnd = pygame.Surface(scr.get_size()).convert()
    for i in range(0, 250, 25) :
        backgnd.fill((0,0,0))
        img.set_alpha(i)
        scr.blit(img, (menu_width,0))
        pygame.display.flip()
	pygame.time.delay(20)

# ******************************************
# List rotate operations
# ******************************************
def rotate_left(lst) :
	i = lst.pop(0)
	lst.append(i)

def rotate_right(lst) :
        i = lst.pop();
        lst.insert(0,i)

# ******************************************
# Update the right frame
# ******************************************
def update_right_frame(screen,img) :
        global right_frame_previous
	fade_out(screen,right_frame_previous)
        right_frame_previous = img[2]
	fade_in(screen,right_frame_previous)

# ******************************************
#  Main
# ******************************************
# Setup the environment
pygame.init()
pygame.mouse.set_visible(0)

verbln     = 0;
screen     = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
disp_info  = pygame.display.Info()
disp_w     = disp_info.current_w
disp_h     = disp_info.current_h 
# Slides:  819 x 768
# Menu  :  205 x 768
# Total : 1024 x 768
menu_width = 205
menu_heigh = 768 # disp_h
auto_list  = []
current_menu_item = {}

verbose(screen,"Setting screen mode: ("+str(disp_w)+","+str(disp_h)+")")

#For testing only 
#menu = load_menu("menu-data")
#sys.exit(1)

# Parser display data
try:
    menu = load_menu("menu-data")
    if len(menu) < 1 : verbose(screen,"No menu items")
    current_menu_item = menu[0]
    auto_list = current_menu_item["imgs"]
    right_frame_previous = (auto_list[0])[2]
except:
    fatal(1,"error when setting up wall display data.")

from time import sleep, time

AUTO_FRAME_DELAY = 15000 # 15s
AUTO_START_DELAY = 20000 # 20s

verbose_clean(screen)

update_menu(screen,menu)

# Add an event to trigger the auto mode
pygame.time.set_timer(pygame.USEREVENT, 3000) # apply force

done = False
while not done:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        done = True
    elif event.type == pygame.USEREVENT:
        # Auto mode. Add a new event to trigger next slide after AUTO_FRAME_DELAY
        pygame.time.set_timer(pygame.USEREVENT, AUTO_FRAME_DELAY) 
        rotate_left(auto_list)
        update_right_frame(screen,auto_list[0])
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            done = True
        if event.key == pygame.K_q:
            done = True
        if event.key == pygame.K_p:
            #Reset timer to stop auto mode
            pygame.time.set_timer(pygame.USEREVENT, 0) # Stop auto
        elif event.key == pygame.K_UP or event.key == pygame.K_KP8: 
            #Add a new event to trigger auto mode after AUTO_START_DELAY
            pygame.time.set_timer(pygame.USEREVENT, AUTO_START_DELAY) 
            rotate_left(menu)
            current_menu_item = menu[0]
            auto_list = current_menu_item["imgs"]
            update_menu(screen,menu)
            update_right_frame(screen,auto_list[0])
        elif event.key == pygame.K_DOWN or event.key == pygame.K_KP2 :
            #Add a new event to trigger auto mode after AUTO_START_DELAY
            pygame.time.set_timer(pygame.USEREVENT, AUTO_START_DELAY) 
            rotate_right(menu)
            current_menu_item = menu[0]
            auto_list = current_menu_item["imgs"]
            update_menu(screen,menu)
            update_right_frame(screen,auto_list[0])
        elif event.key == pygame.K_LEFT or event.key == pygame.K_KP4 :
            #Add a new event to trigger auto mode after AUTO_START_DELAY
            pygame.time.set_timer(pygame.USEREVENT, AUTO_START_DELAY)
            rotate_right(auto_list)
            update_right_frame(screen,auto_list[0])
        elif event.key == pygame.K_RIGHT or event.key == pygame.K_KP6 :
            #Add a new event to trigger auto mode after AUTO_START_DELAY
            pygame.time.set_timer(pygame.USEREVENT, AUTO_START_DELAY) 
            rotate_left(auto_list)
            update_right_frame(screen,auto_list[0])
        #else :
        #    print "Key pressed: "+str(event.key)
            
pygame.quit();

"""
