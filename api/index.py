from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import json
import os

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyticsRequest(BaseModel):
    regions: list[str]
    threshold_ms: int


@app.get("/")
def home():
    return {"message": "Analytics API running"}


# Support BOTH routes:
# POST /
# POST /analytics
@app.post("/")
@app.post("/analytics")
def analytics(req: AnalyticsRequest):

    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "telemetry.json"
    )

    with open(file_path, "r") as f:
        data = json.load(f)

    results = {}

    for region in req.regions:

        region_data = [
            row for row in data
            if row["region"] == region
        ]

        if not region_data:
            continue

        latencies = [row["latency_ms"] for row in region_data]
        uptimes = [row["uptime_pct"] for row in region_data]

        results[region] = {
            "avg_latency": round(float(np.mean(latencies)), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(float(np.mean(uptimes)), 2),
            "breaches": sum(
                1
                for row in region_data
                if row["latency_ms"] > req.threshold_ms
            )
        }

    return results