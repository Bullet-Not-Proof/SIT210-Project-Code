import urllib.request
import json
import textwrap
import tkinter as tk
from tkinter import *
from tkinter import ttk
import cv2
from pyzbar import pyzbar

books = []
seperator = "/s"

def bookLookUp(isbn):
    base_api_link = "https://www.googleapis.com/books/v1/volumes?q=isbn:"

    with urllib.request.urlopen(base_api_link + isbn) as f:
        text = f.read()

    decoded_text = text.decode("utf-8")
    obj = json.loads(decoded_text)
    volume_info = obj["items"][0]
    
    try:
        title = volume_info["volumeInfo"]["title"]
    except:
        title = "unknown"
    try:
        summary = textwrap.fill(volume_info["searchInfo"]["textSnippet"], width=65)
    except:
        summary = "unknown"
    try:
        authors = obj["items"][0]["volumeInfo"]["authors"]
        authors = ",".join(authors)
    except:
        authors = "unknown"
    try:
        pages = volume_info["volumeInfo"]["pageCount"]
    except:
        pages = "unknown"
    try:
        language = volume_info["volumeInfo"]["language"]
    except:
        language = "unknown"
    
    book = {
        "isbn": isbn,
        "title": title,
        "summary": summary,
        "author": authors,
        "pageCount": pages,
        "language": language
    }
    return(book)

def read_barcodes(frame):
    barcodes = pyzbar.decode(frame)
    barcodeInfos = []
    for barcode in barcodes:
        x, y , w, h = barcode.rect
        barcodeInfo = barcode.data.decode('utf-8')
        cv2.rectangle(frame, (x, y),(x+w, y+h), (0, 255, 0), 2)
        
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, barcodeInfo, (x + 6, y - 6), font, 2.0, (255, 255, 255), 1)
        barcodeInfos.append(barcodeInfo)
    return frame, barcodeInfos

def barcodeUI():
    camera = cv2.VideoCapture(0)
    ret, frame = camera.read()
    while ret:
        ret, frame = camera.read()
        frame, barcodes = read_barcodes(frame)
        if (len(barcodes) >= 1):
            camera.release()
            cv2.destroyAllWindows()
            return barcodes[0]
        cv2.imshow('Barcode/QR code reader', frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    camera.release()
    cv2.destroyAllWindows()
    
class mainUI( Frame ):
    def __init__( self ):
        
        tk.Frame.__init__(self)
        self.pack()
        self.master.title("LibraryUI")
        
        ttk.Style().configure('Treeview', rowheight=50)
        
        self.treeView = ttk.Treeview(self)
        self.treeView['columns']=('isbn', 'title', 'summary', 'author', 'pageCount', 'language')
        self.treeView.grid( row = 0, column = 1, columnspan = 2, sticky = W+E+N+S )
        
        self.treeView.column('#0', width=0, stretch=NO)
        self.treeView.column('isbn', anchor=CENTER, width=80)
        self.treeView.column('title', anchor=CENTER, width=200)
        self.treeView.column('summary', anchor=CENTER, width=450)
        self.treeView.column('author', anchor=CENTER, width=80)
        self.treeView.column('pageCount', anchor=CENTER, width=60)
        self.treeView.column('language', anchor=CENTER, width=80)
        
        self.treeView.heading('#0', text='', anchor=CENTER)
        self.treeView.heading('isbn', text='ISBN', anchor=CENTER)
        self.treeView.heading('title', text='Title', anchor=CENTER)
        self.treeView.heading('summary', text='Summary', anchor=CENTER)
        self.treeView.heading('author', text='Author', anchor=CENTER)
        self.treeView.heading('pageCount', text='Pages', anchor=CENTER)
        self.treeView.heading('language', text='Language', anchor=CENTER)
        
        self.loadList()
        
        self.button1 = Button( self, text = "Scan Book", width = 25, command = self.captureBarcode )
        self.button1.grid( row = 1, column = 1, columnspan = 2, sticky = W+E+N+S )
        
        self.button2 = Button( self, text = "Delete Item", width = 25, command = self.deleteItem )
        self.button2.grid( row = 2, column = 1, columnspan = 2, sticky = W+E+N+S )
        
        self.button2 = Button( self, text = "Save List", width = 25, command = self.saveList )
        self.button2.grid( row = 3, column = 1, columnspan = 2, sticky = W+E+N+S )
        
    def captureBarcode(self):
        addBook = True
        bookToAdd = bookLookUp(barcodeUI())
        for book in books:
            if (book["isbn"] == bookToAdd["isbn"]):
                addBook = False
        if(addBook):
            books.append(bookToAdd)
        self.printBookList()
            
    def printBookList(self):
        for item in self.treeView.get_children():
            self.treeView.delete(item)
        for i in range(len(books)):
            self.treeView.insert(parent='', index=i, iid=i, text='', values=(books[i]['isbn'],
                                                                             books[i]['title'],
                                                                             books[i]['summary'],
                                                                             books[i]['author'],
                                                                             books[i]['pageCount'],
                                                                             books[i]['language']))
        
    
    def deleteItem(self):
        books.pop(int(self.treeView.focus()))
        self.printBookList()
    
    def saveList(self):
        file = open("SavedValues.txt", "w")
        lines = ""
        for i in books:
            line = i['isbn'] + seperator + i['title'] + seperator + i['summary'] + seperator + i['author'] + seperator + str(i['pageCount']) + seperator + i['language']
            #print([line])
            line = line.replace("\n", "/n")
            #print([line])
            line += "\n"
            lines += line
        file.write(lines)
        file.close()
    
    def loadList(self):
        file = open("SavedValues.txt", "r")
        lines = file.readlines()
        #print(lines)
        for line in lines:
            line = line.replace("/n", "\n")
            line = line.split(seperator)
            book = {
                "isbn": line[0],
                "title": line[1],
                "summary": line[2],
                "author": line[3],
                "pageCount": line[4],
                "language": line[5]
            }
            books.append(book)
        file.close()
        self.printBookList()
        
def main(): 
    mainUI().mainloop()
    
if __name__ == '__main__':
    main()