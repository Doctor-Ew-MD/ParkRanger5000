#!/usr/bin/env python3
import sys
import traceback

sys.path.insert(0, "/home/ec2-user/discord-bots/ParkRanger5000")

from datetime import datetime, date, timedelta

from ParkRanger5000.tasks.tasks import Task
from ParkRanger5000.categories import EventCategory
from ParkRanger5000.utils import PAST_EVENTS_CATEGORY_NAME, GUILD_ID, EVENTS_CATEGORY_NAME, STATIC_TOKEN, \
    EVENTS_CHANNEL_NAME

task = Task()

task_failed = False


async def update_past_events_task(guild):
    """
    Scan the Event Category for channels whose date has past, and move them
    into the Past Events category, then sort.
    """
    all_channels = await guild.fetch_channels()
    event_category = [c for c in all_channels if c.name == EVENTS_CATEGORY_NAME][0]
    event_channels = [c for c in all_channels if c.category_id == event_category.id]
    past_event_category = [c for c in all_channels if c.name == PAST_EVENTS_CATEGORY_NAME][0]

    for channel in event_channels:
        if channel.name == EVENTS_CHANNEL_NAME or "wrestling" in channel.name:
            continue  # ignore channel, it should not be moved
        channel_date = channel.name.split("-")[:3]

        try:
            # Check if this is a ranged date so that we use the latest date possible in the event name
            int(channel_date[2])
        except ValueError:
            date_index = 1
        else:
            date_index = 2

        current_year = date.today().year
        parsed = datetime.strptime(f"{channel_date[0]}-{channel_date[date_index]}-{current_year}", "%b-%d-%Y")
        event_date = parsed.replace(year=date.today().year).date()

        if event_date + timedelta(days=3) < date.today():
            await channel.move(beginning=True, category=past_event_category)

    # Re-fetch updated Past Events category
    updated_channels = await guild.fetch_channels()
    past_event_category_channels = [c for c in updated_channels if c.category_id == past_event_category.id]

    past_event_category_obj = EventCategory(guild, PAST_EVENTS_CATEGORY_NAME, past_event_category_channels)
    await past_event_category_obj.sort(reverse=True)


@task.client.event
async def on_ready():
    global task_failed
    try:
        guild = await task.client.fetch_guild(GUILD_ID)
        if guild is None:
            raise RuntimeError(f"Guild {GUILD_ID} not found — check GUILD_ID or bot membership")
        await update_past_events_task(guild)
        print("update_past_events_task completed successfully")
    except Exception as e:
        print(f"update_past_events_task failed: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        task_failed = True
    finally:
        await task.client.close()


if __name__ == '__main__':
    task.client.run(STATIC_TOKEN)
    if task_failed:
        sys.exit(1)