"""
Adversarial Security Test Suite for TinPyUI SessionBindingGuard
Tests negative tamper scenarios: HMAC signature forging, device fingerprint mismatches,
post-rotation session replay attempts, IP mismatch enforcement, and malformed input resilience.
"""

import unittest
from unittest.mock import patch
import sys
import os

# Ensure tinpyui module path is importable
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
import tinpyui as tin


class TestSessionBindingGuardAdversarial(unittest.TestCase):
    def setUp(self):
        self.guard = tin.SessionBindingGuard(secret_key="test_adversarial_master_secret")
        self.user_id = "user_test_88192"

    def test_valid_session_passes(self):
        """Happy Path: An untampered valid token should pass validation."""
        token = self.guard.create_bound_session(self.user_id, client_ip="127.0.0.1")
        self.assertTrue(self.guard.validate_session(token, request_client_ip="127.0.0.1"))

    def test_hmac_tampering_fails(self):
        """Adversarial Test 1: Forging or altering HMAC signature MUST fail validation."""
        token = self.guard.create_bound_session(self.user_id)
        session_id, sig = token.split(".", 1)

        # Mutate last character of signature to forge a payload
        forged_sig = sig[:-1] + ("0" if sig[-1] != "0" else "1")
        forged_token = f"{session_id}.{forged_sig}"

        self.assertFalse(self.guard.validate_session(forged_token))

    def test_tampered_session_id_fails(self):
        """Adversarial Test 2: Swapping or altering session_id payload MUST fail validation."""
        token = self.guard.create_bound_session(self.user_id)
        _, sig = token.split(".", 1)

        # Create a forged session_id with valid signature format
        forged_session_id = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
        forged_token = f"{forged_session_id}.{sig}"

        self.assertFalse(self.guard.validate_session(forged_token))

    def test_device_fingerprint_mismatch_fails(self):
        """Adversarial Test 3: Simulating a request from a different device fingerprint MUST fail validation."""
        # Create token under genuine device fingerprint
        token = self.guard.create_bound_session(self.user_id)

        # Validate token under an attacker's different device fingerprint
        with patch.object(tin.Security, 'get_device_fingerprint', return_value="attacker_different_hardware_fingerprint_hash"):
            self.assertFalse(self.guard.validate_session(token))

    def test_post_rotation_replay_fails(self):
        """Adversarial Test 4: Attempting to replay an old token after rotation MUST fail validation."""
        old_token = self.guard.create_bound_session(self.user_id)
        self.assertTrue(self.guard.validate_session(old_token))

        # Rotate token
        new_token = self.guard.rotate_session(old_token, self.user_id)

        # Verify old token is evicted & rejected
        self.assertFalse(self.guard.validate_session(old_token))
        # Verify new token is valid
        self.assertTrue(self.guard.validate_session(new_token))

    def test_ip_mismatch_fails_when_ip_bound(self):
        """Adversarial Test 5: Changing IP address on an IP-bound session (bind_ip=True) MUST fail validation."""
        ip_bound_token = self.guard.create_bound_session(self.user_id, client_ip="10.0.0.50", bind_ip=True)

        # Validation from same IP passes
        self.assertTrue(self.guard.validate_session(ip_bound_token, request_client_ip="10.0.0.50"))

        # Validation from different IP fails
        self.assertFalse(self.guard.validate_session(ip_bound_token, request_client_ip="198.51.100.22"))

    def test_garbage_and_malformed_input_resilience(self):
        """Adversarial Test 6: Malformed/garbage input MUST fail validation cleanly without uncaught exceptions."""
        malformed_inputs = [
            "",
            "no_period_token",
            "too.many.periods.in.token",
            None,
            12345,
            [1, 2, 3],
            {"session": "tampered"},
            object()
        ]
        for bad_input in malformed_inputs:
            with self.subTest(bad_input=bad_input):
                self.assertFalse(self.guard.validate_session(bad_input))


if __name__ == "__main__":
    unittest.main()
