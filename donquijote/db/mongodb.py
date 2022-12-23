import os

from pymongo import MongoClient


class Mongo:
    """A class for connecting to and interacting with a MongoDB database.

    Attributes:
        client (MongoClient): A client object for connecting to the MongoDB server.
        db (Database): A database object for interacting with the specified database.

    Methods:
        __init__(self) -> None: Initializes the Mongo class and establishes a connection to the MongoDB server.
    """

    def __init__(self) -> None:
        """Initializes the Mongo class and establishes a connection to the MongoDB server."""
        self.client = MongoClient(os.environ["MONGO_URI"])
        self.db = self.client[os.environ["MONGO_DB"]]


class User(Mongo):
    """
    A class for interacting with user documents in a MongoDB database.

    Attributes:
        col (Collection): A collection object for interacting with the 'user' collection.

    Methods:
        __init__(self): Initializes the User class and establishes a connection to the MongoDB server.
        find(self, user_id): Retrieves a single user document with the specified user ID.
        find_all(self): Retrieves a list of all user documents.
        update(self, user_id, update_dict): Updates a single user document with the specified user ID and update dict.
        insert(self, user_id, name, n_words, reminder, sign_up): Inserts a new user document into the 'user' collection.
        exists(self, user_id): Returns True if a user document with the specified user ID exists, False otherwise.
    """

    def __init__(self):
        """
        Initializes the User class and establishes a connection to the MongoDB server.

        Returns:
            None
        """
        super().__init__()
        self.col = self.db.user

    def find(self, user_id):
        """
        Retrieves a single user document with the specified user ID.

        Args:
            user_id (int): The user ID of the user document to retrieve.

        Returns:
            Dict: The user document with the specified user ID.
        """
        return self.col.find_one({"user_id": user_id})

    def find_all(self):
        """
        Retrieves a list of all user documents.

        Returns:
            List[Dict]: A list of all user documents.
        """
        return list(self.col.find())

    def update(self, user_id, update_dict):
        """
        Updates a single user document with the specified user ID.

        Args:
            user_id (int): The user ID of the user document to update.
            update_dict (Dict): The update to apply to the user document.

        Returns:
            None
        """
        self.col.update_one({"user_id": user_id}, update_dict)

    def insert(self, user_id, name, n_words, reminder, sign_up):
        """
        Inserts a new user document into the 'user' collection.

        Args:
            user_id (int): The user ID of the new user document.
            name (str): The name of the new user.
            n_words (int): The number of words the user has learned.
            reminder (bool): A flag indicating whether the user wants to receive reminders.
            sign_up (datetime): The date and time the user signed up.

        Returns:
            None
        """
        self.col.insert_one(
            {
                "user_id": user_id,
                "name": name,
                "n_words": n_words,
                "reminder": reminder,
                "max_vocabs": 30,
                "sign_up": sign_up,
                "streak": 0,
            }
        )

    def exists(self, user_id):
        """
        Returns True if a user document with the specified user ID exists, False otherwise.

        Args:
            user_id (int): The user ID to check for.

        Returns:
            bool: True if a user document with the specified user ID exists, False otherwise.
        """
        return (
            True
            if self.col.count_documents({"user_id": user_id}) > 0
            else False
        )


