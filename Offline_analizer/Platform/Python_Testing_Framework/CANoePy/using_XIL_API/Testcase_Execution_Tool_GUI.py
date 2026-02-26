import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import sys
#changes the current working directory to the folder where the file is (this prevents import issues)
#print(sys.argv[0])
wkspFldr = os.path.dirname(os.path.abspath(sys.argv[0]))
#print(wkspFldr)
os.chdir(wkspFldr)

sys.path.append(r"..\..\..\..\Python_Testing_Framework\CANoePy\using_XIL_API")
sys.path.append(r"..\..\ReportGen")
sys.path.append(r"..\..\..\..\adas_sim\Python_Testing_Framework\common_test_functions")
sys.path.append(r"..\..\..\..\adas_sim\Python_Testing_Framework\sysint_tests")
import HTML_Logger
import CAPL_Wrapper_Functions_XIL_API as capl
import Test_Functions_XIL_API as tf

class PythonFileExecutor:
    """
    A GUI application to select, list, and execute multiple Python files.

    Attributes:
    - root: tk.Tk
        The main window of the application.
    - file_listbox: tk.Listbox
        The listbox to display selected Python files.
    - progress_bar: ttk.Progressbar
        The progress bar to show execution progress.
    - results_table: ttk.Treeview
        The table to display results of executed files.
    """

    def __init__(self, master):
        """
        Initializes the PythonFileExecutor class.

        Parameters:
        - master: tk.Tk
            The main window of the application.
        """
        self.root = master
        self.root.title("CANoePy : Python Tests Execution Tool")

        # Create a frame for the file selection
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        # Listbox to display Python files
        self.file_listbox = tk.Listbox(self.frame, selectmode=tk.MULTIPLE, width=150, height=20)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        # Scrollbar for the listbox
        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.file_listbox.yview)

        # Buttons for file selection
        self.select_button = tk.Button(self.root, text="Select Python Testcases", command=self.select_files)
        self.select_button.pack(pady=5)

        self.select_all_button = tk.Button(self.root, text="Select All", command=self.select_all_files)
        self.select_all_button.pack(side=tk.LEFT, padx=5)

        self.unselect_all_button = tk.Button(self.root, text="Unselect All", command=self.unselect_all_files)
        self.unselect_all_button.pack(side=tk.LEFT, padx=5)

        self.execute_button = tk.Button(self.root, text="Execute", command=self.execute_files)
        self.execute_button.pack(side=tk.LEFT, padx=5)

        self.quit_button = tk.Button(self.root, text="Quit", command=self.root.quit)
        self.quit_button.pack(side=tk.LEFT, padx=5)

        # Progress bar for execution
        self.progress_bar = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.progress_bar.pack(pady=10)

        # Results table to display execution results
        self.results_table = ttk.Treeview(self.root, columns=("File", "Result"), show='headings')
        self.results_table.heading("File", text="File")
        self.results_table.heading("Result", text="Result")
        self.results_table.pack(pady=10)

        # Configure column widths
        self.results_table.column("File", width=400)
        self.results_table.column("Result", width=200)

    def select_files(self):
        """
        Opens a file dialog to select multiple Python files and adds them to the listbox.
        """
        file_paths = filedialog.askopenfilenames(title="Select Python Files", filetypes=[("Python Files", "*.py")])
        for file_path in file_paths:
            self.file_listbox.insert(tk.END, file_path)

    def select_all_files(self):
        """
        Selects all files in the listbox.
        """
        self.file_listbox.select_set(0, tk.END)

    def unselect_all_files(self):
        """
        Unselects all files in the listbox.
        """
        self.file_listbox.select_clear(0, tk.END)

    def execute_files(self):
        """
        Executes the selected Python files one by one and updates the progress bar and results table.
        """
        selected_files = self.file_listbox.curselection()
        total_files = len(selected_files)

        if total_files == 0:
            messagebox.showwarning("No Selection", "Please select at least one Python file to execute.")
            return

        self.results_table.delete(*self.results_table.get_children())
        self.progress_bar['maximum'] = total_files

        for index in selected_files:
            file_path = self.file_listbox.get(index)
            self.progress_bar['value'] = index + 1
            self.root.update_idletasks()  # Update the GUI

            try:
                # Execute the Python file
                result = subprocess.run([r'X:\Tools\venv\Scripts\python.exe', file_path], capture_output=True, text=True)
                if result.returncode == 0:
                    self.results_table.insert("", "end", values=(os.path.basename(file_path), "PASSED"),
                                              tags=('passed',))
                else:
                    self.results_table.insert("", "end", values=(os.path.basename(file_path), "FAILED"),
                                              tags=('failed',))
            except Exception as e:
                self.results_table.insert("", "end", values=(os.path.basename(file_path), "FAILED"), tags=('failed',))

        self.progress_bar['value'] = total_files
        self.root.update_idletasks()  # Update the GUI

        # Configure colors for results
        self.results_table.tag_configure('passed', foreground='green')
        self.results_table.tag_configure('failed', foreground='red')


if __name__ == "__main__":
    root = tk.Tk()
    app = PythonFileExecutor(root)
    root.mainloop()