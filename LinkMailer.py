#
import schedule
import time
import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

# SECTION 1: Configuration and Setup

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Validate environment variables
def validate_env_vars():
    """Ensure all required environment variables are set."""
    required_vars = ['EMAIL_USER', 'EMAIL_PASS', 'SMTP_SERVER', 'SMTP_PORT', 'RECIPIENT_EMAIL']
    for var in required_vars:
        if not os.getenv(var):
            raise EnvironmentError(f"Environment variable {var} is not set.")

# SECTION 2: Email Handling

def send_email(subject, body, to_email):
    """Compose and send an email with the specified subject and body."""
    try:
        from_email = os.getenv('EMAIL_USER')
        password = os.getenv('EMAIL_PASS')

        # Set up the MIME
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # Create the server connection and send the email
        with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
            server.starttls()
            server.login(from_email, password)
            server.sendmail(from_email, to_email, msg.as_string())

        logging.info(f"Email sent successfully to {to_email} with subject: {subject}")

    except smtplib.SMTPAuthenticationError:
        logging.error("Failed to authenticate with the SMTP server. Check your email credentials.")
    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
    except Exception as e:
        logging.error(f"Failed to send email: {e}")

def send_links(links, subject, to_email):
    """Format and send an email containing the provided links."""
    try:
        body = "Please find the requested links below:\n\n" + "\n".join(links)
        send_email(subject, body, to_email)
    except Exception as e:
        logging.error(f"Failed to send links: {e}")

# SECTION 3: Scheduling

def schedule_emails(links_list, subject, recipient_email, schedule_times):
    """Schedule emails to be sent at specified times with different sets of links."""
    for index, time_slot in enumerate(schedule_times):
        if index < len(links_list):
            schedule.every().day.at(time_slot).do(
                send_links, links=links_list[index], subject=subject, to_email=recipient_email
            )
        else:
            logging.warning(f"No links provided for the time slot {time_slot}, skipping scheduling.")

# SECTION 4: Main Execution

def main():
    """Main function to initialize the scheduler."""
    try:
        validate_env_vars()

        # Example list of link sets to be sent at different times
        links_list = [
            ["https://example.com/link1", "https://example.com/link2", "https://example.com/link3"],
            ["https://example.com/link4", "https://example.com/link5"],
            ["https://example.com/link6", "https://example.com/link7", "https://example.com/link8"]
        ]

        # Configuration
        email_subject = "Here are your scheduled links"
        recipient_email = os.getenv('RECIPIENT_EMAIL')
        schedule_times = ["09:00", "13:00", "18:00"]

        schedule_emails(links_list, email_subject, recipient_email, schedule_times)

        logging.info("Scheduler started. Waiting for scheduled tasks...")
        while True:
            schedule.run_pending()
            time.sleep(1)

    except EnvironmentError as e:
        logging.critical(f"Configuration error: {e}")
    except Exception as e:
        logging.critical(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
