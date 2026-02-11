"""
Базовый класс для всех HD циклов
"""
from abc import ABC, abstractmethod
import schedule
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseCycle(ABC):
    """Базовый HD цикл"""
    
    def __init__(self, name: str, interval: int):
        """
        Инициализация базового цикла
        
        Args:
            name (str): Название цикла
            interval (int): Интервал выполнения в секундах
        """
        self.name = name
        self.interval = interval
        self.is_running = False
        self.last_run = None
        self.error_count = 0
        self.max_errors = 3
        
    @abstractmethod
    def execute(self):
        """
        Логика выполнения цикла
        Должна быть переопределена в каждом конкретном цикле
        """
        pass
    
    def start(self):
        """Запуск цикла"""
        logger.info(f"Starting cycle: {self.name}")
        self.is_running = True
        schedule.every(self.interval).seconds.do(self._run)
        
    def _run(self):
        """Внутренний метод запуска с обработкой ошибок"""
        try:
            logger.debug(f"Executing cycle: {self.name}")
            self.execute()
            self.last_run = datetime.now()
            self.error_count = 0  # Сброс счетчика ошибок после успешного выполнения
        except Exception as e:
            self.error_count += 1
            logger.error(f"Error in cycle {self.name}: {e}")
            
            if self.error_count >= self.max_errors:
                logger.critical(f"Cycle {self.name} exceeded maximum error count. Stopping cycle.")
                self.stop()
    
    def stop(self):
        """Остановка цикла"""
        self.is_running = False
        schedule.cancel_job(self._run)
        logger.info(f"Stopped cycle: {self.name}")
    
    def get_status(self) -> dict:
        """Получение текущего статуса цикла"""
        return {
            "name": self.name,
            "running": self.is_running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "error_count": self.error_count,
            "interval": self.interval
        }
