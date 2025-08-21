from app.db.recordManager import RecordManager


class RepositoriesRepo(RecordManager):
    def __init__(self):
        super().__init__('repositories')