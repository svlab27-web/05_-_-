"""
Точка входа для запуска Агента 4
"""
import os
import time
import signal
import logging
import logging.config
import yaml
from dotenv import load_dotenv
from agents.agent_4.agent import Agent4

def setup_logging():
    """Настройка логирования"""
    # Создание директории для логов если её нет
    os.makedirs('data/logs', exist_ok=True)
    
    # Базовая конфигурация логирования
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'standard',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'standard',
                'filename': 'data/logs/agent4.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file'],
                'level': 'INFO',
                'propagate': True
            }
        }
    }
    
    # Применение конфигурации
    logging.config.dictConfig(logging_config)

def handle_shutdown(signum, frame):
    """Обработчик сигналов остановки"""
    raise KeyboardInterrupt

def main():
    """Основная функция запуска агента"""
    try:
        # Настройка логирования
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting Agent 4 application...")
        
        # Загрузка переменных окружения
        load_dotenv()
        
        # Регистрация обработчиков сигналов
        signal.signal(signal.SIGTERM, handle_shutdown)
        signal.signal(signal.SIGINT, handle_shutdown)
        
        # Создание и запуск агента
        agent = Agent4()
        agent.start()
        
        # Бесконечный цикл ожидания
        logger.info("Agent 4 is running in background mode. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        
        # Корректное завершение работы
        logger.info("Shutting down Agent 4...")
        agent.stop()
        logger.info("Agent 4 shutdown complete")
        
    except Exception as e:
        logger.error(f"Critical error in Agent 4: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
