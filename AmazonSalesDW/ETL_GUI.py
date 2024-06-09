import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import subprocess
import os
import sys

def get_script_path(script_name):
    """Get the path to the script file, considering if the app is bundled."""
    if getattr(sys, 'frozen', False):
        # If the application is bundled, get the path to the bundled directory
        current_dir = sys._MEIPASS
    else:
        # If the application is not bundled, get the directory of this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(current_dir, script_name)

def run_etl_script():
    folder_path = folder_path_var.get()
    sql_user = sql_user_var.get()
    sql_host = sql_host_var.get()
    sql_database = sql_database_var.get()

    application_script = get_script_path('ETL.py')
    
    try:
        subprocess.run(["python", application_script, folder_path, sql_user, sql_host, sql_database], check=True)
        messagebox.showinfo("Success", "ETL process completed successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"ETL process failed: {e}")

def run_creation_script():
    sql_user = sql_user_var.get()
    sql_host = sql_host_var.get()
    sql_database = sql_database_var.get()

    creation_script = get_script_path('creating_DW.py')

    try:
        subprocess.run(["python", creation_script, sql_user, sql_host, sql_database], check=True)
        messagebox.showinfo("Success", "creating_DW completed successfully!")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"creating_DW failed: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def browse_folder():
    folder_path = filedialog.askdirectory()
    folder_path_var.set(folder_path)

# Create the main window
window = tk.Tk()
window.title("ETL Script GUI")

# Create and place labels and entry fields for input parameters
tk.Label(window, text="Folder Path:").grid(row=0, column=0, padx=10, pady=5)
folder_path_var = tk.StringVar()
tk.Entry(window, textvariable=folder_path_var, width=50).grid(row=0, column=1, padx=10, pady=5)
tk.Button(window, text="Browse", command=browse_folder).grid(row=0, column=2, padx=10, pady=5)

tk.Label(window, text="SQL Username:").grid(row=1, column=0, padx=10, pady=5)
sql_user_var = tk.StringVar(value="root")
tk.Entry(window, textvariable=sql_user_var, width=50).grid(row=1, column=1, padx=10, pady=5)

tk.Label(window, text="SQL Host:").grid(row=2, column=0, padx=10, pady=5)
sql_host_var = tk.StringVar(value="127.0.0.1")
tk.Entry(window, textvariable=sql_host_var, width=50).grid(row=2, column=1, padx=10, pady=5)

tk.Label(window, text="SQL Database:").grid(row=3, column=0, padx=10, pady=5)
sql_database_var = tk.StringVar(value="sales_dw")
tk.Entry(window, textvariable=sql_database_var, width=50).grid(row=3, column=1, padx=10, pady=5)

# Create and place the "Run" buttons
tk.Button(window, text="Run ETL Script to update sales_dw", command=run_etl_script, width=30).grid(row=4, column=0, columnspan=3, padx=10, pady=20)
tk.Button(window, text="Create sales dw test", command=run_creation_script, width=30).grid(row=5, column=0, columnspan=3, padx=10, pady=20)

# Run the main event loop
window.mainloop()
