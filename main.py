"""App B: Diagnostic Receiver with CPU Load Testing

Simple FastAPI app that returns all request information received.
Now with Fibonacci calculation for CPU load testing and autoscaling.
"""

import asyncio
import random
import socket
import time
from fastapi import FastAPI, Request, Query
from typing import Dict, Any, Optional

app = FastAPI(title="VPC Test App B - Diagnostic Receiver")


def fibonacci(n: int) -> int:
    """Recursive Fibonacci - exponentially CPU intensive."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@app.get("/")
async def root():
    """Simple hello endpoint."""
    return {"app": "test-header-b", "message": "VPC diagnostic receiver"}


@app.get("/diagnostic")
async def diagnostic(
    request: Request,
    fib: Optional[int] = Query(None, description="Fibonacci number to calculate (CPU load)")
) -> Dict[str, Any]:
    """Return all request information received.

    This endpoint dumps:
    - Client IP (request.client.host)
    - All HTTP headers
    - Request method and path
    - Optional: CPU-intensive Fibonacci calculation

    Query params:
    - fib: If provided, calculate fibonacci(fib) - VERY CPU intensive!
           fib(35) ~= 1-2s, fib(38) ~= 5-8s, fib(40) ~= 30s, fib(42) ~= 2min
    """
    # Get this pod's hostname
    app_b_pod_name = socket.gethostname()

    # CPU load test or random delay
    if fib is not None:
        start_time = time.time()
        fib_result = fibonacci(fib)
        cpu_time = time.time() - start_time
        load_type = "fibonacci"
        load_value = fib
        load_result = fib_result
        load_duration = cpu_time
    else:
        # Legacy: random sleep delay
        app_b_delay = random.randint(1, 10)
        await asyncio.sleep(app_b_delay)
        load_type = "sleep"
        load_value = app_b_delay
        load_result = None
        load_duration = app_b_delay

    # Get client IP
    client_ip = request.client.host if request.client else "unknown"

    # Extract all headers
    all_headers = dict(request.headers)

    # Extract specific headers of interest
    specific_headers = {
        "x-forwarded-for": request.headers.get("x-forwarded-for"),
        "x-real-ip": request.headers.get("x-real-ip"),
        "do-connecting-ip": request.headers.get("do-connecting-ip"),
        "user-agent": request.headers.get("user-agent"),
        "host": request.headers.get("host"),
    }

    return {
        "app": "test-header-b",
        "app_b_pod_name": app_b_pod_name,
        "load_test": {
            "type": load_type,
            "input": load_value,
            "result": load_result,
            "duration_seconds": round(load_duration, 2)
        },
        "client_ip": client_ip,
        "specific_headers": specific_headers,
        "all_headers": all_headers,
        "method": request.method,
        "path": str(request.url.path),
        "full_url": str(request.url),
    }


@app.get("/health")
async def health():
    """Health check endpoint for Digital Ocean."""
    return {"status": "healthy"}
