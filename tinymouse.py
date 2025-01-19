import tkinter as tk
from tkinter import filedialog, messagebox
import json
import threading
import time
import pyautogui

class TinyMouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TinyMouse Autoclicker")

        # Initialize variables
        self.clicks = []  # Stores the click configurations
        self.running = False

        # GUI Layout
        self.create_widgets()

    def create_widgets(self):
        # Frame for click configurations
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        tk.Label(self.frame, text="X Position:").grid(row=0, column=0, padx=5)
        self.x_entry = tk.Entry(self.frame, width=10)
        self.x_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.frame, text="Y Position:").grid(row=0, column=2, padx=5)
        self.y_entry = tk.Entry(self.frame, width=10)
        self.y_entry.grid(row=0, column=3, padx=5)

        tk.Label(self.frame, text="Interval (ms):").grid(row=0, column=4, padx=5)
        self.interval_entry = tk.Entry(self.frame, width=10)
        self.interval_entry.grid(row=0, column=5, padx=5)

        tk.Button(self.frame, text="Add Click", command=self.add_click).grid(row=0, column=6, padx=5)
        tk.Button(self.frame, text="Select Position", command=self.select_position).grid(row=0, column=7, padx=5)

        # Click list display
        self.click_listbox = tk.Listbox(self.root, width=60, height=10)
        self.click_listbox.pack(pady=10)

        # Control Buttons
        self.control_frame = tk.Frame(self.root)
        self.control_frame.pack(pady=10)

        tk.Button(self.control_frame, text="Start", command=self.start_clicking).grid(row=0, column=0, padx=5)
        tk.Button(self.control_frame, text="Stop", command=self.stop_clicking).grid(row=0, column=1, padx=5)
        tk.Button(self.control_frame, text="Save Config", command=self.save_config).grid(row=0, column=2, padx=5)
        tk.Button(self.control_frame, text="Load Config", command=self.load_config).grid(row=0, column=3, padx=5)
        tk.Button(self.control_frame, text="Remove Selected", command=self.remove_selected_click).grid(row=0, column=4, padx=5)
        tk.Button(self.control_frame, text="Move Up", command=lambda: self.move_click(-1)).grid(row=0, column=5, padx=5)
        tk.Button(self.control_frame, text="Move Down", command=lambda: self.move_click(1)).grid(row=0, column=6, padx=5)

    def add_click(self):
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            interval = int(self.interval_entry.get()) / 1000  # Convert milliseconds to seconds
            self.clicks.append((x, y, interval))
            self.click_listbox.insert(tk.END, f"X: {x}, Y: {y}, Interval: {interval * 1000}ms")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for X, Y, and Interval.")

    def select_position(self):
        messagebox.showinfo("Info", "Move the mouse to the desired position and press Enter.")
        position = pyautogui.position()
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, position.x)
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, position.y)

    def remove_selected_click(self):
        selected_index = self.click_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            self.click_listbox.delete(index)
            del self.clicks[index]
        else:
            messagebox.showerror("Error", "No click selected.")

    def move_click(self, direction):
        selected_index = self.click_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            new_index = index + direction

            if 0 <= new_index < len(self.clicks):
                self.clicks.insert(new_index, self.clicks.pop(index))
                listbox_item = self.click_listbox.get(index)
                self.click_listbox.delete(index)
                self.click_listbox.insert(new_index, listbox_item)
                self.click_listbox.select_set(new_index)
        else:
            messagebox.showerror("Error", "No click selected.")

    def start_clicking(self):
        if not self.clicks:
            messagebox.showerror("Error", "No clicks configured.")
            return
        
        self.running = True
        threading.Thread(target=self.click_loop, daemon=True).start()

    def stop_clicking(self):
        self.running = False

    def click_loop(self):
        while self.running:
            for x, y, interval in self.clicks:
                if not self.running:
                    break
                pyautogui.click(x, y)
                time.sleep(interval)

    def save_config(self):
        config_file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if config_file:
            with open(config_file, 'w') as f:
                json.dump(self.clicks, f)

    def load_config(self):
        config_file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if config_file:
            with open(config_file, 'r') as f:
                self.clicks = json.load(f)
                self.click_listbox.delete(0, tk.END)
                for x, y, interval in self.clicks:
                    self.click_listbox.insert(tk.END, f"X: {x}, Y: {y}, Interval: {interval * 1000}ms")

if __name__ == "__main__":
    root = tk.Tk()
    app = TinyMouseApp(root)
    root.mainloop()
