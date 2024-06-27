from math import floor
from pythontuio import TuioClient
from pythontuio import TuioListener
from threading import Thread
from decimal import Decimal
import os
import tkinter as tk
from PIL import Image, ImageTk, ImageDraw
from helper_files.ConfigParser import Ruleset

##
# DEFAULT CONFIG
#   w,h - paremeters of tkinter window, same parameters are used in thesis-tracker
#   scale - relative scale of shown objects
multiplier = 1
w = int(1280 * multiplier)
h = int(800 * multiplier)
scale = int(15 * multiplier) #jen pro ukazovatko
tile_size = int(120 * multiplier)
#variables for projection calibration
# x_coef = Decimal(0.005)
x_coef = Decimal(0.2)
y_coef = Decimal(0.07)
x_offset = 17
y_offset = -53


config_path = 'helper_files/config.json'

ruleset = Ruleset.parse_json(config_path)
print(ruleset)

num_of_QR_codes = 20 # how many QR codes are there
qr_per_obj = num_of_QR_codes // len(ruleset.nodes) # how many QR codes are there per object
#qr_per_obj = 5

qr_mode = 1 # 0 -> 1 QR per object, 1 -> 5 QR per object
            # 0..4 -> 0. object, 5..9 -> 1. object, 10..14 -> 2. object, 15..19 -> 3. object

plocha = tk.Canvas(width=w,height=h, bg="black")
plocha.pack(fill = "none", expand=True)

plocha.create_oval(w/2-5, h/2 - 5, w/2 +5, h/2 +5, fill = "red", outline="white")

#------------------------------------------------------------
# Image vizualization

#------------------------------------------------------------
images = {
    'Park': ImageTk.PhotoImage(Image.open('images/park.png').resize((tile_size, tile_size))),
    'Apartment Buildings': ImageTk.PhotoImage(Image.open('images/apartment_buildings.png').resize((tile_size, tile_size))),
    'Fire Station': ImageTk.PhotoImage(Image.open('images/fire_house.png').resize((tile_size, tile_size))),
    'Lake': ImageTk.PhotoImage(Image.open('images/lake.png').resize((tile_size, tile_size))),    
}

def create_overlay(color, size, opacity):
    overlay = Image.new('RGBA', size, color + (int(255 * opacity),))
    return ImageTk.PhotoImage(overlay)

opacity_settings = 0.5
green_overlay = create_overlay((0, 255, 0), (tile_size, tile_size), opacity_settings)
yellow_overlay = create_overlay((255, 255, 0), (tile_size, tile_size), opacity_settings)
red_overlay = create_overlay((255, 0, 0), (tile_size, tile_size), opacity_settings)

#------------------------------------------------------------

