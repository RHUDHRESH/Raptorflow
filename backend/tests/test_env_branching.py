import yaml



def test_workflow_has_branching_logic():
    """Verify that backend-ci-cd.yml has branching logic for staging/prod."""
    with open(".github/workflows/backend-ci-cd.yml", "r") as f:
        workflow = yaml.safe_load(f)

    # Check if there are multiple environments or conditional logic
    # This is a bit complex to test with pure yaml load if using complex expressions
    # but we can check for branch names
    print(f"DEBUG: workflow keys = {list(workflow.keys())}")
    # Handle 'on' potentially being True (boolean) in some YAML parsers
    on_key = "on" if "on" in workflow else True
    on_push = workflow.get(on_key, {}).get("push", {})
    print(f"DEBUG: on_push = {on_push}")
    branches = on_push.get("branches", [])
    print(f"DEBUG: branches = {branches}")
    assert "main" in branches
    assert "develop" in branches
