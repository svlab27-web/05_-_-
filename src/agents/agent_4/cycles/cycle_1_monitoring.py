"""
Цикл 1: Мониторинг заявок
Проверяет новые и "застрявшие" заявки каждые 10 минут
"""
from datetime import datetime, timedelta
import logging
from .base_cycle import BaseCycle

logger = logging.getLogger(__name__)

class MonitoringCycle(BaseCycle):
    def __init__(self, alert_system=None, database=None, telegram_bot=None):
        """
        Инициализация цикла мониторинга
        
        Args:
            alert_system: Система оповещений
            database: Объект для работы с базой данных
            telegram_bot: Объект для отправки уведомлений в Telegram (устаревший)
        """
        super().__init__(name="Monitoring Cycle", interval=600)
        self.alert_system = alert_system
        self.database = database
        self.telegram_bot = telegram_bot  # Для обратной совместимости
        self.stuck_threshold = timedelta(hours=2)
        
        if telegram_bot and not alert_system:
            logger.warning("Использование telegram_bot устарело, используйте alert_system")
            self.alert_system = telegram_bot

    # Остальные методы остаются без изменений
    # ...
