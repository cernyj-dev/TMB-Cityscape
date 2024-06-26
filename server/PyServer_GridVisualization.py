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
multiplier = 1.5
w = int(640 * multiplier)
h = int(480 * multiplier)
scale = int(15 * multiplier) #jen pro ukazovatko
magic_number = int(40 * multiplier)


config_path = 'helper_files/config.json'

ruleset = Ruleset.parse_json(config_path)
print(ruleset)

num_of_QR_codes = 20
qr_per_obj = num_of_QR_codes // len(ruleset.nodes)
#qr_per_obj = 5

qr_mode = 1 # 0 -> 1 QR per object, 1 -> 5 QR per object
            # 0..4 -> 0. object, 5..9 -> 1. object, 10..14 -> 2. object, 15..19 -> 3. object

plocha = tk.Canvas(width=w,height=h)
plocha.pack()

#------------------------------------------------------------
# Image vizualization

#------------------------------------------------------------
images = {
    'Park': ImageTk.PhotoImage(Image.open('images/park.png').resize((magic_number, magic_number))),
    'Apartment Buildings': ImageTk.PhotoImage(Image.open('images/apartment_buildings.png').resize((magic_number, magic_number))),
    'Fire Station': ImageTk.PhotoImage(Image.open('images/fire_house.png').resize((magic_number, magic_number))),
    'Lake': ImageTk.PhotoImage(Image.open('images/lake.png').resize((magic_number, magic_number))),    
}

def create_overlay(color, size, opacity):
    overlay = Image.new('RGBA', size, color + (int(255 * opacity),))
    return ImageTk.PhotoImage(overlay)

