import tkinter as tk
from math import cos, sin
from PIL import Image, ImageTk


def update_visualization():
    # Calculate the distance for each area
    distances = [50,55,65,90,110,110,110,90,65,55,50,55,65,90,110,110,110,90,65,55]  # distances close
    distances = [70,75,85,102,111,130,110,95,85,75,70,75,85,110,130,130,130,110,85,75]  # distances close

    draw_car_boundary(canvas, distances)

    # Schedule the next update
    root.after(100, update_visualization)  # Update every 100 ms


def draw_car_boundary(canvas, distances):
    # Clear previous drawings
    canvas.delete("car_boundary")

    # Calculate points for line segments
    points = []  # List of points (x, y) for drawing line segments
    num_areas = len(distances)
    for i, distance in enumerate(distances):
        angle = 2 * 3.14159 * i / num_areas  # Angle in radians
        x_offset = distance * cos(angle)
        y_offset = distance * sin(angle)
        x = car_center_x + x_offset
        y = car_center_y + y_offset
        points.append((x, y))

    # Draw line segments
    for i in range(num_areas):
        distance = distances[i]

        # Calculate the difference between the current distance and the base distance
        base_distance = [50, 55, 65, 90, 110, 110, 110, 90, 65, 55, 50, 55, 65, 90, 110, 110, 110, 90, 65, 55]
        distance_diff = distance - base_distance[i]

        if distance_diff >= 20:
            color = "green"
        elif distance_diff >= 10:
            color = "yellow"
        else:
            color = "red"

        canvas.create_line(points[i], points[(i + 1) % num_areas], fill=color, width=2, tags="car_boundary")



root = tk.Tk()
root.attributes('-alpha', 0.7)  # Set transparency
root.geometry('800x800')  # Set window size
canvas = tk.Canvas(root, bg='white')
canvas.pack(fill=tk.BOTH, expand=True)

# Load car image
car_image = Image.open("car_top_down.png")
car_image_resized = car_image.resize((200, 200), Image.ANTIALIAS)
car_image_tk = ImageTk.PhotoImage(car_image_resized)
car_center_x, car_center_y = 400, 400
canvas.create_image(car_center_x, car_center_y, image=car_image_tk)

# Initial drawing of car boundary
init_distances = [100] * 10  # Initialize distances (assuming 100 is the default distance)
draw_car_boundary(canvas, init_distances)

update_visualization()  # Start updating the visualization
root.mainloop()
