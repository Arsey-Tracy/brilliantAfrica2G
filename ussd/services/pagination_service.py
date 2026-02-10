import africastalking
from django.core.cache import cache

sms = africastalking.SMS

class PaginationService:
    """
    Pagination service for navigating the ai tutor.
    """
    def __init__(self):
        pass
    def smart_split_message(self, message: str, chunk_size: int = 150):
        messages = []
        if len(message) <= chunk_size:
            return [message]
        
        start = 0
        while start < len(message):
            end = start + chunk_size
            if end >= len(message):
                messages.append(message[start:].strip())
                break
            last_space = message.rfind(' ', start, end)
            if last_space == -1 or last_space <= start:
                chunk = message[start:end].strip()
                start = end
            else:
                chunk = message[start:last_space].strip()
                start = last_space + 1
            if chunk:
                messages.append(chunk)
        return messages
    
    def initiate_paginated_sms(self, phone_number, full_message, command_str=" (NEXT)"):
        chunks = self.smart_split_message(full_message)
        if not chunks:
            return
        first_chunk = chunks[0]
        if len(chunks) > 1:
            first_chunk += command_str
            cache.set(f"sms_pagination_{phone_number}",{
                "chunks": chunks,
                "current_index": 1
            }, timeout=3600)
        sms.send(first_chunk, [phone_number])
    
    def handle_next_chunk(phone_number):
        cache_key = f"sms_pagination_{phone_number}"
        session_data = cache.get(cache_key)
        if not session_data:
            sms.send("No more messages to display.", [phone_number])
            return
        chunks = session_data["chunks"]
        index = session_data["current_index"]
        if index >= len(chunks):
            sms.send("No more messages to display.", [phone_number])
            cache.delete(cache_key)
            return
        next_chunk = chunks[index]
        if index < len(chunks) - 1:
            next_chunk += " (NEXT)"
            session_data["current_index"] += 1
            cache.set(cache_key, session_data, timeout=3600)
        else:
            cache.delete(cache_key)