import logging


class Logger:
    isDebug = False
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        if Logger.isDebug:
            logging.basicConfig(level=logging.DEBUG, format=self.format)
        else:
            logging.basicConfig(level=logging.INFO, format=self.format)

    @classmethod
    def error(cls, msg):
        cls.logger.error(msg)

    @classmethod
    def info(cls, msg):
        cls.logger.info(msg)

    @classmethod
    def debug(self, msg):
        self.logger.debug(msg)

    @classmethod
    def dict(self, dict):
        for k, v in dict.items():
            print(k.encode("utf-8"))
            try:
                print(v.encode("utf-8"))
            except:
                print(v)
    @classmethod
    def list(self, _list):
        for v in _list:
            print(v.encode("utf-8"))
