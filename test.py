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
    #Gear: cansend vcan0 115#ABCDEFABCDEF02FF
    def run(self):
        while self.running:
            message = self.bus.recv()
            if message.arbitration_id == 277 and self.pageName == "MainWindow":  # Adjust this ID according to your CAN message
                self.updateLabelMain(str(message.data)[39:40])
                

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
        # self.button= Button(self, text="Change1", command = self.showSecondWindow, 
        #                     height=0, width=0, bd=0,  bg='black', fg='black', highlightthickness=0, 
        #                     activebackground="black", activeforeground="black" )
        # self.button.pack()
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
        self.counter="N"
        self.size()
        self.createWidgets()
        self.show_frame=master.show_frame

    def showMainWindow(self):
        self.show_frame("MainWindow")

    def createWidgets(self):
        parameters = ["Parameter1", "Parameter2", "Parameter3", "Parameter4", "Parameter5"]

            
        self.label1=Label(self, text="Parameter1:",font=("Arial", 24), bg = "black", fg = "white")
        self.label1.place(relx = 0, x = 10, y = 20)
        self.label2=Label(self, text="Parameter2:",font=("Arial", 24), bg = "black", fg = "white")
        self.label2.place(relx = 0, x = 10, y = 80)
        self.label3=Label(self, text="Parameter3:",font=("Arial", 24), bg = "black", fg = "white")
        self.label3.place(relx = 0, x = 10, y = 140)
        self.label4=Label(self, text="Parameter4:",font=("Arial", 24), bg = "black", fg = "white")
        self.label4.place(relx = 0, x = 10, y = 200)
        self.label5=Label(self, text="Parameter5:",font=("Arial", 24), bg = "black", fg = "white")
        self.label5.place(relx = 0, x = 10, y = 260)

       

        # self.button= Button(self, text="Change2", command = self.showMainWindow)
        # self.button.pack()
        # self.label_text = StringVar()
        # self.label_text.set(str(self.counter))
        # label = Label(self, textvariable=self.label_text, font=("Arial", 200), bg='black', fg='white')
        # label.pack(padx=0, pady=0)

    def updateLabel(self, data):
        self.label_text.set(str(data))
        
    


class WindowManager(Tk):
    def __init__(self):
        super().__init__()
        self.title("Tkinter App")
        self.geometry("480x320")
        self.resizable(False, False)
        self.current_frame=None
        self.configure(bg="black")
        self.overrideredirect(True) #Hide title bar
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






