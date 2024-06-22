import base64
import logging
import os

from smtplib import SMTP
SCOPE = ['https://www.googleapis.com/auth/gmail.send']

class GmailService:
    def __init__(self):
        self.email = os.environ["SENDER_MAIL"]
        password = os.environ["SENDER_MAIL_PWD"]
        self.server = SMTP('smtp.gmail.com', 587)
        self.server.ehlo()
        self.server.starttls()
        self.server.ehlo()
        self.server.login(self.email, password)

    def disconnect(self):
        self.server.close()

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