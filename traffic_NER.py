# @Author Richard Yue
# Identifies road name and relevant traffic data from natural language sentences
# and adds it to a Python dictionary, then exports the data to a CSV

# Imports the necessary libraries
import urllib
from urllib import request
import re
import csv

URL = "https://www.511virginia.org/mobile/?menu_id=incidents"

# If regex stops working, it can be tested at the following address:
# https://www.regextester.com/94730

# Reads traffic data in raw format from a web page
# Parameters: a string, the URL
# Returns: a list of strings, the natural language traffic sentences
def url_to_list(url: str):
    r = urllib.request.urlopen(url)
    html = str(r.read())
    url_list = []
    # Loops through all of the table data on the webpage
    for item in html.split('<td>'):
        # All traffic sentences start with On <road_name>, so only
        # take the elements on the page that start with this.
        if item.startswith('On'):
            # Append the traffic data to a list, remove tabs
            # and line breaks.
            url_list.append(item.strip('\\tn'))
    return url_list

# Check a given sentence for a roadway and any incidents against a
# list of incidents
# Parameters: a string (sentence), a list (events), a list (roadway),
# a Python dictionary (roads_and_incidents)
# Returns: nothing
def check_roads(sentence, events, roadway, roads_and_incidents):
        # Regex to check for any road name (starts with Rt., US-, etc.)
        complete_road_names = re.findall("On\sVA-\d+N?E?S?W?|On\sI-\d+N?E?S?W?|On\sUS-\d+N?E?S?W?|On\sRt\.\s\d+N?E?S?W?", sentence)
        for road in complete_road_names:
            if (f"{road[3:]}" in sentence and f"{road[3:]}" not in roadway):
                roads_and_incidents[road[3:]] = ''
                event_list = []
                road_data = []
                for event in events or event.capitalize() in sentence:
                    if event in sentence:
                        event_list.append(event)
                if ('lane are closed' in sentence or 'lanes are closed' in sentence):
                    event_list.append('lanes closed')
                elif ('lane is closed' in sentence):
                    event_list.append('lane closed')
                if ('shoulder are closed' in sentence or 'shoulders are closed' in sentence):
                    event_list.append('shoulders closed')
                elif ('shoulder is closed' in sentence):
                    event_list.append('shoulder closed')
                if 'due to' in sentence:
                    cause = re.findall('due to.*\.', sentence)[0].split('.')[0][7:]
                    road_data.append(cause.capitalize())
                else:
                    road_data.append('')
                if 'from mile marker' in sentence:
                    mile_markers = re.findall('from mile marker.*\d\d?\.?\d?\d?\sto mile marker \d\d?\.?\d?\d?', sentence)[0]
                    mile_markers = mile_markers[0].upper() + mile_markers[1:]
                    road_data.append(mile_markers)
                elif 'at mile marker' in sentence:
                    mile_markers = re.findall('at mile marker.*\d\s,|at mile marker.*,', sentence)
                    mile_markers = mile_markers[0][0].upper() + mile_markers[0][1:]
                    road_data.append(mile_markers.strip(','))
                elif 'County of' in sentence or 'City of' in sentence:
                    place = re.findall('County of.*,|City of.*,', sentence)[0].split(',')[0].strip(',')
                    road_data.append(place)
                else:
                    road_data.append('')
                if 'AM' in sentence or 'PM' in sentence:
                    time = re.findall('\d\d?:\d\d\sAM|\d\d?:\d\d\sPM', sentence)
                    road_data.append(time[0])
                else:
                    road_data.append('')
                roads_and_incidents[road[3:]] = [event_list, road_data]

def main():
    roads_and_incidents = {}
    events = ['crash', 'delay', 'backup', 'alternating closure' or 'mobile closure' or 'closure', 'ramp is closed', 'detour', 'All north lanes are closed', 'All south lanes are closed', 'All east lanes are closed', 'All west lanes are closed']
    traffic_data = (url_to_list(URL))
    roadway = []
    sentences = traffic_data
    print(sentences)
    for sentence in sentences:
        # Prints each natural language traffic sentence to stdout
        print(sentence)
        print()
        check_roads(sentence, events, roadway, roads_and_incidents)
    with open('traffic_data.csv', 'w', newline='') as traffic_csv:
        writer = csv.writer(traffic_csv)
        writer.writerow(["Roadway", "Incidents", "Reason", "Location", "Time"])
        for key in roads_and_incidents:
            incidents = ', '.join(roads_and_incidents[key][0]).capitalize()
            # Prints data to stdout for verification purposes
            print()
            print(f'Roadway: {key}')
            print(f'Incidents: {incidents}')
            print(f'Reason: {roads_and_incidents[key][1][0]}')
            print(f'Location: {roads_and_incidents[key][1][1]}')
            print(f'Time: {roads_and_incidents[key][1][2]}')
            # Adds the data row-wise to the CSV
            row = [key, incidents, roads_and_incidents[key][1][0], roads_and_incidents[key][1][1], roads_and_incidents[key][1][2]]
            writer.writerow(row)

if __name__ == "__main__":
    main()