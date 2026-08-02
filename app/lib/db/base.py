from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

class DatabaseAdapter(ABC):
    @abstractmethod
    async def connect(self, context: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    async def insert(self, submission: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    async def query(self, form_id: str, options: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def update_submission(self, form_id: str, submission_id: str, patch: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> bool:
        pass

    @abstractmethod
    async def delete_submission(self, form_id: str, submission_id: str, hard: bool, options: Optional[Dict[str, Any]] = None) -> bool:
        pass

    async def disconnect(self) -> None:
        pass

    # Auth methods
    @abstractmethod
    async def find_user_by_email(self, email: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    async def insert_user(self, user: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    async def update_user_last_login(self, user_id: str, context: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    async def update_user_password(self, user_id: str, new_password_hash: str, context: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    async def verify_user_email(self, user_id: str, context: Optional[Dict[str, Any]] = None) -> None:
        pass

    @abstractmethod
    async def update_user_otp(self, user_id: str, otp: str, expires_at: Any, context: Optional[Dict[str, Any]] = None) -> None:
        pass
