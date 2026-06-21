"""Integration tests for Evaluation endpoints."""


class TestEvaluationMetrics:
    async def test_metrics_default(self, auth_client):
        res = await auth_client.get("/api/v1/evaluation/metrics")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["overall"]["precision"] == 0
        assert data["overall"]["recall"] == 0
        assert data["overall"]["f1_score"] == 0


class TestRunEvaluation:
    async def test_run_empty(self, auth_client):
        res = await auth_client.post("/api/v1/evaluation/run")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["true_positives"] == 0
        assert data["false_positives"] == 0
        assert data["false_negatives"] == 0
        assert data["ground_truth_source"] == "self-comparison"


class TestUploadLabels:
    async def test_upload_labels_csv(self, auth_client, sample_vendor):
        csv_content = f"vendor_id,anomaly_type,severity\n{sample_vendor.vendor_id},HIGH_RISK_SCORE,HIGH\n{sample_vendor.vendor_id},EXPIRED_CERTIFICATION,MEDIUM\n"
        res = await auth_client.post(
            "/api/v1/evaluation/upload-labels",
            files={"file": ("labels.csv", csv_content, "text/csv")},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["loaded"] == 2

    async def test_upload_invalid_file(self, auth_client):
        res = await auth_client.post(
            "/api/v1/evaluation/upload-labels",
            files={"file": ("data.txt", "not csv", "text/plain")},
        )
        assert res.status_code == 422

    async def test_upload_nonexistent_vendor(self, auth_client):
        csv_content = "vendor_id,anomaly_type,severity\n00000000-0000-0000-0000-000000000000,HIGH_RISK_SCORE,HIGH\n"
        res = await auth_client.post(
            "/api/v1/evaluation/upload-labels",
            files={"file": ("labels.csv", csv_content, "text/csv")},
        )
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["loaded"] == 0
        assert len(data["errors"]) > 0
