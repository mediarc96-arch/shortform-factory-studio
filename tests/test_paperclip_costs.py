from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from paperclip_costs import (  # noqa: E402
    resolve_supertone_estimated_usd_per_minute,
    supertone_cost_usd_from_duration,
    xai_cost_usd_from_payload,
)


class PaperclipCostHelpersTest(unittest.TestCase):
    def test_xai_ticks_are_converted_to_usd(self) -> None:
        payload = {
            "usage": {
                "cost_in_usd_ticks": 4_220_000_000,
            }
        }
        self.assertAlmostEqual(xai_cost_usd_from_payload(payload), 0.422)

    def test_supertone_uses_default_minute_rate(self) -> None:
        previous = os.environ.pop("SUPERTONE_ESTIMATED_USD_PER_MINUTE", None)
        try:
            self.assertAlmostEqual(resolve_supertone_estimated_usd_per_minute(), 0.10)
            self.assertAlmostEqual(supertone_cost_usd_from_duration(30.0), 0.05)
        finally:
            if previous is not None:
                os.environ["SUPERTONE_ESTIMATED_USD_PER_MINUTE"] = previous

    def test_supertone_allows_env_override(self) -> None:
        previous = os.environ.get("SUPERTONE_ESTIMATED_USD_PER_MINUTE")
        os.environ["SUPERTONE_ESTIMATED_USD_PER_MINUTE"] = "0.12"
        try:
            self.assertAlmostEqual(resolve_supertone_estimated_usd_per_minute(), 0.12)
            self.assertAlmostEqual(supertone_cost_usd_from_duration(15.0), 0.03)
        finally:
            if previous is None:
                os.environ.pop("SUPERTONE_ESTIMATED_USD_PER_MINUTE", None)
            else:
                os.environ["SUPERTONE_ESTIMATED_USD_PER_MINUTE"] = previous


if __name__ == "__main__":
    unittest.main()
