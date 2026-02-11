"""
Цикл 4: Обучение и оптимизация
Анализирует эффективность и выполняет самооптимизацию
Запускается каждый день в 23:00
"""
from datetime import datetime, timedelta
import logging
import pandas as pd
from typing import Dict, List
from .base_cycle import BaseCycle

logger = logging.getLogger(__name__)

class OptimizationCycle(BaseCycle):
    def __init__(self, alert_system=None, database=None, telegram_bot=None):
        """
        Инициализация цикла оптимизации
        
        Args:
            alert_system: Система оповещений
            database: Объект для работы с базой данных
            telegram_bot: Клиент для отправки уведомлений в Telegram (устаревший)
        """
        super().__init__(name="Optimization Cycle", interval=86400)  # 86400 секунд = 24 часа
        self.alert_system = alert_system
        self.database = database
        self.telegram_bot = telegram_bot  # Для обратной совместимости
        self.kpi_targets = {
            'response_time': 3600,  # 1 час
            'automation_rate': 0.7,  # 70%
            'success_rate': 0.95    # 95%
        }
        
        if telegram_bot and not alert_system:
            logger.warning("Использование telegram_bot устарело, используйте alert_system")
            self.alert_system = telegram_bot

    # Остальные методы остаются без изменений
    # ...
