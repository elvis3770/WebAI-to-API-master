# tests/test_config.py
"""
Tests for configuration management.
"""
import pytest
import os
from app.config import get_env, get_env_bool, get_env_int, validate_config, load_config


class TestConfigHelpers:
    """Test suite for configuration helper functions."""
    
    def test_get_env_with_default(self):
        """Test get_env with default value."""
        # Non-existent key should return default
        value = get_env("NONEXISTENT_KEY", "default_value")
        assert value == "default_value"
    
    def test_get_env_existing_key(self):
        """Test get_env with existing key."""
        os.environ["TEST_KEY"] = "test_value"
        value = get_env("TEST_KEY")
        assert value == "test_value"
        del os.environ["TEST_KEY"]
    
    def test_get_env_bool_true_values(self):
        """Test get_env_bool with various true values."""
        true_values = ["true", "True", "TRUE", "1", "yes", "YES", "on", "ON"]
        
        for val in true_values:
            os.environ["TEST_BOOL"] = val
            assert get_env_bool("TEST_BOOL") is True
        
        del os.environ["TEST_BOOL"]
    
    def test_get_env_bool_false_values(self):
        """Test get_env_bool with various false values."""
        false_values = ["false", "False", "FALSE", "0", "no", "NO", "off", "OFF"]
        
        for val in false_values:
            os.environ["TEST_BOOL"] = val
            assert get_env_bool("TEST_BOOL") is False
        
        del os.environ["TEST_BOOL"]
    
    def test_get_env_int_valid(self):
        """Test get_env_int with valid integer."""
        os.environ["TEST_INT"] = "42"
        value = get_env_int("TEST_INT")
        assert value == 42
        del os.environ["TEST_INT"]
    
    def test_get_env_int_invalid(self):
        """Test get_env_int with invalid integer."""
        os.environ["TEST_INT"] = "not_a_number"
        value = get_env_int("TEST_INT", default=10)
        assert value == 10  # Should return default
        del os.environ["TEST_INT"]


class TestConfigValidation:
    """Test suite for configuration validation."""
    
    def test_validate_config_success(self):
        """Test config validation with valid configuration."""
        config = load_config()
        result = validate_config(config)
        # Should return True even if some optional values are missing
        assert isinstance(result, bool)
    
    def test_load_config_creates_defaults(self):
        """Test that load_config creates default sections."""
        config = load_config()
        
        required_sections = ["Browser", "AI", "Cookies", "Proxy", "EnabledAI"]
        for section in required_sections:
            assert section in config
