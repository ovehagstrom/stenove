import json
from haversine import haversine, Unit
import re
import sys

with open("tramstops.json", 'r', encoding='utf-8') as f:
    tramstops = json.load(f)

with open("tramlines.txt", 'r', encoding='utf-8') as f:
    tramlines = f.read()

def build_tram_stops(jsonobject):
    return {
        stop: {"lat": info["position"][0], "lon": info["position"][1]}
        for stop, info in jsonobject.items()
    }

def build_tram_lines(lines):
    tram_lines, current_line, stops = {}, None, []

    for line in lines.splitlines():
        line = line.strip()
        if line.endswith(":"):
            if current_line:
                tram_lines[current_line] = stops
            current_line = line[:-1].strip()
            stops = []
        elif line:
            stopname = " ".join(line.split()[:-1])
            stops.append(stopname)

    if current_line:
        tram_lines[current_line] = stops

    return tram_lines

def build_tram_lines_and_times(lines):
    time_dict, current_line, last_time, last_stop = {}, None, None, None

    for line in lines.splitlines():
        line = line.strip()
        if line.endswith(":"):
            current_line, last_time, last_stop = line[:-1].strip(), None, None
        elif line:
            parts = line.rsplit(" ", 1)
            stop_name = parts[0].strip()
            time = parts[1].strip()
            hours, minutes = map(int, time.split(":"))
            time_in_minutes = hours * 60 + minutes

            if last_time is not None:
                transition_time = time_in_minutes - last_time
                time_dict.setdefault(last_stop, {})[stop_name] = transition_time
                time_dict.setdefault(stop_name, {})[last_stop] = transition_time

            last_stop, last_time = stop_name, time_in_minutes

    return time_dict

def build_tram_network():
    network = {
        "stops": build_tram_stops(tramstops),
        "lines": build_tram_lines(tramlines),
        "times": build_tram_lines_and_times(tramlines),
    }

    filename = "tramnetwork.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(network, f, ensure_ascii=False, indent=4)

    return filename  # Return the filename

def lines_via_stop(linedict, stop):
    lines_with_stop = [line for line, stops in linedict.items() if stop in stops]
    return f"Linjer {lines_with_stop} går via {stop}"

def lines_between_stops(linedict, stop1, stop2):
    lines_with_stops = [line for line, stops in linedict.items() if stop1 in stops and stop2 in stops]
    return f"Linjer {lines_with_stops} går mellan {stop1} och {stop2}"

def time_between_stops(linedict, timedict, line, stop1, stop2):

    stops = linedict[line]
    start = stops.index(stop1)
    end = stops.index(stop2)

    if start > end:
        start, end = end, start

    total_time = 0
    for i in range(start, end):
        stop_a, stop_b = stops[i], stops[i + 1]
        if stop_a in timedict and stop_b in timedict[stop_a]:
            total_time += timedict[stop_a][stop_b]
        else:
            return 0

    return total_time


def distance_between_stops(stopdict, stop1, stop2):
    point1 = (float(stopdict[stop1]["lat"]), float(stopdict[stop1]["lon"]))
    point2 = (float(stopdict[stop2]["lat"]), float(stopdict[stop2]["lon"]))
    return haversine(point1, point2)

def dialog(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        tramfile = json.load(f)

    stops = tramfile["stops"]
    lines = tramfile["lines"]
    times = tramfile["times"]

    print("Welcome to the tram system!")
    print("Available commands:")
    print(" - via <stop>")
    print(" - between <stop1> and <stop2>")
    print(" - time with <line> from <stop1> to <stop2>")
    print(" - distance from <stop1> to <stop2>")
    print("Type 'quit' to exit.")

    while True:
        user_input = input("> ").strip()

        if user_input == "quit":
            print("Goodbye!")
            break

        if user_input.startswith("via "):
            stop = user_input[4:].strip()
            if stop in stops:
                print(lines_via_stop(lines, stop))
            else:
                print("unknown arguments")

        elif " and " in user_input and user_input.startswith("between "):
            try:
                match = re.findall(r"between (.*?) and (.+)", user_input)[0]
                stop1, stop2 = map(str.strip, match)
                if stop1 in stops and stop2 in stops:
                    print(lines_between_stops(lines, stop1, stop2))
                else:
                    print("unknown arguments")
            except (ValueError, IndexError):
                print("unknown arguments")

        elif user_input.startswith("time with "):
            try:
                match = re.findall(r"time with (.+?) from (.+?) to (.+)", user_input)[0]
                line, stop1, stop2 = map(str.strip, match)
                if line in lines and stop1 in stops and stop2 in stops:
                    print(f"Time: {time_between_stops(lines, times, line, stop1, stop2)} minutes")
                else:
                    print("unknown arguments")
            except (ValueError, IndexError):
                print("unknown arguments")

        elif user_input.startswith("distance from "):
            try:
                match = re.findall(r"distance from (.+?) to (.+)", user_input)[0]
                stop1, stop2 = map(str.strip, match)
                if stop1 in stops and stop2 in stops:
                    print(f"Distance: {distance_between_stops(stops, stop1, stop2):.2f} km")
                else:
                    print("unknown arguments")
            except (ValueError, IndexError):
                print("unknown arguments")

        else:
            print("sorry, try again")


if __name__ == '__main__':
    if sys.argv[1:] == ['init']:
        build_tram_network()
    else:
        filename = build_tram_network()
        dialog(filename)