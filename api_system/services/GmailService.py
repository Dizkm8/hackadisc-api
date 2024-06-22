import base64
import logging
import os

from smtplib import SMTP
SCOPE = ['https://www.googleapis.com/auth/gmail.send']

class GmailService:
    def __init__(self, credentials):
        self.email = os.environ["EMAIL"]
        password = os.environ["EMAIL_PWD"]
        self.server = SMTP('smtp.gmail.com', 587)
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(self.email, password)


    def send_email(self, message):
        """
        Sends an email.

        Parameters
        ----------
        message : EmailMessage
            Composed message.
        """
        if self.server is None:
            return # log error, exception?
        self.server.send_message(message)
        #encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        #result = self.service.users().messages().send(userId="me", body={"raw": encoded_message}).execute()
        #logging.info(result)