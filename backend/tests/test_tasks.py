from datetime import datetime, timedelta, timezone

API = "/api/v1/tasks"


def _iso(days: int = 1) -> str:
    """ISO 8601 timestamp `days` from now, in UTC."""
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def _create(client, **overrides):
    """Helper: POST a task with sensible defaults."""
    payload = {"title": "Default task", "dueDate": _iso(), **overrides}
    return client.post(API, json=payload)


# --- health -----------------------------------------------------------------


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# --- create -----------------------------------------------------------------


def test_create_task_minimal(client):
    r = _create(client, title="Review case file")
    assert r.status_code == 201
    body = r.json()
    assert body["id"] > 0
    assert body["title"] == "Review case file"
    assert body["description"] is None
    assert body["status"] == "TODO"
    assert "createdAt" in body and "updatedAt" in body
    assert "dueDate" in body


def test_create_task_full(client):
    r = _create(
        client,
        title="Prepare bundle",
        description="Collate evidence for hearing",
        status="IN_PROGRESS",
        dueDate=_iso(3),
    )
    assert r.status_code == 201
    body = r.json()
    assert body["description"] == "Collate evidence for hearing"
    assert body["status"] == "IN_PROGRESS"


def test_create_task_blank_title_rejected(client):
    r = _create(client, title="   ")
    assert r.status_code == 422


def test_create_task_missing_due_date_rejected(client):
    r = client.post(API, json={"title": "No due date"})
    assert r.status_code == 422


def test_create_task_invalid_status_rejected(client):
    r = _create(client, status="NOT_A_STATUS")
    assert r.status_code == 422


# --- list -------------------------------------------------------------------


def test_list_tasks_ordered_by_due_date(client):
    for days in (5, 1, 3):
        _create(client, title=f"task-{days}", dueDate=_iso(days))
    r = client.get(API)
    assert r.status_code == 200
    titles = [t["title"] for t in r.json()]
    assert titles == ["task-1", "task-3", "task-5"]


def test_list_tasks_empty(client):
    r = client.get(API)
    assert r.status_code == 200
    assert r.json() == []


# --- retrieve ---------------------------------------------------------------


def test_get_task_by_id(client):
    created = _create(client, title="Find me").json()
    r = client.get(f"{API}/{created['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "Find me"


def test_get_task_not_found(client):
    r = client.get(f"{API}/9999")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


# --- update status ----------------------------------------------------------


def test_update_task_status(client):
    created = _create(client, title="Move me").json()
    r = client.patch(f"{API}/{created['id']}/status", json={"status": "IN_PROGRESS"})
    assert r.status_code == 200
    assert r.json()["status"] == "IN_PROGRESS"

    r = client.patch(f"{API}/{created['id']}/status", json={"status": "DONE"})
    assert r.json()["status"] == "DONE"


def test_update_status_invalid_value(client):
    created = _create(client).json()
    r = client.patch(f"{API}/{created['id']}/status", json={"status": "NOPE"})
    assert r.status_code == 422


def test_update_status_task_not_found(client):
    r = client.patch(f"{API}/9999/status", json={"status": "DONE"})
    assert r.status_code == 404


# --- delete -----------------------------------------------------------------


def test_delete_task(client):
    created = _create(client, title="Delete me").json()
    r = client.delete(f"{API}/{created['id']}")
    assert r.status_code == 204
    assert client.get(f"{API}/{created['id']}").status_code == 404


def test_delete_task_not_found(client):
    r = client.delete(f"{API}/9999")
    assert r.status_code == 404
