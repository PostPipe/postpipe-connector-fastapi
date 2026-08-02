import os
from .base import DatabaseAdapter

_adapter_cache = {}

def get_adapter(forced_type: str = None) -> DatabaseAdapter:
    db_type = (forced_type or os.environ.get("DB_TYPE") or "").lower()

    if not db_type:
        if os.environ.get("POSTGRES_URL") or os.environ.get("DATABASE_URL"):
            db_type = 'postgres'
        elif os.environ.get("MONGODB_URI"):
            db_type = 'mongodb'

    if db_type in _adapter_cache:
        return _adapter_cache[db_type]

    adapter = None
    if db_type == 'mongodb':
        from .mongodb import MongoAdapter
        adapter = MongoAdapter()
    elif db_type in ['postgres', 'postgresql']:
        from .postgres import PostgresAdapter
        adapter = PostgresAdapter()
    else:
        print(f"[Config] No valid DB_TYPE set (got '{db_type}').")
        # In a real app we might fallback to a MemoryAdapter.
        # Here we just raise an error or return a mock.
        raise ValueError("No valid database adapter configured.")

    _adapter_cache[db_type] = adapter
    return adapter
