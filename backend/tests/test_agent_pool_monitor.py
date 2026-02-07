import pytest

from agents.shared.pool_monitor import AgentPoolMonitor


def test_agent_pool_monitor_registration():
    """Test registering and unregistering agent threads."""
    monitor = AgentPoolMonitor()

    # Initial state
    assert monitor.get_active_thread_count() == 0

    # Register
    monitor.register_thread("thread_1", "researcher")
    assert monitor.get_active_thread_count() == 1
    assert "thread_1" in monitor.get_active_threads()

    # Unregister
    monitor.unregister_thread("thread_1")
    assert monitor.get_active_thread_count() == 0


def test_agent_pool_monitor_singleton():
    """Test that AgentPoolMonitor acts as a singleton (shared state)."""
    monitor1 = AgentPoolMonitor()
    monitor2 = AgentPoolMonitor()

    monitor1.register_thread("thread_shared", "strategist")
    assert monitor2.get_active_thread_count() == 1
    assert "thread_shared" in monitor2.get_active_threads()

    # Cleanup
    monitor1.unregister_thread("thread_shared")
