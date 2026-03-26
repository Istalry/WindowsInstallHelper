"""
Tests for utility modules (config, logger).
"""

import logging
from pathlib import Path

from migration_tool.utils import config
from migration_tool.utils.logger import logger, setup_logger

def test_config_variables():
    """Verify that expected configuration variables are set correctly."""
    assert config.APP_NAME == "Windows Install Helper"
    assert isinstance(config.APP_VERSION, str)
    assert isinstance(config.BASE_DIR, Path)
    assert isinstance(config.REGISTRY_PATHS, list)
    assert isinstance(config.EXCLUDED_KEYWORDS, list)
    
    # Check that some common critical keywords are excluded
    assert "kb" in config.EXCLUDED_KEYWORDS
    assert "microsoft visual c++" in config.EXCLUDED_KEYWORDS

def test_logger_exists():
    """Verify that the logger singleton is instantiated properly."""
    assert isinstance(logger, logging.Logger)
    assert logger.name == "MigrationTool"
    
    # Ensure handlers are attached (FileHandler and StreamHandler)
    assert len(logger.handlers) >= 2 

def test_setup_logger_idempotent():
    """Verify that calling setup_logger multiple times does not duplicate handlers."""
    initial_handler_count = len(logger.handlers)
    
    # Call it again
    new_logger_instance = setup_logger()
    
    # Should be the same exact instance and not have extra handlers added
    assert new_logger_instance is logger
    assert len(new_logger_instance.handlers) == initial_handler_count
