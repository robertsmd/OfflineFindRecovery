import threading
import signal
import folium
import json
import pdb
import sys
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

for j in location_history:
    location = [j['lat'], j['lon']]
    time = j["time"].rsplit(":", 2)[0].replace("T", " ")
    folium.Marker(location, popup = f'time: {time}\nconfidence: {j["confidence"]}').add_to(map)

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
sleep(0.5)
raise KeyboardInterrupt
x.join()
