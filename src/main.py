"""
Точка входа для запуска Агента 4
"""
import os
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

def main():
    """Основная функция запуска агента"""
    try:
        # Настройка логирования
        setup_logging()
        logger = logging.getLogger(__name__)
        logger.info("Starting Agent 4 application...")
        
        # Загрузка переменных окружения
        load_dotenv()
        
        # Создание и запуск агента
        agent = Agent4()
        agent.start()
        
        # Ожидание команды на завершение
        try:
            while True:
                command = input().strip().lower()
                if command == 'stop':
                    break
                elif command == 'status':
                    status = agent.get_status()
                    print("\nAgent 4 Status:")
                    print(f"Running: {status['agent']['running']}")
                    print(f"Uptime: {status['agent']['uptime']}")
                    print("\nCycles Status:")
                    for cycle_name, cycle_status in status['cycles'].items():
                        print(f"{cycle_name}: {'Running' if cycle_status['running'] else 'Stopped'}")
                    print()
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
