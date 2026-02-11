"""
Цикл 1: Мониторинг заявок
Проверяет новые и "застрявшие" заявки каждые 10 минут
"""
from datetime import datetime, timedelta
import logging
from .base_cycle import BaseCycle

logger = logging.getLogger(__name__)

class MonitoringCycle(BaseCycle):
    def __init__(self, telegram_bot=None, database=None):
        """
        Инициализация цикла мониторинга
        
        Args:
            telegram_bot: Объект для отправки уведомлений в Telegram
            database: Объект для работы с базой данных
        """
        super().__init__(name="Monitoring Cycle", interval=600)  # 600 секунд = 10 минут
        self.telegram_bot = telegram_bot
        self.database = database
        self.stuck_threshold = timedelta(hours=2)  # Порог для "застрявших" заявок
        
    def execute(self):
        """Выполнение цикла мониторинга"""
        try:
            # 1. Проверка новых заявок
            new_requests = self._check_new_requests()
            if new_requests:
                self._process_new_requests(new_requests)
            
            # 2. Проверка "застрявших" заявок
            stuck_requests = self._check_stuck_requests()
            if stuck_requests:
                self._process_stuck_requests(stuck_requests)
                
            logger.info(f"Monitoring cycle completed. Found {len(new_requests)} new and {len(stuck_requests)} stuck requests")
            
        except Exception as e:
            logger.error(f"Error in monitoring cycle: {e}")
            raise
    
    def _check_new_requests(self) -> list:
        """
        Проверка новых заявок из всех источников
        
        Returns:
            list: Список новых заявок
        """
        if not self.database:
            return []
            
        try:
            # Получаем все заявки со статусом NEW
            requests = self.database.data.get('requests', [])
            new_requests = [
                req for req in requests 
                if req.get('status') == 'NEW'
            ]
            
            logger.info(f"Found {len(new_requests)} new requests")
            return new_requests
            
        except Exception as e:
            logger.error(f"Error checking new requests: {e}")
            return []
    
    def _process_new_requests(self, requests: list):
        """
        Обработка новых заявок
        
        Args:
            requests (list): Список новых заявок
        """
        for request in requests:
            try:
                # 1. Установка статуса "Новая"
                self._update_request_status(request, "NEW")
                
                # 2. Отправка уведомления оператору
                if self.telegram_bot:
                    self._send_notification(
                        f"🆕 Новая заявка!\n"
                        f"ID: {request.get('id')}\n"
                        f"Источник: {request.get('source')}\n"
                        f"Время: {datetime.now().strftime('%H:%M:%S')}"
                    )
                    
                logger.info(f"Processed new request {request.get('id')}")
                
            except Exception as e:
                logger.error(f"Error processing request {request.get('id')}: {e}")
    
    def _check_stuck_requests(self) -> list:
        """
        Проверка "застрявших" заявок
        
        Returns:
            list: Список застрявших заявок
        """
        if not self.database:
            return []
            
        try:
            # Получаем все заявки в работе
            requests = self.database.data.get('requests', [])
            current_time = datetime.now()
            
            # Фильтруем заявки, которые "застряли"
            stuck_requests = [
                req for req in requests
                if (
                    req.get('status') == 'IN_PROGRESS' and
                    req.get('started_at') and
                    current_time - req['started_at'] >= self.stuck_threshold
                )
            ]
            
            logger.info(f"Found {len(stuck_requests)} stuck requests")
            return stuck_requests
            
        except Exception as e:
            logger.error(f"Error checking stuck requests: {e}")
            return []
    
    def _process_stuck_requests(self, requests: list):
        """
        Обработка "застрявших" заявок
        
        Args:
            requests (list): Список застрявших заявок
        """
        for request in requests:
            try:
                # 1. Установка статуса "Требует внимания"
                self._update_request_status(request, "NEEDS_ATTENTION")
                
                # 2. Эскалация руководителю
                if self.telegram_bot:
                    self._send_notification(
                        f"⚠️ Застрявшая заявка!\n"
                        f"ID: {request.get('id')}\n"
                        f"Время в работе: {request.get('time_in_progress')}\n"
                        f"Текущий исполнитель: {request.get('assignee')}",
                        is_urgent=True
                    )
                    
                logger.info(f"Processed stuck request {request.get('id')}")
                
            except Exception as e:
                logger.error(f"Error processing stuck request {request.get('id')}: {e}")
    
    def _update_request_status(self, request: dict, status: str):
        """
        Обновление статуса заявки в базе данных
        
        Args:
            request (dict): Заявка
            status (str): Новый статус
        """
        if not self.database:
            return
            
        try:
            # Формируем запрос на обновление
            query = "UPDATE requests SET status = :status WHERE id = :id"
            params = {
                'id': request.get('id'),
                'status': status
            }
            
            # Выполняем запрос
            self.database.execute(query, params)
            logger.info(f"Updated request {request.get('id')} status to {status}")
            
        except Exception as e:
            logger.error(f"Error updating request status: {e}")
    
    def _send_notification(self, message: str, is_urgent: bool = False):
        """
        Отправка уведомления в Telegram
        
        Args:
            message (str): Текст сообщения
            is_urgent (bool): Флаг срочности
        """
        if not self.telegram_bot:
            return
            
        try:
            # Для срочных сообщений добавляем пометку
            if is_urgent:
                message = "🚨 СРОЧНО!\n" + message
            
            # Отправляем сообщение
            self.telegram_bot.send_message(
                chat_id="support_chat",  # ID чата поддержки
                text=message
            )
            
            logger.info(f"Sent notification: {message[:100]}...")
            
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
