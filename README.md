# Kubernetes Resource Optimization Agent

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue.svg" alt="Python Version" />
  <img src="https://img.shields.io/badge/FastAPI-0.111+-green.svg" alt="FastAPI Version" />
  <img src="https://img.shields.io/badge/Docker-Supported-blue.svg" alt="Docker Supported" />
  <img src="https://img.shields.io/badge/Kubernetes-Native-purple.svg" alt="Kubernetes Native" />
</div>

## 🚀 Project Overview

In many Kubernetes environments, workloads are often overprovisioned to prevent performance degradation, leading to massive infrastructure cost bloat and inefficient cluster utilization. 

This project is a **Kubernetes Resource Optimization Agent**, a lightweight service built in Python (FastAPI) that analyzes raw workload metrics and intelligently recommends safer, more optimized CPU and memory requests. 

It was developed with a focus on **Systems Thinking**—moving beyond static ratios to account for real-world reliability factors such as:
- **Safety Buffers** for traffic spikes
- **OOM (Out Of Memory) Risks**
- **Aggressive Downsize Prevention**
- **CPU Starvation Protection**
## Features

- **API-Based Implementation**: Exposes a `/optimize` endpoint to receive batch workload metrics and return recommendations.
- **Safety Buffers**: Adds configurable safety margins (default 20% for CPU, 25% for Memory) above average usage to handle spikes and prevent OOM issues.
- **Downsize Capping**: Prevents aggressive downsizing by limiting the maximum reduction in a single step (default max 50% reduction).
- **Minimum Thresholds**: Enforces minimum resource limits (e.g., 50m CPU, 64Mi Memory) to avoid CPU starvation and container startup crashes.
- **Dockerized**: Includes a secure, multi-stage `Dockerfile` running as a non-root user.
- **Kubernetes-Native**: Includes sample `Deployment` and `Service` manifests with resource limits, liveness/readiness probes, and security contexts.
- **Unit Tested**: Includes test suite for core optimization logic and API routing.

## Setup Instructions

### Local Development

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```

3. Run Tests:
   ```bash
   pytest
   ```

### Docker

1. Build the image:
   ```bash
   docker build -t k8s-resource-optimizer .
   ```

2. Run the container:
   ```bash
   docker run -p 8080:8080 k8s-resource-optimizer
   ```

## Sample Input/Output

You can test the API using `curl` or Postman.

**Request:**
```bash
curl -X POST http://localhost:8080/optimize \
     -H "Content-Type: application/json" \
     -d '[
          {
            "deployment": "api-service",
            "cpu_request": 1000,
            "cpu_usage_avg": 180,
            "memory_request": 2048,
            "memory_usage_avg": 700
          },
          {
            "deployment": "worker-service",
            "cpu_request": 500,
            "cpu_usage_avg": 450,
            "memory_request": 1024,
            "memory_usage_avg": 900
          }
        ]'
```

**Output:**
```json
[
  {
    "deployment": "api-service",
    "recommended_cpu": 500,
    "recommended_memory": 1024,
    "reason": "CPU downsize capped at 50.0% of request; Memory downsize capped at 50.0% of request"
  },
  {
    "deployment": "worker-service",
    "recommended_cpu": 540,
    "recommended_memory": 1125,
    "reason": "CPU request is too low, risk of throttling; Memory request is too low, high risk of OOMKilled"
  }
]
```

## Assumptions Made

1. **Input Format**: Assumes metrics represent "average" usage over a meaningful time window (e.g., 7-14 days). Peak/percentile usage isn't provided in the input, so safety margins act as the buffer for spikes.
2. **Stateless Service**: The optimizer itself is stateless. It does not store historical metrics or state, making it highly scalable and easy to deploy across multiple replicas.
3. **Downsize Capping over Immediate Savings**: It is assumed that safety is prioritized over immediate cost savings. An aggressive 90% downsize in one step could be catastrophic. Capping it at 50% allows for iterative, safe resizing.
4. **Units**: CPU is in millicores (m), Memory is in MiB.

## Discussion Questions

### How would you extend this system to work in real Kubernetes clusters at scale?

To take this from a simple API to a production-grade optimization platform at scale:

1. **Metrics Collection (Prometheus Integration)**:
   - Instead of accepting JSON payloads manually, the service should query an existing observability stack (e.g., Prometheus, Thanos, VictoriaMetrics).
   - Use PromQL to fetch `p95` or `p99` percentiles instead of just averages, providing a much safer baseline for recommendations.

2. **Kubernetes APIs & Automation**:
   - Integrate with the Kubernetes API (`client-go` or `kubernetes-client/python`) to directly watch Deployments/StatefulSets and patch their resource definitions automatically (if running in "Auto-Apply" mode).
   - Implement a custom `MutatingWebhookConfiguration` to inject optimized resource requests dynamically upon pod creation, or use VPA (Vertical Pod Autoscaler) CRDs to drive recommendations.

3. **Scalability Considerations**:
   - For massive multi-cluster environments, use an event-driven architecture (e.g., Kafka or RabbitMQ). Agents deployed in each cluster publish metric summaries to a central processing engine.
   - Cache API responses and state using Redis to prevent overwhelming the Kubernetes API Server with frequent reads.

4. **Autoscaling Interactions**:
   - The engine must be aware of Horizontal Pod Autoscalers (HPA). If an HPA scales based on CPU utilization (e.g., target 70%), reducing the CPU request will instantly alter the scaling behavior, potentially causing thrashing. The optimizer should calculate recommendations that align with HPA targets.

5. **Reliability Challenges**:
   - Rollbacks: If an automated downsize causes performance degradation, the system needs an immediate, automated rollback mechanism.
   - Blackouts: Support for "maintenance windows" or "do not touch" annotations on specific critical workloads.
