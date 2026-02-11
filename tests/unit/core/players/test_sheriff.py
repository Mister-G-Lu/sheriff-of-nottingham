"""
Unit tests for core/players/sheriff.py
Tests the Sheriff class
"""

import pytest
import sys
import os
from pathlib import Path

# Setup headless mode
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from core.players.sheriff import Sheriff

class TestSheriffInit:
    """Tests for Sheriff initialization"""
    
    def test_sheriff_default_init(self):
        """Test Sheriff with default values"""
        sheriff = Sheriff()
        
        assert sheriff.reputation == 5
        assert sheriff.authority == 1
        assert sheriff.perception == 1  # STARTING_PERCEPTION = 1
    
    def test_sheriff_custom_reputation(self):
        """Test Sheriff with custom reputation"""
        sheriff = Sheriff(reputation=8)
        
        assert sheriff.reputation == 8
        assert sheriff.authority == 1
    
    def test_sheriff_custom_authority(self):
        """Test Sheriff with custom authority"""
        sheriff = Sheriff(authority=3)
        
        assert sheriff.reputation == 5
        assert sheriff.authority == 3
    
    def test_sheriff_custom_perception(self):
        """Test Sheriff with custom perception"""
        sheriff = Sheriff(perception=7)
        
        assert sheriff.perception == 7
    
    def test_sheriff_all_custom(self):
        """Test Sheriff with all custom values"""
        sheriff = Sheriff(reputation=10, authority=5, perception=8)
        
        assert sheriff.reputation == 10
        assert sheriff.authority == 5
        assert sheriff.perception == 8

class TestSheriffAttributes:
    """Tests for Sheriff attribute manipulation"""
    
    def test_reputation_can_change(self):
        """Test that reputation can be modified"""
        sheriff = Sheriff(reputation=5)
        
        sheriff.reputation = 3
        assert sheriff.reputation == 3
        
        sheriff.reputation = 10
        assert sheriff.reputation == 10
    
    def test_authority_can_change(self):
        """Test that authority can be modified"""
        sheriff = Sheriff(authority=1)
        
        sheriff.authority = 5
        assert sheriff.authority == 5
    
    def test_perception_can_change(self):
        """Test that perception can be modified"""
        sheriff = Sheriff(perception=5)
        
        sheriff.perception = 10
        assert sheriff.perception == 10
    
    def test_reputation_floor(self):
        """Test reputation can go to 0"""
        sheriff = Sheriff(reputation=1)
        
        sheriff.reputation = 0
        assert sheriff.reputation == 0
    
    def test_reputation_ceiling(self):
        """Test reputation can reach maximum"""
        sheriff = Sheriff(reputation=9)
        
        sheriff.reputation = 10
        assert sheriff.reputation == 10

