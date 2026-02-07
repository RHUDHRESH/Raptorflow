from datetime import datetime
from uuid import uuid4

import pytest

from models.blackbox import BlackboxLearning, BlackboxOutcome, BlackboxTelemetry


def test_blackbox_telemetry_schema():
    data = {
        "tenant_id": uuid4(),
        "move_id": uuid4(),
        "agent_id": "test-agent-v1",
        "trace": {"steps": ["thought", "action"]},
        "tokens": 150,
        "latency": 0.45,
        "timestamp": datetime.now(),
    }
    model = BlackboxTelemetry(**data)
    assert model.agent_id == "test-agent-v1"
    assert model.tokens == 150


def test_blackbox_outcome_schema():
    if BlackboxOutcome is None:
        pytest.fail("BlackboxOutcome model not imported")

    data = {
        "tenant_id": uuid4(),
        "source": "conversion_pixel",
        "value": 1500.0,
        "confidence": 0.95,
        "timestamp": datetime.now(),
    }
    model = BlackboxOutcome(**data)
    assert model.source == "conversion_pixel"
    assert model.value == 1500.0


def test_blackbox_learning_schema():
    if BlackboxLearning is None:
        pytest.fail("BlackboxLearning model not imported")

    data = {
        "content": "Users prefer short-form content on platform X",
        "embedding": [0.1, 0.2, 0.3],
        "source_ids": [uuid4(), uuid4()],
        "learning_type": "tactical",
        "timestamp": datetime.now(),
    }
    model = BlackboxLearning(**data)
    assert model.learning_type == "tactical"
    assert len(model.embedding) == 3
