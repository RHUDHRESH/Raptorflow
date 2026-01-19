import pytest
from backend.utils.ucid import UCIDGenerator
from backend.services.bcm_service import BCMService
from backend.schemas.business_context import BusinessContext

def test_ucid_generation_and_validation():
    ucid = UCIDGenerator.generate()
    assert UCIDGenerator.validate(ucid) is True
    assert ucid.startswith("RF-")
    
    assert UCIDGenerator.validate("INVALID-ID") is False

def test_bcm_calculation():
    context = BusinessContext(
        ucid="RF-2026-TEST",
        identity={"name": "TestCorp", "core_promise": "We test things"},
        audience={"primary_segment": "Testers"},
        positioning={"category": "Testing Software"}
    )
    
    bcm = BCMService.calculate_bcm(context)
    
    assert bcm["ucid"] == "RF-2026-TEST"
    assert len(bcm["nodes"]) == 3
    assert len(bcm["edges"]) == 2
    
    node_ids = [n["id"] for n in bcm["nodes"]]
    assert "identity" in node_ids
    assert "audience" in node_ids
    assert "positioning" in node_ids
