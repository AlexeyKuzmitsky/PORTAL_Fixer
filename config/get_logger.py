import logging
from os import path
from datetime import datetime


def get_logger(name: str = __file__,
               file: str = 'log.log',
               encoding: str = 'UTF-8',
               level=logging.ERROR,
               format_log: str = '[%(asctime)s] %(levelname)-6s %(filename)-30s:%(lineno)-5d %(message)s',
               print_log: bool = True) -> logging.Logger:
    """
    Функция создания логирования.
    :param name: Имя функции лога(для каждого лога свое).
    :param file: Имя и формат файла куда будут писаться логи.
    :param encoding: Кодировка файла.
    :param format_log: Формат лога.
    :param print_log: Выводить в консоль сообщение (True) или нет (False).
    :param level: С какого уровня выводить сообщение в консоль (формат logging.DEBUG).
    :return: logging
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(fmt=format_log, datefmt='%Y-%m-%d %H:%M')

    if print_log:
        log_console_out = logging.StreamHandler()
        log_console_out.setLevel(level=level)
        log_console_out.setFormatter(logging.Formatter(fmt='%(message)s'))
        logger.addHandler(log_console_out)

    log_file_info = logging.FileHandler(file, encoding=encoding)
    log_file_info.setLevel(level=logging.INFO)
    log_file_info.setFormatter(formatter)
    logger.addHandler(log_file_info)

    log_file_error = logging.FileHandler(path.join('logs', 'ERRORS.log'), encoding=encoding)
    log_file_error.setLevel(level=logging.ERROR)
    log_file_error.setFormatter(formatter)
    logger.addHandler(log_file_error)
    return logger


name_log = f'{datetime.now().strftime("%Y-%m-%d")}.log'
log_error: logging.Logger = get_logger(name=f'{__name__}_error',
                                       file=path.join('logs', name_log),
                                       encoding='UTF-8',
                                       print_log=False,
                                       level=logging.ERROR)

log_error_print: logging.Logger = get_logger(name=f'{__name__}_error_print',
                                             file=path.join('logs', name_log),
                                             encoding='UTF-8',
                                             print_log=True,
                                             level=logging.ERROR)

log_info: logging.Logger = get_logger(name=f'{__name__}_info',
                                      file=path.join('logs', name_log),
                                      encoding='UTF-8',
                                      print_log=False,
                                      level=logging.INFO)


log_info_print: logging.Logger = get_logger(name=f'{__name__}_info_print',
                                            file=path.join('logs', name_log),
                                            encoding='UTF-8',
                                            print_log=True,
                                            level=logging.INFO)


if __name__ == '__main__':
    pass
