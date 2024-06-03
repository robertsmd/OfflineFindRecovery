import os
import json
import folium
import threading
from time import sleep

from datetime import datetime

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
colors = ['darkred', 'red', 'orange', 'darkgreen', 'green', 'darkblue', 'blue', 'darkblue', 'darkpurple', 'purple', 'pink', 'white', 'lightgray', 'gray', 'black']
# all_colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 'gray', 'black', 'lightgray']

# map colors to days
color_mapping = {dates[i]: colors[i] for i in range(len(dates))}

for j in location_history:
    location = [j['lat'], j['lon']]
    # time = j["time"].rsplit(":", 2)[0].replace("T", " ")
    time = datetime.strptime(j['time'], "%Y-%m-%dT%H:%M:%S%z").strftime("%Y-%m-%d %H:%M:%S")
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

if 'DEVICE_NAME' in os.environ:
    DEVICE_NAME = os.environ['DEVICE_NAME']
print(f'Showing location plot for \'{DEVICE_NAME}\'')

first_datetime = datetime.strptime(location_history[0]['time'], "%Y-%m-%dT%H:%M:%S%z")
last_datetime = datetime.strptime(location_history[-1]['time'], "%Y-%m-%dT%H:%M:%S%z")
first_time_string = first_datetime.strftime("%Y-%m-%d %H:%M:%S")
last_time_string = last_datetime.strftime("%Y-%m-%d %H:%M:%S")

html_range_slider = f'''
    <script src="https://code.jquery.com/ui/1.13.2/jquery-ui.js" integrity="sha256-xLD7nhI62fcsEZK2/v8LsBcb4lG7dgULkuXoXB/j91c=" crossorigin="anonymous"></script>
    <script src="https://cdn.cdnhub.io/jQRangeSlider/5.8.3/jQAllRangeSliders-min.js"></script>
    <link rel="stylesheet" id="themeCSS" href="https://cdn.cdnhub.io/jQRangeSlider/5.7.2/css/classic.min.css" type="text/css" />

    <div id="slider" style="position:absolute;bottom:0%;width:70%;margin-left:15%;z-index:1000000"></div>
    <script>
        $(document).ready(function() {{
            $("#slider").dateRangeSlider({{
                formatter: function(val){{
                    var minutes = val.getMinutes(),
                    hours = val.getHours(),
                    days = val.getDate(),
                    month = val.getMonth() + 1,
                    year = val.getFullYear();
                    return year + "-" + month + "-" + days + " @ " + String("0" + hours).slice(-2) + ":" + String("0" + minutes).slice(-2);
                }},
                bounds: {{
                    min: new Date({first_datetime.year}, {first_datetime.month - 1}, {first_datetime.day}, {first_datetime.hour}, 0, 0),
                    max: new Date({last_datetime.year}, {last_datetime.month - 1}, {last_datetime.day}, {last_datetime.hour + 1}, 0, 0)
                }},
                defaultValues: {{
                    min: new Date({first_datetime.year}, {first_datetime.month - 1}, {first_datetime.day}, {first_datetime.hour}, 0, 0),
                    max: new Date({last_datetime.year}, {last_datetime.month - 1}, {last_datetime.day}, {last_datetime.hour + 1}, 0, 0)
                }},
                step: {{
                    minutes: 5
                }}
            }});
            $("#slider").bind("valuesChanged", function(e, data){{
                console.log("Values just changed. min: " + data.values.min + " max: " + data.values.max);
                markers = $(".leaflet-marker-pane").children()
                shadows = $(".leaflet-shadow-pane").children()
                for (let i=0;i<markers.length;i++) {{
                    markers[i].click();
                    let tagText = $(".leaflet-popup-pane").children()[0].children[0].children[0].children[0].textContent
                    const tagTextArr = tagText.split(" ")
                    let date = tagTextArr[1]
                    let time = tagTextArr[2]
                    let datetime = date + " " + time
                    console.log(datetime)
                    let markerDate = new Date(datetime)
                    console.log(markerdate)
                    console.log(tagText)
                    if (markerDate > data.values.min && markerDate < data.values.max) {{
                        markers[i].style.display = 'none'
                        shadows[i].style.display = 'none'
                    }} else {{
                        markers[i].style.display = 'inline'
                        shadows[i].style.display = 'inline'
                    }}
                }}
            }});
        }});
    </script>
'''
map.get_root().html.add_child(folium.Element(html_range_slider))

html_heading = f'''
    <div style="position:fixed;top:0%;width:100%;text-align:center;z-index:1000000">
        <h1>{DEVICE_NAME}</h1>
        <h4>First observation: {first_time_string}</h4>
        <h4>Last observation: {last_time_string}</h4>
        <div id="slider"></div>
    </div>
'''

map.get_root().html.add_child(folium.Element(html_heading))

map.show_in_browser()
# x = threading.Thread(target=map.show_in_browser, daemon=True)
# x.start()
# sleep(1)
# raise KeyboardInterrupt
# x.join()
