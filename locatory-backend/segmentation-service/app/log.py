import logging
from .configs import cfg


class Log:
    __instance__ = None
    root_logger = None

    def __init__(self):
        """ Constructor.
        """
        if Log.__instance__ is None:
            Log.__instance__ = self
            self.root_logger = self.get_logger('segmentation_logs')
        else:
            raise Exception("You cannot create another Singleton Log class")

    @staticmethod
    def get_instance():
        """ Static method to fetch the current instance.
        """
        if not Log.__instance__:
            Log()
        return Log.__instance__

    def setup_custom_logger(self, log_filename):
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s')

        # handler = logging.FileHandler(log_filename,'w') encoding='bz2' for compression
        handler = logging.handlers.RotatingFileHandler(
            log_filename, maxBytes=50000000, backupCount=10)
        handler.setFormatter(formatter)

        logger = logging.getLogger(log_filename)
        # Change to DEBUG later
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        return logger

    def get_logger(self, filename):
        log_path = cfg.LOG_PATH
        log_file_path = log_path+filename+".log"
        logger = self.setup_custom_logger(log_file_path)
        return logger
