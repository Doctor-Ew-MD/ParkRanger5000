import calendar
import os
import re
from string import ascii_lowercase

class SilentError(Exception):
    """
    Used by on_command_error to prevent an exception from being messaged in the client.
    """
    pass

STATIC_TOKEN = os.getenv("STATIC_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")

BOT_ROLE_NAMES = {"ParkRanger5000", "ParkRanger",}
INTRODUCTION_CHANNEL_NAME = "introduction"

CHANNEL_ERROR_MSG = (
    "Remember to include a month, day (or a range, like: 25-26), and description, like this:"
    "\n**!create dec 31 nye dance party**"
)

QUOTES = [
    "\u2018",
    "\u2019",
    "\u201c",
    "\u201d",
    "'",
    '"',
]
EMOJI_RANGES = [
    "\U0001F300-\U0001FAFF",
    "\U00002600-\U000027BF",
    "\U0001F1E6-\U0001F1FF",
    "\u200d",
    "\ufe0f",
]

VALID_MONTHS = [month.lower() for month in calendar.month_name]
VALID_MONTHS += [month.lower() for month in calendar.month_abbr]
VALID_MONTHS += ["june", "july", "sept"]

MONTHS_ABBR = list(map(lambda x: x.lower(), list(calendar.month_abbr)))
MONTHS_ABBR[6] = "june"
MONTHS_ABBR[7] = "july"
MONTHS_ABBR[9] = "sept"

EVENTS_CHANNEL_NAME = "event-planner"
EVENTS_CATEGORY_NAME = "Events"
PAST_EVENTS_CATEGORY_NAME = "Past Events (AUG 2026 -)"

UNVERIFIED_ROLE = "Unverified"
VERIFIED_ROLE = "Verified"
VERIFICATION_REACTION_COUNT = 5
VERIFICATION_REACTION_BLOCK = "❌"

CHANNEL_SORT_DAYS_THRESHOLD = 2
