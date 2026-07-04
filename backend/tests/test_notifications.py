import pytest
from app.models.notification import Notification
from app.core.notifications import NotificationType
from tests.helpers import create_user

def create_test_notification(db, recipient_id: int, title: str = "Test", is_read: bool = False):
    notif = Notification(
        recipient_id=recipient_id,
        type=NotificationType.SYSTEM,
        title=title,
        message="Test message",
        is_read=is_read
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif

def test_list_notifications(client, db):
    user = create_user(client, email="notif1@example.com")
    
    # Create 3 notifications for this user
    create_test_notification(db, user["id"], title="N1")
    create_test_notification(db, user["id"], title="N2")
    create_test_notification(db, user["id"], title="N3")
    
    response = client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer testuser_{user['id']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["notifications"]) == 3
    assert data["total_unread"] == 3
    
    # Check descending order
    assert data["notifications"][0]["title"] == "N3"
    assert data["notifications"][2]["title"] == "N1"

def test_notification_pagination(client, db):
    user = create_user(client, email="notif_page@example.com")
    
    for i in range(5):
        create_test_notification(db, user["id"], title=f"Notif {i}")
        
    response = client.get(
        "/api/v1/notifications?page=1&page_size=2",
        headers={"Authorization": f"Bearer testuser_{user['id']}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["notifications"]) == 2
    assert data["total_unread"] == 5
    assert data["page"] == 1
    assert data["page_size"] == 2

def test_unread_count(client, db):
    user = create_user(client, email="notif2@example.com")
    
    create_test_notification(db, user["id"], is_read=False)
    create_test_notification(db, user["id"], is_read=True)
    
    response = client.get(
        "/api/v1/notifications/unread-count",
        headers={"Authorization": f"Bearer testuser_{user['id']}"}
    )
    assert response.status_code == 200
    assert response.json()["unread_count"] == 1

def test_mark_as_read(client, db):
    user = create_user(client, email="notif3@example.com")
    notif = create_test_notification(db, user["id"])
    
    response = client.patch(
        f"/api/v1/notifications/{notif.id}/read",
        headers={"Authorization": f"Bearer testuser_{user['id']}"}
    )
    assert response.status_code == 200
    assert response.json()["is_read"] == True
    assert response.json()["read_at"] is not None

def test_mark_all_as_read(client, db):
    user = create_user(client, email="notif4@example.com")
    
    create_test_notification(db, user["id"])
    create_test_notification(db, user["id"])
    
    response = client.patch(
        "/api/v1/notifications/read-all",
        headers={"Authorization": f"Bearer testuser_{user['id']}"}
    )
    assert response.status_code == 200
    assert response.json()["marked_read_count"] == 2
    
    # Verify via unread count
    count_resp = client.get(
        "/api/v1/notifications/unread-count",
        headers={"Authorization": f"Bearer testuser_{user['id']}"}
    )
    assert count_resp.json()["unread_count"] == 0

def test_data_isolation(client, db):
    user_a = create_user(client, email="a@example.com")
    user_b = create_user(client, email="b@example.com")
    
    create_test_notification(db, user_a["id"], title="A's Notif")
    create_test_notification(db, user_b["id"], title="B's Notif")
    
    # A should only see A's
    resp_a = client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer testuser_{user_a['id']}"}
    )
    assert len(resp_a.json()["notifications"]) == 1
    assert resp_a.json()["notifications"][0]["title"] == "A's Notif"
    
    # A cannot mark B's as read
    b_notif = db.query(Notification).filter(Notification.recipient_id == user_b["id"]).first()
    resp_hack = client.patch(
        f"/api/v1/notifications/{b_notif.id}/read",
        headers={"Authorization": f"Bearer testuser_{user_a['id']}"}
    )
    assert resp_hack.status_code == 404
