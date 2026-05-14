from pydantic import BaseModel, Field

class WorkloadMetrics(BaseModel):
    deployment: str
    cpu_request: float
    cpu_usage_avg: float
    memory_request: float
    memory_usage_avg: float

class OptimizationRecommendation(BaseModel):
    deployment: str
    recommended_cpu: float
    recommended_memory: float
    reason: str
