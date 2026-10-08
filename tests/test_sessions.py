from datetime import datetime, timedelta, timezone

import lifecycle
from models import WorkSession


def create_session(client):
    response = client.post(
        "/sessions/",
        json={
            "title": "Test session",
            "goal": "Verify backend rules",
            "duration": 25,
        },
    )

    assert response.status_code == 201
    assert response.json()["status"] == "scheduled"
    return response.json()["id"]


def test_create_and_complete(client):
    session_id = create_session(client)

    response = client.patch(f"/sessions/{session_id}/start")
    assert response.status_code == 200
    assert response.json()["status"] == "active"

    response = client.patch(f"/sessions/{session_id}/complete")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["end_time"] is not None

    response = client.patch(f"/sessions/{session_id}/complete")
    assert response.status_code == 409

    response = client.get("/sessions/history")
    assert response.status_code == 200

    history = response.json()
    assert history["completed_sessions"] == 1
    assert history["finished_sessions"] == 1
    assert history["completion_ratio"] == 1.0


def test_invalid_status_changes(client):
    session_id = create_session(client)

    response = client.patch(
        f"/sessions/{session_id}/pause",
        json={"reason": "A break"},
    )
    assert response.status_code == 409

    assert client.patch(
        f"/sessions/{session_id}/resume"
    ).status_code == 409

    assert client.patch(
        f"/sessions/{session_id}/complete"
    ).status_code == 409

    assert client.patch(
        f"/sessions/{session_id}/start"
    ).status_code == 200

    assert client.patch(
        f"/sessions/{session_id}/start"
    ).status_code == 409


def test_fourth_pause_interrupts_session(client):
    session_id = create_session(client)
    assert client.patch(
        f"/sessions/{session_id}/start"
    ).status_code == 200

    for pause_number in range(1, 5):
        response = client.patch(
            f"/sessions/{session_id}/pause",
            json={"reason": f"Break {pause_number}"},
        )

        assert response.status_code == 200

        if pause_number < 4:
            assert response.json()["status"] == "paused"

            # Repeated pause must not add another interruption.
            assert client.patch(
                f"/sessions/{session_id}/pause",
                json={"reason": "Duplicate pause"},
            ).status_code == 409

            assert client.patch(
                f"/sessions/{session_id}/resume"
            ).status_code == 200
        else:
            assert response.json()["status"] == "interrupted"
            assert response.json()["end_time"] is not None

    assert client.patch(
        f"/sessions/{session_id}/resume"
    ).status_code == 409

    response = client.get("/sessions/history")
    assert response.status_code == 200

    session = response.json()["sessions"][0]
    assert session["pause_count"] == 4
    assert len(session["interruptions"]) == 4


def test_validation_and_missing_session(client):
    response = client.post(
        "/sessions/",
        json={"title": "Invalid duration", "duration": 0},
    )
    assert response.status_code == 422

    response = client.post(
        "/sessions/",
        json={"title": "   ", "duration": 25},
    )
    assert response.status_code == 422

    assert client.patch(
        "/sessions/99999/start"
    ).status_code == 404

    response = client.get("/sessions/history")
    assert response.status_code == 200
    assert response.json()["total_sessions"] == 0
    
def set_elapsed_time(session_id, seconds):
    with lifecycle.SessionLocal() as db:
        work_session = db.get(WorkSession, session_id)
        work_session.start_time = (
            datetime.now(timezone.utc).replace(tzinfo=None)
            - timedelta(seconds=seconds)
        )
        db.commit()


def test_late_completion_is_overdue(client):
    session_id = create_session(client)

    assert client.patch(
        f"/sessions/{session_id}/start"
    ).status_code == 200

    # A 25-minute session allows 1650 seconds.
    set_elapsed_time(session_id, 1700)

    response = client.patch(
        f"/sessions/{session_id}/complete"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "overdue"
    assert response.json()["end_time"] is not None

    history = client.get("/sessions/history").json()
    assert history["finished_sessions"] == 1
    assert history["completed_sessions"] == 0
    assert history["completion_ratio"] == 0.0


def test_expired_pause_cannot_resume(client):
    session_id = create_session(client)

    assert client.patch(
        f"/sessions/{session_id}/start"
    ).status_code == 200

    assert client.patch(
        f"/sessions/{session_id}/pause",
        json={"reason": "Expired break"},
    ).status_code == 200

    set_elapsed_time(session_id, 1700)

    response = client.patch(
        f"/sessions/{session_id}/resume"
    )

    assert response.status_code == 409

    history = client.get("/sessions/history").json()
    session = history["sessions"][0]

    assert session["status"] == "abandoned"
    assert session["end_time"] is not None
    assert session["pause_count"] == 1


def test_automatic_abandonment_preserves_active_sessions(client):
    paused_id = create_session(client)
    active_id = create_session(client)

    for session_id in (paused_id, active_id):
        assert client.patch(
            f"/sessions/{session_id}/start"
        ).status_code == 200

    assert client.patch(
        f"/sessions/{paused_id}/pause",
        json={"reason": "Left paused"},
    ).status_code == 200

    set_elapsed_time(paused_id, 1700)
    set_elapsed_time(active_id, 1700)

    lifecycle.abandon_expired_sessions()

    history = client.get("/sessions/history").json()
    sessions = {
        session["id"]: session
        for session in history["sessions"]
    }

    assert sessions[paused_id]["status"] == "abandoned"
    assert sessions[paused_id]["end_time"] is not None
    assert sessions[active_id]["status"] == "active"
    assert sessions[active_id]["end_time"] is None    