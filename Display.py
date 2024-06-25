from tkinter import *
import can
import threading
#import pyautogui
import time
import subprocess
# import RPi.GPIO as GPIO
from DeltaTime import DeltaTime 

class CanListener(threading.Thread):
    def __init__(self, deltaTime, updateLabel, pageName, errorFrame):
        super().__init__()
        self.updateLabelMain = updateLabel
        self.errorFrame = errorFrame
        self.running = True
        self.pageName = pageName
        self.parameterIds = [1520, 1522, 1523, 152, 277, 0x116]
        self.bus = None
        self.deltaTime = deltaTime

    def run(self):
        try:
            self.bus = can.interface.Bus(channel='vcan0', bustype='socketcan', bitrate=500000)
            while self.running:
                message = self.bus.recv()
                print(message)
                self.process_message(message)
        except can.CanError as e:
            print("Error receiving CAN message:", e)
            
            # Handle error here

    def process_message(self, message):
        if message.arbitration_id in self.parameterIds:
            print(message)
            if message.arbitration_id == 0x116: 
                delta = self.deltaTime.process_message_from_string(message)
                print(delta)
                self.updateLabelMain(delta, 1)
                print("If 116")
                
            if message.arbitration_id == 1520 and self.pageName== "SecondWindow":
                parameter = 1
                message= self.getDataFromMessage(message, 6, 2)
                self.updateLabelMain(message, parameter, 1)
            
            elif message.arbitration_id == 1522:
                message = round(self.convertFtoC(self.getDataFromMessage(message, 6, 2)), 1)
                parameter = 2
                if message > 105:
                    if self.pageName == "MainWindow":
                        print("Test")
                        self.errorFrame(self.pageName, "CLT TEMP", message)
                    elif self.pageName == "SecondWindow":
                        self.updateLabelMain(message, parameter, 1)
                elif message <= 100 and self.pageName == "SecondWindow":
                    self.updateLabelMain(message, parameter, 0)
                    
            elif message.arbitration_id ==1523:
                if self.pageName == "SecondWindow":
                    message1 = round(self.getDataFromMessage(message, 0, 2)/10, 2)
                    parameter = 3
                    self.updateLabelMain(message1, parameter, 0)
                message2 = round(self.getDataFromMessage(message, 2, 2)/10, 2)
                parameter=5
                if message2 < 10:
                    if self.pageName == "MainWindow":
                        self.errorFrame(self.pageName, "BATT VOL LOW", message2)
                    elif self.pageName == "SecondWindow":
                        self.updateLabelMain(message, parameter, 1)
                elif message2 > 15:
                    if self.pageName == "MainWindow":
                        self.errorFrame(self.pageName, "BATT VOL HIGH", message2)
                    elif self.pageName== "SecondWindow":
                        self.updateLabelMain(message2, parameter, 1)
                else:
                    self.updateLabelMain(message2, parameter, 0)
            elif message.arbitration_id == 277:
                print(message.arbitration_id)
                if self.pageName=="SecondWindow":
                    parameter = 4
                    if self.getDataFromMessage(message, 0, 2)>300:
                        self.updateLabelMain(True,parameter,1)
                    else: 
                        self.updateLabelMain(False, parameter, 0)
                elif self.pageName=="MainWindow":
                    self.updateLabelMain(self.getDataFromMessage(message, 6, 1), 0)

    def stop(self):
        self.running = False
        if self.bus:
            self.bus.shutdown()      
        
    def convertFtoC(self, degree):
        return (((degree / 10) - 32) / 9) * 5

    def getDataFromMessage(self, message, position, DL):
        #return int((str(message)[78 - 3 + position * 3:78 - 3 + position * 3 + DL * 3]).replace(" ", ""), 16)
        return int((str(message)[76 + position * 3:76 + position * 3 + DL * 3]).replace(" ", ""), 16)






