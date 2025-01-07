import folium
from tkinter import Tk, filedialog, messagebox, ttk, Entry, Button, Label
import os
import webbrowser
import requests

def fetch_route_coordinates_osrm(origin, destination):
    url = f"http://router.project-osrm.org/route/v1/driving/{origin};{destination}?overview=full&geometries=geojson"
    response = requests.get(url)

    if response.status_code != 200:
        messagebox.showerror("Error", "Failed to fetch route. Check your connection or input coordinates.")
        return None

    data = response.json()

    if "routes" not in data or len(data["routes"]) == 0:
        messagebox.showerror("Error", "No route found.")
        return None

    # Extract the route geometry
    route_geometry = data["routes"][0]["geometry"]["coordinates"]
    # Convert the coordinates into (lat, lon) format for folium
    route_points = [(point[1], point[0]) for point in route_geometry]
    total_distance = data["routes"][0]["distance"] / 1000  # Convert to kilometers

    return route_points, total_distance

def create_route_map(route_points, start_name, start_lat, start_lon, end_name, end_lat, end_lon):
    if not route_points:
        return None

    # Create a Folium map centered around the midpoint of the route
    mid_index = len(route_points) // 2
    center = route_points[mid_index]

    route_map = folium.Map(location=center, zoom_start=12)
    folium.PolyLine(route_points, color="blue", weight=5, opacity=0.7).add_to(route_map)

    # Add markers for start and end points with popups
    folium.Marker(route_points[0],
                  popup=f"<b>Start:</b> {start_name}<br><b>Lat:</b> {start_lat}<br><b>Lon:</b> {start_lon}",
                  tooltip="Start",
                  icon=folium.Icon(color="green")).add_to(route_map)

    folium.Marker(route_points[-1],
                  popup=f"<b>End:</b> {end_name}<br><b>Lat:</b> {end_lat}<br><b>Lon:</b> {end_lon}",
                  tooltip="End",
                  icon=folium.Icon(color="red")).add_to(route_map)

    return route_map

def generate_route_map():
    start_name = entry_start_name.get()
    start_lat = entry_start_lat.get()
    start_lon = entry_start_lon.get()

    end_name = entry_end_name.get()
    end_lat = entry_end_lat.get()
    end_lon = entry_end_lon.get()

    if not start_name or not start_lat or not start_lon or not end_name or not end_lat or not end_lon:
        messagebox.showerror("Input Error", "Please fill in all fields.")
        return

    try:
        # Validate coordinates
        origin_coords = f"{float(start_lon)},{float(start_lat)}"
        destination_coords = f"{float(end_lon)},{float(end_lat)}"
    except ValueError:
        messagebox.showerror("Input Error", "Coordinates must be numeric values.")
        return

    route_points, total_distance = fetch_route_coordinates_osrm(origin_coords, destination_coords)
    if route_points:
        route_map = create_route_map(route_points, start_name, start_lat, start_lon, end_name, end_lat, end_lon)
        if route_map:
            output_file = "route_map.html"
            route_map.save(output_file)
            webbrowser.open(f"file://{os.path.abspath(output_file)}")
            messagebox.showinfo("Success", f"Route map saved as {output_file}.Total Distance: {total_distance:.2f} km")
        

def main():
    root = Tk()
    root.title("Route Planner (OSM/OSRM)")

    global entry_start_name, entry_start_lat, entry_start_lon, entry_end_name, entry_end_lat, entry_end_lon

    # Create input fields for start location
    Label(root, text="Start Location Name:").pack(pady=5)
    entry_start_name = Entry(root, width=50)
    entry_start_name.pack(pady=5)

    Label(root, text="Start Latitude:").pack(pady=5)
    entry_start_lat = Entry(root, width=50)
    entry_start_lat.pack(pady=5)

    Label(root, text="Start Longitude:").pack(pady=5)
    entry_start_lon = Entry(root, width=50)
    entry_start_lon.pack(pady=5)

    # Create input fields for end location
    Label(root, text="End Location Name:").pack(pady=5)
    entry_end_name = Entry(root, width=50)
    entry_end_name.pack(pady=5)

    Label(root, text="End Latitude:").pack(pady=5)
    entry_end_lat = Entry(root, width=50)
    entry_end_lat.pack(pady=5)

    Label(root, text="End Longitude:").pack(pady=5)
    entry_end_lon = Entry(root, width=50)
    entry_end_lon.pack(pady=5)

    # Generate button
    Button(root, text="Generate Route Map", command=generate_route_map).pack(pady=10)

    # Exit button
    Button(root, text="Quit", command=root.destroy).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
