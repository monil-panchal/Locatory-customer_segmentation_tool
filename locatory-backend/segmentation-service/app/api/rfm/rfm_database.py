from app.configs import cfg

class RFMDatabase:
    __instance__ = None
    _client = None
    _db = None

    def __init__(self):
        """ Constructor.
        """
        if RFMDatabase.__instance__ is None:
            RFMDatabase.__instance__ = self
            self._client = MongoClient(host=self.get_database_url(), port=self.get_database_port())
            self._db = self._client[self.get_database_name()]
        else:
            raise Exception("You cannot create another Singleton RFMDatabase class")

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
        """
        if not RFMDatabase.__instance__:
            RFMDatabase()
        return RFMDatabase.__instance__

    def get_database_url(self):
        return cfg.MONGODB_URL

    def get_database_port(self):
        return cfg.MONGODB_PORT

    def get_database_name(self):
        return cfg.MONGODB_DATABASE_NAME

    def get_database_username(self):
        return cfg.MONGODB_USERNAME

    def get_database_password(self):
        return cfg.MONGODB_PASSWORD