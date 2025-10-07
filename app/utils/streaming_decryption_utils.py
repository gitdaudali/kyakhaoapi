"""
Streaming Decryption Utilities
Chunk-based encryption/decryption for video streaming
"""

import base64
import hashlib
import json
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import settings


class StreamingDecryption:
    """Streaming decryption for video chunks"""

    def __init__(self):
        # Use a master key from settings or generate one
        self.master_key = getattr(settings, "STREAMING_MASTER_KEY", None)
        if not self.master_key:
            # Generate a random master key (in production, this should be in settings)
            self.master_key = Fernet.generate_key()

    def generate_file_key(self, content_id: str, file_id: str) -> Tuple[str, str]:
        """
        Generate a unique encryption key for a specific file

        Args:
            content_id: Content ID
            file_id: File ID

        Returns:
            Tuple of (key_id, encrypted_key)
        """
        # Generate a random key for this file
        file_key = Fernet.generate_key()

        # Create a unique key ID
        key_id = f"stream_key_{content_id}_{file_id}_{secrets.token_hex(8)}"

        # Encrypt the file key with the master key
        fernet = Fernet(self.master_key)
        encrypted_key = fernet.encrypt(file_key)

        return key_id, base64.b64encode(encrypted_key).decode("utf-8")

    def decrypt_file_key(self, encrypted_key: str) -> bytes:
        """
        Decrypt a file key

        Args:
            encrypted_key: Base64 encoded encrypted key

        Returns:
            Decrypted file key
        """
        try:
            # Decode from base64
            encrypted_data = base64.b64decode(encrypted_key.encode("utf-8"))

            # Decrypt with master key
            fernet = Fernet(self.master_key)
            file_key = fernet.decrypt(encrypted_data)

            return file_key
        except Exception:
            raise ValueError("Invalid encrypted key")

    def create_access_token(
        self, key_id: str, file_id: str, expires_hours: int = 24
    ) -> str:
        """
        Create an access token for streaming

        Args:
            key_id: Encryption key ID
            file_id: File ID
            expires_hours: Token expiration in hours

        Returns:
            Base64 encoded access token
        """
        # Create token data
        token_data = {
            "key_id": key_id,
            "file_id": file_id,
            "expires_at": (
                datetime.utcnow() + timedelta(hours=expires_hours)
            ).isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "type": "streaming_access",
        }

        # Convert to JSON
        token_json = json.dumps(token_data)

        # Encrypt token
        fernet = Fernet(self.master_key)
        encrypted_token = fernet.encrypt(token_json.encode("utf-8"))

        # Return base64 encoded
        return base64.b64encode(encrypted_token).decode("utf-8")

    def validate_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate and decode an access token

        Args:
            token: Base64 encoded access token

        Returns:
            Token data if valid, None if invalid/expired
        """
        try:
            # Decode from base64
            encrypted_token = base64.b64decode(token.encode("utf-8"))

            # Decrypt token
            fernet = Fernet(self.master_key)
            token_json = fernet.decrypt(encrypted_token).decode("utf-8")

            # Parse JSON
            token_data = json.loads(token_json)

            # Check expiration
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            if datetime.utcnow() > expires_at:
                return None

            return token_data

        except Exception:
            return None

    def generate_chunk_key(
        self, file_key: bytes, chunk_index: int
    ) -> Tuple[bytes, bytes]:
        """
        Generate a unique key and IV for a specific chunk

        Args:
            file_key: Base file encryption key
            chunk_index: Chunk index

        Returns:
            Tuple of (chunk_key, iv)
        """
        # Create chunk-specific salt
        chunk_salt = f"chunk_{chunk_index}".encode("utf-8")

        # Derive chunk key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=chunk_salt,
            iterations=100000,
            backend=default_backend(),
        )
        chunk_key = kdf.derive(file_key)

        # Generate IV for this chunk
        iv = secrets.token_bytes(16)  # 128 bits

        return chunk_key, iv

    def encrypt_chunk(self, chunk_data: bytes, chunk_key: bytes, iv: bytes) -> bytes:
        """
        Encrypt a chunk of data

        Args:
            chunk_data: Raw chunk data
            chunk_key: Chunk-specific encryption key
            iv: Initialization vector

        Returns:
            Encrypted chunk data
        """
        # Create cipher
        cipher = Cipher(
            algorithms.AES(chunk_key), modes.CBC(iv), backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # Pad data to block size
        block_size = 16
        padding_length = block_size - (len(chunk_data) % block_size)
        padded_data = chunk_data + bytes([padding_length] * padding_length)

        # Encrypt
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        return encrypted_data

    def decrypt_chunk(
        self, encrypted_data: bytes, chunk_key: bytes, iv: bytes
    ) -> bytes:
        """
        Decrypt a chunk of data

        Args:
            encrypted_data: Encrypted chunk data
            chunk_key: Chunk-specific decryption key
            iv: Initialization vector

        Returns:
            Decrypted chunk data
        """
        # Create cipher
        cipher = Cipher(
            algorithms.AES(chunk_key), modes.CBC(iv), backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # Decrypt
        decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()

        # Remove padding
        padding_length = decrypted_padded[-1]
        decrypted_data = decrypted_padded[:-padding_length]

        return decrypted_data

    def calculate_chunks(self, file_size: int, chunk_size: int = 1048576) -> int:
        """
        Calculate total number of chunks for a file

        Args:
            file_size: Total file size in bytes
            chunk_size: Chunk size in bytes (default 1MB)

        Returns:
            Total number of chunks
        """
        return (file_size + chunk_size - 1) // chunk_size  # Ceiling division


# Global streaming decryption instance
streaming_decryption = StreamingDecryption()


def get_streaming_decryption_instance() -> StreamingDecryption:
    """Get the global streaming decryption instance"""
    return streaming_decryption


def generate_streaming_file_key(content_id: str, file_id: str) -> Tuple[str, str]:
    """Generate streaming encryption key for a file"""
    return streaming_decryption.generate_file_key(content_id, file_id)


def decrypt_streaming_file_key(encrypted_key: str) -> bytes:
    """Decrypt a streaming file key"""
    return streaming_decryption.decrypt_file_key(encrypted_key)


def create_streaming_access_token(
    key_id: str, file_id: str, expires_hours: int = 24
) -> str:
    """Create streaming access token"""
    return streaming_decryption.create_access_token(key_id, file_id, expires_hours)


def validate_streaming_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Validate streaming access token"""
    return streaming_decryption.validate_access_token(token)


def generate_chunk_encryption_key(
    file_key: bytes, chunk_index: int
) -> Tuple[bytes, bytes]:
    """Generate encryption key and IV for a chunk"""
    return streaming_decryption.generate_chunk_key(file_key, chunk_index)


def encrypt_streaming_chunk(chunk_data: bytes, chunk_key: bytes, iv: bytes) -> bytes:
    """Encrypt a streaming chunk"""
    return streaming_decryption.encrypt_chunk(chunk_data, chunk_key, iv)


def decrypt_streaming_chunk(
    encrypted_data: bytes, chunk_key: bytes, iv: bytes
) -> bytes:
    """Decrypt a streaming chunk"""
    return streaming_decryption.decrypt_chunk(encrypted_data, chunk_key, iv)


def calculate_streaming_chunks(file_size: int, chunk_size: int = 1048576) -> int:
    """Calculate total number of chunks for streaming"""
    return streaming_decryption.calculate_chunks(file_size, chunk_size)
