# ParkRanger5000

This bot is here help you perform some of the functions that our Park Rangers usually handle.
If you prefer a human's help, the Park Rangers are always around, so feel free to @-mention them if you need anything.

## Commands

---

### `!create <channel name>`

Allows a member to create a new event channel. 
The channel will appear in the *Events* category.
Once the create command succeeds, the Event channels will be resorted. 
(e.g., a January 2027 event channel created in 2026 will appear below all channels for events happening in 2026.)

**Requirements**
- Must include a month, day (or date range), and a description.
- Maximum 40 characters.
- Channel name must be unique; cannot be identical to a channel currently in the *Events* category.
- `<channel name>` accepts spaces or hyphens between words.
- Month abbreviations are auto-enforced. The bot recognizes the first three letters of each month, and will convert your input to match that.
- Any invalid characters will be stripped out of the channel name before creation, so you might not end up with the exact title you expected.

**Example usage**
```
!create may 4 star wars marathon
!create may-4-star-wars-marathon
```

---

### `!rename <old channel name> -> <new channel name>`

Allows a member to rename an existing event channel. 
All posts in that channel will persist, only the name will change.
Once the rename succeeds, the Event channels will be resorted.

**Requirements**
- `<old channel name>` must exactly match the name of a channel in the *Events* category.
- `<new channel name>` must follow the requirements outlined in the `!create` command.
- The `->` characters must be present in the command.
- Both parameters accept spaces or hyphens between words, but be consistent.

**Example usage**
```
!rename july 4 sound bath -> july 5 hearing test
!rename july-4-sound-bath -> july-5-hearing-test
```

---

### `@ParkRanger5000`

@-mentioning the bot will result in it sending a message to the current channel.
The message contains some useful guidance on how to use it.
You can't chat with it though, it's not AI!

Similarly, @-mentioning the ParkRanger role will alert all human Park Rangers, but will also trigger a small help message from the bot.

---

## About the Bot

* Allows anyone to create a channel when using the proper command.
* The bot will only create channels from the event-planner channel, nowhere else.
* Does not allow editing channel names or deleting channels.
* Only allows channel creation: is not programmed to do anything else.
* @-mentioning ParkRanger or ParkRanger5000 will result in an automated help message. It no longers pings any of the users/members in the server.


## Tech Stuff

This bot is a bundle of code that is being hosted and run on an AWS EC2 instance. 
It has the potential to go down or have service disrupted at any time, for reasons that are beyond our control. 
If it isn't working, ping DrewpyDrawers for help, assuming he hasn't started investigating the issue already.

Security is always a major concern in web development, and this bot has been written to prevent sensitive information about our server-- and by extension the people in it-- from being exposed or made easily available. 
Deployment and secrets are handled and stored by AWS, and no sensitive information is in the bot's code or on GitHub.
If you find a token in the commit history, it has already been rotated!

If you would like to contribute, hmu!