import json
import os
import uuid
from pathlib import Path
import shutil
from typing import Dict, Any, Optional

class Storage:
    def __init__(self):
        self.data = {}

    def store_data(self, session_id, data):
        self.data[session_id] = data

    def get_data(self, session_id):
        return self.data.get(session_id)

    def create_session(self):
        return os.urandom(16).hex()
