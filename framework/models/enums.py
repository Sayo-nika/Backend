# Stdlib
from enum import Enum


class ModStatus(Enum):
    """All valid statuses for a mod."""
    archived = 0
    planning = 1
    in_development = 2
    playtesting = 3
    released = 4


class ConnectionType(Enum):
    """All valid service types for profile connections."""
    github = 1
    gitlab = 2
    discord = 3


class MediaType(Enum):
    image = 0
    video = 1


class ModCategory(Enum):
    """All valid categories for a mod."""
    unassigned = 0
    tools = 1
    comedy = 2
    tragic_comedy = 3
    drama = 4
    rom_com = 5
    romance = 6
    horror = 7
    mystery = 8
    satire = 9  # Elected Satire instead of Memes and Satire since Memes can fall under satire anyways.
    thriller = 10  # Compressed Suspense/Thriller into this since they're almost the same.
    sci_fi = 11


class ModColor(Enum):
    """All valid theme colours for a mod."""
    default = 0  # Default Sayonika theme colour
    red = 1
    pink = 2
    purple = 3
    deep_purple = 4
    indigo = 5
    blue = 6
    cyan = 7
    teal = 8
    green = 9
    lime = 10
    yellow = 11
    orange = 12
    deep_orange = 13


class AuthorRole(Enum):
    """All valid roles for mod authors."""
    unassigned = 0
    owner = 1
    co_owner = 2
    programmer = 3
    artist = 4
    writer = 5
    musician = 6
    public_relations = 7


class ReportType(Enum):
    ipg_violation = 0
    conduct_violation = 1
    dmca = 2


class ReactionType(Enum):
    upvote = 1
    downvote = 2
    funny = 3
