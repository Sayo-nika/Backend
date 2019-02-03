# Stdlib
from enum import Enum


class ModStatus(Enum):
    Planning = 1
    InDevelopment = 2
    PlayTesting = 3
    Released = 4
    Archived = 5


class ConnectionType(Enum):
    GitHub = 1
    GitLab = 2
    Discord = 3


class MediaType(Enum):
    Video = 1
    Image = 2


class ModCategory(Enum):
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
    Thriller = 10  # compressed Suspense/Thriller into this since they're almost the same.
    SciFi = 11
