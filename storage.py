import json
import uuid
from pathlib import Path
import shutil
from typing import Dict, Any, Optional

class Storage:
    def __init__(self, base_path: str = "./storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def create_session(self) -> str:
        """Create a new session and return session ID."""
        session_id = str(uuid.uuid4())
        (self.base_path / session_id).mkdir(exist_ok=True)
        return session_id

    def store_data(self, session_id: str, data: Dict[str, Any]) -> None:
        """Store data for a session."""
        session_path = self.base_path / session_id
        with open(session_path / "data.json", "w") as f:
            json.dump(data, f)

    def get_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve data for a session."""
        try:
            session_path = self.base_path / session_id
            with open(session_path / "data.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Clean up sessions older than max_age_hours."""
        # Implementation for cleanup (can be added later)
        pass
