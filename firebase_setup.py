"""
Firebase Firestore initialization and management
CRITICAL: All state management goes through Firestore
"""
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from config import FIREBASE

# Configure logging
logging.basicConfig(level=getattr(logging, SYSTEM.LOG_LEVEL))
logger = logging.getLogger(__name__)

class FirebaseManager:
    """Singleton Firebase manager for Liquid Cortex"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_firebase()
            self._initialized = True
    
    def _initialize_firebase(self) -> None:
        """Initialize Firebase app and Firestore client"""
        try:
            # Check if credentials file exists
            if not os.path.exists(FIREBASE.CREDENTIALS_PATH):
                logger.error(f"Firebase credentials file not found at {FIREBASE.CREDENTIALS_PATH}")
                raise FileNotFoundError("Firebase credentials file not found")
            
            # Load credentials
            cred = credentials.Certificate(FIREBASE.CREDENTIALS_PATH)
            
            # Initialize app if not already initialized
            if not firebase_admin._apps:
                firebase_admin.initialize_app(cred, {
                    'projectId': FIREBASE.PROJECT_ID
                })
            
            self.db = firestore.client()
            logger.info("Firebase Firestore initialized successfully")
            
            # Initialize collections if they don't exist
            self._initialize_collections()
            
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    def _initialize_collections(self) -> None:
        """Create base documents in each collection if they don't exist"""
        try:
            # System state document
            system_ref = self.db.collection(FIREBASE.COLLECTIONS["system_state"]).document("liquid_cortex")
            if not system_ref.get().exists:
                initial_state = {
                    "capital": RISK.INITIAL_CAPITAL,
                    "active_positions": [],
                    "total_trades": 0,
                    "win_rate": 0.0,
                    "current_mode": "CONSERVATIVE",
                    "last_adaptation": firestore.SERVER_TIMESTAMP,
                    "parameters": {
                        "liquidity_threshold": RISK.MIN_LIQUIDITY,
                        "momentum_sensitivity": 0.3,
                        "profit_target_multiplier": 1.0
                    },
                    "created_at": firestore.SERVER_TIMESTAMP,
                    "updated_at": firestore.SERVER_TIMESTAMP
                }
                system_ref.set(initial_state)
                logger.info("Initialized system state document")
            
            # Blacklist collection
            blacklist_ref = self.db.collection(FIREBASE.COLLECTIONS["blacklist"])
            
            # Check if there's at least one document to verify collection exists
            test_doc = blacklist_ref.document("test").get()
            if not test_doc.exists:
                # Collection exists but is empty, which is fine
                pass
                
        except Exception as e:
            logger.error(f"Failed to initialize collections: {e}")
    
    def update_system_state(self, updates: Dict[str, Any]) -> None:
        """Update system state document with atomic operations"""
        try:
            system_ref = self.db.collection(FIREBASE.COLLECTIONS["system_state"]).document("liquid_cortex")
            
            # Add timestamp
            updates["updated_at"] = firestore.SERVER_TIMESTAMP
            
            system_ref.update(updates)
            logger.debug("Updated system state")
            
        except Exception as e:
            logger.error(f"Failed to update system state: {e}")
    
    def log_market_signal(self, signal_type: str, data: Dict[str, Any]) -> str:
        """Log market signal to Firestore with timestamp"""
        try:
            collection = self.db.collection(FIREBASE.COLLECTIONS["market_signals"])
            
            document_data = {
                "type": signal_type,
                "data": data,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "processed": False
            }
            
            # Add confidence score if present
            if "confidence" in data:
                document_data["confidence"] = data["confidence"]
            
            doc_ref = collection.add(document_data)[1]
            logger.debug(f"Logged market signal: {signal_type}")
            return doc_ref.id
            
        except Exception as e:
            logger.error(f"Failed to log market signal: {e}")
            return ""
    
    def log_trade_signal(self, signal: Dict[str, Any]) -> str:
        """Log trade decision to Firestore"""
        try:
            collection = self.db.collection(FIREBASE.COLLECTIONS["trade_signals"])
            
            signal_data = {
                **signal,
                "timestamp": firestore.SERVER_TIMESTAMP,
                "executed": False,
                "execution_id": None
            }
            
            doc_ref = collection.add(signal_data)[1]
            logger.info(f"Logged trade signal for {signal.get('token_address', 'unknown')}")
            return doc_ref.id
            
        except Exception as e:
            logger.error(f"Failed to log trade signal: {e}")
            return ""
    
    def log_execution(self, execution_data: Dict[str, Any]) -> str:
        """Log trade execution details"""
        try:
            collection = self.db.collection(FIREBASE.COLLECTIONS["execution_logs"])
            
            execution_data["timestamp"] = firestore.SERVER_TIMESTAMP
            execution_data["status"] = "PENDING"
            
            doc_ref = collection.add(execution_data)[1]
            logger.info(f"Logged execution with tx: {execution_data.get('tx_hash', 'pending')}")
            return doc_ref.id
            
        except Exception as e:
            logger.error(f"Failed to log execution: {e}")
            return ""
    
    def get_active_positions(self) -> list:
        """Get all active positions from system state"""
        try:
            system_ref = self.db.collection(FIREBASE.COLLECTIONS["system_state"]).document("liquid_cortex")
            doc = system_ref.get()
            
            if doc.exists:
                return doc.to_dict().get("active_positions", [])
            return []
            
        except Exception as e:
            logger.error(f"Failed to get active positions: {e}")
            return []
    
    def add_to_blacklist(self, address: str, reason: str, details: Dict[str, Any] = None) -> None:
        """Add contract address to blacklist"""
        try:
            collection = self.db.collection(FIREBASE.COLLECTIONS["blacklist"])
            
            blacklist_data = {
                "address": address,
                "reason": reason,
                "details": details or {},
                "timestamp": firestore.SERVER_TIMESTAMP,
                "active": True
            }
            
            # Use address as document ID for easy lookup
            collection.document(address.lower()).set(blacklist_data)
            logger.warning(f"Added {address} to blacklist: {reason}")
            
        except Exception as e:
            logger.error(f"Failed to add to blacklist: {e}")
    
    def is_blacklisted(self, address: str) -> bool:
        """Check if address is in blacklist"""
        try:
            collection = self.db.collection(FIREBASE.COLLECTIONS["blacklist"])
            doc = collection.document(address.lower()).get()
            
            if doc.exists:
                data = doc.to_dict()
                return data.get("active", True)
            return False
            
        except Exception as e:
            logger.error(f"Failed to check blacklist: {e}")
            return True  # Err on side of caution
    
    def get_parameter(self, param_name: str, default: Any = None) -> Any:
        """Get current system parameter"""
        try:
            system_ref = self.db.collection(FIREBASE.COLLECTIONS["system_state"]).document("liquid_cortex")
            doc = system_ref.get()
            
            if doc.exists:
                params = doc.to_dict().get("parameters", {})
                return params.get(param_name, default)
            return default
            
        except Exception as e:
            logger.error(f"Failed to get parameter {param_name}: {e}")
            return default

# Global instance
firebase_manager = FirebaseManager()