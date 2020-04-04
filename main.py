import email
import imaplib
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class MailWorker:
    def __init__(self, config):
        self.smtp_host = config.get('smtp_host')
        self.smtp_port = config.get('smtp_port')
        self.imap_host = config.get('imap_host')
        self.login = config.get('login')
        self.password = config.get('password')
        self.subject = config.get('subject')
        self.recipients = config.get('recipients')
        self.message = config.get('message')
        self.header = config.get('header')

    def send_message(self):
        message = MIMEMultipart()
        message['From'] = self.login
        message['To'] = ', '.join(self.recipients)
        message['Subject'] = self.subject
        message.attach(MIMEText(self.message))
        mailserver = smtplib.SMTP(self.smtp_host, self.smtp_port)
        # Identify ourselves to smtp gmail client
        mailserver.ehlo()
        # Secure our email with tls encryption
        mailserver.starttls()
        # Re-identify ourselves as an encrypted connection
        mailserver.ehlo()
        mailserver.login(self.login, self.password)
        mailserver.sendmail(self.login, mailserver, message.as_string())
        mailserver.quit()

    def receive(self):
        mail = imaplib.IMAP4_SSL(self.imap_host)
        mail.login(self.login, self.password)
        mail.list()
        mail.select("inbox")
        criterion = '(HEADER Subject "%s")' % self.header if self.header else 'ALL'
        result, data = mail.uid('search', None, criterion)
        assert data[0], 'There are no letters with current header'
        latest_email_uid = data[0].split()[-1]
        result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
        raw_email = data[0][1]
        email_message = email.message_from_bytes(raw_email)
        mail.logout()
        return email_message


if __name__ == '__main__':
    MailWorker({
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 587,
        'imap_host': 'imap.gmail.com',
        'login': 'login@gmail.com',
        'password': 'qwerty',
        'subject': 'Subject',
        'recipients': ['vasya@email.com', 'petya@email.com'],
        'message': 'Message',
        'header': None,
    })
