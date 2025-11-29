"""
External resources management
"""

from .github_resources import GitHubResourceManager
from .proxy_sources import ProxySources
from .resource_manager import ResourceManager
from .wordlist_updater import WordlistUpdater

__all__ = [
    'GitHubResourceManager',
    'ProxySources',
    'ResourceManager', 
    'WordlistUpdater'
]