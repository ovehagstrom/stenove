import unittest
from tramdata import *

filename = './tramnetwork.json'


class TestTramSystem(unittest.TestCase):

    def setUp(self):
        with open(filename, 'r', encoding= 'utf-8') as trams:
            tramdict = json.loads(trams.read())
            self.tram_data = build_tram_network()
            self.stops = tramdict["stops"]
            self.lines = tramdict["lines"]
            self.times = tramdict["times"]

    def test_stops_exist(self):
        stopset = {stop for line in self.lines for stop in self.lines[line]}
        for stop in stopset:
            self.assertIn(stop, self.stops, msg = stop + ' not in stops')

    def test_all_tram_lines_exist(self):
        with open("tramlines.txt", "r", encoding="utf-8") as f:
            tramlines_txt = f.read()

        tramlines_txt_lines = set(
            line.strip(" :") for line in tramlines_txt.splitlines() if line.endswith(":")
        )
        linedict_lines = set(self.lines.keys())

        self.assertEqual(
            tramlines_txt_lines,
            linedict_lines,
            msg="Mismatch between tramlines.txt and linedict"
        )

    def test_tramline_stops_match(self):
        with open("tramlines.txt", "r", encoding="utf-8") as f:
            tramlines_txt = f.read()

        tramlines_txt_parsed = {}
        current_line = None
        for line in tramlines_txt.splitlines():
            line = line.strip()
            if line.endswith(":"):
                current_line = line.strip(":")
                tramlines_txt_parsed[current_line] = []
            elif line and current_line:
                stop_name = " ".join(line.split()[:-1])
                tramlines_txt_parsed[current_line].append(stop_name)

        for line, stops in tramlines_txt_parsed.items():
            self.assertEqual(
                self.lines.get(line, []),
                stops,
                msg=f"Mismatch in stops for line {line}"
            )

    def test_feasible_distances(self):
        for line, stops in self.lines.items():
            for i in range(len(stops) - 1):
                stop1, stop2 = stops[i], stops[i + 1]
                distance = distance_between_stops(self.stops, stop1, stop2)
                self.assertLess(
                    distance,
                    20,
                    msg=f"Distance between {stop1} and {stop2} on line {line} is {distance:.2f} km"
                )

    def test_symmetric_travel_times(self):
        for stop1, connections in self.times.items():
            for stop2, time in connections.items():
                self.assertEqual(
                    time,
                    self.times[stop2].get(stop1, None),
                    msg=f"Travel time mismatch between {stop1} and {stop2}: {time} vs {self.times[stop2].get(stop1, 'N/A')}"
                )


if __name__ == '__main__':
    unittest.main()
