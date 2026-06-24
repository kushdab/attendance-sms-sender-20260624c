import os
import csv
import logging
import africastalking
from dotenv import load_dotenv

# Configure logging to track SMS delivery attempts
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AttendanceSMS")

class AttendanceSMSManager:
    """Manages school attendance alerts via Africa's Talking API."""

    def __init__(self, username, api_key, sender_id=None):
        """
        Initialize Africa's Talking SDK.
        :param username: 'sandbox' or production username
        :param api_key: API Key from Africa's Talking dashboard
        :param sender_id: Shortcode or Alphanumeric sender ID (optional)
        """
        africastalking.initialize(username, api_key)
        self.sms = africastalking.SMS
        self.sender_id = sender_id
        logger.info("Africa's Talking SDK initialized successfully.")

    def send_notification(self, student_name, parent_phone, status):
        """
        Sends a customized SMS based on the student's attendance status.
        """
        message = self._generate_message(student_name, status)
        
        try:
            # Phone numbers must be in international format (e.g., +254...)
            if not parent_phone.startswith('+'):
                logger.warning(f"Phone number {parent_phone} might be invalid. Use E.164 format.")

            response = self.sms.send(message, [parent_phone], self.sender_id)
            
            recipients = response['SMSMessageData']['Recipients']
            for recipient in recipients:
                status_code = recipient['statusCode']
                if status_code == 101: # Success code for AT
                    logger.info(f"Alert sent for {student_name} to {parent_phone}. MessageID: {recipient['messageId']}")
                else:
                    logger.error(f"Failed to send to {parent_phone}. Error: {recipient['status']}")
            return response

        except Exception as e:
            logger.error(f"Critical error while sending SMS to {parent_phone}: {str(e)}")
            return None

    def _generate_message(self, name, status):
        """Helper to format the message body."""
        status_lower = status.strip().lower()
        if status_lower == 'absent':
            return f"ATTENDANCE ALERT: {name} was marked ABSENT from school today. Please contact the administration if this is an error."
        elif status_lower == 'late':
            return f"ATTENDANCE ALERT: {name} arrived at school LATE today. Please ensure timely arrival in the future."
        else:
            return f"ATTENDANCE NOTICE: {name} has arrived safely at school today. Status: {status.upper()}."

    def process_attendance_file(self, csv_file_path):
        """
        Reads a CSV file and sends alerts for each entry.
        CSV Header expected: student_name, parent_phone, status
        """
        if not os.path.exists(csv_file_path):
            logger.error(f"CSV File not found: {csv_file_path}")
            return

        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            count = 0
            for row in reader:
                name = row.get('student_name')
                phone = row.get('parent_phone')
                status = row.get('status')

                if name and phone and status:
                    self.send_notification(name.strip(), phone.strip(), status.strip())
                    count += 1
            
            logger.info(f"Batch processing completed. {count} records handled.")

def main():
    """Entry point for the attendance tool."""
    load_dotenv() # Load credentials from .env file

    username = os.getenv("AT_USERNAME")
    api_key = os.getenv("AT_API_KEY")
    sender_id = os.getenv("AT_SENDER_ID") # Optional

    if not username or not api_key:
        logger.critical("Missing credentials! Ensure AT_USERNAME and AT_API_KEY are in your .env file.")
        return

    manager = AttendanceSMSManager(username, api_key, sender_id)

    # Check for attendance.csv or run a manual test
    csv_path = "attendance.csv"
    if os.path.exists(csv_path):
        logger.info(f"Found {csv_path}. Starting batch process...")
        manager.process_attendance_file(csv_path)
    else:
        logger.info("No CSV found. Sending single test notification...")
        # Example: Replace with a real number for testing
        manager.send_notification("Test Student", "+254700000000", "absent")

if __name__ == "__main__":
    main()