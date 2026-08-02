import os
from typing import Optional

def get_prefixed_env(key: str) -> Optional[str]:
    prefix = os.environ.get("POSTPIPE_VAR_PREFIX", "")
    if prefix:
        val = os.environ.get(f"{prefix}_{key}")
        if val:
            return val
    return os.environ.get(key)
