import tkinter as tk
from tkinter import filedialog, messagebox
import json
import threading
import time
import pyautogui
import keyboard

class TinyMouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TinyMouse Autoclicker")
        self.root.iconbitmap("tinymouse.ico")  # Set the application icon

        # Initialize variables
        self.clicks = []  # Stores the click configurations
        self.running = False  # Tracks whether the autoclicker is running
        self.total_time = None  # Total time for the autoclicker (in seconds)
        self.repeat_count = None  # Repeat count for the clicks
        self.hotkeys_enabled = True  # Enable or disable hotkeys
        self.mode = tk.StringVar(value="time")  # Mode selector: "time" or "repeat"
        self.current_theme = "dark"  # Tracks the current theme

        # GUI Layout
        self.create_widgets()
        self.configure_hotkeys()  # Set up hotkeys for starting/stopping
        self.apply_theme()  # Apply the default theme

    def create_widgets(self):
        # Frame for click configurations
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        # Input for X coordinate
        tk.Label(self.frame, text="X Position:").grid(row=0, column=0, padx=5)
        self.x_entry = tk.Entry(self.frame, width=10)
        self.x_entry.grid(row=0, column=1, padx=5)

        # Input for Y coordinate
        tk.Label(self.frame, text="Y Position:").grid(row=0, column=2, padx=5)
        self.y_entry = tk.Entry(self.frame, width=10)
        self.y_entry.grid(row=0, column=3, padx=5)

        # Input for click interval
        tk.Label(self.frame, text="Interval (ms):").grid(row=0, column=4, padx=5)
        self.interval_entry = tk.Entry(self.frame, width=10)
        self.interval_entry.grid(row=0, column=5, padx=5)

        # Buttons for adding clicks and selecting positions
        tk.Button(self.frame, text="Add Click", command=self.add_click).grid(row=0, column=6, padx=5)
        tk.Button(self.frame, text="Select Position", command=self.select_position).grid(row=0, column=7, padx=5)

        # Frame for mode selection (Timer or Repeat)
        self.mode_frame = tk.Frame(self.root)
        self.mode_frame.pack(pady=10)

        tk.Label(self.mode_frame, text="Mode:").grid(row=0, column=0, padx=5)

        # Timer mode
        tk.Radiobutton(self.mode_frame, text="Timer (s)", variable=self.mode, value="time").grid(row=0, column=1, padx=5)
        self.total_time_entry = tk.Entry(self.mode_frame, width=10)
        self.total_time_entry.grid(row=0, column=2, padx=5)

        # Repeat mode
        tk.Radiobutton(self.mode_frame, text="Repeats", variable=self.mode, value="repeat").grid(row=0, column=3, padx=5)
        self.repeat_count_entry = tk.Entry(self.mode_frame, width=10)
        self.repeat_count_entry.grid(row=0, column=4, padx=5)

        # Listbox to display configured clicks
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
        tk.Button(self.control_frame, text="Help", command=self.show_help).grid(row=0, column=7, padx=5)
        tk.Button(self.control_frame, text="Switch Theme", command=self.switch_theme).grid(row=0, column=8, padx=5)

    def add_click(self):
        # Add a click configuration to the list
        try:
            x = int(self.x_entry.get())  # X-coordinate
            y = int(self.y_entry.get())  # Y-coordinate
            interval = int(self.interval_entry.get()) / 1000  # Convert ms to seconds
            self.clicks.append((x, y, interval))
            self.click_listbox.insert(tk.END, f"X: {x}, Y: {y}, Interval: {interval * 1000}ms")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for X, Y, and Interval.")

    def select_position(self):
        # Capture the current mouse position and populate the X/Y fields
        messagebox.showinfo("Info", "Move the mouse to the desired position and press Enter.")
        position = pyautogui.position()
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, position.x)
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, position.y)

    def remove_selected_click(self):
        # Remove the selected click configuration from the list
        selected_index = self.click_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            self.click_listbox.delete(index)
            del self.clicks[index]
        else:
            messagebox.showerror("Error", "No click selected.")

    def move_click(self, direction):
        # Move a click configuration up or down in the list
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
        # Start the autoclicker process
        if self.running:
            return

        if not self.clicks:
            messagebox.showerror("Error", "No clicks configured.")
            return

        self.parse_timer_or_repeats()  # Determine stopping conditions
        self.running = True
        threading.Thread(target=self.click_loop, daemon=True).start()

    def stop_clicking(self):
        # Stop the autoclicker process
        self.running = False

    def configure_hotkeys(self):
        # Set up global hotkeys for starting and stopping
        if self.hotkeys_enabled:
            keyboard.add_hotkey('ctrl+shift+s', self.hotkey_start)
            keyboard.add_hotkey('ctrl+shift+e', self.stop_clicking)

    def hotkey_start(self):
        # Start the autoclicker via hotkey
        if not self.running:
            self.parse_timer_or_repeats()
            self.running = True
            threading.Thread(target=self.click_loop, daemon=True).start()

    def parse_timer_or_repeats(self):
        # Parse the stopping condition based on the selected mode
        try:
            if self.mode.get() == "time":
                self.total_time = float(self.total_time_entry.get())
                self.repeat_count = None
            elif self.mode.get() == "repeat":
                self.repeat_count = int(self.repeat_count_entry.get())
                self.total_time = None
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for the selected mode.")

    def click_loop(self):
        # Main loop for executing clicks
        start_time = time.time()
        repeats = 0
        while self.running:
            for x, y, interval in self.clicks:
                if not self.running:
                    break
                if self.total_time and (time.time() - start_time) >= self.total_time:
                    self.running = False
                    break
                if self.repeat_count and repeats >= self.repeat_count:
                    self.running = False
                    break
                pyautogui.click(x, y)
                time.sleep(interval)
            repeats += 1

    def save_config(self):
        # Save the current click configuration to a .tiny file
        config_file = filedialog.asksaveasfilename(defaultextension=".tiny", filetypes=[("TinyMouse files", "*.tiny")])
        if config_file:
            with open(config_file, 'w') as f:
                json.dump(self.clicks, f)

    def load_config(self):
        # Load a click configuration from a .tiny file
        config_file = filedialog.askopenfilename(filetypes=[("TinyMouse files", "*.tiny")])
        if config_file:
            with open(config_file, 'r') as f:
                self.clicks = json.load(f)
                self.click_listbox.delete(0, tk.END)
                for x, y, interval in self.clicks:
                    self.click_listbox.insert(tk.END, f"X: {x}, Y: {y}, Interval: {interval * 1000}ms")

    def show_help(self):
        # Display help information
        help_text = (
            "TinyMouse Autoclicker Help:\n\n"
            "1. Add clicks by specifying X, Y coordinates and interval (ms).\n"
            "2. Use 'Select Position' to capture the current mouse position.\n"
            "3. Choose between Timer or Repeat mode for stopping conditions.\n"
            "4. Save and Load configurations for reuse (.tiny files).\n"
            "5. Use hotkeys (Ctrl+Shift+S to start, Ctrl+Shift+E to stop).\n"
            "6. Switch between light and dark themes using the 'Switch Theme' button."
        )
        messagebox.showinfo("Help", help_text)

    def apply_theme(self):
        # Apply a dark theme to the GUI
        if self.current_theme == "dark":
            self.root.configure(bg="#282c34")
            fg_color = "#abb2bf"
            bg_color = "#282c34"
            entry_bg = "#3e4451"
            select_bg = "#61afef"
        else:  # Light theme
            self.root.configure(bg="#f0f0f0")
            fg_color = "#000000"
            bg_color = "#f0f0f0"
            entry_bg = "#ffffff"
            select_bg = "#cce7ff"

        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=bg_color)
                for sub_widget in widget.winfo_children():
                    if isinstance(sub_widget, (tk.Label, tk.Button, tk.Radiobutton)):
                        sub_widget.configure(bg=bg_color, fg=fg_color, activebackground=select_bg, activeforeground=bg_color)
                    elif isinstance(sub_widget, tk.Entry):
                        sub_widget.configure(bg=entry_bg, fg=fg_color, insertbackground=fg_color, relief="flat")
                    elif isinstance(sub_widget, tk.Listbox):
                        sub_widget.configure(bg=entry_bg, fg=fg_color, selectbackground=select_bg, selectforeground=bg_color)

    def switch_theme(self):
        # Switch between dark and light themes
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.apply_theme()

if __name__ == "__main__":
    root = tk.Tk()
    app = TinyMouseApp(root)
    root.mainloop()
