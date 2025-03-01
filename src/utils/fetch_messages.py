import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

async def fetch_all_today_messages(client, channel_entity):
    """
    Fetch all messages from the start of the current day using a chunked approach.

    This function retrieves all messages from the specified Telegram channel starting
    from the beginning of the current day (in UTC). It uses chunked retrieval to bypass
    the default limit of 100 messages and converts message timestamps to offset-aware UTC
    for proper comparison. The returned list is sorted from oldest to newest.

    Args:
        client: An instance of TelegramClient used to fetch messages.
        channel_entity: The channel entity (username or entity object) to fetch messages from.

    Returns:
        list: A list of message objects from the start of the current day, sorted from oldest to newest.
    """
    start_of_today_aware = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    all_messages = []
    offset_id = 0

    while True:
        chunk = await client.get_messages(entity=channel_entity, offset_id=offset_id, limit=100)
        if not chunk:
            break
        for msg in chunk:
            msg_date = (msg.date.astimezone(timezone.utc)
                        if msg.date.tzinfo else msg.date.replace(tzinfo=timezone.utc))
            if msg_date >= start_of_today_aware:
                all_messages.append(msg)
            else:
                break
        offset_id = chunk[-1].id
        last_msg_date = (chunk[-1].date.astimezone(timezone.utc)
                         if chunk[-1].date.tzinfo else chunk[-1].date.replace(tzinfo=timezone.utc))
        if last_msg_date < start_of_today_aware:
            break

    all_messages.reverse()
    logger.info("Fetched %d messages for 'today' from the channel.", len(all_messages))
    return all_messages
