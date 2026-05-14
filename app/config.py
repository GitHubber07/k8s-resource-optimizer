import os

class Config:
    # Multiplier for CPU recommendations (e.g., 1.2 = 20% safety buffer)
    CPU_SAFETY_MARGIN = float(os.getenv("CPU_SAFETY_MARGIN", "1.20"))
    
    # Multiplier for Memory recommendations (e.g., 1.25 = 25% safety buffer for OOM protection)
    MEMORY_SAFETY_MARGIN = float(os.getenv("MEMORY_SAFETY_MARGIN", "1.25"))
    
    # Minimum CPU to recommend to avoid starvation (millicores)
    MIN_CPU_MILLICORES = float(os.getenv("MIN_CPU_MILLICORES", "50.0"))
    
    # Minimum Memory to recommend to avoid OOM loop on startup (MiB)
    MIN_MEMORY_MIB = float(os.getenv("MIN_MEMORY_MIB", "64.0"))
    
    # Maximum allowed reduction in one step (e.g., 0.5 = at most 50% reduction at a time)
    MAX_DOWNSIZE_RATIO = float(os.getenv("MAX_DOWNSIZE_RATIO", "0.5"))

config = Config()
