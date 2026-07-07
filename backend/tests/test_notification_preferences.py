import pytest
from unittest.mock import patch, MagicMock
from app.models.user import User
from app.models.notification_preference import NotificationPreference, NotificationChannel, NotificationType
from app.services.notification_preference_service import NotificationPreferenceService, DEFAULT_PREFERENCES_MATRIX

def test_default_preferences_created_on_registration(client, db):
    # Register a new user
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "pref_test@test.com", "full_name": "Pref Test", "password": "Password123!"}
    )
    assert response.status_code == 201

    user = db.query(User).filter_by(email="pref_test@test.com").first()
    assert user is not None

    # Check if preferences were generated
    prefs = db.query(NotificationPreference).filter_by(user_id=user.id).all()
    
    # We should have one pref per channel per notification type defined in the matrix
    expected_count = sum(len(channels) for channels in DEFAULT_PREFERENCES_MATRIX.values())
    assert len(prefs) == expected_count

    # Specifically check Ticket Assigned -> Email is True by default
    ticket_assigned_email = next((
        p for p in prefs 
        if p.notification_type == NotificationType.TICKET_ASSIGNED and p.channel == NotificationChannel.EMAIL
    ), None)
    
    assert ticket_assigned_email is not None
    assert ticket_assigned_email.enabled is True

def test_update_notification_preference(client, db):
    # Register
    reg_response = client.post(
        "/api/v1/auth/register",
        json={"email": "unique_verified@test.com", "full_name": "Verified", "password": "Password123!"}
    )
    assert reg_response.status_code == 201
    # Hack DB to verify directly for login tests
    from datetime import datetime, timezone
    user = db.query(User).filter_by(email="unique_verified@test.com").first()
    user.email_verified = True
    user.email_verified_at = datetime.now(timezone.utc)
    db.commit()

    # Get the preferences first via the new API endpoint
    db_prefs = db.query(NotificationPreference).filter_by(user_id=user.id).all()
    assert len(db_prefs) > 0, f"No prefs in DB for user {user.id}"

    # We don't even need to login since conftest mocks it with "Bearer testuser_X"
    headers = {"Authorization": f"Bearer testuser_{user.id}"}

    pref_response = client.get("/api/v1/notification-preferences/", headers=headers)
    assert pref_response.status_code == 200
    
    prefs = pref_response.json()
    assert len(prefs) > 0

    # Pick one to update
    pref_to_update = prefs[0]
    initial_enabled = pref_to_update["enabled"]
    
    # Toggle it
    update_response = client.patch(
        f"/api/v1/notification-preferences/{pref_to_update['id']}",
        headers=headers,
        json={"enabled": not initial_enabled}
    )
    assert update_response.status_code == 200
    assert update_response.json()["enabled"] == (not initial_enabled)
    
    # Verify in DB
    db.expire_all()
    updated_pref = db.query(NotificationPreference).filter_by(id=pref_to_update["id"]).first()
    assert updated_pref.enabled == (not initial_enabled)

def test_dispatcher_respects_preferences(db):
    from app.services.notification_delivery_dispatcher import NotificationDeliveryDispatcher
    from app.models.notification import Notification
    from app.core.notification_templates import NotificationContent
    
    mock_email_service = MagicMock()
    mock_pref_service = MagicMock()
    
    dispatcher = NotificationDeliveryDispatcher(
        email_service=mock_email_service,
        preference_service=mock_pref_service
    )
    
    notification = Notification(
        id=1,
        recipient_id=99,
        type=NotificationType.TICKET_ASSIGNED.value,
        title="Test",
        message="Test content",
        entity_id=1
    )
    content = NotificationContent(title="Test", message="Test")
    
    # Simulate email channel enabled
    mock_pref_service.is_channel_enabled.side_effect = lambda user_id, type_, channel: channel == NotificationChannel.EMAIL
    
    dispatcher.dispatch(notification, content)
    
    # In a full implementation, email_service.send() would be called.
    # We just ensure it doesn't crash and the preference service is consulted.
    mock_pref_service.is_channel_enabled.assert_any_call(99, NotificationType.TICKET_ASSIGNED, NotificationChannel.EMAIL)
    mock_pref_service.is_channel_enabled.assert_any_call(99, NotificationType.TICKET_ASSIGNED, NotificationChannel.BROWSER)

def test_dispatcher_skips_unknown_types(db):
    from app.services.notification_delivery_dispatcher import NotificationDeliveryDispatcher
    from app.models.notification import Notification
    from app.core.notification_templates import NotificationContent
    
    mock_email_service = MagicMock()
    mock_pref_service = MagicMock()
    
    dispatcher = NotificationDeliveryDispatcher(
        email_service=mock_email_service,
        preference_service=mock_pref_service
    )
    
    notification = Notification(
        id=1,
        recipient_id=99,
        type="UNKNOWN_TYPE_THAT_WAS_JUST_ADDED",
        title="Test",
        message="Test content",
        entity_id=1
    )
    content = NotificationContent(title="Test", message="Test")
    
    dispatcher.dispatch(notification, content)
    
    # Preference service shouldn't be queried because the type is unknown
    mock_pref_service.is_channel_enabled.assert_not_called()
