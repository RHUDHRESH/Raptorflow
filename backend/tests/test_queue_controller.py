from models.queue_controller import CapabilityProfile, QueueController, QueuedTask


def test_queue_controller_enforces_per_agent_concurrency():
    profile = CapabilityProfile(default_concurrency=1, per_agent_concurrency={"researcher": 2})
    controller = QueueController(capability_profile=profile)

    task_one = QueuedTask(task_id="t1", agent_type="researcher")
    task_two = QueuedTask(task_id="t2", agent_type="researcher")
    task_three = QueuedTask(task_id="t3", agent_type="researcher")

    assert controller.enqueue(task_one) is True
    assert controller.enqueue(task_two) is True
    assert controller.enqueue(task_three) is False
    assert len(controller.queue) == 1

    released = controller.complete("researcher")
    assert [task.task_id for task in released] == ["t3"]
    assert controller.inflight_by_agent["researcher"] == 2


def test_queue_controller_respects_default_limit():
    controller = QueueController()

    task_one = QueuedTask(task_id="t1", agent_type="strategist")
    task_two = QueuedTask(task_id="t2", agent_type="strategist")

    assert controller.enqueue(task_one) is True
    assert controller.enqueue(task_two) is False
