"""
A generic logger for poefixer
"""


import logging


def get_poefixer_logger(level=logging.INFO):
    """
    Return a logger for this application.

    Logging `level` is the only parameter and should be one of the logging
    module's defined levels such as `logging.INFO`
    """

    logger = logging.getLogger('poefixer')
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger
