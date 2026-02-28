from enum import Enum


class SummaryLength(str, Enum):
    SHORT = "short"
    VERBOSE = "verbose"


class SummaryAudience(str, Enum):
    CLINICIANS = "clinicians"
    LAYPEOPLE = "laypeople"
