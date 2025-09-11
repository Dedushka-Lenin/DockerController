from app.db.record_manager import RecordManager


class VersionRepo(RecordManager):
    def __init__(self):
        super().__init__("version")
