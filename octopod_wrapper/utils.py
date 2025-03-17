from typing import Optional
from uuid import UUID


def convert_str_to_uuid(str_val: str) -> Optional[UUID]:
    try:
        return UUID(str(str_val))
    except ValueError:
        return None
