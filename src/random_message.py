import random
import re

def get_random_right_channel(channels, ctx):
    random_i = random.randint(0, len(channels) - 1)
    random_channel = channels[random_i]
    if random_channel.permissions_for(ctx.guild.me).read_message_history:
        return random_channel
    else:
        # Remove the channel from the list and try again
        channels.pop(random_i)
        if len(channels) == 0:
            return None
        return get_random_right_channel(channels, ctx)

def get_random_url_in_messages(messages, bot_user):
    random_i = random.randint(0, len(messages) - 1)
    message = messages[random_i]
    # Look for youtubes links in the message
    urls = re.findall(r'(https?://www.youtube.com/[^\s]+)', message.content)
    
    if urls and message.author != bot_user:
        # Take the vidio id from the link
        id = urls[0].split('v=')[1]
        id = id.split('&')[0]
        return id, message.content
    
    else:
        # Remove the message from the list and try again
        messages.pop(random_i)
        if len(messages) == 0:
            return None, None
        return get_random_url_in_messages(messages, bot_user)