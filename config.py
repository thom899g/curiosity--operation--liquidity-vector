"""
Configuration management for Liquid Cortex
Centralized config with environment variable fallbacks
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

@dataclass
class NetworkConfig:
    """Base L2 network configuration"""
    RPC_URL: str = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
    CHAIN_ID: int = 8453
    EXPLORER_URL: str = "https://basescan.org"
    NATIVE_TOKEN: str = "ETH"
    GAS_LIMIT_BUFFER: float = 1.2  # 20% buffer
    
@dataclass
class DEXConfig:
    """DEX addresses on Base"""
    UNISWAP_V3_FACTORY: str = "0x33128a8fC17869897dcE68Ed026d694621f6FDfD"
    BASESWAP_FACTORY: str = "0xFDa619b6d20975be80A10332cD39b9a4b0FAa8BB"
    AERODROME_FACTORY: str = "0x420DD381b31aEf6683db6B902084cB0FFECe40Da"
    
    # Router addresses
    UNISWAP_ROUTER: str = "0x2626664c2603336E57B271c5C0b26F421741e481"
    BASESWAP_ROUTER: str = "0x327Df1E6de05895d2ab08513aaDD9313Fe505d86"
    
@dataclass
class RiskConfig:
    """Risk management parameters"""
    INITIAL_CAPITAL: float = 13.0  # USD
    SOFT_STOP: float = 9.0
    HARD_STOP: float = 7.0
    MAX_POSITION_SIZE: float = 0.5  # 50% of capital
    MIN_LIQUIDITY: float = 50000.0  # USD
    MAX_SLIPPAGE: float = 0.03  # 3%
    GAS_COST_MULTIPLIER: float = 5.0  # Profit must be 5x gas
    
@dataclass
class StrategyConfig:
    """Trading strategy parameters"""
    TRACK_A_TIMEOUT: int = 60  # seconds
    TRACK_A_TARGET_PROFIT: float = 0.25  # 25%
    TRACK_B_TAKE_PROFIT_1: float = 0.10  # 10%
    TRACK_B_TAKE_PROFIT_2: float = 0.15  # 15%
    TRACK_B_TRAILING_STOP: float = 0.07  # 7%
    VOLUME_SPIKE_THRESHOLD: float = 2.0  # 200% of average
    
@dataclass
class FirebaseConfig:
    """Firebase configuration"""
    CREDENTIALS_PATH: str = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase_credentials.json")
    PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "")
    COLLECTIONS: dict = None
    
    def __post_init__(self):
        if self.COLLECTIONS is None:
            self.COLLECTIONS = {
                "market_signals": "market_signals",
                "trade_signals": "trade_signals", 
                "execution_logs": "execution_logs",
                "system_state": "system_state",
                "blacklist": "blacklist"
            }

@dataclass
class APIConfig:
    """External API configurations"""
    INFURA_KEY: Optional[str] = os.getenv("INFURA_API_KEY")
    QUICKNODE_KEY: Optional[str] = os.getenv("QUICKNODE_API_KEY")
    FLASHBOTS_RPC: str = "https://rpc.flashbots.net"
    COINGECKO_API: str = "https://api.coingecko.com/api/v3"
    
@dataclass
class SystemConfig:
    """System-wide configuration"""
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    CHECK_INTERVAL: int = 15  # seconds for perception layer
    ADAPTATION_INTERVAL: int = 21600  # 6 hours in seconds
    CANARY_ALLOCATION: float = 0.1  # 10% for experimental
    
# Global config instance
NETWORK = NetworkConfig()
DEX = DEXConfig()
RISK = RiskConfig()
STRATEGY = StrategyConfig()
FIREBASE = FirebaseConfig()
API = APIConfig()
SYSTEM = SystemConfig()