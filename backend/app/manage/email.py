import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(sender,cred,subj,content,recipients=['dali.braham.mohamed13@gmail.com','bloodyangelofdespair@gmail.com']):
    sender_email = send_email
    #receiver_email = ",".join(recipients)
    password = cred  
    #subject = subj
    #body = content

    # Email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subj
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)  # this is just for the email header (visible in inbox)



    # Attach the HTML content to the message
    msg.attach(MIMEText(content, "html"))

    


    with smtplib.SMTP("smtp.gmail.com",587) as server:
        server.starttls()
        server.login(sender_email,password)
        server.sendmail(sender_email,recipients,msg.as_string())
