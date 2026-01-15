"""
Push Notifications API Routes
Handles device registration and notification settings
"""
from typing import Optional, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from supabase import Client

from ..api.deps import get_supabase_client, get_current_user
from ..services import PushNotificationService

router = APIRouter(prefix="/notifications", tags=["notifications"])


# Request/Response Models
class DeviceRegistrationRequest(BaseModel):
    """Device registration request"""
    registration_id: str = Field(..., description="JPush registration ID")
    platform: str = Field(..., description="Platform (ios/android)")
    device_name: Optional[str] = Field(None, description="Device name")
    device_model: Optional[str] = Field(None, description="Device model")
    os_version: Optional[str] = Field(None, description="OS version")
    app_version: Optional[str] = Field(None, description="App version")


class DeviceUnregistrationRequest(BaseModel):
    """Device unregistration request"""
    registration_id: str = Field(..., description="JPush registration ID")


class NotificationSettingsRequest(BaseModel):
    """Notification settings update request"""
    enabled: Optional[bool] = Field(None, description="Enable/disable notifications")
    quiet_hours_enabled: Optional[bool] = Field(None, description="Enable quiet hours")
    quiet_hours_start: Optional[str] = Field(None, description="Quiet hours start time (HH:MM)")
    quiet_hours_end: Optional[str] = Field(None, description="Quiet hours end time (HH:MM)")
    min_priority: Optional[str] = Field(None, description="Minimum priority (P0/P1/P2)")
    notify_types: Optional[list] = Field(None, description="Notification types to receive")


class NotificationSettingsResponse(BaseModel):
    """Notification settings response"""
    enabled: bool
    quiet_hours_enabled: bool
    quiet_hours_start: str
    quiet_hours_end: str
    min_priority: str
    notify_types: list


class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool
    message: str


# API Endpoints
@router.post("/register-device", response_model=SuccessResponse)
async def register_device(
    request: DeviceRegistrationRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Register a device for push notifications

    Args:
        request: Device registration data
        current_user: Current authenticated user
        supabase: Supabase client

    Returns:
        Success response
    """
    push_service = PushNotificationService(supabase)

    device_info = {
        'device_name': request.device_name,
        'device_model': request.device_model,
        'os_version': request.os_version,
        'app_version': request.app_version
    }

    success = await push_service.register_device(
        user_id=current_user['id'],
        registration_id=request.registration_id,
        platform=request.platform,
        device_info=device_info
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register device"
        )

    return SuccessResponse(
        success=True,
        message="Device registered successfully"
    )


@router.post("/unregister-device", response_model=SuccessResponse)
async def unregister_device(
    request: DeviceUnregistrationRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Unregister a device from push notifications

    Args:
        request: Device unregistration data
        current_user: Current authenticated user
        supabase: Supabase client

    Returns:
        Success response
    """
    push_service = PushNotificationService(supabase)

    success = await push_service.unregister_device(
        user_id=current_user['id'],
        registration_id=request.registration_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unregister device"
        )

    return SuccessResponse(
        success=True,
        message="Device unregistered successfully"
    )


@router.get("/settings", response_model=NotificationSettingsResponse)
async def get_notification_settings(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Get user notification settings

    Args:
        current_user: Current authenticated user
        supabase: Supabase client

    Returns:
        Notification settings
    """
    try:
        response = supabase.table('user_notification_settings') \
            .select('*') \
            .eq('user_id', current_user['id']) \
            .single() \
            .execute()

        if not response.data:
            # Return default settings if not found
            return NotificationSettingsResponse(
                enabled=True,
                quiet_hours_enabled=True,
                quiet_hours_start="22:00",
                quiet_hours_end="08:00",
                min_priority="P1",
                notify_types=["alert", "insight", "action"]
            )

        settings = response.data
        return NotificationSettingsResponse(
            enabled=settings.get('enabled', True),
            quiet_hours_enabled=settings.get('quiet_hours_enabled', True),
            quiet_hours_start=str(settings.get('quiet_hours_start', '22:00')),
            quiet_hours_end=str(settings.get('quiet_hours_end', '08:00')),
            min_priority=settings.get('min_priority', 'P1'),
            notify_types=settings.get('notify_types', ["alert", "insight", "action"])
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch notification settings: {str(e)}"
        )


@router.put("/settings", response_model=SuccessResponse)
async def update_notification_settings(
    request: NotificationSettingsRequest,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    Update user notification settings

    Args:
        request: Notification settings update data
        current_user: Current authenticated user
        supabase: Supabase client

    Returns:
        Success response
    """
    try:
        # Build update data (only include provided fields)
        update_data = {}
        if request.enabled is not None:
            update_data['enabled'] = request.enabled
        if request.quiet_hours_enabled is not None:
            update_data['quiet_hours_enabled'] = request.quiet_hours_enabled
        if request.quiet_hours_start is not None:
            update_data['quiet_hours_start'] = request.quiet_hours_start
        if request.quiet_hours_end is not None:
            update_data['quiet_hours_end'] = request.quiet_hours_end
        if request.min_priority is not None:
            update_data['min_priority'] = request.min_priority
        if request.notify_types is not None:
            update_data['notify_types'] = request.notify_types

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No settings provided to update"
            )

        # Upsert settings
        update_data['user_id'] = current_user['id']
        supabase.table('user_notification_settings') \
            .upsert(update_data, on_conflict='user_id') \
            .execute()

        return SuccessResponse(
            success=True,
            message="Notification settings updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update notification settings: {str(e)}"
        )


@router.get("/devices")
async def list_devices(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """
    List user's registered devices

    Args:
        current_user: Current authenticated user
        supabase: Supabase client

    Returns:
        List of devices
    """
    try:
        response = supabase.table('user_devices') \
            .select('*') \
            .eq('user_id', current_user['id']) \
            .eq('is_active', True) \
            .order('last_active_at', desc=True) \
            .execute()

        return {
            "success": True,
            "devices": response.data or []
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch devices: {str(e)}"
        )
