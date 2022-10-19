import os

from pymongo import MongoClient


class Mongo:
    def __init__(self) -> None:
        self.client = MongoClient(os.environ["MONGO_URI"])
        self.db = self.client[os.environ["MONGO_DB"]]


class User(Mongo):
    def __init__(self):
        super().__init__()
        self.col = self.db.user

    def find(self, user_id):
        return self.col.find_one({"user_id": user_id})

    def find_all(self):
        return list(self.col.find())

    def update(self, user_id, update_dict):
        self.col.update_one({"user_id": user_id}, update_dict)

    def insert(self, user_id, name, n_words, reminder, sign_up):
        self.col.insert_one(
            {
                "user_id": user_id,
                "name": name,
                "n_words": n_words,
                "reminder": reminder,
                "max_vocabs": 30,
                "sign_up": sign_up,
            }
        )

    def exists(self, user_id):
        return (
            True
            if self.col.count_documents({"user_id": user_id}) > 0
            else False
        )


class Vocabulary(Mongo):
    def __init__(self):
        super().__init__()
        self.col = self.db.vocabulary

    def sample(self, n_words, nin=[]):
        return self.col.aggregate(
            [
                {"$match": {"vocab_id": {"$nin": nin}}},
                {"$sample": {"size": n_words}},
                {"$project": {"_id": 0}},
            ]
        )

    def find(self, vocab_id):
        return self.col.find_one({"vocab_id": vocab_id}, {"_id": 0})

    def range(self, start, end, abbr=None):
        where = {}
        if abbr:
            where = {**where, **{"abbr": abbr}}

        return list(self.col.find(where).sort("freq", 1))[start:end]

    def vocab_count(self, abbr):
        return self.col.count_documents({"abbr": abbr})

    def from_vocab_list(self, vocab_list):
        return self.col.aggregate(
            [
                {"$match": {"vocab_id": {"$in": vocab_list}}},
                {"$project": {"_id": 0}},
            ]
        )


class Practice(Mongo):
    def __init__(self):
        super().__init__()
        self.col = self.db.practice

    def max_id(self):
        try:
            return self.col.find_one(sort=[("practice_id", -1)])["practice_id"]
        except (KeyError, TypeError):
            return -1

    def find(self, user_id, timestamp):
        dt_start = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        dt_end = timestamp.replace(
            hour=23, minute=59, second=59, microsecond=0
        )

        return self.col.find_one(
            {
                "user_id": user_id,
                "timestamp": {"$gte": dt_start, "$lte": dt_end},
            }
        )

    def update(self, practice_id, update_dict):
        self.col.update_one({"practice_id": practice_id}, update_dict)

    def insert(self, practice_id, user_id, timestamp, vocabs):
        self.col.insert_one(
            {
                "practice_id": practice_id,
                "user_id": user_id,
                "timestamp": timestamp,
                "vocabs": vocabs,
                "attempts": {str(v): 0 for v in vocabs},
            }
        )

    def exists(self, user_id, timestamp, return_count=False):
        dt_start = timestamp.replace(hour=0, minute=0, second=0, microsecond=0)
        dt_end = timestamp.replace(
            hour=23, minute=59, second=59, microsecond=0
        )

        if not return_count:
            return (
                True
                if self.col.count_documents(
                    {
                        "user_id": user_id,
                        "timestamp": {"$gte": dt_start, "$lte": dt_end},
                    }
                )
                > 0
                else False
            )
        else:
            return self.col.count_documents(
                {
                    "user_id": user_id,
                    "timestamp": {"$gte": dt_start, "$lte": dt_end},
                }
            )


class SRS(Mongo):
    def __init__(self):
        super().__init__()
        self.col = self.db.srs

    def repeat(self, user_id, timestamp, max_vocabs=None):
        vocabs = list(
            self.col.aggregate(
                [
                    {
                        "$match": {
                            "user_id": user_id,
                            "next_learn": {"$lte": timestamp},
                        }
                    },
                    {"$sort": {"quick_repeat": -1, "next_learn": 1}},
                    {"$project": {"_id": 0}},
                ]
            )
        )

        if max_vocabs:
            vocabs = vocabs[:max_vocabs]

        return vocabs

    def find(self, user_id, vocab_id):
        return self.col.find_one(
            {"user_id": user_id, "vocab_id": vocab_id}, {"_id": 0}
        )

    def update(self, user_id, vocab_id, update_dict):
        self.col.update_one(
            {"user_id": user_id, "vocab_id": vocab_id}, update_dict
        )

    def insert(self, user_id, vocab_id):
        self.col.insert_one(
            {
                "user_id": user_id,
                "vocab_id": vocab_id,
                "level": 1,
                "last_learn": None,
                "next_learn": None,
                "quick_repeat": False,
            }
        )

    def exists(self, user_id, vocab_id):
        return (
            True
            if self.col.count_documents(
                {"user_id": user_id, "vocab_id": vocab_id}
            )
            > 0
            else False
        )
