from fastapi import FastAPI, HTTPException
from typing import List
from app.models import WorkloadMetrics, OptimizationRecommendation
from app.optimizer import OptimizationEngine

app = FastAPI(
    title="Kubernetes Resource Optimization Agent",
    description="Analyzes Kubernetes workload resource usage and recommends optimized CPU and memory requests.",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/optimize", response_model=List[OptimizationRecommendation])
def optimize_resources(workloads: List[WorkloadMetrics]):
    if not workloads:
        raise HTTPException(status_code=400, detail="Input list cannot be empty")
    
    try:
        recommendations = OptimizationEngine.optimize_batch(workloads)
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during optimization: {str(e)}")
