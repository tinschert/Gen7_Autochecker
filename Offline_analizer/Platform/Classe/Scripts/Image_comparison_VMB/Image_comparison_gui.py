import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import tkinter.filedialog
from threading import Thread
from Image_comparison import main_gui
import os



class ImageComparisonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Comparison Tool")
        self.root.update_idletasks()
        width = 900
        height = 500
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2) - 50 
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.create_widgets()

    def create_widgets(self):
        # variables
        self.vehicle_folder = tk.StringVar()
        self.vmb_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        #heading label
        tool_compare_label = ttk.Label(self.root, text='VMB Picture Comparision', font=('calibre', 15, 'bold'))
        tool_compare_label.place(x=360,y=15)

        # Create a frame for the folder inputs
        folder_frame = ttk.Frame(self.root)
        folder_frame.pack(side=tk.LEFT, padx=50, pady=10)

        # Vehicle folder
        vehicle_folder_label = ttk.Label(folder_frame, text='Source folder Vehicle picture:', font=('calibre', 13, 'bold'))
        vehicle_folder_label.grid(row=0, column=0, sticky=tk.W)
        vehicle_folder_entry = ttk.Entry(folder_frame, textvariable=self.vehicle_folder, font=('calibre', 10, 'normal'), width=50)
        vehicle_folder_entry.grid(row=1, column=0, padx=5, pady=5)
        self.vehicle_folder_button = ttk.Button(folder_frame, text="Browse", command=self.browse_vehicle_folder, width=7)
        self.vehicle_folder_button.grid(row=1, column=1, padx=1, pady=5, sticky='w')

        # Add a gap
        folder_frame.grid_rowconfigure(2, minsize=20)

        # VMB folder
        vmb_folder_label = ttk.Label(folder_frame, text='Source folder VMB picture:', font=('calibre', 13, 'bold'))
        vmb_folder_label.grid(row=3, column=0, sticky=tk.W)
        vmb_folder_entry = ttk.Entry(folder_frame, textvariable=self.vmb_folder, font=('calibre', 10, 'normal'), width=50)
        vmb_folder_entry.grid(row=4, column=0, padx=5, pady=5)
        self.vmb_folder_button = ttk.Button(folder_frame, text="Browse", command=self.browse_vmb_folder, width=7)
        self.vmb_folder_button.grid(row=4, column=1, padx=1, pady=5, sticky='w')

        # Add a gap
        folder_frame.grid_rowconfigure(5, minsize=20)

        # Output folder
        output_folder_label = ttk.Label(folder_frame, text='Output folder for results:', font=('calibre', 13, 'bold'))
        output_folder_label.grid(row=6, column=0, sticky=tk.W)
        output_folder_entry = ttk.Entry(folder_frame, textvariable=self.output_folder, font=('calibre', 10, 'normal'), width=50)
        output_folder_entry.grid(row=7, column=0, padx=5, pady=5)
        self.output_folder_button = ttk.Button(folder_frame, text="Browse", command=self.browse_output_folder, width=7)
        self.output_folder_button.grid(row=7, column=1, padx=1, pady=5, sticky='w')

        # Add a gap
        folder_frame.grid_rowconfigure(8, minsize=20)
        folder_frame.grid_rowconfigure(9, minsize=20)
        folder_frame.grid_rowconfigure(10, minsize=20)

        # Submit button
        style = ttk.Style()
        style.configure('Submit.TButton', font=('calibri', 13), foreground='green', )
        self.submit_button = ttk.Button(folder_frame, text='Submit', command=lambda: Thread(target=self.submit).start(),style='Submit.TButton')
        self.submit_button.grid(row=11, column=1, pady=10)

        # Create a frame for the transparency options
        transparency_frame = ttk.Frame(self.root)
        transparency_frame.place(x=600,y=90)

        # Transparency label
        transparency_label = ttk.Label(transparency_frame, text='Select Comparison Transparency:', font=('calibre', 13, 'bold'))
        transparency_label.grid(row=0, column=0, sticky=tk.W)
        
        # Add space after transparency label
        transparency_frame.grid_rowconfigure(1, minsize=10)
        
        # Transparency checkboxes
        style.configure("Custom.TCheckbutton", font=("calibri", 13, 'bold'))
        self.transparency_vars = [tk.BooleanVar() for _ in range(4)]
        transparency_values = [0.3, 0.5, 0.7, 'Absolut diff']
        for i, value in enumerate(transparency_values):
            checkbox = ttk.Checkbutton(transparency_frame, text=str(value), variable=self.transparency_vars[i], style="Custom.TCheckbutton")
            checkbox.grid(row=i+2, column=0, sticky=tk.W, padx=60, pady=5)


    def submit(self):

        self.disable_btns()

        #get values from entry box
        vehicle_folder = self.vehicle_folder.get()
        vmb_folder = self.vmb_folder.get()
        output_folder = self.output_folder.get()
        transparency_values = [0.3, 0.5, 0.7, 'Absolut diff']
        selected_transparencies = [value for var, value in zip(self.transparency_vars, transparency_values) if var.get()]
        
        #check if given folders are valid
        if not os.path.isdir(vehicle_folder):
            tk.messagebox.showerror("Error", "Invalid vehicle folder path")
            self.enable_btns()
            return

        if not os.path.isdir(vmb_folder):
            tk.messagebox.showerror("Error", "Invalid VMB folder path")
            self.enable_btns()
            return
        
        if not selected_transparencies:
            tk.messagebox.showerror("Error", "No transparency option selected")
            self.enable_btns()
            return

        if not os.path.isdir(output_folder):
            try:
                os.makedirs(output_folder, exist_ok=True)
            except Exception as e:
                tk.messagebox.showerror("Error", f"Invalid output folder path")
                print(f"Invalid output folder path {e}")
                self.enable_btns()
                return
        
        print(' ')
        print('GIVEN INPUTS:')
        print(f"Vehicle folder: {vehicle_folder}")
        print(f"VMB folder: {vmb_folder}")
        print(f"Output folder: {output_folder}")
        print(f"Selected transparencies: {selected_transparencies}")
        print(' ')

        try:
            main_gui(vehicle_folder, vmb_folder, output_folder, selected_transparencies)
            tk.messagebox.showinfo("Success", "Image comparison completed successfully")
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {e}")

        self.enable_btns()


    def browse_vehicle_folder(self):
        folder_selected = tk.filedialog.askdirectory()
        self.vehicle_folder.set(folder_selected)

    def browse_vmb_folder(self):
        folder_selected = tk.filedialog.askdirectory()
        self.vmb_folder.set(folder_selected)

    def browse_output_folder(self):
        folder_selected = tk.filedialog.askdirectory()
        self.output_folder.set(folder_selected)

    def enable_btns(self):
        """Enables buttons"""
        self.vehicle_folder_button.config(state=tk.NORMAL)
        self.vmb_folder_button.config(state=tk.NORMAL)
        self.output_folder_button.config(state=tk.NORMAL)
        self.submit_button.config(state=tk.NORMAL)

    def disable_btns(self):
        """Disables buttons"""
        self.vehicle_folder_button.config(state=tk.DISABLED)
        self.vmb_folder_button.config(state=tk.DISABLED)
        self.output_folder_button.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageComparisonApp(root)
    root.mainloop()