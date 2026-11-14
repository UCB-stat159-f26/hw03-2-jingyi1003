import unittest
from datetime import date
from pathlib import Path

from tennis_career import _match_frame, _read_array

FIXTURES = Path(__file__).parent / "fixtures"


class CareerMatchTests(unittest.TestCase):
    def test_serena_ages_from_birth_dates(self):
        source = (FIXTURES / "serena_career.js").read_text(encoding="utf-8")
        rows = _read_array(source, "morematchmx")
        matches = _match_frame(rows, "Serena Williams", date(1981, 9, 26))

        self.assertEqual(len(matches), 3)
        first = matches.iloc[0]
        self.assertEqual(first["event_date"], date(1995, 10, 30))
        self.assertEqual(first["opponent"], "Anne Miller")
        self.assertEqual(first["result"], "Loss")
        self.assertAlmostEqual(first["player_age"], 14.092007, places=6)
        self.assertAlmostEqual(first["opponent_age"], 18.776566, places=6)
        self.assertAlmostEqual(first["age_difference"], -4.684559, places=6)
