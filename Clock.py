import tkinter as tk
from datetime import datetime
import pytz

class DigitalClock:
    def __init__(self, root):
        self.root = root
        self.root.title("Clock (Los Angeles Time)")
        self.root.geometry("1920x1080")  # Set the window size for 1920x1080
        self.root.configure(bg='black')

        # Create a label for the clock with a larger font size
        self.label = tk.Label(self.root, font=('Helvetica', 120, 'bold'), bg='black', fg='red')
        self.label.pack(expand=True)  # Center the label in the window

        self.color_step = 0  # Step for color transition
        self.update_clock()

    def update_clock(self):
        # Get the current time in Los Angeles
        los_angeles_tz = pytz.timezone('America/Los_Angeles')
        current_time = datetime.now(los_angeles_tz)

        # Format the time in 12-hour format with AM/PM
        formatted_time = current_time.strftime('%I:%M:%S %p')
        self.label.config(text=formatted_time)

        # Print the current time for debugging
        print("Current time in Los Angeles:", formatted_time)

        # Update the color to create a flame effect
        self.update_color()
        
        self.root.after(1000, self.update_clock)  # Update every second

    def update_color(self):
        # Calculate the color based on the current step
        red = 255
        green = int(165 * (self.color_step / 100))  # Gradually increase green
        blue = 0
        
        # Set the color
        self.label.config(fg=f'#{red:02x}{green:02x}{blue:02x}')
        
        # Update the color step
        self.color_step += 1
        if self.color_step > 100:
            self.color_step = 0  # Reset after reaching the end of the gradient

if __name__ == "__main__":
    root = tk.Tk()
    clock = DigitalClock(root)
    root.mainloop()
