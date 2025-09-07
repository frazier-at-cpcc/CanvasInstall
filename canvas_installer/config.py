"""
Configuration management for Canvas LMS installer
"""

from dataclasses import dataclass, asdict
from typing import Dict


@dataclass
class InstallationConfig:
    """Configuration class to store all installation parameters"""
    domain: str = ""
    canvas_password: str = ""
    smtp_server: str = ""
    smtp_port: str = "465"
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = ""
    smtp_from_name: str = ""
    flickr_api_key: str = ""
    youtube_api_key: str = ""
    skip_ssl: bool = False
    skip_rce: bool = False
    skip_optimization: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'InstallationConfig':
        return cls(**data)