class MainWindow(Frame):

    def __init__(self, master):

        super().__init__(master, bg='black', padx=0, pady=0, width=1280, height=720)

        self.master=master

        self.counter="N"
        
        self.size()

        self.createWidgets()

        self.show_frame=master.show_frame

    

    def showSecondWindow(self):

        self.show_frame("SecondWindow")



    def createWidgets(self):

        self.label_text = StringVar()

        self.label_text.set(str(self.counter))

        label = Label(self, textvariable=self.label_text, font=("Arial", 550), bg='black', fg='white')

        label.place(x = 350, y = 10)
        self.canvas_width = 500
        self.canvas_height = 50
        self.deltaTimeRectangle = Canvas(width=self.canvas_width, height=self.canvas_height)
        
        self.deltaTimeRectangle.place(x=375, y=40)
        
        self.labelDelta = StringVar()
        self.labelDelta.set('0.0')
        self.deltaLabel = Label(self, textvariable=self.labelDelta, font=("Arial", 50), bg='black', fg='red')
        self.deltaLabel.place(x=950, y=30)
        
    def draw_filled_rectangle(self, fillPercentage):
        print(fillPercentage)
        self.deltaTimeRectangle.delete("all") 
        # if fillPercentage < int(0) and fillPercentage < int(-1):
        #     fillPercentage = int(-1)
        # if fillPercentage > int(0) and fillPercentage > int(1):
        #     fillPercentage = int(1)
        
        # Draw background rectangle
        self.deltaTimeRectangle.create_rectangle(0, 0, self.canvas_width, self.canvas_height, fill="white", outline="black")
        
        # Calculate filled rectangle dimensions
        center_x = self.canvas_width / 2
        fill_width = self.canvas_width * fillPercentage / 2
        
        # Draw filled rectangles
        if fillPercentage < 0:
            self.deltaTimeRectangle.create_rectangle(center_x, 0, center_x + fill_width, self.canvas_height, fill="red", outline="")
        else:
            fill_width = fill_width * -1
            self.deltaTimeRectangle.create_rectangle(center_x - fill_width, 0, center_x, self.canvas_height, fill="green", outline="")
    
        

    def updateLabel(self, data, parameter):
        if parameter == 0:
            if data == "0":

                self.label_text.set(str("N"))

            else: 

                self.label_text.set(str(data))  
        if parameter == 1:
            self.labelDelta.set(data)
            self.draw_filled_rectangle(data)
            
    



class SecondWindow(Frame):

    def __init__(self, master):

        super().__init__(master, bg='black', padx=0, pady=0, width=1280, height=720)

        self.master=master

        self.initial="0"

        self.size()

        self.createWidgets()

        self.show_frame=master.show_frame
        

        

    def showMainWindow(self):
        self.show_frame("MainWindow")



    def createWidgets(self):       

        self.label1=Label(self, text="RPM:",font=("Arial", 84), bg = "black", fg = "white")

        self.label1.place(relx = 0, x = 10, y = 20)

        self.label2=Label(self, text="Coolant:",font=("Arial", 84), bg = "black", fg = "white")

        self.label2.place(relx = 0, x = 10, y = 160)

        self.label3=Label(self, text="TPS:",font=("Arial", 84), bg = "black", fg = "white")

        self.label3.place(relx = 0, x = 10, y = 300)

        self.label4=Label(self, text="BSPD:",font=("Arial", 84), bg = "black", fg = "white")

        self.label4.place(relx = 0, x = 10, y = 440)

        self.label5=Label(self, text="Battery Voltage:",font=("Arial", 84), bg = "black", fg = "white")

        self.label5.place(relx = 0, x = 10, y = 580)



        self.valueVar1 = StringVar()

        self.valueVar1.set(str(self.initial))

        self.valueStr1 = Label(self, textvariable=self.valueVar1, font=("Arial", 84), bg='black', fg='white')

        self.valueStr1.place(relx=0, x= 10 + self.label1.winfo_reqwidth() + 20 , y = 20)



        

        self.valueVar2 = StringVar()

        self.valueVar2.set(str(self.initial))

        self.valueStr2 = Label(self, textvariable=self.valueVar2, font=("Arial", 84), bg='black', fg='white')

        self.valueStr2.place(relx=0, x= 10 + self.label2.winfo_reqwidth() + 20 , y = 160)

        

        self.valueVar3 = StringVar()

        self.valueVar3.set(str(self.initial))

        self.valueStr3 = Label(self, textvariable=self.valueVar3, font=("Arial", 84), bg='black', fg='white')

        self.valueStr3.place(relx=0, x= 10 + self.label3.winfo_reqwidth() + 20 , y = 300)

        

        self.valueVar4 = StringVar()

        self.valueVar4.set("OFF")

        self.valueStr4 = Label(self, textvariable=self.valueVar4, font=("Arial", 84), bg='black', fg='white')

        self.valueStr4.place(relx=0, x= 10 + self.label4.winfo_reqwidth() + 20 , y = 440)

        

        self.valueVar5 = StringVar()

        self.valueVar5.set(str(self.initial))

        self.valueStr5 = Label(self, textvariable=self.valueVar5, font=("Arial", 84), bg='black', fg='white')

        self.valueStr5.place(relx=0, x= 10 + self.label5.winfo_reqwidth() + 20 , y = 580)

        

    def updateLabel(self, message, parameter, err):
        if parameter == 1:
            self.valueVar1.set(message)
        
        if parameter == 2:
            self.valueVar2.set(message)
            if err == 1:
                self.valueStr2.config(fg='red')
            if self.valueStr2.cget("fg") == 'red' and err == 0:
                self.valueStr2.config(fg='white')
        if parameter == 3:
            self.valueVar3.set(message)        
        if parameter ==4:
            if err == 1:
                self.valueVar4.set("ON")
                self.valueStr4.config(fg='red')           
            if self.valueStr4.cget("fg") == 'red' and err == 0:
                self.valueStr4.config(fg='white')
                self.valueVar4.set("OFF")
        if parameter == 5:
            self.valueVar5.set(message)
            if err == 1:
                self.valueStr5.config(fg='red')
            if self.valueStr5.cget("fg") == 'red' and err == 0:
                self.valueStr5.config(fg='white')
            
        
            

        #cansend vcan0 5f0#041d080008001375
        # if message.arbitration_id == 1520:

        #     self.valueVar1.set(self.getDataFromMessage(message, 6, 2))

        # #cansend vcan0 5f2#03e8037502bc0650
        # 03 e8 03 75 02 bc 06 50

        # if message.arbitration_id == 1522:

        #     self.valueVar2.set(round(self.convertFtoC(self.getDataFromMessage(message, 6, 2)), 1))

        # #cansend vcan0 5f3#00770089004a0000

        # if message.arbitration_id == 1523:

        #     self.valueVar3.set(round(self.getDataFromMessage(message, 0, 2)/10, 2))

        #     self.valueVar5.set(round(self.getDataFromMessage(message, 2, 2)/10, 1))

        # if message.arbitration_id == 277:

        #     if self.getDataFromMessage(message, 0, 2)>300:

        #         self.valueVar4.set("ON")

        #     else: self.valueVar4.set("OFF")

    def convertFtoC(self, degree):
        return (((degree/10)-32)/9)*5

    def getDataFromMessage(self, message, position, DL):

        return int((str(message)[78-3+position*3:78-3+position*3+DL*3]).replace(" ",  ""), 16)#!-3 for Rx in frame, change if necessary

  

