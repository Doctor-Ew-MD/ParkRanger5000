#!/usr/bin/env python3
import sys
sys.path.insert(0, "/home/ec2-user/discord-bots/ParkRanger5000")

from ParkRanger5000.tasks.tasks import Task
from ParkRanger5000.utils import STATIC_TOKEN

task = Task()

task_failed = False


@task.client.event
async def on_ready():
    global task_failed
    try:
        print(f"Connected as {task.client.user}")
        print("log_test_task completed successfully")
    except Exception as e:
        print(f"log_test_task failed: {e}", file=sys.stderr)
        task_failed = True
    finally:
        await task.client.close()


if __name__ == '__main__':
    task.client.run(STATIC_TOKEN)
    if task_failed:
        sys.exit(1)
