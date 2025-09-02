"""Tests for WireGuard cryptography class."""

import base64

import pytest

from awg_meshconf.wireguard import WireGuard


class TestWireGuard:
    """Test cases for WireGuard class methods."""

    def test_genkey_returns_valid_base64_string(self):
        """Test that genkey returns a valid base64 encoded string."""
        key = WireGuard.genkey()

        # Should be a string
        assert isinstance(key, str)

        # Should be valid base64
        try:
            decoded = base64.b64decode(key)
            assert len(decoded) == 32  # X25519 private key is 32 bytes
        except Exception as e:
            pytest.fail(f"Generated key is not valid base64: {e}")

    def test_pubkey_from_private_key(self):
        """Test that pubkey correctly derives public key from private key."""
        # Generate a private key
        privkey = WireGuard.genkey()

        # Get corresponding public key
        pubkey = WireGuard.pubkey(privkey)

        # Verify it's a valid base64 string
        assert isinstance(pubkey, str)
        try:
            decoded = base64.b64decode(pubkey)
            assert len(decoded) == 32  # X25519 public key is 32 bytes
        except Exception as e:
            pytest.fail(f"Generated public key is not valid base64: {e}")

    def test_pubkey_consistency(self):
        """Test that the same private key always produces the same public key."""
        privkey = WireGuard.genkey()

        pubkey1 = WireGuard.pubkey(privkey)
        pubkey2 = WireGuard.pubkey(privkey)

        assert pubkey1 == pubkey2

    def test_pubkey_different_for_different_private_keys(self):
        """Test that different private keys produce different public keys."""
        privkey1 = WireGuard.genkey()
        privkey2 = WireGuard.genkey()

        pubkey1 = WireGuard.pubkey(privkey1)
        pubkey2 = WireGuard.pubkey(privkey2)

        assert pubkey1 != pubkey2

    def test_genpsk_returns_valid_key(self):
        """Test that genpsk returns a valid key (alias for genkey)."""
        psk = WireGuard.genpsk()

        # Should be same as genkey
        assert isinstance(psk, str)
        try:
            decoded = base64.b64decode(psk)
            assert len(decoded) == 32
        except Exception as e:
            pytest.fail(f"Generated PSK is not valid base64: {e}")

    def test_gen_jc_returns_valid_range(self):
        """Test that gen_jc returns value in valid range (3-10)."""
        jc = WireGuard.gen_jc()

        assert isinstance(jc, int)
        assert 3 <= jc <= 10

    def test_gen_junk_sizes_returns_valid_tuple(self):
        """Test that gen_junk_sizes returns valid (jmin, jmax) tuple."""
        jmin, jmax = WireGuard.gen_junk_sizes()

        assert isinstance(jmin, int)
        assert isinstance(jmax, int)
        assert 50 <= jmin <= 500
        assert jmin <= jmax <= 1000

    def test_gen_handshake_prefixes_returns_valid_tuple(self):
        """Test that gen_handshake_prefixes returns valid (s1, s2) tuple."""
        s1, s2 = WireGuard.gen_handshake_prefixes()

        assert isinstance(s1, int)
        assert isinstance(s2, int)
        assert 15 <= s1 <= 150
        assert 15 <= s2 <= 150
        assert s1 + 56 != s2  # Ensure they're not conflicting

    def test_gen_custom_types_returns_unique_values(self):
        """Test that gen_custom_types returns 4 unique values."""
        h1, h2, h3, h4 = WireGuard.gen_custom_types()

        types = [h1, h2, h3, h4]

        # All should be integers
        assert all(isinstance(t, int) for t in types)

        # All should be unique
        assert len(set(types)) == 4

        # All should be in valid range
        assert all(5 <= t <= 2**31 - 1 for t in types)

    def test_gen_signature_packets_returns_valid_list(self):
        """Test that gen_signature_packets returns list of 5 hex strings."""
        signatures = WireGuard.gen_signature_packets()

        assert isinstance(signatures, list)
        assert len(signatures) == 5

        for sig in signatures:
            assert isinstance(sig, str)
            # Should be valid hex
            try:
                bytes.fromhex(sig)
            except ValueError:
                pytest.fail(f"Signature '{sig}' is not valid hex")

            # Should be reasonable length (20-100 bytes = 40-200 hex chars)
            assert 40 <= len(sig) <= 200

    def test_generate_amneziawg_params_returns_complete_dict(self):
        """Test that generate_amneziawg_params returns all required parameters."""
        params = WireGuard.generate_amneziawg_params()

        assert isinstance(params, dict)

        required_keys = ["Jc", "Jmin", "Jmax", "S1", "S2", "H1", "H2", "H3", "H4"]
        for key in required_keys:
            assert key in params
            assert isinstance(params[key], int)

        # Validate ranges
        assert 3 <= params["Jc"] <= 10
        assert 50 <= params["Jmin"] <= 500
        assert params["Jmin"] <= params["Jmax"] <= 1000
        assert 15 <= params["S1"] <= 150
        assert 15 <= params["S2"] <= 150
        assert params["S1"] + 56 != params["S2"]

        # H values should be unique
        h_values = [params["H1"], params["H2"], params["H3"], params["H4"]]
        assert len(set(h_values)) == 4
        assert all(5 <= h <= 2**31 - 1 for h in h_values)

    def test_pubkey_invalid_input(self):
        """Test that pubkey raises appropriate error for invalid input."""
        with pytest.raises(ValueError):
            WireGuard.pubkey("invalid_base64")

        with pytest.raises(ValueError):
            WireGuard.pubkey("")

        with pytest.raises(ValueError):
            WireGuard.pubkey("not_base64_at_all!")
