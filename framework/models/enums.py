# Stdlib
from enum import Enum


class ModStatus(Enum):
    """All valid statuses for a mod."""
    Archived = 0
    Planning = 1
    InDevelopment = 2
    Playtesting = 3
    Released = 4


class ConnectionType(Enum):
    """All valid service types for profile connections."""
    GitHub = 1
    GitLab = 2
    Discord = 3


class MediaType(Enum):
    Image = 0
    Video = 1


class ModCategory(Enum):
    """All valid categories for a mod."""
    Unassigned = 0
    Tools = 1
    Comedy = 2
    TragicComedy = 3
    Drama = 4
    RomCom = 5
    Romance = 6
    Horror = 7
    Mystery = 8
    Satire = 9  # Elected Satire instead of Memes and Satire since Memes can fall under satire anyways.
    Thriller = 10  # Compressed Suspense/Thriller into this since they're almost the same.
    SciFi = 11


class ModColor(Enum):
    """All valid theme colours for a mod."""
    Default = 0  # Default Sayonika theme colour
    Red = 1
    Pink = 2
    Purple = 3
    DeepPurple = 4
    Indigo = 5
    Blue = 6
    Cyan = 7
    Teal = 8
    Green = 9
    Lime = 10
    Yellow = 11
    Orange = 12
    DeepOrange = 13


class AuthorRole(Enum):
    """All valid roles for mod authors."""
    Unassigned = 0
    Owner = 1
    CoOwner = 2
    Programmer = 3
    Artist = 4
    Writer = 5
    Musician = 6
    PublicRelations = 7
