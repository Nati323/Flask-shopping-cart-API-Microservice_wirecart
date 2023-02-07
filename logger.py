import logging

def logger_factory(name):
    logger = logging.getLogger(name)

    sys_log_handler = logging.StreamHandler()
    info_handler    = logging.StreamHandler()
    to_file_handler = logging.FileHandler(filename='info.log')

    sys_log_handler.setLevel(logging.ERROR)
    info_handler.setLevel(logging.INFO)
    to_file_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    sys_log_handler.setFormatter(formatter)
    info_handler.setFormatter(formatter)
    to_file_handler.setFormatter(formatter)

    logger.addHandler(sys_log_handler)
    logger.addHandler(info_handler)
    logger.addHandler(to_file_handler)

    logger.setLevel(logging.WARNING)
    return logger
