import africastalking
import threading


sms = africastalking.SMS

class SMSService:
    """
    Service for sending SMS messages.
    """
    def __init__(self):
        pass
    
    def send_sms(self, phone_number, message):
        # def _send():
        #     sms.send(message, [phone_number])
        # threading.Thread(target=_send).start()
        sms.send(message, [phone_number])
        
    
    def send_sms_async(self, phone_number, message):
        threading.Thread(target=self.send_sms, args=(phone_number, message)).start()