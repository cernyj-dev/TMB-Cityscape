from pythontuio import TuioClient
from pythontuio import TuioListener
from threading import Thread
from decimal import Decimal
import os
import tkinter as tk

w=640
h=480
plocha = tk.Canvas(width=w,height=h)
plocha.pack()
#--------------------------------------------------------------------
#
#--------------------------------------------------------------------
class MyObject():
    def __init__(self,class_id,x,y,vx,vy):
        self.class_id = class_id
        self.myImage = []
        #---------------
        #   We calculate the vector between our 2 points
        #--------------
        vec_x = (vx - x)
        vec_y = (vy - y)
        #---------------
        #   We then find the vector perpendicular to our previous vector
        #--------------
        inv_vec_x = - vec_y
        inv_vec_y = vec_x
        #---------------
        #   We can then add these vector values to our known coordinates to get the remaining 2 points of the marker
        #--------------
        rl_corner_x = (vx+inv_vec_x)
        rl_corner_y = (vy+inv_vec_y)
        ll_corner_x = (x+inv_vec_x)
        ll_corner_y = (y+inv_vec_y)

        self.myImage.append(plocha.create_line(x,y,vx,vy,rl_corner_x,rl_corner_y,ll_corner_x,ll_corner_y,x,y,width=2))
        self.myImage.append(plocha.create_oval(vx-2,vy-2,vx+2,vy+2,fill="blue"))
        self.myImage.append(plocha.create_oval(x-2,y-2,x+2,y+2,fill="red"))

    def delete(self):
        for i in self.myImage:
            plocha.delete(i)
    def reDraw(self,x,y,vx,vy):
        self.myImage = []

        vec_x = (vx - x)
        vec_y = (vy - y)

        inv_vec_x = - vec_y
        inv_vec_y = vec_x

        rl_corner_x = (vx+inv_vec_x)
        rl_corner_y = (vy+inv_vec_y)
        ll_corner_x = (x+inv_vec_x)
        ll_corner_y = (y+inv_vec_y)

        self.myImage.append(plocha.create_line(x,y,vx,vy,rl_corner_x,rl_corner_y,ll_corner_x,ll_corner_y,x,y,width=2))
        self.myImage.append(plocha.create_oval(vx-2,vy-2,vx+2,vy+2,fill="blue"))
        self.myImage.append(plocha.create_oval(x-2,y-2,x+2,y+2,fill="red"))
#--------------------------------------------------------------------
#
#--------------------------------------------------------------------
# Dictionary for all obejcts on screen
myObjects = {}
# obj.position - goes from 0 to 1, 0 being total left/top and 1 being total right/bottom of camera
# We use Decimal for more precise calculation of floats.
class MyListener(TuioListener):
    def add_tuio_object(self,obj):
        x,y = obj.position
        vx,vy = obj.velocity # we store our second corner into the predefined velocity vector
        
        x,vx= Decimal(x),Decimal(vx)
        y,vy= Decimal(y),Decimal(vy)

        actual_x=Decimal(x*w)
        actual_y=Decimal(y*h)
        actual_vx=Decimal(vx*w)
        actual_vy=Decimal(vy*h)
        #   ------------------------------------------------------------------------------------------------------------------------
        #   Now actual_x and actual_y stores the coordinates of the left upper corner of the marker
        #   and vx,vy stores the coordinates of the right upper corner of the marker. We can use this to calculate the remaining 2
        #   points of the marker.
        #   ------------------------------------------------------------------------------------------------------------------------
        myObjects.update({obj.session_id : MyObject(obj.class_id,actual_x,actual_y,actual_vx,actual_vy)})

    def update_tuio_object(self, obj):
        #print("object has [x,y] = ", obj.position," and its vector = ", obj.velocity )
        x,y = obj.position
        vx,vy = obj.velocity 
        x,vx= Decimal(x),Decimal(vx)
        y,vy= Decimal(y),Decimal(vy)
        actual_x=Decimal(x*w)
        actual_y=Decimal(y*h)
        actual_vx=Decimal(vx*w)
        actual_vy=Decimal(vy*h)

        myObjects[obj.session_id].delete()
        myObjects[obj.session_id].reDraw(actual_x,actual_y,actual_vx,actual_vy)

    def remove_tuio_object(self, obj):
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
