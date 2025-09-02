#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: WireGuard/AmneziaWG Cryptography Class
Creator: K4YT3X
Modified by: SamuraJ
Date Created: October 11, 2019
Last Modified: September 1, 2025

The WireGuard class implements some of wireguard-tools' cryptographic
    functions such as generating WireGuard private and public keys.
    Extended to support AmneziaWG obfuscation parameters.
"""

import base64
import random
import secrets

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey


class WireGuard:
    """WireGuard/AmneziaWG Cryptography Class

    generates WireGuard public key, private key, PSK, and AmneziaWG obfuscation parameters
    """

    @staticmethod
    def genkey() -> str:
        """generate WireGuard private key

        Returns:
            str: X25519 private key encoded in base64 format
        """
        return base64.b64encode(
            X25519PrivateKey.generate().private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption(),
            )
        ).decode()

    @staticmethod
    def pubkey(privkey: str) -> str:
        """convert WireGuard private key into public key

        Args:
            privkey (str): WireGuard X25519 private key
                encoded in base64 format

        Returns:
            str: corresponding public key of the provided
                private key encoded as a base64 string
        """
        return base64.b64encode(
            X25519PrivateKey.from_private_bytes(base64.b64decode(privkey.encode()))
            .public_key()
            .public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
        ).decode()

    @staticmethod
    def genpsk() -> str:
        """generate a WireGuard PSK

        This is an alias of WireGuard.genkey since they both
            produce a random sequence of bytes. This generated
            X25519 private key can also be used as a symmetric key.

        Returns:
            str: generated PSK encoded as a base64 string
        """
        return WireGuard.genkey()

    @staticmethod
    def gen_jc() -> int:
        """generate random Jc value for AmneziaWG junk packets

        Returns:
            int: number of junk packets (3-10 recommended)
        """
        return random.randint(3, 10)

    @staticmethod
    def gen_junk_sizes() -> tuple[int, int]:
        """generate random Jmin and Jmax values for AmneziaWG junk packet sizes

        Returns:
            tuple: (Jmin, Jmax) where Jmin <= Jmax, both 50-1000 recommended
        """
        jmin = random.randint(50, 500)
        jmax = random.randint(jmin, 1000)
        return jmin, jmax

    @staticmethod
    def gen_handshake_prefixes() -> tuple[int, int]:
        """generate random S1 and S2 values for AmneziaWG handshake prefixes

        Returns:
            tuple: (S1, S2) where S1 and S2 are 15-150, and S1+56 != S2
        """
        s1 = random.randint(15, 150)
        s2 = random.randint(15, 150)
        while s1 + 56 == s2:
            s2 = random.randint(15, 150)
        return s1, s2

    @staticmethod
    def gen_custom_types() -> tuple[int, int, int, int]:
        """generate random H1-H4 values for AmneziaWG custom packet types

        Returns:
            tuple: (H1, H2, H3, H4) all different random values
        """
        types = []
        while len(types) < 4:
            t = random.randint(5, 2**31 - 1)
            if t not in types:
                types.append(t)
        return tuple(types)

    @staticmethod
    def gen_signature_packets() -> list[str]:
        """generate example I1-I5 signature packets for AmneziaWG protocol masking

        Returns:
            list: [I1, I2, I3, I4, I5] as hex strings
        """
        signatures = []
        for i in range(5):
            # Generate a random hex signature, e.g., mimicking QUIC or other protocols
            length = random.randint(20, 100)
            signature = secrets.token_hex(length)
            signatures.append(signature)
        return signatures

    @staticmethod
    def generate_amneziawg_params() -> dict:
        """generate a complete set of AmneziaWG obfuscation parameters

        Returns:
            dict: dictionary containing all AmneziaWG parameters
        """
        jc = WireGuard.gen_jc()
        jmin, jmax = WireGuard.gen_junk_sizes()
        s1, s2 = WireGuard.gen_handshake_prefixes()
        h1, h2, h3, h4 = WireGuard.gen_custom_types()

        return {
            "Jc": jc,
            "Jmin": jmin,
            "Jmax": jmax,
            "S1": s1,
            "S2": s2,
            "H1": h1,
            "H2": h2,
            "H3": h3,
            "H4": h4,
        }
