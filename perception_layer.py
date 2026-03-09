"""
Perception Layer - Market intelligence and safety inspection
Multi-source data collection with redundancy and safety checks
"""
import logging
from web3 import Web3
from web3.exceptions import ContractLogicError, TimeExhausted
from typing import Dict, List, Tuple, Optional, Any
import time
import json
from datetime import datetime, timedelta
import requests

from config import NETWORK, DEX, RISK, SYSTEM
from firebase_setup import firebase_manager

logger = logging.getLogger(__name__)

class PoolScraper:
    """Monitor Base DEX pools for new tokens and liquidity events"""
    
    def __init__(self, web3_client: Web3):
        self.web3 = web3_client
        self.last_block_processed = 0
        self.pool_cache = {}  # Cache pool data to reduce RPC calls
        
        # ABI fragments for