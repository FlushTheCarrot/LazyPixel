import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw, ImageTk

class PixelPaintingApp:
    def __init__(self, master):
        self.master = master
        master.title("Pixel Painting")

        self.create_menu()

        self.sidebar = tk.Frame(master)
        self.sidebar.pack(side="left", fill="y")

        self.color = "black"
        self.color_button = tk.Button(self.sidebar, text="Select Color", command=self.choose_color)
        self.color_button.pack(pady=10)

        self.layer_listbox = tk.Listbox(self.sidebar, height=8)
        self.layer_listbox.pack(pady=10)
        self.layer_listbox.bind("<<ListboxSelect>>", self.select_layer)

        
        self.rename_entry = tk.Entry(self.sidebar)
        self.rename_entry.pack(pady=5)
        self.rename_button = tk.Button(self.sidebar, text="Rename Layer", command=self.rename_layer)
        self.rename_button.pack(pady=5)

        
        self.canvas_width = 600
        self.canvas_height = 400
        self.cell_size = 10  # cell size --> remember to addd as opt
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(side="right", fill="both", expand=True)

        self.tool_frame = tk.Frame(self.sidebar)
        self.tool_frame.pack(pady=10)
        self.brush_button = tk.Button(self.tool_frame, text="Brush", command=lambda: self.set_tool("brush"))
        self.brush_button.pack(side="left")
        self.eraser_button = tk.Button(self.tool_frame, text="Eraser", command=lambda: self.set_tool("eraser"))
        self.eraser_button.pack(side="left")
        self.current_tool = "brush"

        #layers....djd
        self.layers = []  
        self.current_layer = 0
        self.add_layer() 

        
        self.master.bind("<F2>", self.start_rename_layer)

        
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)

    def create_menu(self):
        
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export PNG", command=self.export_as_png)
        file_menu.add_command(label="Export GIF", command=self.export_as_gif)

        
        layer_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Layer", menu=layer_menu)
        layer_menu.add_command(label="Add Layer", command=self.add_layer)
        layer_menu.add_command(label="Remove Layer", command=self.remove_layer)

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Color")[1]
        if color:
            self.color = color
            self.color_button.config(bg=color)

    def set_tool(self, tool):
        self.current_tool = tool

    def draw(self, event):
        if self.current_tool == "brush":
            x = (event.x // self.cell_size) * self.cell_size
            y = (event.y // self.cell_size) * self.cell_size
            self.layers[self.current_layer]["draw"].rectangle(
                [x, y, x + self.cell_size, y + self.cell_size], fill=self.color
            )
            self.update_canvas()
        elif self.current_tool == "eraser":
            x = (event.x // self.cell_size) * self.cell_size
            y = (event.y // self.cell_size) * self.cell_size
            self.layers[self.current_layer]["draw"].rectangle(
                [x, y, x + self.cell_size, y + self.cell_size], fill=(255, 255, 255, 0)  
            )
            self.update_canvas()

    def stop_draw(self, event):
        pass

    def update_canvas(self):
        self.canvas.delete("all")  
        for layer in self.layers:
            layer_image = ImageTk.PhotoImage(layer["image"])
            self.canvas.create_image(0, 0, anchor="nw", image=layer_image)
            layer["canvas_image"] = layer_image  

    def add_layer(self):
        new_image = Image.new("RGBA", (self.canvas_width, self.canvas_height), (255, 255, 255, 0))
        new_layer = {
            "image": new_image,
            "draw": ImageDraw.Draw(new_image),
            "canvas_image": None
        }
        self.layers.append(new_layer)
        self.layer_listbox.insert(tk.END, f"Layer {len(self.layers)}")
        self.current_layer = len(self.layers) - 1
        self.layer_listbox.select_set(self.current_layer)
        self.update_canvas()

    def remove_layer(self):
        if len(self.layers) > 1:
            del self.layers[self.current_layer]
            self.layer_listbox.delete(self.current_layer)
            self.current_layer = max(self.current_layer - 1, 0)
            self.update_canvas()
        else:
            messagebox.showwarning("Warning", "Cannot remove the last layer.")

    def rename_layer(self):
        new_name = self.rename_entry.get()
        if new_name:
            self.layer_listbox.delete(self.current_layer)
            self.layer_listbox.insert(self.current_layer, new_name)
            self.layer_listbox.select_set(self.current_layer)

    def start_rename_layer(self, event):
        self.rename_entry.delete(0, tk.END)
        self.rename_entry.insert(0, self.layer_listbox.get(self.current_layer))
        self.rename_entry.focus_set()

    def select_layer(self, event):
        selection = self.layer_listbox.curselection()
        if selection:
            self.current_layer = selection[0]
        self.update_canvas()

    def export_as_png(self):
        self.export_image("png")

    def export_as_gif(self):
        self.export_image("gif")

    def export_image(self, file_format): #combine everything into soup....boredom suckcs
        
        combined_image = Image.new("RGBA", (self.canvas_width, self.canvas_height))
        for layer in self.layers:
            combined_image.alpha_composite(layer["image"])
        file_path = filedialog.asksaveasfilename(defaultextension=f".{file_format}")
        if file_path:
            combined_image.save(file_path)

root = tk.Tk()
app = PixelPaintingApp(root)
root.mainloop()
