import tkinter as tk
import time
import threading
import sys

class ScreenLocker:
    def __init__(self, master, duration_minutes):
        self.master = master
        self.duration_seconds = duration_minutes * 60
        self.remaining_seconds = self.duration_seconds
        self.is_running = True

        # Configure the main window
        self.master.title("Screen Locked - Focus Time!")
        self.master.attributes('-fullscreen', True) 
        self.master.attributes('-topmost', True)  
        self.master.overrideredirect(True)         

        # Attempt to prevent common ways to close the window
        # These are not foolproof, especially against Task Manager or system restarts.
        self.master.protocol("WM_DELETE_WINDOW", self._prevent_close) 
        self.master.bind("<Escape>", self._prevent_close)             
        self.master.bind("<Alt-F4>", self._prevent_close)            
        self.master.bind("<Control-w>", self._prevent_close)         
        # Create a frame to hold the content and center it
        self.main_frame = tk.Frame(master, bg="black")
        self.main_frame.pack(expand=True, fill="both")

        # Create a label for the timer
        self.timer_label = tk.Label(
            self.main_frame,
            text="",
            font=("Inter", 120, "bold"), 
            fg="white",                  
            bg="black"                   
        )
        self.timer_label.pack(expand=True)

        # Create a message label
        self.message_label = tk.Label(
            self.main_frame,
            text=f"Your screen is locked for {duration_minutes} minutes.\nFocus on your task!",
            font=("Inter", 24),
            fg="lightgray",
            bg="black"
        )
        self.message_label.pack(pady=20)

        # Start the countdown in a separate thread
        self.countdown_thread = threading.Thread(target=self._countdown_logic)
        self.countdown_thread.daemon = True
        self.countdown_thread.start()

    def _prevent_close(self, event=None):
        """A dummy function to prevent window closure attempts."""
        print("Attempted to close window, but it's locked!")
        # Optionally, you could show a small message box here, but avoid alert()
        # For instance, a temporary label that says "Cannot close!"

    def format_time(self, seconds):
        """Formats seconds into HH:MM:SS string."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def _countdown_logic(self):
        """Decrements the timer and updates the label."""
        while self.remaining_seconds > 0 and self.is_running:
            # Use master.after to update GUI from a non-GUI thread
            self.master.after(0, self._update_timer_display)
            self.remaining_seconds -= 1
            time.sleep(1) # Wait for 1 second

        if self.is_running: # Only proceed if not manually stopped/closed
            self.master.after(0, self._timer_finished)

    def _update_timer_display(self):
        """Updates the timer label on the GUI thread."""
        self.timer_label.config(text=self.format_time(self.remaining_seconds))

    def _timer_finished(self):
        """Actions to take when the timer runs out."""
        self.timer_label.config(text="TIME'S UP!", fg="lime green")
        self.message_label.config(text="You can now close this window or use your computer.")
        # After a short delay, allow the window to be closed
        self.master.after(3000, self._allow_closure)

    def _allow_closure(self):
        """Re-enables window closure after timer ends."""
        # Re-enable standard close protocols
        self.master.protocol("WM_DELETE_WINDOW", self.master.destroy)
        self.master.bind("<Escape>", lambda e: self.master.destroy())
        self.master.bind("<Alt-F4>", lambda e: self.master.destroy())
        self.master.bind("<Control-w>", lambda e: self.master.destroy())
        self.master.overrideredirect(False) # Show title bar and close button again

    def stop_locker(self):
        """Stops the countdown and closes the window immediately (e.g., for external call)."""
        self.is_running = False
        self.master.destroy()
        sys.exit() # Ensure the program exits

if __name__ == "__main__":
    root = tk.Tk()
    # Set the duration here (e.g., 30 minutes)
    locker = ScreenLocker(root, duration_minutes=30)
    root.mainloop()
