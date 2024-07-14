import logging


class CommonLogger(logging.Logger):
    def __init__(self, *args, **kwargs):
        logger_format = kwargs.pop("logger_format")
        super().__init__(*args, **kwargs)
        formatter = logging.Formatter(fmt=logger_format, datefmt="%Y-%m-%d %H:%M:%S")
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.addHandler(handler)
        self.setLevel(logging.INFO)


logger = CommonLogger(
    name="common_logger",
    logger_format="[%(levelname)s %(asctime)s - %(message)s]"
)
