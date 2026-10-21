import csv
import tempfile
import unittest
from pathlib import Path

from analyze import load_trials, summarize


class AnalyzerTests(unittest.TestCase):
    def test_known_group_statistics_and_reproducible_interval(self):
        rows = [dict(participant_code='P01', input_mode='pointer', movement_time_ms=t) for t in (100, 200, 300)]
        first = summarize(rows, seed=9, iterations=200)
        self.assertEqual(first, summarize(rows, seed=9, iterations=200))
        self.assertEqual(first[0]['median_ms'], 200)
        self.assertEqual(first[0]['mean_ms'], 200)
        self.assertEqual(first[0]['sd_ms'], 100)
        self.assertGreaterEqual(first[0]['median_ci95_ms'][0], 100)
        self.assertLessEqual(first[0]['median_ci95_ms'][1], 300)

    def test_rejects_invalid_timing_with_line_number(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'bad.csv'
            with path.open('w', newline='') as stream:
                writer = csv.DictWriter(stream, fieldnames=['session_id','participant_code','trial','movement_time_ms','input_mode'])
                writer.writeheader()
                writer.writerow(dict(session_id='a', participant_code='P01', trial=1, movement_time_ms='-1', input_mode='pointer'))
            with self.assertRaisesRegex(ValueError, 'bad.csv:2'):
                load_trials([path])


if __name__ == '__main__':
    unittest.main()
