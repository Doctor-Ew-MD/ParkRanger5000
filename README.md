# ParkRanger5000

About the Bot
-------------
* Allows anyone to create a channel when using the proper command
* The bot will only create channels from the event-planner channel, nowhere else
* Does not allow editing channel names or deleting channels
* Only allows channel creation: is not programmed to do anything else
* @-mentioning ParkRanger or ParkRanger5000 will result in an automated help message. It no longers pings any of the users/members in the server.

Restrictions
------------
* Channel names will require a month, day, and description (this means "tbd" channels are no longer allowed)
* Channel name length must be 40 characters or less
* Duplicate channels cannot be created
* The event-planner channel has a 30-second message timer to prevent anyone from spamming it

Tech Stuff
----------
Security is always a major concern in web development, and this bot has been written to prevent sensitive information about our server, and by extension the people in it. Deployment and secrets are handled and stored by Railway, and no sensitive information is in the bot's code or on GitHub. The code utilizes the Discord API and Python library. If you would to contribute to it, or see how it was made, reach out to Drew!
