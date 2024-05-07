import threading
import folium
import json
from time import sleep

with open('location_history.json') as f:
	location_history = json.load(f)

first_location = location_history[0]
first_latlon = [first_location['lat'], first_location['lon']]

# creating map
map = folium.Map(
    location = first_latlon,
    zoom_start = 13,
    control_scale=True)

# list unique dates (set makes unique)
dates = list(set(j['time'].split('T')[0] for j in location_history))
# sort dates
dates.sort()

# list of colors to use, redder side of rainbow matches older
colors = ['darkred', 'red', 'orange', 'darkgreen', 'green', 'darkblue', 'blue', 'purple', 'pink']
# all_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']

# map colors to days
color_mapping = {dates[i]: colors[i] for i in range(len(dates))}

for j in location_history:
    location = [j['lat'], j['lon']]
    time = j["time"].rsplit(":", 2)[0].replace("T", " ")
    marker_color = color_mapping[j['time'].split('T')[0]]
    folium.Marker(
        location,
        popup = f'time: {time}\nconfidence: {j["confidence"]}',
        icon=folium.Icon(color=marker_color)
        ).add_to(map)

# create list of lines
locations = [[j['lat'], j['lon']] for j in location_history]
lines = []
for start, end in zip(locations[:-1],locations[1:]):
    lines.append([start, end])

# add lines between points
feature_group = folium.FeatureGroup("Lines")
folium.PolyLine(locations, weight=1).add_to(feature_group)
feature_group.add_to(map)
folium.LayerControl(position='bottomright').add_to(map)

x = threading.Thread(target=map.show_in_browser, daemon=True)
x.start()
sleep(1)
raise KeyboardInterrupt
x.join()
