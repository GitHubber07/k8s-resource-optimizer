import pytest
from app.models import WorkloadMetrics
from app.optimizer import OptimizationEngine
from app.config import config

def test_optimization_downsize():
    # Setup
    metrics = WorkloadMetrics(
        deployment="api-service",
        cpu_request=1000.0,
        cpu_usage_avg=180.0,
        memory_request=2048.0,
        memory_usage_avg=700.0
    )

    # Execute
    recommendation = OptimizationEngine.calculate_recommendation(metrics)

    # Verify
    # Max downsize is 50%, so CPU shouldn't drop below 500, even if usage is 180
    assert recommendation.recommended_cpu == 500.0
    assert "CPU downsize capped" in recommendation.reason

    # Memory downsize capped at 50% of 2048 = 1024
    assert recommendation.recommended_memory == 1024.0
    assert "Memory downsize capped" in recommendation.reason

def test_optimization_upsize_due_to_high_usage():
    metrics = WorkloadMetrics(
        deployment="worker-service",
        cpu_request=500.0,
        cpu_usage_avg=600.0,  # Higher than request
        memory_request=1024.0,
        memory_usage_avg=900.0 # High usage, close to request
    )

    recommendation = OptimizationEngine.calculate_recommendation(metrics)

    # CPU recommended should be usage * margin (600 * 1.2 = 720)
    assert recommendation.recommended_cpu == 720.0
    assert "CPU request is too low" in recommendation.reason

    # Memory recommended should be usage * margin (900 * 1.25 = 1125)
    assert recommendation.recommended_memory == 1125.0
    assert "Memory request is too low" in recommendation.reason

def test_optimization_minimum_thresholds():
    metrics = WorkloadMetrics(
        deployment="idle-service",
        cpu_request=100.0,
        cpu_usage_avg=5.0,
        memory_request=128.0,
        memory_usage_avg=10.0
    )

    recommendation = OptimizationEngine.calculate_recommendation(metrics)

    # Should hit minimums (50 CPU, 64 Memory)
    assert recommendation.recommended_cpu == config.MIN_CPU_MILLICORES
    assert recommendation.recommended_memory == config.MIN_MEMORY_MIB