def decide_overlay_based_on_limits(space, delete = False):
    if not ruleset.nodes[space.obj_class_id].limits: # if the space doesnt have limits - doesnt have an overlay
        return    
    all_limits_satisfied = True
    any_limits_satisfied = False
    for limit in ruleset.nodes[space.obj_class_id].limits:
        limit_value = space.obj_limits[limit.blockType]
        if limit_value >= limit.lowerLimit:
            any_limits_satisfied = True
        else:
            all_limits_satisfied = False

    # all limits satisfied -> "transparent" overlay
    if all_limits_satisfied:
        if(delete):
            plocha.delete(space.overlay)

        return
    if any_limits_satisfied:
        if(delete):
            plocha.delete(space.overlay)
        space.overlay = plocha.create_image(space.top_l + tile_size // 2, space.top_r + tile_size // 2, image=yellow_overlay)
    else:
        if(delete):
            plocha.delete(space.overlay)
        space.overlay = plocha.create_image(space.top_l + tile_size // 2, space.top_r + tile_size // 2, image=red_overlay)

#------------------------------------------------------------
# Grid vizualization 
#
#------------------------------------------------------------


class MySpace():
    def __init__(self,x1,y1,x2,y2,col,row):
        self.top_l = x1
        self.top_r = y1
        self.bot_l = x2
        self.bot_r = y2
        self.col = col
        self.row = row
        self.obj_class_id = -1
        self.obj_name = ""  
        self.obj_limits = {}  
        self.image = plocha.create_rectangle(x1, y1, x2, y2, outline="white")
        self.text = plocha.create_text(x1 + tile_size//2, y1 + tile_size//2, text='{},{}'.format(col, row), font="Arial 10", fill="white")
        self.fill = None
        self.overlay = None

    def __eq__(self, other) -> bool:
        if not isinstance(other,MySpace):
            return NotImplemented
        return self.top_l == other.top_l and self.bot_r == other.bot_r
    
    def Fill(self):
        draw(self)


    # Goes through all of the objects which exist in the grid and checks if the object which is being erased is in the range of any other object
    # Which would change the color of the overlay of the neighboring object    
    def Erase(self):
        for col in range(0, w // tile_size):
            for row in range(0, h // tile_size):
                if col == self.col and row == self.row:
                    continue
                if mygrid.m_grid[col][row].obj_class_id == -1:
                    continue
                searched_self = mygrid.m_grid[col][row]
                col_rel = abs(self.col - searched_self.col)
                row_rel = abs(self.row - searched_self.row)
                
                # calculating limits of the iterated neighbor object when the current object gets deleted
                if (col_rel <= ruleset.nodes[searched_self.obj_class_id].range) and (row_rel <= ruleset.nodes[searched_self.obj_class_id].range):
                    for limit in ruleset.nodes[searched_self.obj_class_id].limits:
                        if limit.blockType == self.obj_name:
                            if searched_self.obj_limits[limit.blockType] > 0:
                                searched_self.obj_limits[limit.blockType] -= 1
                            # if searched_self.obj_limits[limit.blockType] == 0:
                            #     searched_self.obj_limits.pop(limit.blockType)
                    decide_overlay_based_on_limits(searched_self, True)

        self.obj_class_id = -1
        self.obj_name = ""
        self.obj_limits.clear()
        plocha.delete(self.fill)
        plocha.delete(self.overlay)


#--------------------------------------------------------------------
#
#--------------------------------------------------------------------

class MyGrid():
    def __init__(self):
        self.m_grid = []
        col_cnt = 0
        for i in range(0,w,tile_size):
            self.m_grid.append([])
            row_cnt=0
            for j in range(0,h,tile_size):
                self.m_grid[col_cnt].append(MySpace(i,j,i+tile_size,j+tile_size,col_cnt,row_cnt)) # Fills the m_grid with "empty objects"
                                                                                                  # Constructor of MySpace sets ID to -1 marking it as empty, because a 
                                                                                                  # used object gets its ID rewritten right away
                row_cnt = row_cnt+1
            col_cnt = col_cnt+1        
mygrid = MyGrid()
#--------------------------------------------------------------------


#--------------------------------------------------------------------
def calculate_id(obj_id):
    if(qr_mode == 0):
        return obj_id

    id_counter = 0
    while(obj_id > qr_per_obj - 1):
        obj_id -= qr_per_obj
        id_counter += 1
    return id_counter


#--------------------------------------------------------------------
def draw(space: MySpace):
    space.obj_name = ruleset.nodes[space.obj_class_id].name
    space_has_limits = False

    if ruleset.nodes[space.obj_class_id].limits:
        space_has_limits = True

    # Initialize the limits of the object in this implementation using the json file
    # Later on due to its neighbours, the limits will be updated and incremented - the int value will represent how many objects specified by the limits 
    # are in the range of the current object
    for limit in ruleset.nodes[space.obj_class_id].limits:
        space.obj_limits.setdefault(limit.blockType, 0)

    # Go through all of the objects and always check the distance between the iterated object and the object being drawn
    # Then depending on the object's limits, change the color of the overlay
    for col in range(0, w // tile_size):
        for row in range(0, h // tile_size):
            if col == space.col and row == space.row:
                continue
            if mygrid.m_grid[col][row].obj_class_id == -1:
                continue

            searched_space = mygrid.m_grid[col][row]
            col_rel = abs(space.col - searched_space.col)
            row_rel = abs(space.row - searched_space.row)
            
            # OBJECT BEING DRAWN SECTION
            if space_has_limits and col_rel <= ruleset.nodes[space.obj_class_id].range and row_rel <= ruleset.nodes[space.obj_class_id].range:
                for limit in ruleset.nodes[space.obj_class_id].limits:
                    # if the limit of the current object is the same as the object being iterated
                    if searched_space.obj_name == limit.blockType:
                        space.obj_limits[limit.blockType] += 1

            if not ruleset.nodes[searched_space.obj_class_id].limits:
                continue

            # ITERATED OBJECT SECTION
            if col_rel <= ruleset.nodes[searched_space.obj_class_id].range and row_rel <= ruleset.nodes[searched_space.obj_class_id].range:
                print("Searching for limits, curr_obj: ", space.obj_name, " iterated_obj: ", searched_space.obj_name)
                print("-----------------------------------")
                for limit in ruleset.nodes[searched_space.obj_class_id].limits:
                    # if the limit of the iterated object is the same as the object being drawn
                    if limit.blockType == space.obj_name:
                        print("Limit found: ", limit.blockType, ", obj-limit: ", searched_space.obj_limits[limit.blockType])
                        searched_space.obj_limits[limit.blockType] += 1
                        print("Incremented limit: ", searched_space.obj_limits[limit.blockType])
                decide_overlay_based_on_limits(searched_space, True)

    image_id = plocha.create_image(space.top_l + tile_size // 2, space.top_r + tile_size // 2, image=images[space.obj_name])
    space.fill = image_id

    decide_overlay_based_on_limits(space)

#------------------------------------------------------------

#function to recalculate coordinates from camera space to projector space
def recalculate_coords(x, y):
     x += x_offset
     y = h - y
     y += y_offset
     y -= (y - h//2) * y_coef
     x -= (x - w//2) * x_coef
     return x,y


#------------------------------------------------------------
class MyObject():
    def __init__(self,class_id,x,y):
        self.class_id = class_id
        self.last_x = x
        self.last_y = y

        self.myImage = [] #pro vsechny objekty - ukazovatko i objekt
        self.myImage.append(plocha.create_rectangle(x-scale,y-scale,x+scale,y+scale,fill="", outline="white")) #ukazovatko
        self.myImage.append(plocha.create_oval(x-4,y-4,x+4,y+4,fill="red")) #ukazovatko

    def move(self,x,y):
        for i in self.myImage:
            plocha.move(i,x,y)
    def delete(self):
        for i in self.myImage:
            plocha.delete(i)
# Dictionary for all obejcts on screen
myObjects = {}



# obj.position - goes from 0 to 1, 0 being total left/top and 1 being total right/bottom of camera
# We use Decimal for more precise calculation of floats.
class MyListener(TuioListener):
    def add_tuio_object(self,obj):
        #print("detected a new object", obj.class_id, " on pos ",obj.position, " with session id : ",obj.session_id)
        x,y = obj.position
        x= Decimal(x)
        y= Decimal(y)
        actual_x, actual_y = recalculate_coords(x*w, y*h)

        myObjects.update({obj.session_id : MyObject(obj.class_id,actual_x,actual_y)})
        mygrid.m_grid[floor(actual_x/tile_size)][floor(actual_y/tile_size)].obj_class_id = calculate_id(obj.class_id) #updating the object class id
        mygrid.m_grid[floor(actual_x/tile_size)][floor(actual_y/tile_size)].Fill() # calling Fill on MySpace object, which holds x,y,ID of the object

    def update_tuio_object(self, obj):
        x,y = obj.position
        x= Decimal(x)
        y= Decimal(y)
        actual_x, actual_y = recalculate_coords(x*w, y*h)


        lx= myObjects[obj.session_id].last_x
        ly= myObjects[obj.session_id].last_y

        delta_x=actual_x - lx
        delta_y=actual_y - ly

        myObjects[obj.session_id].move(delta_x,delta_y)

        if (not mygrid.m_grid[floor(lx/tile_size)][floor(ly/tile_size)].__eq__(mygrid.m_grid[floor(actual_x/tile_size)][floor(actual_y/tile_size)])):
            mygrid.m_grid[floor(lx/tile_size)][floor(ly/tile_size)].Erase()
            mygrid.m_grid[floor(actual_x/tile_size)][floor(actual_y/tile_size)].obj_class_id = calculate_id(obj.class_id) #updating the object class id

            mygrid.m_grid[floor(actual_x/tile_size)][floor(actual_y/tile_size)].Fill() # calling Fill on MySpace object, which holds x,y,ID of the object

        myObjects[obj.session_id].last_x = actual_x
        myObjects[obj.session_id].last_y = actual_y

    def remove_tuio_object(self, obj):
        #print("Object " ,obj.session_id, " of class ",obj.class_id," was deleted.")
        lx= myObjects[obj.session_id].last_x
        ly= myObjects[obj.session_id].last_y
        mygrid.m_grid[floor(lx/tile_size)][floor(ly/tile_size)].Erase()
        myObjects[obj.session_id].delete()
        del myObjects[obj.session_id]

client = TuioClient(("localhost",3333))
t = Thread(target=client.start)
listener = MyListener()
client.add_listener(listener)

t.start()

def my_quit(par):
    print("Quitting program.")
    os._exit(1)
plocha.bind_all("q",my_quit)

plocha.mainloop()

# barvy cervena - zadna podminka neni splnena
# barvy pruhledna - vsechny podminky jsou splneny
# barvy zluta - splnena je alespon jedna podminka