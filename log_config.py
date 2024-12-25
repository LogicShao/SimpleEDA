import logging
from logging.handlers import RotatingFileHandler


logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

log_file = "app.log"
file_handler = RotatingFileHandler(
    log_file, maxBytes=5*1024*1024, backupCount=0, encoding='utf-8')  # 设置最大文件大小为5MB，备份文件数量为0
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
