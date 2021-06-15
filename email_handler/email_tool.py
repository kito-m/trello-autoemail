import smtplib
import ssl

class Email_tool():
    def __init__(self, sender_email, password):
        self.smtp_server = "smtp.gmail.com"
        self.port = 587
        self.sender_email = sender_email
        self.password = password
        self.context = ssl.create_default_context()

    def send_email(self, recipient_email, subject, message_body):
        message = f"Subject: {subject}\n{message_body}"
        try:
            server = smtplib.SMTP(self.smtp_server, self.port)
            server.starttls(context=self.context)           
            server.login(self.sender_email, self.password)
            server.sendmail(self.sender_email, recipient_email, message)
        except Exception as e:
            print(e)
        finally:
            server.quit()

