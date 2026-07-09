import calendar
import os
from string import ascii_lowercase

STATIC_TOKEN = os.getenv("STATIC_TOKEN")

BOT_ROLE_NAMES = {"ParkRanger5000", "ParkRanger",}
INTRODUCTION_CHANNEL_NAME = "introduction"

CHANNEL_ERROR_MSG = (
    "Remember to include a month, day (or a range, like: 25-26), and description, like this:"
    "\n**!create dec 31 nye dance party**"
)
CHANNEL_NAME_CHARS = ascii_lowercase + " " +  "-" + "".join(str(i) for i in range(0, 10))

VALID_MONTHS = [month.lower() for month in calendar.month_name]
VALID_MONTHS += [month.lower() for month in calendar.month_abbr]
VALID_MONTHS += ["june", "july", "sept"]

MONTHS_ABBR = list(map(lambda x: x.lower(), list(calendar.month_abbr)))
MONTHS_ABBR[6] = "june"
MONTHS_ABBR[7] = "july"
MONTHS_ABBR[9] = "sept"

EVENTS_CHANNEL_NAME = "event-planner"  # Delete af
