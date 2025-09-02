"""Integration tests for full awg-meshconf workflow."""

import pathlib
import shutil
import subprocess
import tempfile


class TestIntegration:
    """Integration tests for complete awg-meshconf functionality."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = pathlib.Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "integration_test.csv"

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        shutil.rmtree(self.temp_dir)

    def test_full_workflow_single_peer(self):
        """Test complete workflow with a single peer."""
        # 1. Initialize database
        result = subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "init"], capture_output=True, text=True, cwd=self.temp_dir)

        assert result.returncode == 0
        assert self.db_path.exists()

        # 2. Add a peer
        result = subprocess.run(
            ["python", "-m", "awg_meshconf", "-d", str(self.db_path), "addpeer", "peer1", "--address", "10.0.0.1/24", "--endpoint", "peer1.example.com:51820", "--listenport", "51820"],
            capture_output=True,
            text=True,
            cwd=self.temp_dir,
        )

        assert result.returncode == 0

        # 3. Show peers
        result = subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "showpeers"], capture_output=True, text=True, cwd=self.temp_dir)

        assert result.returncode == 0
        assert "peer1" in result.stdout
        assert "10.0.0.1/24" in result.stdout

        # 4. Generate configuration
        output_dir = self.temp_dir / "configs"
        result = subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "genconfig", "peer1", "-o", str(output_dir)], capture_output=True, text=True, cwd=self.temp_dir)

        assert result.returncode == 0
        assert output_dir.exists()

        config_file = output_dir / "peer1.conf"
        assert config_file.exists()

        content = config_file.read_text()
        assert "[Interface]" in content
        assert "Address = 10.0.0.1/24" in content
        assert "PrivateKey =" in content

    def test_full_workflow_multiple_peers(self):
        """Test complete workflow with multiple peers forming a mesh."""
        # 1. Initialize database
        subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "init"], capture_output=True, cwd=self.temp_dir)

        # 2. Add multiple peers
        peers = [
            ("peer1", "10.0.0.1/24", "peer1.example.com:51820"),
            ("peer2", "10.0.0.2/24", "peer2.example.com:51820"),
            ("peer3", "10.0.0.3/24", "peer3.example.com:51820"),
        ]

        for name, address, endpoint in peers:
            result = subprocess.run(
                ["python", "-m", "awg_meshconf", "-d", str(self.db_path), "addpeer", name, "--address", address, "--endpoint", endpoint, "--listenport", "51820"],
                capture_output=True,
                cwd=self.temp_dir,
            )

            assert result.returncode == 0

        # 3. Show all peers
        result = subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "showpeers"], capture_output=True, text=True, cwd=self.temp_dir)

        assert result.returncode == 0
        for name, address, _ in peers:
            assert name in result.stdout
            assert address in result.stdout

        # 4. Generate configurations for all peers
        output_dir = self.temp_dir / "configs"
        result = subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "genconfig", "-o", str(output_dir)], capture_output=True, text=True, cwd=self.temp_dir)

        assert result.returncode == 0

        # 5. Verify all config files were created
        for name, _, _ in peers:
            config_file = output_dir / f"{name}.conf"
            assert config_file.exists()

            content = config_file.read_text()
            assert "[Interface]" in content
            assert f"# Name: {name}" in content

            # Each peer should have 2 other peers as peers in the config
            peer_count = content.count("[Peer]")
            assert peer_count == 2

    def test_amneziawg_workflow(self):
        """Test workflow with AmneziaWG obfuscation parameters."""
        # 1. Initialize database
        subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "init"], capture_output=True, cwd=self.temp_dir)

        # 2. Add peer with AmneziaWG parameters
        result = subprocess.run(
            [
                "python",
                "-m",
                "awg_meshconf",
                "-d",
                str(self.db_path),
                "addpeer",
                "amnezia_peer",
                "--address",
                "10.0.0.1/24",
                "--endpoint",
                "amnezia.example.com:51820",
                "--jc",
                "5",
                "--jmin",
                "100",
                "--jmax",
                "500",
                "--s1",
                "20",
                "--s2",
                "30",
                "--h1",
                "12345",
                "--h2",
                "23456",
                "--h3",
                "34567",
                "--h4",
                "45678",
            ],
            capture_output=True,
            cwd=self.temp_dir,
        )

        assert result.returncode == 0

        # 3. Generate configuration
        output_dir = self.temp_dir / "configs"
        result = subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "genconfig", "amnezia_peer", "-o", str(output_dir)], capture_output=True, cwd=self.temp_dir)

        assert result.returncode == 0

        # 4. Verify AmneziaWG parameters in config
        config_file = output_dir / "amnezia_peer.conf"
        content = config_file.read_text()

        assert "Jc = 5" in content
        assert "Jmin = 100" in content
        assert "Jmax = 500" in content
        assert "S1 = 20" in content
        assert "S2 = 30" in content
        assert "H1 = 12345" in content
        assert "H2 = 23456" in content
        assert "H3 = 34567" in content
        assert "H4 = 45678" in content

    def test_update_peer_workflow(self):
        """Test updating peer information."""
        # 1. Initialize and add peer
        subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "init"], capture_output=True, cwd=self.temp_dir)

        subprocess.run(
            ["python", "-m", "awg_meshconf", "-d", str(self.db_path), "addpeer", "update_test", "--address", "10.0.0.1/24", "--endpoint", "old.example.com:51820"],
            capture_output=True,
            cwd=self.temp_dir,
        )

        # 2. Update peer
        result = subprocess.run(
            ["python", "-m", "awg_meshconf", "-d", str(self.db_path), "updatepeer", "update_test", "--endpoint", "new.example.com:51820", "--listenport", "51821"],
            capture_output=True,
            text=True,
            cwd=self.temp_dir,
        )

        assert result.returncode == 0

        # 3. Verify update
        result = subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "showpeers", "update_test"], capture_output=True, text=True, cwd=self.temp_dir)

        assert result.returncode == 0
        assert "new.example.com:51820" in result.stdout

    def test_delete_peer_workflow(self):
        """Test deleting a peer."""
        # 1. Initialize and add peer
        subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "init"], capture_output=True, cwd=self.temp_dir)

        subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "addpeer", "delete_test", "--address", "10.0.0.1/24"], capture_output=True, cwd=self.temp_dir)

        # 2. Verify peer exists
        result = subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "showpeers"], capture_output=True, text=True, cwd=self.temp_dir)

        assert "delete_test" in result.stdout

        # 3. Delete peer
        result = subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "delpeer", "delete_test"], capture_output=True, text=True, cwd=self.temp_dir)

        assert result.returncode == 0

        # 4. Verify peer is gone
        result = subprocess.run(["python", "-m", "awg_meshconf", "-d", str(self.db_path), "showpeers"], capture_output=True, text=True, cwd=self.temp_dir)

        assert "delete_test" not in result.stdout
