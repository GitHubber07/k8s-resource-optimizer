from app.models import WorkloadMetrics, OptimizationRecommendation
from app.config import config

class OptimizationEngine:
    @staticmethod
    def calculate_recommendation(metrics: WorkloadMetrics) -> OptimizationRecommendation:
        reasons = []
        
        # Calculate CPU Recommendation
        target_cpu = metrics.cpu_usage_avg * config.CPU_SAFETY_MARGIN
        recommended_cpu = max(target_cpu, config.MIN_CPU_MILLICORES)
        
        # Apply max downsize constraint
        min_allowed_cpu = metrics.cpu_request * (1.0 - config.MAX_DOWNSIZE_RATIO)
        if recommended_cpu < min_allowed_cpu:
            recommended_cpu = min_allowed_cpu
            reasons.append(f"CPU downsize capped at {config.MAX_DOWNSIZE_RATIO*100}% of request")
        elif target_cpu < metrics.cpu_request:
            reasons.append("CPU average usage significantly below requested resources")
        elif target_cpu > metrics.cpu_request:
            reasons.append("CPU request is too low, risk of throttling")

        # Calculate Memory Recommendation
        target_memory = metrics.memory_usage_avg * config.MEMORY_SAFETY_MARGIN
        recommended_memory = max(target_memory, config.MIN_MEMORY_MIB)
        
        # Apply max downsize constraint
        min_allowed_memory = metrics.memory_request * (1.0 - config.MAX_DOWNSIZE_RATIO)
        if recommended_memory < min_allowed_memory:
            recommended_memory = min_allowed_memory
            reasons.append(f"Memory downsize capped at {config.MAX_DOWNSIZE_RATIO*100}% of request")
        elif target_memory < metrics.memory_request:
            reasons.append("Memory average usage significantly below requested resources")
        elif target_memory > metrics.memory_request:
            reasons.append("Memory request is too low, high risk of OOMKilled")

        # Combine reasons or provide a default
        final_reason = "; ".join(reasons) if reasons else "Resources are appropriately provisioned"

        return OptimizationRecommendation(
            deployment=metrics.deployment,
            recommended_cpu=round(recommended_cpu),
            recommended_memory=round(recommended_memory),
            reason=final_reason
        )

    @staticmethod
    def optimize_batch(workloads: list[WorkloadMetrics]) -> list[OptimizationRecommendation]:
        return [OptimizationEngine.calculate_recommendation(w) for w in workloads]
