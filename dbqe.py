import tkinter as tk
from tkinter import ttk as ttk
from datetime import datetime
import sqlite3, glob, platform, json, os

SCREEN_MIN_HEIGHT = 440
SCREEN_MIN_WIDTH = 600

LOG_QUERIES_ONSUCCES = True
SAVE_RESULT_AS_JSON = True

fontSmall = 10 # 20
fontMedium = 12 # 24
fontLarge = 14 # 28

class ScrollFrame(tk.Frame):
    def __init__(self, parent, scrollDirection="v"):
        super().__init__(parent) # create a frame (self)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
        self.viewPort = tk.Frame(self.canvas)                    #place a frame on the canvas, this frame will hold the child widgets 
                
        if scrollDirection.lower().count("h") == 1:
            self.hsb = tk.Scrollbar(self, orient="horizontal", command=self.canvas.xview) #place a scrollbar on self 
            self.canvas.configure(xscrollcommand=self.hsb.set)                          #attach scrollbar action to scroll of canvas
            self.hsb.pack(side="bottom", fill="x")  

        if scrollDirection.lower().count("v") == 1:
            self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
            self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas
            self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self                                     #pack scrollbar to right of self
         
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw", tags="self.viewPort") #add view port frame to canvas

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       #bind an event whenever the size of the canvas frame changes.
            
        self.viewPort.bind('<Enter>', self.onEnter)                                 # bind wheel events when the cursor enters the control
        self.viewPort.bind('<Leave>', self.onLeave)                                 # unbind wheel events when the cursorl leaves the control

        self.onFrameConfigure(None)                                                 #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize
    
    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.


    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.

    def onMouseWheel(self, event):                                                  # cross platform scroll wheel event
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                self.canvas.yview_scroll( 1, "units" )
    
    def onEnter(self, event):                                                       # bind wheel events when the cursor enters the control
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                                       # unbind wheel events when the cursorl leaves the control
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")



def fillDBContainer():
    availibleDBs = glob.glob("*.db")
    if len(availibleDBs) == 0:
        showMessageResult('No Databases Found', "red")
        clearFrame(queryContainer)
    else:
        if len(availibleDBs) > 1:
            dbIndicator = ttk.Combobox(dbFrame, values=availibleDBs, textvariable=selectedDB, state="readonly", font=("bold", fontMedium))
            dbIndicator.bind("<<ComboboxSelected>>", lambda *args: showTables())
        else:
            dbIndicator = tk.Label(dbFrame, fg="black", textvariable=selectedDB ,font=("bold", fontMedium))
        
        dbIndicator.pack(side=tk.TOP, anchor="w")
        tableContent.pack(side=tk.TOP, anchor="w")
        selectedDB.set(availibleDBs[0])
        showTables()

    # tk.Button(dbFrame, text='New DB', command=execQuery, bg="lightgray").pack(pady=5, anchor="w")

def showTables():
    clearFrame(tableContent)
    conn = None
    try:
        conn = sqlite3.connect(selectedDB.get())
        cursor=conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
        data = cursor.fetchall()
        
        if len(data) > 0:
            for table in data:
                tk.Label(tableContent, fg="black", text=" - " + table[0] ,font=("bold", fontSmall)).pack(side=tk.TOP, anchor="w")
        else:
            tk.Label(tableContent, fg="red", text="no tables found" ,font=("bold", fontSmall, "italic")).pack(side=tk.TOP, anchor="w")

    except Exception as exceptionError:
        showMessageResult(repr(exceptionError), "red")

    reorganizeLayout()
    conn.close()

def execQuery():
    print('starting database request')
    loadingLabel = tk.Label(root, text='Loading...', fg='black', font=('Arial',fontLarge,'bold'))
    loadingLabel.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    root.update()

    dbName = selectedDB.get()
    conn = sqlite3.connect(dbName)
    query = queryInput.get("1.0", "end-1c")

    if len(query) < 8:  
        showMessageResult('"{}" is not a query'.format(query), "red")
    else:
        try:
            print('executing query')
            cursor=conn.cursor()
            cursor.execute(query)
            conn.commit()
            print('fetching data')
            data = cursor.fetchall()

            timestamp = datetime.now().strftime("%H:%M:%S")

            if LOG_QUERIES_ONSUCCES == True:
                print('logging query')

                if not os.path.exists('querylog'):
                    os.makedirs('querylog')

                filename = datetime.now().strftime("%d_%m_%Y")
                f = open("querylog/"+filename+".log", "a")
                f.write(query+'; #'+timestamp+'@'+dbName+'\n')
                f.close()

            if (len(data) == 0 and cursor.description == None):
                showMessageResult("Query Excecuted", "green")
            else:
                columns = [description[0] for description in cursor.description]
                showTableResult(columns, data)

                if SAVE_RESULT_AS_JSON == True:
                    saveResult(query, columns, data, timestamp.replace(':',''))

        except sqlite3.OperationalError as dberror:
            showMessageResult(dberror, "red")
        except Exception as exceptionError:
            showMessageResult(repr(exceptionError), "red")
    
    conn.close()
    loadingLabel.destroy()
    showTables()
    print('database request ended')

