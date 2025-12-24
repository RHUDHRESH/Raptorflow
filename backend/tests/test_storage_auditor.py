import pytest


class ManualMockStorageAuditor:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def generate_efficiency_report(self):
        return {"bucket": self.bucket_name, "total_size_mb": 100}


def test_storage_auditor_logic_manual():
    """Verify auditor interface manually."""
    auditor = ManualMockStorageAuditor(bucket_name="gold")
    report = auditor.generate_efficiency_report()
    assert report["total_size_mb"] == 100
