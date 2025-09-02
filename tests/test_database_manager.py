"""Tests for DatabaseManager class."""

import csv
import pathlib
import shutil
import tempfile

import pytest

from awg_meshconf.database_manager import KEY_TYPE, DatabaseManager


class TestDatabaseManager:
    """Test cases for DatabaseManager class methods."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = pathlib.Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_database.csv"

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        shutil.rmtree(self.temp_dir)

    def test_init_creates_empty_database_file(self, caplog):
        """Test that init creates an empty database file."""
        db_manager = DatabaseManager(self.db_path)

        # File shouldn't exist initially
        assert not self.db_path.exists()

        # Initialize database
        db_manager.init()

        # File should now exist
        assert self.db_path.exists()

        # Check that it contains the header
        with open(self.db_path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)
            expected_header = [
                "Name",
                "Address",
                "Endpoint",
                "AllowedIPs",
                "ListenPort",
                "PersistentKeepalive",
                "FwMark",
                "PrivateKey",
                "DNS",
                "MTU",
                "Table",
                "PreUp",
                "PostUp",
                "PreDown",
                "PostDown",
                "SaveConfig",
                "Jc",
                "Jmin",
                "Jmax",
                "S1",
                "S2",
                "H1",
                "H2",
                "H3",
                "H4",
                "I1",
                "I2",
                "I3",
                "I4",
                "I5",
            ]
            assert header == expected_header

    def test_init_with_existing_file_and_missing_required_fields_exits(self):
        """Test that init exits when required fields are missing."""
        # Create a database file with missing required fields
        with open(self.db_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, KEY_TYPE.keys())
            writer.writeheader()
            writer.writerow(
                {
                    "Name": "test_peer",
                    "Address": "",  # Missing required field
                    "Endpoint": "",  # Missing required field
                }
            )

        db_manager = DatabaseManager(self.db_path)

        # This should exit with sys.exit(1)
        with pytest.raises(SystemExit) as excinfo:
            db_manager.init()

        assert excinfo.value.code == 1

    def test_read_database_with_nonexistent_file(self):
        """Test reading database when file doesn't exist."""
        db_manager = DatabaseManager(self.db_path)

        database = db_manager.read_database()

        # Should return template database
        assert database == {"peers": {}}

    def test_read_database_with_existing_file(self):
        """Test reading database with existing file."""
        # Create a test database file
        test_data = {
            "Name": "test_peer",
            "Address": "10.0.0.1/24",
            "Endpoint": "example.com:51820",
            "ListenPort": "51820",
            "PrivateKey": "test_private_key",
        }

        with open(self.db_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, KEY_TYPE.keys())
            writer.writeheader()
            writer.writerow(test_data)

        db_manager = DatabaseManager(self.db_path)
        database = db_manager.read_database()

        assert "test_peer" in database["peers"]
        peer = database["peers"]["test_peer"]
        assert peer["Address"] == ["10.0.0.1/24"]
        assert peer["Endpoint"] == "example.com:51820"
        assert peer["ListenPort"] == 51820
        assert peer["PrivateKey"] == "test_private_key"

    def test_write_database(self):
        """Test writing database to file."""
        db_manager = DatabaseManager(self.db_path)

        test_database = {
            "peers": {
                "peer1": {
                    "Address": ["10.0.0.1/24"],
                    "Endpoint": "example.com:51820",
                    "ListenPort": 51820,
                    "PrivateKey": "test_key_1",
                },
                "peer2": {
                    "Address": ["10.0.0.2/24"],
                    "Endpoint": "example2.com:51820",
                    "ListenPort": 51821,
                    "PrivateKey": "test_key_2",
                },
            }
        }

        db_manager.write_database(test_database)

        # Verify file was written correctly
        assert self.db_path.exists()

        with open(self.db_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2

        # Find peer1 and peer2 rows
        peer1_row = next(row for row in rows if row["Name"] == "peer1")
        peer2_row = next(row for row in rows if row["Name"] == "peer2")

        assert peer1_row["Address"] == "10.0.0.1/24"
        assert peer1_row["Endpoint"] == "example.com:51820"
        assert peer1_row["ListenPort"] == "51820"

        assert peer2_row["Address"] == "10.0.0.2/24"
        assert peer2_row["Endpoint"] == "example2.com:51820"
        assert peer2_row["ListenPort"] == "51821"

    def test_addpeer_success(self):
        """Test successfully adding a peer."""
        db_manager = DatabaseManager(self.db_path)
        db_manager.init()  # Create empty database

        db_manager.addpeer(Name="test_peer", Address=["10.0.0.1/24"], Endpoint="example.com:51820")

        # Verify peer was added
        database = db_manager.read_database()
        assert "test_peer" in database["peers"]
        peer = database["peers"]["test_peer"]
        assert peer["Address"] == ["10.0.0.1/24"]
        assert peer["Endpoint"] == "example.com:51820"
        assert "PrivateKey" in peer  # Should be auto-generated

    def test_addpeer_duplicate_name_warning(self, caplog):
        """Test adding a peer with duplicate name shows warning."""
        db_manager = DatabaseManager(self.db_path)
        db_manager.init()

        # Add first peer
        db_manager.addpeer(Name="test_peer", Address=["10.0.0.1/24"], Endpoint="example.com:51820")

        # Try to add peer with same name
        db_manager.addpeer(Name="test_peer", Address=["10.0.0.2/24"], Endpoint="example2.com:51820")

        # Should contain warning message
        assert "Peer with name test_peer already exists" in caplog.text

    def test_updatepeer_success(self):
        """Test successfully updating a peer."""
        db_manager = DatabaseManager(self.db_path)
        db_manager.init()

        # Add a peer first
        db_manager.addpeer(Name="test_peer", Address=["10.0.0.1/24"], Endpoint="example.com:51820")

        # Update the peer
        db_manager.updatepeer(Name="test_peer", Endpoint="new.example.com:51820", ListenPort=51821)

        # Verify update
        database = db_manager.read_database()
        peer = database["peers"]["test_peer"]
        assert peer["Endpoint"] == "new.example.com:51820"
        assert peer["ListenPort"] == 51821

    def test_updatepeer_nonexistent_peer_warning(self, caplog):
        """Test updating non-existent peer shows warning."""
        db_manager = DatabaseManager(self.db_path)
        db_manager.init()

        db_manager.updatepeer(Name="nonexistent_peer", Endpoint="example.com:51820")

        assert "Peer with name nonexistent_peer does not exist" in caplog.text

    def test_delpeer_success(self):
        """Test successfully deleting a peer."""
        db_manager = DatabaseManager(self.db_path)
        db_manager.init()

        # Add a peer first
        db_manager.addpeer(Name="test_peer", Address=["10.0.0.1/24"], Endpoint="example.com:51820")

        # Verify peer exists
        database = db_manager.read_database()
        assert "test_peer" in database["peers"]

        # Delete the peer
        db_manager.delpeer("test_peer")

        # Verify peer is gone
        database = db_manager.read_database()
        assert "test_peer" not in database["peers"]

    def test_delpeer_nonexistent_peer_warning(self, caplog):
        """Test deleting non-existent peer shows warning."""
        db_manager = DatabaseManager(self.db_path)
        db_manager.init()

        db_manager.delpeer("nonexistent_peer")

        assert "Peer with ID nonexistent_peer does not exist" in caplog.text

    def test_showpeers_nonexistent_peer_warning(self, caplog):
        """Test showing non-existent peer shows warning."""
        db_manager = DatabaseManager(self.db_path)
        db_manager.init()

        db_manager.showpeers("nonexistent_peer")

        assert "Peer with ID nonexistent_peer does not exist" in caplog.text

    def test_genconfig_creates_output_directory(self):
        """Test that genconfig creates output directory if it doesn't exist."""
        db_manager = DatabaseManager(self.db_path)
        db_manager.init()

        # Add a peer
        db_manager.addpeer(Name="test_peer", Address=["10.0.0.1/24"], Endpoint="example.com:51820")

        output_dir = self.temp_dir / "output"

        # Directory shouldn't exist
        assert not output_dir.exists()

        db_manager.genconfig("test_peer", output_dir)

        # Directory should now exist
        assert output_dir.exists()
        assert output_dir.is_dir()

    def test_genconfig_invalid_output_path_error(self):
        """Test genconfig with invalid output path raises error."""
        db_manager = DatabaseManager(self.db_path)
        db_manager.init()

        # Create a file where we want to create directory
        invalid_path = self.temp_dir / "invalid_dir"
        invalid_path.write_text("not a directory")

        with pytest.raises(FileExistsError):
            db_manager.genconfig("test_peer", invalid_path)

    def test_genconfig_creates_config_file(self):
        """Test that genconfig creates configuration file."""
        db_manager = DatabaseManager(self.db_path)
        db_manager.init()

        # Add two peers to create a mesh
        db_manager.addpeer(Name="peer1", Address=["10.0.0.1/24"], Endpoint="peer1.example.com:51820")

        db_manager.addpeer(Name="peer2", Address=["10.0.0.2/24"], Endpoint="peer2.example.com:51820")

        output_dir = self.temp_dir / "output"
        db_manager.genconfig("peer1", output_dir)

        config_file = output_dir / "peer1.conf"
        assert config_file.exists()

        # Check content contains expected sections
        content = config_file.read_text()
        assert "[Interface]" in content
        assert "[Peer]" in content  # Now there should be a peer section
        assert "Address = 10.0.0.1/24" in content
        assert "PrivateKey =" in content
        assert "# Name: peer1" in content
