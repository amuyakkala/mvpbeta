from typing import Dict, Any, Optional
import os
import logging
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ExternalNotificationService:
    """Service for handling external notifications (Slack/Email)."""
    
    def __init__(self):
        self.slack_client = None
        self.smtp_server = None
        self.smtp_port = None
        self.smtp_username = None
        self.smtp_password = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize external notification clients."""
        # Initialize Slack client
        slack_token = os.getenv("SLACK_BOT_TOKEN")
        if slack_token:
            logger.info(f"Initializing Slack client with token: {slack_token[:10]}...")
            self.slack_client = WebClient(token=slack_token)
        else:
            logger.warning("SLACK_BOT_TOKEN not found in environment variables")
        
        # Initialize SMTP settings
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        
        logger.info(f"SMTP settings: server={self.smtp_server}, port={self.smtp_port}, username={self.smtp_username}")
    
    async def send_slack_notification(
        self,
        channel: str,
        message: str,
        blocks: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send a notification to a Slack channel.
        
        Args:
            channel: Slack channel to send to
            message: Message text
            blocks: Optional Slack message blocks for rich formatting
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.slack_client:
            logger.warning("Slack client not initialized")
            return False
        
        try:
            # Remove # symbol if present
            channel = channel.lstrip("#")
            logger.info(f"Attempting to send Slack message to channel: {channel}")
            logger.info(f"Message content: {message}")
            if blocks:
                logger.info(f"Message blocks: {json.dumps(blocks, indent=2)}")
            
            # First, try to join the channel if we're not already in it
            try:
                logger.info(f"Attempting to join channel: {channel}")
                join_response = self.slack_client.conversations_join(channel=channel)
                logger.info(f"Join response: {join_response}")
            except SlackApiError as join_error:
                logger.warning(f"Could not join channel {channel}: {str(join_error)}")
                if join_error.response.get("error") != "already_in_channel":
                    logger.error(f"Join error: {join_error.response}")
                    return False
            
            # Now send the message
            logger.info("Sending message to Slack")
            try:
                response = self.slack_client.chat_postMessage(
                    channel=channel,
                    text=message,
                    blocks=blocks
                )
                logger.info(f"Slack API response: {response}")
                
                if response["ok"]:
                    logger.info("Slack message sent successfully")
                    return True
                else:
                    logger.error(f"Slack API returned error: {response.get('error', 'Unknown error')}")
                    return False
            except SlackApiError as e:
                logger.error(f"Slack API error while sending message: {str(e)}")
                logger.error(f"Error response: {e.response}")
                return False
            
        except Exception as e:
            logger.error(f"Unexpected error sending Slack message: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            return False
    
    async def send_email_notification(
        self,
        to_email: str,
        subject: str,
        message: str,
        html_message: Optional[str] = None
    ) -> bool:
        """
        Send an email notification.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            message: Plain text message
            html_message: Optional HTML message
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not all([self.smtp_server, self.smtp_username, self.smtp_password]):
            logger.warning("SMTP settings not configured")
            return False
        
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_username
            msg["To"] = to_email
            msg["Subject"] = subject
            
            # Add plain text message
            msg.attach(MIMEText(message, "plain"))
            
            # Add HTML message if provided
            if html_message:
                msg.attach(MIMEText(html_message, "html"))
            
            # Connect to SMTP server and send
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"Email sending error: {str(e)}")
            return False
    
    def format_issue_notification(
        self,
        issue_type: str,
        severity: str,
        message: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Format a notification for an issue.
        
        Args:
            issue_type: Type of issue
            severity: Severity level
            message: Base message
            metadata: Additional metadata
            
        Returns:
            Dict containing formatted messages for different channels
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format Slack message
        slack_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{issue_type} Alert*\nSeverity: {severity}\n{message}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Timestamp:*\n{timestamp}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Trace ID:*\n{metadata.get('trace_id', 'N/A')}"
                    }
                ]
            }
        ]
        
        # Format email message
        email_html = f"""
        <html>
            <body>
                <h2>{issue_type} Alert</h2>
                <p><strong>Severity:</strong> {severity}</p>
                <p>{message}</p>
                <hr>
                <p><strong>Timestamp:</strong> {timestamp}</p>
                <p><strong>Trace ID:</strong> {metadata.get('trace_id', 'N/A')}</p>
                <p><strong>Additional Details:</strong></p>
                <ul>
                    {''.join(f'<li><strong>{k}:</strong> {v}</li>' for k, v in metadata.items())}
                </ul>
            </body>
        </html>
        """
        
        return {
            "slack": {
                "text": f"{issue_type} Alert: {message}",
                "blocks": slack_blocks
            },
            "email": {
                "subject": f"{severity.upper()} Alert: {issue_type}",
                "text": f"{issue_type} Alert\nSeverity: {severity}\n{message}\n\nTimestamp: {timestamp}\nTrace ID: {metadata.get('trace_id', 'N/A')}",
                "html": email_html
            }
        } 