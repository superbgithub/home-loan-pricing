from __future__ import annotations

import hashlib
import json
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Generator, Optional
from uuid import UUID, uuid4


def _default(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return str(obj)
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serialisable")


def hash_inputs(data: Any) -> str:
    serialised = json.dumps(data, default=_default, sort_keys=True)
    return hashlib.sha256(serialised.encode()).hexdigest()


@contextmanager
def audit_context(
    loan_type: str,
    scenario_count: int,
    inputs: Any,
    request_id: Optional[UUID] = None,
) -> Generator[Dict[str, Any], None, None]:
    """Context manager that emits one JSON audit line to stdout on exit."""
    rid = request_id or uuid4()
    started = time.monotonic()
    record: Dict[str, Any] = {
        "request_id": str(rid),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "loan_type": loan_type,
        "scenario_count": scenario_count,
        "inputs_hash": hash_inputs(inputs),
        "outputs_summary": {},
        "duration_ms": 0,
        "error": None,
    }
    try:
        yield record
    except Exception as exc:
        record["error"] = str(exc)
        raise
    finally:
        record["duration_ms"] = round((time.monotonic() - started) * 1000)
        print(json.dumps(record, default=_default), file=sys.stdout, flush=True)
