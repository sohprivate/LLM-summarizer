"""Security utilities for handling sensitive data."""
import os
import json
from pathlib import Path
from typing import Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64


class SecureConfigManager:
    """Manage encrypted configuration and credentials."""
    
    def __init__(self, config_dir: Path = Path.home() / '.paperpile-notion'):
        self.config_dir = config_dir
        self.config_dir.mkdir(exist_ok=True)
        self._cipher = self._get_or_create_cipher()
    
    def _get_or_create_cipher(self) -> Fernet:
        """Get or create encryption key."""
        key_file = self.config_dir / '.key'
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            # Generate key from machine-specific info
            machine_id = f"{os.environ.get('USER', 'default')}-{os.uname().nodename}"
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'paperpile-notion-salt',
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(machine_id.encode()))
            
            # Save key with restricted permissions
            key_file.touch(mode=0o600)
            with open(key_file, 'wb') as f:
                f.write(key)
        
        return Fernet(key)
    
    def save_credentials(self, credentials: Dict[str, str]) -> None:
        """Save encrypted credentials."""
        cred_file = self.config_dir / 'credentials.enc'
        encrypted = self._cipher.encrypt(json.dumps(credentials).encode())
        
        # Save with restricted permissions
        cred_file.touch(mode=0o600)
        with open(cred_file, 'wb') as f:
            f.write(encrypted)
    
    def load_credentials(self) -> Optional[Dict[str, str]]:
        """Load and decrypt credentials."""
        cred_file = self.config_dir / 'credentials.enc'
        
        if not cred_file.exists():
            return None
        
        try:
            with open(cred_file, 'rb') as f:
                encrypted = f.read()
            
            decrypted = self._cipher.decrypt(encrypted)
            return json.loads(decrypted.decode())
        except Exception:
            return None
    
    def validate_path(self, path: str) -> Path:
        """Validate and sanitize file paths to prevent traversal attacks."""
        # Convert to Path object and resolve
        clean_path = Path(path).resolve()
        
        # Ensure it's within allowed directories
        allowed_dirs = [
            Path.cwd(),
            Path.home() / 'Downloads',
            Path('/tmp'),
        ]
        
        if not any(str(clean_path).startswith(str(allowed)) for allowed in allowed_dirs):
            raise ValueError(f"Path {path} is outside allowed directories")
        
        return clean_path