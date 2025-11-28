"""
Secure Credential Storage

Uses macOS Keychain for encryption key storage and Fernet for credential encryption.
From Gmail Module SRS Section 6.1.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet
import keyring

from ...config import Config

logger = logging.getLogger(__name__)


class CredentialStore:
    """
    Secure credential storage using macOS Keychain
    
    Encryption flow:
    1. Generate/retrieve encryption key from Keychain
    2. Use Fernet to encrypt credentials
    3. Store encrypted credentials in files
    4. Never log credentials or keys
    """
    
    def __init__(self):
        self.service_name = Config.KEYCHAIN_SERVICE
        self.key_name = Config.KEYCHAIN_ENCRYPTION_KEY
        self.credentials_dir = Config.CREDENTIALS_DIR
        
        # Ensure credentials directory exists
        self.credentials_dir.mkdir(parents=True, exist_ok=True)
        
        # Get or create encryption key
        self.cipher = self._initialize_cipher()
        
        logger.info("CredentialStore initialized with macOS Keychain")
    
    def _initialize_cipher(self) -> Fernet:
        """Initialize Fernet cipher with key from Keychain"""
        try:
            # Try to retrieve existing key from Keychain
            key_str = keyring.get_password(self.service_name, self.key_name)
            
            if key_str:
                logger.debug("Retrieved encryption key from Keychain")
                key = key_str.encode()
            else:
                # Generate new key
                key = Fernet.generate_key()
                key_str = key.decode()
                
                # Store in Keychain
                keyring.set_password(self.service_name, self.key_name, key_str)
                logger.info("Generated and stored new encryption key in Keychain")
            
            return Fernet(key)
            
        except Exception as e:
            logger.error(f"Failed to initialize cipher: {e}")
            raise
    
    def store_credential(self, service: str, credential: Dict[str, Any]) -> bool:
        """
        Encrypt and store credential
        
        Args:
            service: Service name (e.g., "gmail_oauth", "imap")
            credential: Credential data to encrypt
            
        Returns:
            bool: Success status
        """
        try:
            # Convert to JSON
            credential_json = json.dumps(credential)
            
            # Encrypt
            encrypted = self.cipher.encrypt(credential_json.encode())
            
            # Store in file
            credential_file = self.credentials_dir / f"{service}.enc"
            credential_file.write_bytes(encrypted)
            
            logger.info(f"Stored encrypted credential for: {service}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store credential for {service}: {e}")
            return False
    
    def retrieve_credential(self, service: str) -> Optional[Dict[str, Any]]:
        """
        Decrypt and retrieve credential
        
        Args:
            service: Service name
            
        Returns:
            dict: Decrypted credential or None if not found
        """
        try:
            credential_file = self.credentials_dir / f"{service}.enc"
            
            if not credential_file.exists():
                logger.debug(f"No credential found for: {service}")
                return None
            
            # Read encrypted data
            encrypted = credential_file.read_bytes()
            
            # Decrypt
            decrypted = self.cipher.decrypt(encrypted)
            
            # Parse JSON
            credential = json.loads(decrypted.decode())
            
            logger.debug(f"Retrieved credential for: {service}")
            return credential
            
        except Exception as e:
            logger.error(f"Failed to retrieve credential for {service}: {e}")
            return None
    
    def delete_credential(self, service: str) -> bool:
        """
        Delete stored credential
        
        Args:
            service: Service name
            
        Returns:
            bool: Success status
        """
        try:
            credential_file = self.credentials_dir / f"{service}.enc"
            
            if credential_file.exists():
                credential_file.unlink()
                logger.info(f"Deleted credential for: {service}")
                return True
            else:
                logger.debug(f"No credential to delete for: {service}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete credential for {service}: {e}")
            return False
    
    def has_credential(self, service: str) -> bool:
        """
        Check if credential exists
        
        Args:
            service: Service name
            
        Returns:
            bool: True if credential exists
        """
        credential_file = self.credentials_dir / f"{service}.enc"
        return credential_file.exists()
    
    def list_credentials(self) -> list:
        """
        List all stored credentials (service names only)
        
        Returns:
            list: Service names
        """
        try:
            services = []
            for file in self.credentials_dir.glob("*.enc"):
                service = file.stem  # filename without extension
                services.append(service)
            
            return services
            
        except Exception as e:
            logger.error(f"Failed to list credentials: {e}")
            return []


# Singleton instance
_credential_store: Optional[CredentialStore] = None


def get_credential_store() -> CredentialStore:
    """Get singleton credential store instance"""
    global _credential_store
    if _credential_store is None:
        _credential_store = CredentialStore()
    return _credential_store


if __name__ == "__main__":
    # Test credential store
    store = get_credential_store()
    
    print("Testing CredentialStore...")
    
    # Test store
    test_cred = {"username": "test@example.com", "password": "secret123"}
    success = store.store_credential("test_service", test_cred)
    print(f"Store: {success}")
    
    # Test retrieve
    retrieved = store.retrieve_credential("test_service")
    print(f"Retrieved: {retrieved}")
    
    # Test has
    exists = store.has_credential("test_service")
    print(f"Exists: {exists}")
    
    # Test list
    services = store.list_credentials()
    print(f"Services: {services}")
    
    # Test delete
    deleted = store.delete_credential("test_service")
    print(f"Deleted: {deleted}")
    
    print("\nCredentialStore test completed")
