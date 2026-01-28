"""Email notification utilities for forms module."""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


def send_form_submission_notification(form, response):
    """
    Send email notification when a form is submitted.
    
    Args:
        form: Form instance
        response: FormResponse instance
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not form.send_email_on_submit or not form.notification_emails:
        return False
    
    try:
        recipients = [email.strip() for email in form.notification_emails.split(',') if email.strip()]
        
        if not recipients:
            logger.warning(f'No valid recipients for form {form.id}')
            return False
        
        # Prepare context
        context = {
            'form': form,
            'response': response,
            'respondent': response.respondent_name,
            'submitted_at': response.submitted_at,
            'answer_count': len(response.answers),
        }
        
        # Render email templates
        subject = f'New Response: {form.title}'
        html_message = render_to_string('tools/forms/emails/submission_notification.html', context)
        plain_message = strip_tags(html_message)
        
        # Create email message
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients
        )
        email.attach_alternative(html_message, "text/html")
        
        # Send email
        email.send(fail_silently=False)
        
        logger.info(f'Form submission notification sent for form {form.id} to {len(recipients)} recipients')
        return True
        
    except Exception as e:
        logger.error(f'Failed to send form notification for {form.id}: {str(e)}')
        return False


def send_form_share_email(form, recipients, sender, message=''):
    """
    Send email with form link to specific recipients.
    
    Args:
        form: Form instance
        recipients: List of email addresses
        sender: User who is sharing the form
        message: Optional personal message
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        if not recipients:
            return False
        
        context = {
            'form': form,
            'sender': sender,
            'message': message,
            'form_url': f'{settings.SITE_URL}/f/{form.share_link}/',
        }
        
        subject = f'{sender.get_full_name()} shared a form with you: {form.title}'
        html_message = render_to_string('tools/forms/emails/share_form.html', context)
        plain_message = strip_tags(html_message)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=recipients
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f'Form share email sent for form {form.id} to {len(recipients)} recipients')
        return True
        
    except Exception as e:
        logger.error(f'Failed to send form share email for {form.id}: {str(e)}')
        return False


def send_form_closed_notification(form, creator):
    """
    Notify form creator when form is automatically closed.
    
    Args:
        form: Form instance
        creator: User who created the form
    
    Returns:
        bool: True if email sent successfully
    """
    try:
        context = {
            'form': form,
            'creator': creator,
            'total_responses': form.responses.count(),
        }
        
        subject = f'Form Closed: {form.title}'
        html_message = render_to_string('tools/forms/emails/form_closed.html', context)
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[creator.email],
            fail_silently=False,
        )
        
        logger.info(f'Form closed notification sent for form {form.id}')
        return True
        
    except Exception as e:
        logger.error(f'Failed to send form closed notification for {form.id}: {str(e)}')
        return False