opacity_settings = 0.5
green_overlay = create_overlay((0, 255, 0), (magic_number, magic_number), opacity_settings)
yellow_overlay = create_overlay((255, 255, 0), (magic_number, magic_number), opacity_settings)
red_overlay = create_overlay((255, 0, 0), (magic_number, magic_number), opacity_settings)

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
        self.image = plocha.create_rectangle(x1, y1, x2, y2)
        self.text = plocha.create_text(x1 + 20, y1 + 20, text='{},{}'.format(col, row), font="Arial 10")
        self.fill = None
        self.overlay = None

    def __eq__(self, other) -> bool:
        if not isinstance(other,MySpace):
            return NotImplemented
        return self.top_l == other.top_l and self.bot_r == other.bot_r
    
    def Fill(self):
        draw(self)
        
    def Erase(self):
        for col in range(0, w // magic_number):
            for row in range(0, h // magic_number):
                if col == self.col and row == self.row:
                    continue
                if mygrid.m_grid[col][row].obj_class_id == -1:
                    continue
                searched_self = mygrid.m_grid[col][row]
                col_rel = abs(self.col - searched_self.col)
                row_rel = abs(self.row - searched_self.row)

                if (col_rel <= ruleset.nodes[searched_self.obj_class_id].range) and (row_rel <= ruleset.nodes[searched_self.obj_class_id].range):
                    limit_counter = 0
                    for limit in ruleset.nodes[searched_self.obj_class_id].limits:
                        if limit.blockType == self.obj_name:
                            if searched_self.obj_limits[limit.blockType] > 0:
                                searched_self.obj_limits[limit.blockType] -= 1
                            if searched_self.obj_limits[limit.blockType] == 0:
                                searched_self.obj_limits.pop(limit.blockType)
                            else:
                                if searched_self.obj_limits[limit.blockType] >= limit.lowerLimit:
                                    limit_counter += 1

                    if limit_counter == 0 and len(ruleset.nodes[searched_self.obj_class_id].limits) > 0:
                        plocha.delete(searched_self.overlay)
                        searched_self.overlay = plocha.create_image(searched_self.top_l + magic_number // 2, searched_self.top_r + magic_number // 2, image=red_overlay)
                    elif len(ruleset.nodes[searched_self.obj_class_id].limits) != 1 and len(ruleset.nodes[searched_self.obj_class_id].limits) > limit_counter > 0:
                        plocha.delete(searched_self.overlay)
                        searched_self.overlay = plocha.create_image(searched_self.top_l + magic_number // 2, searched_self.top_r + magic_number // 2, image=yellow_overlay)

        self.obj_class_id = -1
        self.obj_name = ""
        plocha.delete(self.fill)
        plocha.delete(self.overlay)


#--------------------------------------------------------------------
#
#--------------------------------------------------------------------

class MyGrid():
    def __init__(self):
        self.m_grid = []
        col_cnt = 0
        for i in range(0,w,magic_number):
            self.m_grid.append([])
            row_cnt=0
            for j in range(0,h,magic_number):
                self.m_grid[col_cnt].append(MySpace(i,j,i+magic_number,j+magic_number,col_cnt,row_cnt))
                row_cnt = row_cnt+1
            col_cnt = col_cnt+1        
mygrid = MyGrid()
#--------------------------------------------------------------------
#
#--------------------------------------------------------------------

def calculate_id(obj_id):
    if(qr_mode == 0):
        return obj_id

    id_counter = 0
    while(obj_id > qr_per_obj - 1):
        obj_id -= qr_per_obj
        id_counter += 1
    return id_counter


# TODO: LQ a Park - 
def draw(space: MySpace):
    space.obj_name = ruleset.nodes[space.obj_class_id].name
    space_has_limits = False

    if ruleset.nodes[space.obj_class_id].limits:
        space_has_limits = True

    for limit in ruleset.nodes[space.obj_class_id].limits:
        space.obj_limits.update({limit.blockType: 0})

    for col in range(0, w // magic_number):
        for row in range(0, h // magic_number):
            if col == space.col and row == space.row:
                continue
            if mygrid.m_grid[col][row].obj_class_id == -1:
                continue

            searched_space = mygrid.m_grid[col][row]
            col_rel = abs(space.col - searched_space.col)
            row_rel = abs(space.row - searched_space.row)

            if space_has_limits and col_rel <= ruleset.nodes[space.obj_class_id].range and row_rel <= ruleset.nodes[space.obj_class_id].range:
                for limit in ruleset.nodes[space.obj_class_id].limits:
                    if searched_space.obj_name == limit.blockType:
                        if limit.blockType not in space.obj_limits:
                            space.obj_limits[limit.blockType] = 1
                        else:
                            space.obj_limits[limit.blockType] += 1

            if not ruleset.nodes[searched_space.obj_class_id].limits:
                continue

            if col_rel <= ruleset.nodes[searched_space.obj_class_id].range and row_rel <= ruleset.nodes[searched_space.obj_class_id].range:
                limit_counter = 0
                for limit in ruleset.nodes[searched_space.obj_class_id].limits:
                    if limit.blockType == space.obj_name:
                        if limit.blockType not in searched_space.obj_limits:
                            searched_space.obj_limits[limit.blockType] = 1
                        else:
                            searched_space.obj_limits[limit.blockType] += 1

                        if searched_space.obj_limits[limit.blockType] >= limit.lowerLimit:
                            limit_counter += 1

                if limit_counter == len(ruleset.nodes[searched_space.obj_class_id].limits) and len(ruleset.nodes[searched_space.obj_class_id].limits) > 0:
                    plocha.delete(searched_space.overlay)
                    #searched_space.fill = plocha.create_image(searched_space.top_l + magic_number // 2, searched_space.top_r + magic_number // 2, image=green_overlay)
                elif len(ruleset.nodes[searched_space.obj_class_id].limits) > limit_counter > 0 and len(ruleset.nodes[searched_space.obj_class_id].limits) > 0:
                    plocha.delete(searched_space.overlay)
                    searched_space.overlay = plocha.create_image(searched_space.top_l + magic_number // 2, searched_space.top_r + magic_number // 2, image=yellow_overlay)
                elif limit_counter == 0 and len(ruleset.nodes[searched_space.obj_class_id].limits) > 0:
                    plocha.delete(searched_space.overlay)
                    searched_space.overlay = plocha.create_image(searched_space.top_l + magic_number // 2, searched_space.top_r + magic_number // 2, image=red_overlay)

    image_id = plocha.create_image(space.top_l + magic_number // 2, space.top_r + magic_number // 2, image=images[space.obj_name])
    space.fill = image_id

    if space_has_limits:
        limits_satisfied = [
            limit.lowerLimit <= space.obj_limits.get(limit.blockType, 0) <= limit.upperLimit
            for limit in ruleset.nodes[space.obj_class_id].limits
        ]
        if all(limits_satisfied):
            return
        elif any(limits_satisfied):
            space.overlay = plocha.create_image(space.top_l + magic_number // 2, space.top_r + magic_number // 2, image=yellow_overlay)
        else:
            space.overlay = plocha.create_image(space.top_l + magic_number // 2, space.top_r + magic_number // 2, image=red_overlay)

#--------------------------------------------------------------------
# all good
#--------------------------------------------------------------------


#------------------------------------------------------------
#
#------------------------------------------------------------
class MyObject():
    def __init__(self,class_id,x,y):
        self.class_id = class_id
        self.last_x = x
        self.last_y = y

        self.myImage = [] #pro vsechny objekty - ukazovatko i objekt
        self.myImage.append(plocha.create_rectangle(x-scale,y-scale,x+scale,y+scale,fill="")) #ukazovatko
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
        actual_x=Decimal(x*w)
        actual_y=Decimal(y*h)
        
        myObjects.update({obj.session_id : MyObject(obj.class_id,actual_x,actual_y)})
        mygrid.m_grid[floor(actual_x/magic_number)][floor(actual_y/magic_number)].obj_class_id = calculate_id(obj.class_id) #updating the object class id
        mygrid.m_grid[floor(actual_x/magic_number)][floor(actual_y/magic_number)].Fill() # calling Fill on MySpace object, which holds x,y,ID of the object

    def update_tuio_object(self, obj):
        x,y = obj.position
        x= Decimal(x)
        y= Decimal(y)
        actual_x=Decimal(x*w)
        actual_y=Decimal(y*h)

        lx= myObjects[obj.session_id].last_x
        ly= myObjects[obj.session_id].last_y

        delta_x=actual_x - lx
        delta_y=actual_y - ly

        myObjects[obj.session_id].move(delta_x,delta_y)



        if (not mygrid.m_grid[floor(lx/magic_number)][floor(ly/magic_number)].__eq__(mygrid.m_grid[floor(actual_x/magic_number)][floor(actual_y/magic_number)])):
            mygrid.m_grid[floor(lx/magic_number)][floor(ly/magic_number)].Erase()
            mygrid.m_grid[floor(actual_x/magic_number)][floor(actual_y/magic_number)].obj_class_id = calculate_id(obj.class_id) #updating the object class id

            mygrid.m_grid[floor(actual_x/magic_number)][floor(actual_y/magic_number)].Fill() # calling Fill on MySpace object, which holds x,y,ID of the object

        myObjects[obj.session_id].last_x = actual_x
        myObjects[obj.session_id].last_y = actual_y

    def remove_tuio_object(self, obj):
        #print("Object " ,obj.session_id, " of class ",obj.class_id," was deleted.")
        lx= myObjects[obj.session_id].last_x
        ly= myObjects[obj.session_id].last_y
        mygrid.m_grid[floor(lx/magic_number)][floor(ly/magic_number)].Erase()
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