import customtkinter
import tkinter
from tkinter import filedialog
import threading
import subprocess
import queue
import os

# Setting up the application's appearance
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Discord Cloud GUI")
        self.geometry("800x600")

        # Configuring the grid to allow elements to expand nicely
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(3, weight=1)

        # --- Widgets (interface elements) ---

        # Download section
        self.download_frame = customtkinter.CTkFrame(self)
        self.download_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="ew")
        self.download_frame.grid_columnconfigure(1, weight=1)

        self.label_download_cloud = customtkinter.CTkLabel(self.download_frame, text="Cloud filename:")
        self.label_download_cloud.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_download_cloud = customtkinter.CTkEntry(self.download_frame, placeholder_text="e.g. my_file.txt")
        self.entry_download_cloud.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.label_download_local = customtkinter.CTkLabel(self.download_frame, text="Save path on disk:")
        self.label_download_local.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_download_local = customtkinter.CTkEntry(self.download_frame, placeholder_text="Select a save location by clicking the button ->")
        self.entry_download_local.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.browse_button = customtkinter.CTkButton(self.download_frame, text="Browse...", command=self.browse_action)
        self.browse_button.grid(row=1, column=2, padx=10, pady=10)

        # Buttons
        self.button_frame = customtkinter.CTkFrame(self)
        self.button_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)

        self.download_button = customtkinter.CTkButton(self.button_frame, text="Download", command=self.download_action)
        self.download_button.grid(row=0, column=0, padx=10, pady=10, sticky="e")
        
        self.upload_button = customtkinter.CTkButton(self.button_frame, text="Select file and Upload", command=self.upload_action)
        self.upload_button.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        
        # Text box for logs and status
        self.log_textbox = customtkinter.CTkTextbox(self, state="disabled", wrap="word")
        self.log_textbox.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

        # Queue for safe inter-thread communication
        self.log_queue = queue.Queue()
        self.after(100, self.process_queue)

    def log(self, message):
        """Adds a message to the log field in a thread-safe manner."""
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message)
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def process_queue(self):
        """Periodically checks the queue and updates the log field."""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log(message)
        except queue.Empty:
            pass
        self.after(100, self.process_queue)

    def run_script_in_thread(self, command):
        """Runs a script in a separate thread to avoid blocking the UI."""
        self.upload_button.configure(state="disabled")
        self.download_button.configure(state="disabled")
        
        self.log_textbox.configure(state="normal")
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.configure(state="disabled")

        def worker():
            """This function will run in a separate thread."""
            try:
                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', bufsize=1, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                
                for line in iter(process.stdout.readline, ''):
                    self.log_queue.put(line)
                
                process.stdout.close()
                return_code = process.wait()
                
                if return_code != 0:
                    self.log_queue.put(f"\n--- Process finished with error code: {return_code} ---\n")
                else:
                    self.log_queue.put("\n--- Process completed successfully ---\n")

            except FileNotFoundError:
                self.log_queue.put(f"CRITICAL ERROR: Interpreter '{command[0]}' or script '{command[1]}' not found.\n")
            except Exception as e:
                self.log_queue.put(f"CRITICAL ERROR: Failed to start process.\n{e}\n")
            finally:
                self.after(0, lambda: self.upload_button.configure(state="normal"))
                self.after(0, lambda: self.download_button.configure(state="normal"))

        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
        
    def upload_action(self):
        """Action for the 'Upload' button."""
        filepath = filedialog.askopenfilename(title="Select a file to upload")
        if not filepath:
            self.log("Upload cancelled.\n")
            return
        
        command = ["python3", "Send.py", filepath]
        self.log(f"Running: {' '.join(command)}\n\n")
        self.run_script_in_thread(command)

    def browse_action(self):
        """Action for the 'Browse...' button."""
        cloud_filename = self.entry_download_cloud.get()
        filepath = filedialog.asksaveasfilename(
            title="Select save location",
            initialfile=cloud_filename or "downloaded_file.txt",
            defaultextension=".*",
            filetypes=(("All files", "*.*"),)
        )
        if filepath:
            self.entry_download_local.delete(0, "end")
            self.entry_download_local.insert(0, filepath)

    def download_action(self):
        """Action for the 'Download' button."""
        cloud_filename = self.entry_download_cloud.get()
        local_filepath = self.entry_download_local.get()

        if not cloud_filename:
            self.log("Error: Enter the cloud file name.\n")
            return

        if not local_filepath:
            self.log("Error: Select a save path on disk.\n")
            # Optional: automatically open the dialog if the path is empty
            self.browse_action()
            local_filepath = self.entry_download_local.get() # Check again after the action
            if not local_filepath: # If still empty (user cancelled)
                self.log("Download cancelled.\n")
                return

        command = ["python3", "Download.py", cloud_filename, local_filepath]
        self.log(f"Running: {' '.join(command)}\n\n")
        self.run_script_in_thread(command)



if __name__ == "__main__":
    app = App()
    app.mainloop()