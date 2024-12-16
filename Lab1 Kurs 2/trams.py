import json
from graphs import WeightedGraph, visualize


class TramStop:
    def __init__(self, name, position=None, lines=None):
        self.name = name
        self.position = position  # (latitude, longitude)
        self.lines = lines or []

    def add_line(self, line):
        if line not in self.lines:
            self.lines.append(line)


class TramLine:
    def __init__(self, name, stops):
        self.name = name
        self.stops = stops  # List of stop names


class TramNetwork(WeightedGraph):
    def __init__(self):
        super().__init__()
        self._stops = {}  # name -> TramStop
        self._lines = {}  # name -> TramLine

    def add_stop(self, stop):
        self._stops[stop.name] = stop
        self.add_vertex(stop.name)

    def add_line(self, line):
        self._lines[line.name] = line
        for i in range(len(line.stops) - 1):
            u, v = line.stops[i], line.stops[i + 1]
            self.add_edge(u, v)

    def set_transition_time(self, u, v, time):
        self.set_weight(u, v, time)

    def get_stop_position(self, stop_name):
        return self._stops[stop_name].position

    def get_transition_time(self, u, v):
        return self.get_weight(u, v)

    def list_lines_through_stop(self, stop_name):
        return self._stops[stop_name].lines

    def list_stops_along_line(self, line_name):
        return self._lines[line_name].stops

    def list_all_stops(self):
        return list(self._stops.values())

    def list_all_lines(self):
        return list(self._lines.values())

    def extreme_position(self):
        latitudes = [stop.position[0] for stop in self._stops.values()]
        longitudes = [stop.position[1] for stop in self._stops.values()]
        return min(latitudes), max(latitudes), min(longitudes), max(longitudes)


def readTramNetwork(file='tramnetwork.json'):
    with open(file, 'r') as f:
        data = json.load(f)

    tram_network = TramNetwork()

    # Add stops
    for stop_name, stop_data in data['stops'].items():
        position = stop_data.get('position')
        tram_stop = TramStop(name=stop_name, position=position)
        tram_network.add_stop(tram_stop)

    # Add lines
    for line_name, line_data in data['lines'].items():
        stops = line_data['stops']
        tram_line = TramLine(name=line_name, stops=stops)
        tram_network.add_line(tram_line)

    # Add transition times
    for (u, v), time in data['times'].items():
        tram_network.set_transition_time(u, v, time)

    return tram_network


def demo():
    G = readTramNetwork()
    a, b = input('from,to ').split(',')
    visualize(G, a, b)

if __name__ == '__main__':
    demo()