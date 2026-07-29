import logging

logger = logging.getLogger(__name__)

class SMSProviderStub:
    """
    Stub SMS Provider mimicking integration with gateways like MSG91 or Twilio.
    Prints OTPs and notifications to server console instead of sending actual messages.
    """
    def __init__(self):
        logger.warning("Using SMSProviderStub — NOT for production use")
        
    async def send_otp(self, phone_number: str, otp: str) -> bool:
        # PII: Mask phone number in logs
        masked_phone = f"******{phone_number[-4:]}" if len(phone_number) >= 4 else "**********"
        logger.info(f"STUB SMS OTP: {otp} sent to {masked_phone}")
        print(f"\n--- STUB SMS OTP SENT --- \nPhone: {phone_number}\nOTP: {otp}\n-------------------------\n")
        return True
        
    async def send_notification(self, phone_number: str, message: str, language: str = 'en') -> bool:
        masked_phone = f"******{phone_number[-4:]}" if len(phone_number) >= 4 else "**********"
        logger.info(f"STUB SMS Notification sent to {masked_phone} in {language}: {message[:50]}...")
        print(f"\n--- STUB SMS NOTIFICATION ---\nPhone: {phone_number}\nMsg: {message}\nLang: {language}\n-----------------------------\n")
        return True
