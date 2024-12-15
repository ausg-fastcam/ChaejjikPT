import logging
import sys
import json


class CustomFormatter(logging.Formatter):

    def __init__(self, formatter):
        logging.Formatter.__init__(self, formatter)

    def format(self, record):
        logging.Formatter.format(self, record)

        return json.dumps(self.make_json_log(record), indent=None, ensure_ascii=False)

    def make_json_log(
        self, record
    ):
        if record.exc_info is None:
            json_obj = {
                "app_log": {
                    "level": record.levelname,
                    "type": "app",
                    "timestamp": record.asctime,
                    #'filename': record.filename,
                    "pathname": record.pathname,
                    "line": record.lineno,
                    "threadId": record.thread,
                    "message": record.message,
                }
            }
        else:
            json_obj = {
                "slack_log": {
                    "level": record.levelname,
                    "type": "app",
                    "timestamp": record.asctime,
                    #'filename': record.filename,
                    "pathname": record.pathname,
                    "line": record.lineno,
                    "threadId": record.thread,
                    "message": record.message,
                    "contents": {
                        "userChat": record.exc_info["userChat"] if "userChat" in record.exc_info else None,
                        "botResponse": record.exc_info["botResponse"] if "botResponse" in record.exc_info else None,
                        "teamId": record.exc_info["teamId"] if "teamId" in record.exc_info else None,
                        "userId": record.exc_info["userId"] if "userId" in record.exc_info else None,
                    },
                }
            }

        return json_obj


def get_file_handler(formatter, log_filename):
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    return file_handler


def get_stream_handler(formatter):
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    return stream_handler


def set_logger(name, formatter, log_filename="logfile.log"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler(formatter, log_filename))
    logger.addHandler(get_stream_handler(formatter))
    return logger


def get_logger():
    formatter = CustomFormatter("%(asctime)s")
    return set_logger(__name__, formatter)
