from pythontuio import TuioClient
from pythontuio import TuioListener
from threading import Thread
from decimal import Decimal
import os
import tkinter as tk

w=640
h=480
scale = 20 # relative scale of shown objects
plocha = tk.Canvas(width=w,height=h)
plocha.pack()


class MyObject():
    def __init__(self,class_id,x,y):
        self.class_id = class_id
        self.last_x = x
        self.last_y = y
        self.image = plocha.create_rectangle(x-scale,y-scale,x+scale,y+scale,fill="blue")
    def move(self,x,y):
        plocha.move(self.image,x,y)


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
        myObjects[obj.session_id].last_x = actual_x
        myObjects[obj.session_id].last_y = actual_y

    def remove_tuio_object(self, obj):
        print("Object " ,obj.session_id, " of class ",obj.class_id," was deleted.")
        plocha.delete(myObjects[obj.session_id].image)
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