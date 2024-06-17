from math import floor
from pythontuio import TuioClient
from pythontuio import TuioListener
from threading import Thread
from decimal import Decimal
import os
import tkinter as tk
from helper_files.ConfigParser import Ruleset

##
# DEFAULT CONFIG
#   w,h - paremeters of tkinter window, same parameters are used in thesis-tracker
#   scale - relative scale of shown objects
w=640
h=480
scale = 15 #jen pro ukazovatko
magic_number = 40
config_path = 'helper_files/config.json'

ruleset = Ruleset.parse_json(config_path)
print(ruleset)

plocha = tk.Canvas(width=w,height=h)
plocha.pack()

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
        self.image = plocha.create_rectangle(x1,y1,x2,y2)
        plocha.create_text(x1+20,y1+20,text='{},{}'.format(col,row),font="Arial 10")

    def __eq__(self, other) -> bool:
        if not isinstance(other,MySpace):
            return NotImplemented
        return self.top_l == other.top_l and self.bot_r == other.bot_r
    
    def Fill(self):
        draw(self)
    def Erase(self):
        self.obj_class_id = -1
        self.obj_name = ""
        plocha.delete(self.fill)

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

def draw(space: MySpace):
    print("===================================")
    print("self object ID: ", space.obj_class_id, "self object name: ", ruleset.nodes[space.obj_class_id].name)
    print("self x: ", space.col, "self y: ", space.row)
    space.obj_name = ruleset.nodes[space.obj_class_id].name
    print("self object name: ", space.obj_name)
    print("limits: ", ruleset.nodes[space.obj_class_id].limits)
    print("===================================")
    
    # fill the limit dictionary counter with each limit and its number of limited objects in its range to 0
    for limit in ruleset.nodes[space.obj_class_id].limits:
        space.obj_limits.update({limit.blockType: 0}) # add the limit to the space    

    # calculate start/end col/row for for cycles - remain in bounds of grid
    start_col = int(max(0,space.col - ruleset.nodes[space.obj_class_id].range))
    end_row = int(min((h/magic_number)-1,space.col + ruleset.nodes[space.obj_class_id].range))
    start_row = int(max(0,space.row - ruleset.nodes[space.obj_class_id].range))
    end_col = int(min((w/magic_number)-1,space.row + ruleset.nodes[space.obj_class_id].range))

    # iterate through rows and columns
    for col in range(start_col,end_col):
        for row in range(start_row,end_row):
            searched_space = mygrid.m_grid[col][row]
            # iterate through limits
            for limit in ruleset.nodes[space.obj_class_id].limits:
                if (searched_space.obj_name == limit.blockType): # if the search space (object) is the same as one of the limits
                    space.obj_limits.update({limit.blockType: space.obj_limits[limit.blockType] + 1}) # increment the limit counter

            # check if space (current object - not the searched one) meets the limits of the search_space 
            for limit in ruleset.nodes[searched_space.obj_class_id].limits: # iterate through limits of the searched space
                tmp_row = abs(searched_space.row - space.row)
                tmp_col = abs(searched_space.col - space.col)
                if tmp_row > ruleset.nodes[searched_space.obj_class_id].range or tmp_col > ruleset.nodes[searched_space.obj_class_id].range: # if the current object isnt in range of the searched object
                    continue
                if (limit.blockType == space.obj_name): # if the limit is the same as the current object
                    searched_space.obj_limits[space.obj_name] = searched_space.obj_limits[space.obj_name] + 1 # increment the limit counter
                    if (searched_space.obj_limits[space.obj_name] >= limit.lowerLimit and searched_space.obj_limits[space.obj_name] <= limit.upperLimit):
                        plocha.itemconfig(searched_space.image,fill="green")
    isLimitOk = True
    # iterate through limits of the current object and check if they are met
    for limit, count in space.obj_limits.items():
        limit_ok = False
        for node_limit in ruleset.nodes[space.obj_class_id].limits:
            if node_limit.blockType == limit:
                if node_limit.lowerLimit <= count <= node_limit.upperLimit:
                    limit_ok = True
                    break
        if not limit_ok:
            isLimitOk = False
            break
        

    if (isLimitOk):
      space.fill = plocha.create_rectangle(space.top_l,space.top_r,space.bot_l,space.bot_r,fill="green")
    else:
      space.fill = plocha.create_rectangle(space.top_l,space.top_r,space.bot_l,space.bot_r,fill="red")
    return
#--------------------------------------------------------------------
#
#--------------------------------------------------------------------

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
        print("detected a new object", obj.class_id, " on pos ",obj.position, " with session id : ",obj.session_id)
        x,y = obj.position
        x= Decimal(x)
        y= Decimal(y)
        actual_x=Decimal(x*w)
        actual_y=Decimal(y*h)
        
        myObjects.update({obj.session_id : MyObject(obj.class_id,actual_x,actual_y)})
        mygrid.m_grid[floor(actual_x/magic_number)][floor(actual_y/magic_number)].obj_class_id = obj.class_id #updating the object class id
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
            mygrid.m_grid[floor(actual_x/magic_number)][floor(actual_y/magic_number)].obj_class_id = obj.class_id #updating the object class id
            mygrid.m_grid[floor(actual_x/magic_number)][floor(actual_y/magic_number)].Fill() # calling Fill on MySpace object, which holds x,y,ID of the object

        myObjects[obj.session_id].last_x = actual_x
        myObjects[obj.session_id].last_y = actual_y

    def remove_tuio_object(self, obj):
        print("Object " ,obj.session_id, " of class ",obj.class_id," was deleted.")
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