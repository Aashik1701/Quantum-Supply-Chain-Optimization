import json
import uuid
import pytest


@pytest.mark.api
@pytest.mark.smoke
def test_enqueue_quantum_batch_job(client, monkeypatch, sample_warehouses, sample_customers):
    """Ensure /optimize enqueues batch job and returns job id without requiring Redis.
    We monkeypatch the service's enqueue method to avoid external dependencies.
    """
    from api import routes as api_routes

    fake_job_id = str(uuid.uuid4())

    def fake_enqueue(data, backend_policy='simulator', backend_name=None):
        return {"job_id": fake_job_id, "rq_id": "rq123", "status": "enqueued"}

    # Ensure optimization_service is initialized
    assert api_routes.optimization_service is not None

    # Patch only the enqueue method
    monkeypatch.setattr(api_routes.optimization_service, 'enqueue_quantum_job', fake_enqueue)

    payload = {
        "method": "quantum",
        "backendPolicy": "simulator",
        "jobMode": "batch",
        "warehouses": sample_warehouses,
        "customers": sample_customers,
    }

    resp = client.post('/api/v1/optimize', data=json.dumps(payload), content_type='application/json')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["success"] is True
    assert data["data"]["job"]["jobId"] == fake_job_id
    assert data["data"]["job"]["status"] == "enqueued"

