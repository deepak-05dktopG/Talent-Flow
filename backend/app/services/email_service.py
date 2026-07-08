import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app import config
import os

def send_html_email(to_email: str, subject: str, html_content: str) -> bool:
    print(f"[Email Service] Preparing SMTP email to: {to_email} | Subject: {subject}")
    
    def write_to_log():
        log_file = "emails.log"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n==================================================\n")
                f.write(f"TO: {to_email}\n")
                f.write(f"SUBJECT: {subject}\n")
                f.write(f"HTML:\n{html_content}\n")
                f.write(f"==================================================\n")
            print(f"[Email Service][LOGGED] Written copy of email to emails.log")
            return True
        except Exception as e:
            print(f"[Email Service] Failed to write mock email log: {e}")
            return False

    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        # Fallback: Write email to local file and log to console
        print(f"[Email Service][FALLBACK] SMTP credentials missing. Writing email to emails.log")
        return write_to_log()
            
    try:
        # Construct MIME message
        msg = MIMEMultipart("alternative")
        msg["From"] = f"TalentFlow Careers <{config.SMTP_USER}>"
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Attach html body
        part = MIMEText(html_content, "html")
        msg.attach(part)
        
        # Deliver via smtplib
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)
            server.sendmail(config.SMTP_USER, [to_email], msg.as_string())
            
        print(f"[Email Service] Email sent successfully via SMTP to {to_email}")
        return True
    except Exception as e:
        print(f"[Email Service] SMTP delivery failed sending to {to_email}: {e}")
        print(f"[Email Service][FALLBACK] Writing copy of email to emails.log")
        return write_to_log()

# Templates
def send_application_received_email(to_email: str, candidate_name: str, job_title: str) -> bool:
    subject = f"Application Received: {job_title} at TalentFlow"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h2 style="color: #0d6efd; margin-bottom: 20px;">Hi {candidate_name},</h2>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            Thank you for applying for the <strong>{job_title}</strong> position outline. We have successfully received your application and resume.
        </p>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            Our HR team is currently reviewing your application. If your profile aligns with our requirements, we will reach out to you for the next steps!
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
        <p style="font-size: 12px; color: #666;">
            Best regards,<br/>
            <strong>TalentFlow Careers Team</strong>
        </p>
    </div>
    """
    return send_html_email(to_email, subject, html)

def send_shortlisted_email(to_email: str, candidate_name: str, job_title: str) -> bool:
    subject = f"Congratulations! You've been Shortlisted for {job_title}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h2 style="color: #198754; margin-bottom: 20px;">Great News, {candidate_name}!</h2>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            Our HR team reviewed your resume and we are excited to let you know that you have been **shortlisted** for the <strong>{job_title}</strong> position!
        </p>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            The next step is a technical interview. We will schedule a virtual call with you shortly. Please keep an eye out for a scheduling invitation.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
        <p style="font-size: 12px; color: #666;">
            Best regards,<br/>
            <strong>TalentFlow Careers Team</strong>
        </p>
    </div>
    """
    return send_html_email(to_email, subject, html)

def send_interview_scheduled_email(to_email: str, candidate_name: str, job_title: str, date_time: str, meeting_link: str, interviewer: str) -> bool:
    subject = f"Interview Scheduled: {job_title} - TalentFlow"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h2 style="color: #0d6efd; margin-bottom: 20px;">Interview Scheduled</h2>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            Hi {candidate_name},<br/><br/>
            Your interview for the <strong>{job_title}</strong> position has been scheduled.
        </p>
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #0d6efd;">
            <p style="margin: 5px 0; font-size: 15px;"><strong>Interviewer:</strong> {interviewer}</p>
            <p style="margin: 5px 0; font-size: 15px;"><strong>Date & Time:</strong> {date_time}</p>
            <p style="margin: 5px 0; font-size: 15px;"><strong>Meeting Link:</strong> <a href="{meeting_link}" target="_blank" style="color: #0d6efd;">Join Meeting</a></p>
        </div>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            Please ensure you join on time, are in a quiet environment, and have a good internet connection. We look forward to speaking with you!
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
        <p style="font-size: 12px; color: #666;">
            Best regards,<br/>
            <strong>TalentFlow Careers Team</strong>
        </p>
    </div>
    """
    return send_html_email(to_email, subject, html)

def send_rejected_email(to_email: str, candidate_name: str, job_title: str) -> bool:
    subject = f"Application Update: {job_title}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h2 style="color: #dc3545; margin-bottom: 20px;">Dear {candidate_name},</h2>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            Thank you for your interest in the <strong>{job_title}</strong> role and for taking the time to apply.
        </p>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            After reviewing our applicant pool, we regret to inform you that we will not be moving forward with your application at this time. We receive many applications from qualified candidates, which makes our decision-making process difficult.
        </p>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            We will keep your resume in our database for future opportunities that match your expertise. We wish you the very best in your job hunt and career goals.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
        <p style="font-size: 12px; color: #666;">
            Best regards,<br/>
            <strong>TalentFlow Careers Team</strong>
        </p>
    </div>
    """
    return send_html_email(to_email, subject, html)

def send_offer_email(to_email: str, candidate_name: str, job_title: str) -> bool:
    subject = f"Job Offer: {job_title} - TalentFlow"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h2 style="color: #198754; margin-bottom: 20px;">Job Offer – Congratulations!</h2>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            Dear {candidate_name},<br/><br/>
            We are absolutely thrilled to extend an offer of employment to you for the position of <strong>{job_title}</strong>!
        </p>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            The HR team will be emailing you the formal offer letter complete with compensation structure, benefits details, and start dates within the next 24 hours. We are excited about the prospect of you joining our team and building great things together.
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
        <p style="font-size: 12px; color: #666;">
            Best regards,<br/>
            <strong>TalentFlow Careers Team</strong>
        </p>
    </div>
    """
    return send_html_email(to_email, subject, html)

def send_custom_round_email(to_email: str, candidate_name: str, job_title: str, round_name: str) -> bool:
    subject = f"Application Update: Stage '{round_name}' for {job_title}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h2 style="color: #0d6efd; margin-bottom: 20px;">Hello {candidate_name},</h2>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            We wanted to provide an update on your application for the <strong>{job_title}</strong> position.
        </p>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            Your candidate status has progressed to: <strong>{round_name}</strong>.
        </p>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            Our talent acquisition team will contact you shortly with the details and coordination for this round. Thank you!
        </p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
        <p style="font-size: 12px; color: #666;">
            Best regards,<br/>
            <strong>TalentFlow Careers Team</strong>
        </p>
    </div>
    """
    return send_html_email(to_email, subject, html)

def send_custom_body_email(to_email: str, subject: str, body_text: str) -> bool:
    # Preserve formatting using HTML linebreaks/pre-wrap
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <div style="font-size: 16px; line-height: 1.6; color: #333; white-space: pre-wrap;">{body_text}</div>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
        <p style="font-size: 12px; color: #666;">
            Best regards,<br/>
            <strong>TalentFlow Careers Team</strong>
        </p>
    </div>
    """
    return send_html_email(to_email, subject, html)


