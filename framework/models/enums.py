# Stdlib
from enum import Enum


class ModStatus(Enum):
    Planning = 1
    InDevelop = 2
    PlayTesting = 3
    Released = 4


class ConnectionType(Enum):
    GitHub = 1
    GitLab = 2
    Discord = 3


class MediaType(Enum):
    Video = 1
    Image = 2


class Category(Enum):
    Unassigned = 0
