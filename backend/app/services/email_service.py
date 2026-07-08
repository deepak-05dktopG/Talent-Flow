"""
services/email_service.py - Email Delivery Service
====================================================
This file handles sending emails to candidates at every stage of the recruitment process.

How it works:
- When a candidate's status changes (e.g., Shortlisted, Rejected, Interview Scheduled),
  the backend automatically sends them a notification email.
- All emails are formatted as clean HTML for a professional look in the inbox.
- If Gmail/SMTP credentials are not configured, emails are saved to a local "emails.log"
  file so you can still test all the email logic without real credentials.

Email types supported:
  1. Application received confirmation
  2. Shortlisting notification
  3. Interview scheduling with link, date, and interviewer
  4. Rejection notification
  5. Job offer notification
  6. Custom recruitment round progress notification
  7. Fully custom body email (recruiter writes the content from the UI)
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app import config
import os

def send_html_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Core email sending function used by all other email functions in this file.
    
    Steps:
    1. Check if SMTP credentials are configured (Gmail username and app password)
    2. If yes: Send the email through Gmail's SMTP server
    3. If no: Write the email content to 'emails.log' for review (development fallback)
    
    Returns True if the email was sent or logged successfully, False otherwise.
    """
    print(f"[Email Service] Preparing SMTP email to: {to_email} | Subject: {subject}")
    
    def write_to_log():
        """Fallback: Save the email to a local log file when SMTP is not configured."""
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

    # If no SMTP credentials exist, fall back to log file
    if not config.SMTP_USER or not config.SMTP_PASSWORD:
        print(f"[Email Service][FALLBACK] SMTP credentials missing. Writing email to emails.log")
        return write_to_log()
            
    try:
        # Build the email structure (MIME = email format standard)
        msg = MIMEMultipart("alternative")  # "alternative" allows HTML fallback to plain text
        msg["From"] = f"TalentFlow Careers <{config.SMTP_USER}>"  # Sender display name
        msg["To"] = to_email
        msg["Subject"] = subject
        
        # Attach the HTML content as the email body
        part = MIMEText(html_content, "html")
        msg.attach(part)
        
        # Connect to Gmail's SMTP server and send the email
        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.ehlo()          # Identify ourselves to the email server
            server.starttls()      # Upgrade connection to secure TLS encryption
            server.ehlo()          # Re-identify after TLS upgrade
            server.login(config.SMTP_USER, config.SMTP_PASSWORD)  # Authenticate with Gmail
            server.sendmail(config.SMTP_USER, [to_email], msg.as_string())  # Send the email
            
        print(f"[Email Service] Email sent successfully via SMTP to {to_email}")
        return True
    except Exception as e:
        # If SMTP fails (network issue, wrong password, etc.), fall back to log file
        print(f"[Email Service] SMTP delivery failed sending to {to_email}: {e}")
        print(f"[Email Service][FALLBACK] Writing copy of email to emails.log")
        return write_to_log()

# ══════════════════════════════════════════════
# EMAIL TEMPLATE FUNCTIONS
# Each function below builds specific HTML email templates
# and calls send_html_email() to deliver them.
# ══════════════════════════════════════════════

def send_application_received_email(to_email: str, candidate_name: str, job_title: str) -> bool:
    """
    Sends a confirmation email to a candidate immediately after they submit their application.
    Message: "Thank you for applying — we've received your resume and will review it."
    """
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
    """
    Sends a "Congratulations, you're shortlisted!" email when HR moves a candidate forward.
    Message: "Great news — you've been selected for the next round!"
    """
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
    """
    Sends a detailed interview invitation email with all the meeting details.
    Includes: Date & Time, Meeting Link (clickable), and Interviewer name.
    """
    subject = f"Interview Scheduled: {job_title} - TalentFlow"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h2 style="color: #0d6efd; margin-bottom: 20px;">Interview Scheduled</h2>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            Hi {candidate_name},<br/><br/>
            Your interview for the <strong>{job_title}</strong> position has been scheduled.
        </p>
        <!-- Interview details box -->
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #0d6efd;">
            <p style="margin: 5px 0; font-size: 15px;"><strong>Interviewer:</strong> {interviewer}</p>
            <p style="margin: 5px 0; font-size: 15px;"><strong>Date &amp; Time:</strong> {date_time}</p>
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
    """
    Sends a polite rejection email when a candidate is not selected.
    Message: "We regret to inform you — we'll keep your resume on file for future openings."
    """
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
    """
    Sends a job offer congratulations email when a candidate is selected.
    Message: "You're hired! Formal offer letter coming in 24 hours."
    """
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
    """
    Sends a generic progress update email for custom hiring rounds.
    Used when the HR team moves a candidate to a company-specific stage
    (e.g., "UX Design Round", "Management Interview", "Background Check").
    """
    subject = f"Application Update: Stage '{round_name}' for {job_title}"
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <h2 style="color: #0d6efd; margin-bottom: 20px;">Hello {candidate_name},</h2>
        <p style="font-size: 16px; line-height: 1.6; color: #333;">
            We wanted to provide an update on your application for the <strong>{job_title}</strong> position.
        </p>
        <!-- Highlight the current stage name prominently -->
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
    """
    Sends an email using completely custom text typed by the HR recruiter.
    
    Used when the recruiter edits the email template in the popup modal before sending.
    The text is wrapped in an HTML container with 'white-space: pre-wrap' to preserve
    line breaks and formatting exactly as the recruiter typed them.
    """
    # Wrap the custom plain text in a styled HTML container
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
        <!-- pre-wrap preserves newlines and spacing from the recruiter's custom text -->
        <div style="font-size: 16px; line-height: 1.6; color: #333; white-space: pre-wrap;">{body_text}</div>
        <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;" />
        <p style="font-size: 12px; color: #666;">
            Best regards,<br/>
            <strong>TalentFlow Careers Team</strong>
        </p>
    </div>
    """
    return send_html_email(to_email, subject, html)