class ErrorWindow(Frame):
    def __init__(self, master, lastFrame, parameter, data=None):
        super().__init__(master, bg='black', padx=0, pady=0, width=1280, height=720)
        self.master= master
        self.size()
        self.parameter = parameter
        self.data = data
        print(data)
        self.show_frame=master.show_frame
        self.lastFrame=lastFrame
        self.createWidgets()
        self.timeout=3000
        self.toggle_color()
        self.after(self.timeout, self.show_last_frame)
        
        
    def createWidgets(self):
        self.label = Label(self, text = self.parameter, font=("Arial", 65), bg = "black", fg = "white")
        self.label.place(relx = 0.5, rely=0.3, anchor="center")
        
        self.label2 = Label(self, text = str(self.data), font=("Arial", 65), bg = "black", fg = "white")
        self.label2.place(relx = 0.5, rely=0.7, anchor="center")
        
    def show_last_frame(self):
        print("Show last frame from error window")
        self.show_frame("MainWindow")
        
        
    def toggle_color(self):
        if self.cget("bg") == "black":
            self.config(bg="white")
            self.label.config(fg="black", bg="white")
            self.label2.config(fg="black", bg="white")
        else:
            self.config(bg="black")
            self.label.config(fg="white", bg="black")
            self.label2.config(fg="white", bg="black")
        self.after(500, self.toggle_color)  # Toggle color every 500 milliseconds (0.5 seconds)

# class DeltaTime(threading.Thread):
#     def calculateDelta(self, message):
#         print(message)
#         return "Doamne fereste"


class WindowManager(Tk):

    def __init__(self):

        super().__init__()

        self.title("Tkinter App")

        self.geometry("1280x720")

        #self.resizable(False, False)

        self.current_frame=None

        self.configure(bg="black")
        self.can_listener = None
        self.deltaTime=DeltaTime()
        self.deltaTime.__init__()
        self.deltaTime.start()

        # self.overrideredirect(True) #Hide title bar
        self.pageName="SecondWindow"
        self.bind("<KeyPress-a>", lambda event: self.show_frame())
        self.bind("<KeyPress-s>", lambda event: self.show_frame())
        self.show_frame()
        
        # GPIO.setmode(GPIO.BOARD)
        # GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Example GPIO pin for Button A
        # GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        # GPIO.add_event_detect(13, GPIO.RISING, callback=lambda x: self.show_frame(), bouncetime=300)
        # GPIO.add_event_detect(15, GPIO.RISING, callback=lambda x: self.show_frame(), bouncetime=300)


    def show_frame(self):
        print("show frame function from window manager")   
        print(self.pageName)
        if self.current_frame is not None:
            self.current_frame.destroy()
            
        if self.can_listener is not None:  
            self.can_listener.stop()  
           

        if self.pageName == "MainWindow":
            self.current_frame = SecondWindow(self)
            self.pageName = "SecondWindow"
        

        elif self.pageName == "SecondWindow":
            self.current_frame = MainWindow(self)
            self.pageName = "MainWindow"

        self.current_frame.pack()
        self.can_listener= CanListener(self.deltaTime, self.current_frame.updateLabel, self.pageName, self.errorFrame)
        self.can_listener.start()
        
    def errorFrame(self, lastPage, parameter, data):
        if self.current_frame is not None:
            self.current_frame.destroy()
        if self.can_listener is not None:  
            self.can_listener.stop() 
        self.current_frame = ErrorWindow(self, lastPage, parameter, data)
        self.current_frame.pack()
        print("ErrorFrame function\n")
        
def disable_screensaver():
    subprocess.call(['xdg-screensaver', 'suspend', ':0'])
        




if __name__ == "__main__":
    disable_screensaver()
    app = WindowManager()
    app.mainloop()
