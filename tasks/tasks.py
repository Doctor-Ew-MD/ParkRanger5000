from discord import Client

from ParkRanger5000.intents import IntentsHandler
from ParkRanger5000.utils import STATIC_TOKEN

class Task:
    def __init__(self):
        if STATIC_TOKEN:
            self.intents = IntentsHandler().set_intents()
            self.client = Client(intents=self.intents)
        else:
            raise Exception("You must set the STATIC_TOKEN environment variable to run automated tasks.")