class Vocabulary(Mongo):
    """
    A class for interacting with vocabulary documents in a MongoDB database.

    Attributes:
        col (Collection): A collection object for interacting with the 'vocabulary' collection.

    Methods:
        __init__(self): Initializes the Vocabulary class and establishes a connection to the MongoDB server.
        sample(self, n_words, nin=[]): Retrieves a list of vocabulary documents randomly sampled from the collection,
            excluding the ones with vocabulary IDs in the specified list.
        find(self, vocab_id): Retrieves a single vocabulary document with the specified vocabulary ID.
        range(self, start, end, abbr=None): Retrieves a list of vocabulary documents within a specified range,
            sorted by frequency.
        vocab_count(self, abbr): Retrieves the number of vocabulary documents with the specified abbreviation.
        from_vocab_list(self, vocab_list): Retrieves a list of vocabulary documents with the specified vocabulary IDs.
    """

    def __init__(self):
        """
        Initializes the Vocabulary class and establishes a connection to the MongoDB server.

        Returns:
            None
        """
        super().__init__()
        self.col = self.db.vocabulary

    def sample(self, n_words, nin=[]):
        """
        Retrieves a list of vocabulary documents randomly sampled from the collection,
        excluding the ones with vocabulary IDs in the specified list.

        Args:
            n_words (int): The number of vocabulary documents to retrieve.
            nin (List[int], optional): A list of vocabulary IDs to exclude from the sample. If not provided,
                retrieves vocabulary documents of all vocabulary IDs.

        Returns:
            List[Dict]: A list of vocabulary documents randomly sampled from the collection,
                excluding the ones with vocabulary IDs in the specified list.
        """
        return self.col.aggregate(
            [
                {"$match": {"vocab_id": {"$nin": nin}}},
                {"$sample": {"size": n_words}},
                {"$project": {"_id": 0}},
            ]
        )

    def find(self, vocab_id):
        """
        Retrieves a single vocabulary document with the specified vocabulary ID.

        Args:
            vocab_id (int): The vocabulary ID of the vocabulary document to retrieve.

        Returns:
            Dict: The vocabulary document with the specified vocabulary ID.
        """
        return self.col.find_one({"vocab_id": vocab_id}, {"_id": 0})

    def range(self, start, end, abbr=None):
        """
        Retrieves a list of vocabulary documents within a specified range, sorted by frequency.

        Args:
            start (int): The starting index of the range.
            end (int): The ending index of the range.
            abbr (str, optional): The abbreviation of the vocabulary documents to retrieve. If not provided,
                retrieves vocabulary documents of all abbreviations.

        Returns:
            List[Dict]: A list of vocabulary documents within the specified range, sorted by frequency.
        """
        where = {}
        if abbr:
            where = {**where, **{"abbr": abbr}}

        return list(self.col.find(where).sort("freq", 1))[start:end]

    def vocab_count(self, abbr):
        """
        Retrieves the number of vocabulary documents with the specified abbreviation.

        Args:
            abbr (str): The abbreviation of the vocabulary documents to count.

        Returns:
            int: The number of vocabulary documents with the specified abbreviation.
        """
        return self.col.count_documents({"abbr": abbr})

    def from_vocab_list(self, vocab_list):
        """
        Retrieves a list of vocabulary documents with the specified vocabulary IDs.

        Args:
            vocab_list (List[int]): A list of vocabulary IDs of the vocabulary documents to retrieve.

        Returns:
            List[Dict]: A list of vocabulary documents with the specified vocabulary IDs.
        """
        return self.col.aggregate(
            [
                {"$match": {"vocab_id": {"$in": vocab_list}}},
                {"$project": {"_id": 0}},
            ]
        )


