"""App B: Diagnostic Receiver

Simple FastAPI app that returns all request information received.
Used to test what headers and IPs appear for external vs internal VPC requests.
"""

import asyncio
import random
import socket
from fastapi import FastAPI, Request
from typing import Dict, Any

app = FastAPI(title="VPC Test App B - Diagnostic Receiver")


@app.get("/")
async def root():
    """Simple hello endpoint."""
    return {"app": "test-header-b", "message": "VPC diagnostic receiver"}


@app.get("/diagnostic")
async def diagnostic(request: Request) -> Dict[str, Any]:
    """Return all request information received.

    This endpoint dumps:
    - Client IP (request.client.host)
    - All HTTP headers
    - Request method and path

    Used to determine what App B sees when called externally vs internally.
    """
    # Get this pod's hostname
    app_b_pod_name = socket.gethostname()

    # Simulate random load (1-3 second delay)
    app_b_delay = random.randint(1, 3)
    await asyncio.sleep(app_b_delay)

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
        "app_b_delay_seconds": app_b_delay,
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
