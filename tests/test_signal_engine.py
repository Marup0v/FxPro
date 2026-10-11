import unittest

import numpy as np
import pandas as pd

from src.signal_engine import calculate_signal


class SignalEngineTests(unittest.TestCase):
    def test_returns_supported_action_with_risk_levels(self):
        close = np.linspace(100, 120, 100)
        frame = pd.DataFrame(
            {
                "Open": close - 0.2,
                "High": close + 0.5,
                "Low": close - 0.5,
                "Close": close,
            }
        )
        signal = calculate_signal(frame)
        self.assertIn(signal.action, {"BUY", "SELL", "WAIT"})
        self.assertGreaterEqual(signal.confidence, 50)
        if signal.action == "BUY":
            self.assertLess(signal.stop_loss, signal.price)
            self.assertGreater(signal.take_profit, signal.price)


if __name__ == "__main__":
    unittest.main()
