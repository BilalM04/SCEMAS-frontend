import streamlit as st
from typing import List
import time
import uuid
import random

from utils.Request import request

from models.LogInformation import LogInformation
from models.SystemHealth import SystemHealth

base_url = st.secrets["BACKEND_BASE_URL"]

USE_MOCKS = st.secrets["OPERATIONAL_MOCKS"].lower() == "true"

# ----------------------
# Stable randomness (per session)
# ----------------------
if "seed" not in st.session_state:
    st.session_state.seed = random.randint(0, 100000)

random.seed(st.session_state.seed)

# ----------------------
# Mock Generators
# ----------------------

LOG_MESSAGES = [
    "User logged in",
    "Alert rule created",
    "Alert dismissed",
    "System configuration updated",
    "Subscription added",
    "Subscription removed"
]


def _mock_log() -> LogInformation:
    return LogInformation(
        log_id=str(uuid.uuid4()),
        user_id=f"user-{random.randint(1,10)}",
        log_message=random.choice(LOG_MESSAGES),
        time=int(time.time()) - random.randint(0, 10000),
        email=f"user{random.randint(1,10)}@example.com"
    )


def _mock_system_health() -> SystemHealth:
    return SystemHealth(
        up_time=round(random.uniform(1000, 100000), 2),
        memory_usage=round(random.uniform(10.0, 95.0), 2),
        disk_space=round(random.uniform(5.0, 90.0), 2),
        cpu_usage=round(random.uniform(1.0, 100.0), 2)
    )


# ----------------------
# Helpers (parsers)
# ----------------------

def _parse_log(data: dict) -> LogInformation:
    return LogInformation(
        log_id=data["log_id"],
        user_id=data["user_id"],
        log_message=data["log_message"],
        time=data["time"],
        email=data["email"]
    )


def _parse_system_health(data: dict) -> SystemHealth:
    return SystemHealth(
        up_time=data["up_time"],
        memory_usage=data["memory_usage"],
        disk_space=data["disk_space"],
        cpu_usage=data["cpu_usage"]
    )


def _unwrap(response):
    if not response["success"]:
        raise Exception(response["error"])
    return response["data"]


# ----------------------
# Logs
# ----------------------

def get_logs() -> List[LogInformation]:
    if USE_MOCKS:
        return [_mock_log() for _ in range(20)]
    else:
        res = request("GET", f"{base_url}/operations/logs")
        return [_parse_log(log) for log in _unwrap(res)]


# ----------------------
# System Health
# ----------------------

def get_system_health() -> SystemHealth:
    if USE_MOCKS:
        return _mock_system_health()
    else:
        res = request("GET", f"{base_url}/operations/health")
        return _parse_system_health(_unwrap(res))