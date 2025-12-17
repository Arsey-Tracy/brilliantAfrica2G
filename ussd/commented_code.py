# # Funtion to send SMS via Africa's Talking
# def send_sms(phone_number, message, command="NEXT"):
#     """
#     Sends an SMS to the specified phone number using Africa's Talking API.
#     If the message exceeds 160 characters, it splits it into multiple messages.
#     """
#     try:
#         messages = split_message(message, command=command)
        
#         for msg in messages:
#             # sms.send(msg, [phone_number])
#             response = sms.send(msg, [phone_number])
#             print(f"SMS sent to {phone_number}: {response}")
#     except Exception as e:
#         print(f"Error sending SMS: {e}")

# Function to split long messages into chunks of 160 characters
def split_message(message, chunk_size=160, command="NEXT"):
    """ 
    Splits a long message into sequential chunks of specified size wih a command at the end of each.
    """
    
    messages = []
    i = 0
    while i < len(message):
        chunk = message[i:i + chunk_size].rstrip()
        # Append command
        chunk += f"[{command}]"
        messages.append(chunk)
        i += chunk_size
    
    return messages
    # return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]

def send_sms_chunk():
    pass

def send_sms_async(phone_number, message):
    """
    Sends an SMS asynchronously to the specified phone number using Africa's Talking API.
    If the message exceeds 160 characters, it splits it into multiple messages.
    """
    import threading

    thread = threading.Thread(target=send_sms_chunk, args=(phone_number, message))
    thread.start()