def clearFrame(container):
    for widget in container.winfo_children():
        widget.destroy()

def showMessageResult(msg, color="black"):
    clearFrame(resultContainer)
    tk.Label(resultContainer, text=msg, fg=color, font=('Arial',fontLarge,'bold')).pack()

def saveResult(query, columns, data, filename):
    print('saving result')
    if not os.path.exists('datalog'):
        os.makedirs('datalog')

    dirname = datetime.now().strftime("%d_%m_%Y")
    if not os.path.exists('datalog/'+dirname):
        os.makedirs('datalog/'+dirname)

    total_rows = len(data)
    total_columns = len(columns)

    result = []
    for i in range(total_rows):
        entry = {}
        for j in range(total_columns):
            entry[columns[j]] = data[i][j]
        result.append(entry)

    json_object = json.dumps({
        'query' : query,
        'resultcount' : total_rows,
        'result' : result
    }, indent=4)

    f = open("datalog/"+dirname+"/"+filename+".json", "w")
    f.write(json_object)
    f.close()

def showTableResult(columns, data):
    clearFrame(resultContainer)
    print('printing result')
    
    total_rows = len(data)
    total_columns = len(columns)

    for i in range(total_columns):
        cell = tk.Label(resultContainer, text=columns[i], fg='blue', font=('Arial',fontLarge,'bold'))
        cell.grid(row=1, column=i, sticky="W")

    for i in range(total_rows):
        for j in range(total_columns):
            content = data[i][j]
            fgCol = "black"
            font = ('Arial',fontMedium)
            
            if content == None:
                content = 'NULL'
                fgCol = "red"
                font = ('Arial',fontMedium,'italic')
            
            cell = tk.Label(resultContainer, text=content, fg=fgCol, font=font)
            cell.grid(row=i+2, column=j, sticky="WS")

    
    resultContainer.update()

def onResizeWindow(event):
    if str(event.widget) == '.':
        reorganizeLayout()

def updateQueryInputHeight():
    height = queryInput.tk.call((queryInput, "count", "-update", "-displaylines", "1.0", "end"))
    if height < 5: height = 5
    if height > 25: height = 25
    queryInput.configure(height=height)
    reorganizeLayout()

def reorganizeLayout():
    root.update()
    dbFrame.update()

    resultContainerFrame.canvas.configure(width=root.winfo_width()-28)
    queryContainer.place_configure(x=dbFrame.winfo_width()+8, 
                                   width=root.winfo_width() - dbFrame.winfo_width()- 12)
    queryContainer.update()
    queryInput.configure(width=queryContainer.winfo_width() - 16)

    maxHeight = dbFrame.winfo_height() if dbFrame.winfo_height() > queryContainer.winfo_height() else queryContainer.winfo_height()
    gParts = root.winfo_geometry().lower().split('x')

    screenHeight = int(gParts[1].split("+")[0])
    leftoverHeight = (screenHeight - maxHeight - 13)
    resultContainerHeight = 204 if leftoverHeight < 204 else leftoverHeight
    resultContainerFrame.place_configure(height=resultContainerHeight)

    resultContainerFrame.update()
    rootHeight = (maxHeight+resultContainerFrame.winfo_height()+13)
    rootWidth = gParts[0] if int(gParts[0]) > SCREEN_MIN_WIDTH else SCREEN_MIN_WIDTH

    root.geometry("{}x{}".format(rootWidth, rootHeight))
    resultContainerFrame.place_configure(y=maxHeight+8)
    


root = tk.Tk()
root.title(".db Query Exexutor")
root.configure(bg="lightgray")
root.geometry("{}x{}".format(SCREEN_MIN_WIDTH,SCREEN_MIN_HEIGHT))
root.bind('<Key>', lambda *args: updateQueryInputHeight())
#root.bind('<Configure>', onResizeWindow)

selectedDB = tk.StringVar()
dbFrame = tk.Frame(root, bg="white")
dbFrame.place(x=3, y=3)
tableContent = tk.Frame(dbFrame)

queryContainer = tk.Frame(root, padx=5)
queryContainer.place(y=3)

resultContainerFrame = ScrollFrame(root, "v")
resultContainerFrame.canvas.configure(width=660)
resultContainerFrame.place(x=3)
resultContainer = resultContainerFrame.viewPort

queryInput = tk.Text(queryContainer, height=5, highlightbackground = "gray", highlightcolor= "gray", font=('Arial', fontLarge))
queryInput.pack(pady=5)
tk.Button(queryContainer, text='Execute Query', command=execQuery, bg="lightgray", font=('Arial', fontSmall)).pack(pady=5)

fillDBContainer()
root.mainloop()
