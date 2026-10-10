import logging


LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


class UvicornCategoryFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.name != "uvicorn.error":
            return True
        
        if record.levelno >= logging.ERROR:
            record.name = "uvicorn.error"
        elif record.levelno >= logging.WARNING:
            record.name = "uvicorn.warning"
        else:
            record.name = "uvicorn.info"
        return True


def configure_logging() -> None:

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {"format": LOG_FORMAT}
            },
            "filters": {
                "uvicorn_category": {"()": UvicornCategoryFilter}
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "filters": ["uvicorn_category"],
                    "stream": "ext://sys.stderr",
                },
            },
            "root": {
                "handlers": ["default"],
                "level": "INFO"
            },
            "loggers": {
                "uvicorn": {
                    "handlers": [],
                    "level": "INFO",
                    "propagate": True
                },
                "uvicorn.info": {
                    "handlers": [],
                    "level": "INFO",
                    "propagate": True
                },
                "uvicorn.access": {
                    "handlers": [],
                    "level": "INFO",
                    "propagate": True
                }
            }
        }
    )