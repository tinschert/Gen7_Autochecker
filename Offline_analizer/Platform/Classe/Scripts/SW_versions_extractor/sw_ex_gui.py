import tkinter as tk
from tkinter import messagebox, filedialog
from sw_versions_extractor import main_sequence


class SWExtractorApp:
    def __init__(self, master):
        self.master = master
        self.master.title("SW Extractor")
        self.selected_file = None  # Variable to store selected file path
        self.master.geometry("220x200")

        # Dropdown menu options 1
        self.options1 = ["FORD", "OD"]
        self.selected_option1 = tk.StringVar(master)
        self.selected_option1.set(self.options1[0])  # Default option

        # Dropdown menu 1
        self.dropdown1 = tk.OptionMenu(master, self.selected_option1, *self.options1)
        self.dropdown1.grid(row=0, column=0, padx=10, pady=20)

        # Dropdown menu options 2
        self.options2 = ["GUI_PC", "RT_Rack", "Rendering_PC", "Datalogger", "Single_PC"]
        self.selected_option2 = tk.StringVar(master)
        self.selected_option2.set(self.options2[0])  # Default option

        # Dropdown menu 2
        self.dropdown2 = tk.OptionMenu(master, self.selected_option2, *self.options2)
        self.dropdown2.grid(row=0, column=1, padx=10, pady=20)

        # Browse button
        self.browse_button = tk.Button(master, text="Select YAML file", command=self.browse)
        self.browse_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Run button (bigger size)
        self.run_button = tk.Button(master, text="Run", command=self.run, width=20, height=2)
        self.run_button.grid(row=2, column=0, columnspan=2, pady=10)

    def browse(self):
        self.selected_file = filedialog.askopenfilename(filetypes=[("Yaml files", "*.yml")])
        if self.selected_file:
            messagebox.showinfo("File Selected", f"Selected file: {self.selected_file}")

    def run(self):
        selected = self.selected_option2.get()
        selected_customer = self.selected_option1.get()
        response = messagebox.askquestion("Run", f"Running with option: {selected}. Continue?")
        if response == "yes":
            status = main_sequence(selected, selected_customer, self.selected_file)  # Pass selected file to main_sequence function
            if status:
                messagebox.showinfo("Info", r"Finished!!!\nFind the output in C:\HIL_INFO")
        else:
            messagebox.showinfo("Cancelled", "Processing cancelled.")


def main():
    root = tk.Tk()
    # Set window size to twice the default size
    root.geometry("400x200")  # width x height
    app = SWExtractorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()