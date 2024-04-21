from math import floor
from pythontuio import TuioClient
from pythontuio import TuioListener
from threading import Thread
from decimal import Decimal
import os
import tkinter as tk

##
# DEFAULT CONFIG
#   w,h - paremeters of tkinter window, same parameters are used in thesis-tracker
#   scale - relative scale of shown objects
w=640
h=480
scale = 15

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
        self.image = plocha.create_rectangle(x1,y1,x2,y2)
        plocha.create_text(x1+20,y1+20,text='{},{}'.format(col,row),font="Arial 10")

    def __eq__(self, other) -> bool:
        if not isinstance(other,MySpace):
            return NotImplemented
        return self.top_l == other.top_l and self.bot_r == other.bot_r
    
    def Fill(self):
        self.fill = plocha.create_rectangle(self.top_l,self.top_r,self.bot_l,self.bot_r,fill="blue")
    def Erase(self):
        plocha.delete(self.fill)

class MyGrid():
    def __init__(self):
        self.m_grid = []
        col_cnt = 0
        for i in range(0,w,40):
            self.m_grid.append([])
            row_cnt=0
            for j in range(0,h,40):
                self.m_grid[col_cnt].append(MySpace(i,j,i+40,j+40,col_cnt,row_cnt))
                row_cnt = row_cnt+1
            col_cnt = col_cnt+1        
#--------------------------------------------------------------------
#
#--------------------------------------------------------------------
class MyObject():
    def __init__(self,class_id,x,y):
        self.class_id = class_id
        self.last_x = x
        self.last_y = y

        self.myImage = []
        self.myImage.append(plocha.create_rectangle(x-scale,y-scale,x+scale,y+scale,fill=""))
        self.myImage.append(plocha.create_oval(x-4,y-4,x+4,y+4,fill="red"))

    def move(self,x,y):
        for i in self.myImage:
            plocha.move(i,x,y)
    def delete(self):
        for i in self.myImage:
            plocha.delete(i)
# Dictionary for all obejcts on screen
myObjects = {}

mygrid = MyGrid()

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
        mygrid.m_grid[floor(actual_x/40)][floor(actual_y/40)].Fill()

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

        if (not mygrid.m_grid[floor(lx/40)][floor(ly/40)].__eq__(mygrid.m_grid[floor(actual_x/40)][floor(actual_y/40)])):
            mygrid.m_grid[floor(lx/40)][floor(ly/40)].Erase()
            mygrid.m_grid[floor(actual_x/40)][floor(actual_y/40)].Fill()

        myObjects[obj.session_id].last_x = actual_x
        myObjects[obj.session_id].last_y = actual_y

    def remove_tuio_object(self, obj):
        print("Object " ,obj.session_id, " of class ",obj.class_id," was deleted.")
        lx= myObjects[obj.session_id].last_x
        ly= myObjects[obj.session_id].last_y
        mygrid.m_grid[floor(lx/40)][floor(ly/40)].Erase()
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