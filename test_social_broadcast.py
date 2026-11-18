"""
Automated Test Harness for Social Broadcast Engine (X / Twitter)
Tests:
1. Character count boundary compliance (<= 280 chars per tweet)
2. Dual-mode X dispatcher (Mode A live OAuth vs Mode B Web Intent sandbox)
3. URL encoding validity of Twitter Web Intent links
4. Title VI equity metrics inclusion in social payloads
"""

import unittest
import urllib.parse
from agent.social_broadcast import (
    format_x_alert_thread,
    broadcast_to_x
)

class TestSocialBroadcastAndReporting(unittest.TestCase):

    def test_twitter_char_limit_compliance(self):

        """Verify every tweet in the emergency and council threads is strictly <= 280 characters."""
        # 1. Emergency heat alert thread
        emergency = format_x_alert_thread(alert_type="EMERGENCY_HEAT", city="Dallas", temp_f=105.2)
        self.assertTrue(emergency["all_under_280"], f"Tweet exceeded 280 chars: {emergency['char_counts']}")
        for t in emergency["thread"]:
            self.assertLessEqual(len(t), 280)
            
        # 2. Council resolution announcement thread
        council = format_x_alert_thread(alert_type="COUNCIL_RESOLUTION", city="Dallas")
        self.assertTrue(council["all_under_280"], f"Tweet exceeded 280 chars: {council['char_counts']}")
        for t in council["thread"]:
            self.assertLessEqual(len(t), 280)

    def test_twitter_web_intent_url_validity(self):
        """Verify generated Web Intent URLs are valid, properly encoded, and openable."""
        emergency = format_x_alert_thread(alert_type="EMERGENCY_HEAT", city="Dallas", temp_f=104.8)
        intent_url = emergency["web_intent_url"]
        
        self.assertTrue(intent_url.startswith("https://twitter.com/intent/tweet?text="))
        # Verify it can be decoded back to clean text
        encoded_query = intent_url.split("?text=")[1]
        decoded_text = urllib.parse.unquote(encoded_query)
        self.assertIn("HEAT ALERT", decoded_text)
        self.assertIn("https://dallas-heat-app", decoded_text)


    def test_equity_audit_presence_in_social_payload(self):
        """Ensure civic social broadcast includes Title VI equity metrics (3.0x poverty, 6.5x transit)."""
        emergency = format_x_alert_thread(alert_type="EMERGENCY_HEAT", city="Dallas")
        full_text = " ".join(emergency["thread"])
        self.assertIn("TITLE VI EQUITY AUDIT", full_text)
        self.assertIn("3.0x higher poverty", full_text)
        self.assertIn("6.5x", full_text)

    def test_dual_mode_broadcast_fallback(self):
        """Verify broadcast_to_x gracefully falls back to Web Intent when API keys are absent or simulated."""
        result = broadcast_to_x(alert_type="EMERGENCY_HEAT", city="Dallas", force_mock=True)
        
        self.assertEqual(result["mode"], "WEB_INTENT_SANDBOX")
        self.assertEqual(result["status"], "ready_to_broadcast")
        self.assertTrue(result["all_under_280"])
        self.assertIn("twitter.com/intent/tweet", result["web_intent_url"])

if __name__ == "__main__":
    unittest.main()
