from tkinter import *
import can
import threading

class CanListener(threading.Thread):
    def __init__(self, updateLabel, pageName):
        super().__init__()
        self.updateLabelMain = updateLabel
        self.bus = can.interface.Bus(channel='vcan0', bustype='socketcan', bitrate = 500000)
        self.running = True
        self.pageName=pageName
        self.parameterIds=[1520, 1522, 1523, 152, 277]
    #Gear: cansend vcan0 115#ABCDEFABCDEF02FF
    def run(self):
        while self.running:
            message = self.bus.recv()
            
            if message.arbitration_id == 277 and self.pageName == "MainWindow":  # Adjust this ID according to your CAN message
                self.updateLabelMain(str(message.data)[39:40])
            if message.arbitration_id in self.parameterIds and self.pageName == "SecondWindow":
                self.updateLabelMain(message)

                

    def stop(self):
        self.running = False
        self.bus.shutdown()


class MainWindow(Frame):
    def __init__(self, master):
        super().__init__(master, bg='black', padx=0, pady=0)
        self.master=master
        self.counter="N"
        self.createWidgets()
        self.show_frame=master.show_frame
    
    def showSecondWindow(self):
        self.show_frame("SecondWindow")

    def createWidgets(self):
        self.label_text = StringVar()
        self.label_text.set(str(self.counter))
        label = Label(self, textvariable=self.label_text, font=("Arial", 200), bg='black', fg='white')
        label.pack(padx=0, pady=0)
        

    def updateLabel(self, data):
        if data == "0":
            self.label_text.set(str("N"))
        else: 
            self.label_text.set(str(data))  
    

class SecondWindow(Frame):
    def __init__(self, master):
        super().__init__(master, bg='black', padx=0, pady=0, width=480, height=320)
        self.master=master
        self.initial="0"
        self.size()
        self.createWidgets()
        self.show_frame=master.show_frame
        
    def showMainWindow(self):
        self.show_frame("MainWindow")

    def createWidgets(self):       
        self.label1=Label(self, text="RPM:",font=("Arial", 24), bg = "black", fg = "white")
        self.label1.place(relx = 0, x = 10, y = 20)
        self.label2=Label(self, text="Coolant:",font=("Arial", 24), bg = "black", fg = "white")
        self.label2.place(relx = 0, x = 10, y = 80)
        self.label3=Label(self, text="Parameter3:",font=("Arial", 24), bg = "black", fg = "white")
        self.label3.place(relx = 0, x = 10, y = 140)
        self.label4=Label(self, text="Parameter4:",font=("Arial", 24), bg = "black", fg = "white")
        self.label4.place(relx = 0, x = 10, y = 200)
        self.label5=Label(self, text="Parameter5:",font=("Arial", 24), bg = "black", fg = "white")
        self.label5.place(relx = 0, x = 10, y = 260)

        self.valueVar1 = StringVar()
        self.valueVar1.set(str(self.initial))
        self.valueStr1 = Label(self, textvariable=self.valueVar1, font=("Arial", 24), bg='black', fg='white')
        self.valueStr1.place(relx=0, x= 10 + self.label1.winfo_reqwidth() + 20 , y = 20)

        
        self.valueVar2 = StringVar()
        self.valueVar2.set(str(self.initial))
        self.valueStr2 = Label(self, textvariable=self.valueVar2, font=("Arial", 24), bg='black', fg='white')
        self.valueStr2.place(relx=0, x= 10 + self.label2.winfo_reqwidth() + 20 , y = 80)
        
        # self.valueVar3 = StringVar()
        # self.valueVar3.set(str(self.initial))
        # self.valueStr3 = Label(self, textvariable=self.valueVar3, font=("Arial", 24), bg='black', fg='white')
        # self.valueStr3.place(relx=0, x= 10 + self.label1.winfo_reqwidth() + 20 , y = 20)
        
        # self.valueVar4 = StringVar()
        # self.valueVar4.set(str(self.initial))
        # self.valueStr4 = Label(self, textvariable=self.valueVar4, font=("Arial", 24), bg='black', fg='white')
        # self.valueStr4.place(relx=0, x= 10 + self.label1.winfo_reqwidth() + 20 , y = 20)
        
        # self.valueVar5 = StringVar()
        # self.valueVar5.set(str(self.initial))
        # self.valueStr5 = Label(self, textvariable=self.valueVar5, font=("Arial", 24), bg='black', fg='white')
        # self.valueStr5.place(relx=0, x= 10 + self.label1.winfo_reqwidth() + 20 , y = 20)
        
    def updateLabel(self, message):
        #cansend vcan0 5f0#041d080008001375
        if message.arbitration_id == 1520:
            self.valueVar1.set(self.getDataFromMessage(message, 6, 2))
        #cansend vcan0 5f2#03e8037502bc0650
        if message.arbitration_id == 1522:
            self.valueVar2.set(round(self.convertFtoC(self.getDataFromMessage(message, 6, 2)), 1))

    def convertFtoC(self, degree):
        return (((degree/10)-32)/9)*5
    
    def getDataFromMessage(self, message, position, DL):
        return int((str(message)[78-3+position*3:78-3+position*3+DL*3]).replace(" ",  ""), 16)#!-3 for Rx in frame, change if necessary

        
    


class WindowManager(Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter App")
        self.geometry("480x320")
        self.resizable(False, False)
        self.current_frame=None
        self.configure(bg="black")
        #self.overrideredirect(True) #Hide title bar
        self.show_frame("MainWindow")
        self.bind("<KeyPress-a>", lambda event: self.show_frame("MainWindow"))
        self.bind("<KeyPress-s>", lambda event: self.show_frame("SecondWindow"))
    
        
        
    def show_frame(self, page_name):
        if self.current_frame is not None:
            self.current_frame.destroy()
        if page_name == "MainWindow":
            self.current_frame = MainWindow(self)
        elif page_name == "SecondWindow":
            self.current_frame = SecondWindow(self)
        self.current_frame.pack()
        self.can_listener= CanListener(self.current_frame.updateLabel, page_name)
        self.can_listener.start()


if __name__ == "__main__":
    app = WindowManager()
    app.mainloop()




# myLabel1= Label(root, text="Hello world!")
# myLabel2= Label(root, text="Hello world2!")

# myLabel1.grid(row =0, column = 0)
# # myLabel2.grid(row =1, column = 0)


# frame = LabelFrame(root, text="Frame  ")
# frame.pack(padx=10, pady=10)


# # def click():
# #     myLabel = Label(root, text="dsadsa")
# #     myLabel.pack()

# myButton = Button(frame, text="Button", padx=50, pady=50)
# myButton.pack()


# root = Tk()


# string=StringVar()
# string.set(str("Da"))

# label1 = Label(root, textvariable=string)

# def update_label(data):
#     string.set(str(data))

# label1.pack()
# can_listener = CanListener(update_label)
# can_listener.start()
    

# root.mainloop()






