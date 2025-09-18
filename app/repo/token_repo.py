from app.db.record_manager import RecordManager


class TokenRepo(RecordManager):
    def __init__(self):
        super().__init__("token")

    def create(self, token, user_id):

        token_list = super().get({"user_id": user_id})

        if not token_list == []:
            for elm in token_list:
                super().delete(elm["id"])

        super().create({"token": token, "user_id": user_id})