class Practice(Mongo):
    """
    This class represents a collection of methods for interacting with the 'practice' collection in the database.
    It provides functions for finding, updating, inserting, and checking for the existence of practice records.

    Methods:
        __init__(self): Initializes the Practice class and establishes a connection to the 'practice' collection in the database.
        max_id(self): Returns the maximum practice_id value from the 'practice' collection.
        find(self, user_id, timestamp): Finds a practice record for the given user_id and timestamp.
        update(self, practice_id, update_dict): Updates a practice record with the given practice_id using the update_dict.
        insert(self, practice_id, user_id, timestamp, vocabs, attempts): Inserts a new practice record with the given practice_id,
            user_id, timestamp, vocabs, and attempts.
        exists(self, user_id, timestamp, return_count=False): Checks if a practice record exists for the given user_id and timestamp.
            If return_count is set to True, returns the count of matching practice records.
    """

    def __init__(self):
        """
        Initializes the Practice class and establishes a connection to the 'practice' collection in the database.
        """
        super().__init__()
        self.col = self.db.practice

    def max_id(self):
        """
        Returns the maximum practice_id value from the 'practice' collection.

        Returns:
            int: The maximum practice_id value from the 'practice' collection.
        """
        try:
            return self.col.find_one(sort=[("practice_id", -1)])["practice_id"]
        except (KeyError, TypeError):
            return -1

    def find(self, user_id, timestamp):
        """
        Finds a practice record for the given user_id and timestamp.

        Args:
            user_id (int): The user_id of the practice record to find.
            timestamp (datetime): The timestamp of the practice record to find.

        Returns:
            dict: The practice record with the given user_id and timestamp.
        """
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
        """
        Updates a practice record with the given practice_id using the update_dict.

        Args:
            practice_id (int): The practice_id of the practice record to update.
            update_dict (dict): A dictionary containing the updates to make to the practice record.
        """
        self.col.update_one({"practice_id": practice_id}, update_dict)

    def insert(self, practice_id, user_id, timestamp, vocabs, attempts):
        """
        Inserts a new practice record with the given practice_id, user_id, timestamp, vocabs, and attempts.

        Args:
        practice_id (int): The practice_id of the new practice record.
        user_id (int): The user_id of the new practice record.
        timestamp (datetime): The timestamp of the new practice record.
        vocabs (list): A list of vocabulary words for the new practice record.
        attempts (int): The number of attempts for the new practice record.
        """
        self.col.insert_one(
            {
                "practice_id": practice_id,
                "user_id": user_id,
                "timestamp": timestamp,
                "vocabs": vocabs,
                "attempts": attempts,
            }
        )

    def exists(self, user_id, timestamp, return_count=False):
        """
        Checks if a practice record exists for the given user_id and timestamp.
        If return_count is set to True, returns the count of matching practice records.

        Args:
            user_id (int): The user_id to check for in the practice records.
            timestamp (datetime): The timestamp to check for in the practice records.
            return_count (bool): Whether to return the count of matching practice records.

        Returns:
            bool: True if a practice record exists for the given user_id and timestamp, False otherwise.
            int: The count of matching practice records if return_count is set to True.
        """
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
    """
    A class for interacting with the SRS collection in a MongoDB database.

    Attributes:
        db (MongoClient): A MongoClient object for interacting with the database.
        col (Collection): A Collection object for interacting with the 'srs' collection.
    """

    def __init__(self):
        """
        Initializes the SRS object and sets the 'srs' collection as an attribute.

        Returns:
            None
        """
        super().__init__()
        self.col = self.db.srs

    def repeat(self, user_id, timestamp, max_vocabs=None):
        """
        Retrieves a list of vocabularies that are ready for repetition for a given user.

        Args:
            user_id (int): The ID of the user.
            timestamp (int): A Unix timestamp used for filter on next_learn.
            max_vocabs (int, optional): The maximum number of vocabularies to retrieve.
                If not provided, all ready vocabularies are retrieved.

        Returns:
            list: A list of dictionaries, each representing a vocabulary that is ready for repetition.
        """
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
        """
        Finds a vocabulary in the 'srs' collection for a given user.

        Args:
            user_id (int): The ID of the user.
            vocab_id (int): The ID of the vocabulary.

        Returns:
            dict: A dictionary representing the vocabulary.
        """
        return self.col.find_one(
            {"user_id": user_id, "vocab_id": vocab_id}, {"_id": 0}
        )

    def update(self, user_id, vocab_id, update_dict):
        """
        Updates a vocabulary in the 'srs' collection for a given user.

        Args:
            user_id (int): The ID of the user.
            vocab_id (int): The ID of the vocabulary.
            update_dict (dict): A dictionary containing the updates to be made to the vocabulary.

        Returns:
            None
        """
        self.col.update_one(
            {"user_id": user_id, "vocab_id": vocab_id}, update_dict
        )

    def insert(self, user_id, vocab_id):
        """
        Inserts a vocabulary into the 'srs' collection for a given user.

        Args:
            user_id (int): The ID of the user.
            vocab_id (int): The ID of the vocabulary.

        Returns:
            None
        """
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
        """
        Checks if a vocabulary exists in the 'srs' collection for a given user.

        Args:
            user_id (int): The ID of the user.
            vocab_id (int): The ID of the vocabulary.

        Returns:
            bool: True if the vocabulary exists, False otherwise.
        """
        return (
            True
            if self.col.count_documents(
                {"user_id": user_id, "vocab_id": vocab_id}
            )
            > 0
            else False
        )
