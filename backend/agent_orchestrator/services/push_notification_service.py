"""
Push Notification Service
Handles sending push notifications via JPush (极光推送)
"""
import os
import base64
import logging
from typing import List, Dict, Optional
from datetime import datetime, time
import requests
from supabase import Client

logger = logging.getLogger(__name__)


class PushNotificationService:
    """Service for sending push notifications to users"""

    def __init__(self, supabase_client: Client):
        """
        Initialize PushNotificationService

        Args:
            supabase_client: Supabase client for database operations
        """
        self.supabase = supabase_client
        self.jpush_app_key = os.getenv("JPUSH_APP_KEY", "")
        self.jpush_master_secret = os.getenv("JPUSH_MASTER_SECRET", "")
        self.jpush_api_url = "https://api.jpush.cn/v3/push"

        if not self.jpush_app_key or not self.jpush_master_secret:
            logger.warning("JPush credentials not configured. Push notifications will be disabled.")

    def _get_jpush_auth(self) -> str:
        """Generate JPush Basic Auth header value"""
        credentials = f"{self.jpush_app_key}:{self.jpush_master_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return encoded

    async def _get_user_registration_ids(self, user_id: str) -> List[str]:
        """
        Get active push registration IDs for a user

        Args:
            user_id: UUID of the user

        Returns:
            List of active registration IDs
        """
        try:
            response = self.supabase.table('user_devices') \
                .select('push_registration_id') \
                .eq('user_id', user_id) \
                .eq('is_active', True) \
                .execute()

            if response.data:
                return [device['push_registration_id'] for device in response.data]
            return []
        except Exception as e:
            logger.error(f"Error fetching registration IDs for user {user_id}: {e}")
            return []

    async def _get_notification_settings(self, user_id: str) -> Optional[Dict]:
        """
        Get notification settings for a user

        Args:
            user_id: UUID of the user

        Returns:
            Notification settings dict or None
        """
        try:
            response = self.supabase.table('user_notification_settings') \
                .select('*') \
                .eq('user_id', user_id) \
                .single() \
                .execute()

            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error fetching notification settings for user {user_id}: {e}")
            return None

    def _is_quiet_hours(self, settings: Dict) -> bool:
        """
        Check if current time is within quiet hours

        Args:
            settings: User notification settings dict

        Returns:
            True if in quiet hours, False otherwise
        """
        if not settings.get('quiet_hours_enabled', True):
            return False

        try:
            now = datetime.now().time()
            start_str = settings.get('quiet_hours_start', '22:00')
            end_str = settings.get('quiet_hours_end', '08:00')

            # Parse time strings (format: HH:MM or HH:MM:SS)
            if isinstance(start_str, str):
                start_parts = start_str.split(':')
                start = time(int(start_parts[0]), int(start_parts[1]))
            else:
                start = start_str

            if isinstance(end_str, str):
                end_parts = end_str.split(':')
                end = time(int(end_parts[0]), int(end_parts[1]))
            else:
                end = end_str

            # Handle cases where quiet hours span midnight
            if start < end:
                return start <= now <= end
            else:
                return now >= start or now <= end
        except Exception as e:
            logger.error(f"Error checking quiet hours: {e}")
            return False

    def _should_send_notification(
        self,
        briefing: Dict,
        settings: Optional[Dict]
    ) -> bool:
        """
        Determine if a notification should be sent based on settings

        Args:
            briefing: Briefing data dict
            settings: User notification settings dict

        Returns:
            True if notification should be sent, False otherwise
        """
        # Default settings if not configured
        if not settings:
            settings = {
                'enabled': True,
                'quiet_hours_enabled': True,
                'min_priority': 'P1',
                'notify_types': ['alert', 'insight', 'action']
            }

        # Check if notifications are enabled
        if not settings.get('enabled', True):
            logger.debug("Notifications disabled for user")
            return False

        # Check quiet hours
        if self._is_quiet_hours(settings):
            logger.debug("In quiet hours, skipping notification")
            return False

        # Check priority threshold
        min_priority = settings.get('min_priority', 'P1')
        briefing_priority = briefing.get('priority', 'P2')

        priority_order = {'P0': 0, 'P1': 1, 'P2': 2}
        if priority_order.get(briefing_priority, 2) > priority_order.get(min_priority, 1):
            logger.debug(f"Briefing priority {briefing_priority} below threshold {min_priority}")
            return False

        # Check importance score (only push P0/P1 with high importance)
        importance_score = briefing.get('importance_score', 0.0)
        if importance_score < 0.7:
            logger.debug(f"Importance score {importance_score} below threshold 0.7")
            return False

        return True

    async def _log_notification(
        self,
        user_id: str,
        briefing_id: str,
        status: str,
        error_message: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Log notification send attempt

        Args:
            user_id: UUID of the user
            briefing_id: UUID of the briefing
            status: Status of notification (sent/failed/clicked/dismissed)
            error_message: Error message if failed
            metadata: Additional metadata
        """
        try:
            self.supabase.table('notification_logs').insert({
                'user_id': user_id,
                'briefing_id': briefing_id,
                'status': status,
                'push_provider': 'jpush',
                'error_message': error_message,
                'metadata': metadata or {}
            }).execute()
        except Exception as e:
            logger.error(f"Error logging notification: {e}")

    async def send_briefing_notification(
        self,
        user_id: str,
        briefing: Dict
    ) -> bool:
        """
        Send push notification for a briefing

        Args:
            user_id: UUID of the user
            briefing: Briefing data dict with keys:
                - id: Briefing UUID
                - title: Briefing title
                - summary: Briefing summary
                - priority: Priority (P0/P1/P2)
                - importance_score: Importance score (0-1)
                - agent_id: Agent UUID
                - agent_name: Agent display name

        Returns:
            True if notification sent successfully, False otherwise
        """
        briefing_id = briefing.get('id')

        try:
            # Check if JPush is configured
            if not self.jpush_app_key or not self.jpush_master_secret:
                logger.warning(f"JPush not configured, skipping notification for briefing {briefing_id}")
                return False

            # Get user's push registration IDs
            registration_ids = await self._get_user_registration_ids(user_id)
            if not registration_ids:
                logger.info(f"No active devices for user {user_id}")
                return False

            # Get user notification settings
            settings = await self._get_notification_settings(user_id)

            # Check if notification should be sent
            if not self._should_send_notification(briefing, settings):
                logger.info(f"Notification filtering applied, skipping briefing {briefing_id}")
                return False

            # Build JPush payload
            agent_name = briefing.get('agent_name', 'AI Employee')
            priority = briefing.get('priority', 'P1')
            title = briefing.get('title', 'New Briefing')
            summary = briefing.get('summary', '')

            # Truncate summary for notification
            notification_text = summary[:100] + '...' if len(summary) > 100 else summary

            payload = {
                "platform": ["android", "ios"],
                "audience": {
                    "registration_id": registration_ids
                },
                "notification": {
                    "alert": notification_text,
                    "android": {
                        "title": f"{agent_name} · {priority}",
                        "alert": notification_text,
                        "priority": 1,
                        "extras": {
                            "type": "briefing",
                            "briefing_id": briefing_id,
                            "agent_id": briefing.get('agent_id'),
                            "priority": priority
                        }
                    },
                    "ios": {
                        "alert": {
                            "title": f"{agent_name} · {priority}",
                            "body": notification_text
                        },
                        "sound": "default",
                        "badge": "+1",
                        "extras": {
                            "type": "briefing",
                            "briefing_id": briefing_id,
                            "agent_id": briefing.get('agent_id'),
                            "priority": priority
                        }
                    }
                },
                "options": {
                    "time_to_live": 86400,  # 24 hours
                    "apns_production": os.getenv("JPUSH_APNS_PRODUCTION", "false").lower() == "true"
                }
            }

            # Send to JPush
            headers = {
                "Authorization": f"Basic {self._get_jpush_auth()}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                self.jpush_api_url,
                json=payload,
                headers=headers,
                timeout=10
            )

            # Log result
            if response.status_code == 200:
                response_data = response.json()
                await self._log_notification(
                    user_id,
                    briefing_id,
                    'sent',
                    metadata={
                        'msg_id': response_data.get('msg_id'),
                        'sendno': response_data.get('sendno')
                    }
                )
                logger.info(f"Push notification sent for briefing {briefing_id}")
                return True
            else:
                error_msg = f"JPush API error: {response.status_code} - {response.text}"
                await self._log_notification(
                    user_id,
                    briefing_id,
                    'failed',
                    error_message=error_msg
                )
                logger.error(error_msg)
                return False

        except Exception as e:
            error_msg = f"Error sending push notification: {str(e)}"
            logger.error(error_msg)
            await self._log_notification(
                user_id,
                briefing_id,
                'failed',
                error_message=error_msg
            )
            return False

    async def register_device(
        self,
        user_id: str,
        registration_id: str,
        platform: str,
        device_info: Optional[Dict] = None
    ) -> bool:
        """
        Register or update a user's device for push notifications

        Args:
            user_id: UUID of the user
            registration_id: JPush registration ID
            platform: Platform (ios/android)
            device_info: Optional device information dict

        Returns:
            True if successful, False otherwise
        """
        try:
            device_data = {
                'user_id': user_id,
                'push_registration_id': registration_id,
                'push_provider': 'jpush',
                'platform': platform,
                'is_active': True,
                'last_active_at': datetime.now().isoformat()
            }

            if device_info:
                device_data.update({
                    'device_name': device_info.get('device_name'),
                    'device_model': device_info.get('device_model'),
                    'os_version': device_info.get('os_version'),
                    'app_version': device_info.get('app_version')
                })

            # Upsert device
            self.supabase.table('user_devices').upsert(
                device_data,
                on_conflict='user_id,push_registration_id'
            ).execute()

            logger.info(f"Device registered for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error registering device: {e}")
            return False

    async def unregister_device(
        self,
        user_id: str,
        registration_id: str
    ) -> bool:
        """
        Unregister a user's device (mark as inactive)

        Args:
            user_id: UUID of the user
            registration_id: JPush registration ID

        Returns:
            True if successful, False otherwise
        """
        try:
            self.supabase.table('user_devices') \
                .update({'is_active': False}) \
                .eq('user_id', user_id) \
                .eq('push_registration_id', registration_id) \
                .execute()

            logger.info(f"Device unregistered for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error unregistering device: {e}")
            return False
