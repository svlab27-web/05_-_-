"""
Цикл 3: Контроль автоматизаций
Проверяет работоспособность запущенных автоматизаций каждые 30 минут
"""
from datetime import datetime, timedelta
import logging
from typing import Dict, List
import psutil
from .base_cycle import BaseCycle

logger = logging.getLogger(__name__)

class HealthCheckCycle(BaseCycle):
    def __init__(self, telegram_bot=None, database=None):
        """
        Инициализация цикла проверки здоровья систем
        
        Args:
            telegram_bot: Клиент для отправки уведомлений в Telegram
            database: Объект для работы с базой данных
        """
        super().__init__(name="Health Check Cycle", interval=1800)  # 1800 секунд = 30 минут
        self.telegram_bot = telegram_bot
        self.database = database
        self.recovery_attempts = {}  # Счетчик попыток восстановления для каждого процесса
        self.max_recovery_attempts = 3
        
    def execute(self):
        """Выполнение цикла проверки здоровья"""
        try:
            # 1. Проверка всех систем
            health_status = self._check_all_systems()
            
            # 2. Обработка сбоев
            if not all(status['healthy'] for status in health_status.values()):
                self._handle_failures(health_status)
            
            # 3. Сохранение результатов проверки
            self._save_health_check_results(health_status)
            
            # 4. Отправка статуса администратору
            self._send_status_report(health_status)
            
            logger.info("Health check cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Error in health check cycle: {e}")
            raise
    
    def _check_all_systems(self) -> Dict[str, Dict]:
        """
        Проверка всех автоматизированных систем
        
        Returns:
            Dict[str, Dict]: Статус каждой системы
        """
        health_status = {}
        
        # 1. Проверка API интеграций
        api_status = self._check_api_integrations()
        health_status.update(api_status)
        
        # 2. Проверка баз данных
        db_status = self._check_databases()
        health_status.update(db_status)
        
        # 3. Проверка активных процессов
        process_status = self._check_running_processes()
        health_status.update(process_status)
        
        return health_status
    
    def _handle_failures(self, health_status: Dict[str, Dict]):
        """
        Обработка обнаруженных сбоев
        
        Args:
            health_status (Dict[str, Dict]): Статус всех систем
        """
        for system_name, status in health_status.items():
            if not status['healthy']:
                logger.warning(f"System {system_name} is unhealthy: {status['message']}")
                
                # Попытка автоматического восстановления
                if self._should_attempt_recovery(system_name):
                    self._attempt_recovery(system_name, status)
                else:
                    # Эскалация администратору
                    self._escalate_issue(system_name, status)
    
    def _check_api_integrations(self) -> Dict[str, Dict]:
        """
        Проверка API интеграций (Telegram, Email, CRM)
        
        Returns:
            Dict[str, Dict]: Статус каждой интеграции
        """
        integrations_status = {}
        
        # Список интеграций для проверки
        integrations = {
            'telegram_bot': self.telegram_bot
        }
        
        for name, integration in integrations.items():
            try:
                # Проверка доступности API
                is_healthy = self._test_api_connection(integration)
                integrations_status[name] = {
                    'healthy': is_healthy,
                    'message': 'OK' if is_healthy else 'API недоступен',
                    'timestamp': datetime.now()
                }
            except Exception as e:
                integrations_status[name] = {
                    'healthy': False,
                    'message': str(e),
                    'timestamp': datetime.now()
                }
        
        return integrations_status
    
    def _check_databases(self) -> Dict[str, Dict]:
        """
        Проверка доступности баз данных
        
        Returns:
            Dict[str, Dict]: Статус каждой базы данных
        """
        db_status = {}
        
        if self.database:
            try:
                # Проверка подключения к БД
                is_healthy = self._test_db_connection()
                db_status['main_db'] = {
                    'healthy': is_healthy,
                    'message': 'OK' if is_healthy else 'Ошибка подключения к БД',
                    'timestamp': datetime.now()
                }
            except Exception as e:
                db_status['main_db'] = {
                    'healthy': False,
                    'message': str(e),
                    'timestamp': datetime.now()
                }
        
        return db_status
    
    def _check_running_processes(self) -> Dict[str, Dict]:
        """
        Проверка работающих процессов
        
        Returns:
            Dict[str, Dict]: Статус каждого процесса
        """
        process_status = {}
        
        try:
            # Получаем список процессов агента
            agent_processes = self._get_agent_processes()
            
            for proc in agent_processes:
                try:
                    # Проверяем статус процесса
                    process_info = proc.as_dict(attrs=['pid', 'name', 'status', 'cpu_percent'])
                    is_healthy = process_info['status'] == 'running'
                    
                    process_status[f"process_{process_info['pid']}"] = {
                        'healthy': is_healthy,
                        'message': (
                            'OK' if is_healthy 
                            else f"Process {process_info['name']} is {process_info['status']}"
                        ),
                        'timestamp': datetime.now(),
                        'details': {
                            'name': process_info['name'],
                            'cpu_percent': process_info['cpu_percent']
                        }
                    }
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            logger.error(f"Error checking processes: {e}")
        
        return process_status
    
    def _should_attempt_recovery(self, system_name: str) -> bool:
        """
        Определяет, нужно ли пытаться восстановить систему
        
        Args:
            system_name (str): Название системы
            
        Returns:
            bool: True если нужно попытаться восстановить
        """
        attempts = self.recovery_attempts.get(system_name, 0)
        return attempts < self.max_recovery_attempts
    
    def _attempt_recovery(self, system_name: str, status: Dict):
        """
        Попытка восстановления системы
        
        Args:
            system_name (str): Название системы
            status (Dict): Текущий статус системы
        """
        logger.info(f"Attempting to recover system: {system_name}")
        
        # Увеличиваем счетчик попыток
        self.recovery_attempts[system_name] = self.recovery_attempts.get(system_name, 0) + 1
        
        try:
            recovered = False
            
            # Определяем тип системы и применяем соответствующую стратегию восстановления
            if 'process' in system_name:
                recovered = self._recover_process(system_name, status)
            elif system_name == 'main_db':
                recovered = self._recover_database()
            elif system_name == 'telegram_bot':
                recovered = self._recover_api_integration(self.telegram_bot)
            
            if recovered:
                logger.info(f"Successfully recovered system: {system_name}")
                self.recovery_attempts[system_name] = 0  # Сброс счетчика
            else:
                logger.warning(f"Failed to recover system: {system_name}")
                
        except Exception as e:
            logger.error(f"Error during recovery of {system_name}: {e}")
    
    def _escalate_issue(self, system_name: str, status: Dict):
        """
        Эскалация проблемы администратору
        
        Args:
            system_name (str): Название системы
            status (Dict): Статус системы
        """
        if self.telegram_bot:
            message = (
                f"🚨 Критическая ошибка!\n"
                f"Система: {system_name}\n"
                f"Статус: {status['message']}\n"
                f"Время: {status['timestamp']}\n"
                f"Попытки восстановления: {self.recovery_attempts.get(system_name, 0)}/{self.max_recovery_attempts}"
            )
            
            try:
                self.telegram_bot.send_message(
                    chat_id="admin_chat",  # ID чата администратора
                    text=message
                )
                logger.info(f"Escalated issue for system: {system_name}")
                
            except Exception as e:
                logger.error(f"Error sending escalation message: {e}")
    
    def _save_health_check_results(self, health_status: Dict[str, Dict]):
        """
        Сохранение результатов проверки
        
        Args:
            health_status (Dict[str, Dict]): Результаты проверки
        """
        if self.database:
            try:
                # Формируем запрос на сохранение
                query = """
                INSERT INTO health_check_results 
                (timestamp, status, healthy_count, total_count) 
                VALUES (:timestamp, :status, :healthy_count, :total_count)
                """
                
                healthy_count = sum(1 for status in health_status.values() if status['healthy'])
                total_count = len(health_status)
                
                self.database.execute(query, {
                    'timestamp': datetime.now(),
                    'status': health_status,
                    'healthy_count': healthy_count,
                    'total_count': total_count
                })
                
                logger.info("Health check results saved to database")
                
            except Exception as e:
                logger.error(f"Error saving health check results: {e}")
    
    def _send_status_report(self, health_status: Dict[str, Dict]):
        """
        Отправка отчета о статусе систем
        
        Args:
            health_status (Dict[str, Dict]): Статус всех систем
        """
        healthy_count = sum(1 for status in health_status.values() if status['healthy'])
        total_count = len(health_status)
        
        status_emoji = "✅" if healthy_count == total_count else "⚠️"
        
        message = (
            f"{status_emoji} Отчет о состоянии систем\n"
            f"Здоровых систем: {healthy_count}/{total_count}\n\n"
        )
        
        # Группируем системы по статусу
        healthy_systems = []
        unhealthy_systems = []
        
        for system_name, status in health_status.items():
            if status['healthy']:
                healthy_systems.append(f"🟢 {system_name}: OK")
            else:
                unhealthy_systems.append(
                    f"🔴 {system_name}: {status['message']}"
                )
        
        # Сначала выводим проблемные системы
        if unhealthy_systems:
            message += "Проблемные системы:\n"
            message += "\n".join(unhealthy_systems)
            message += "\n\n"
        
        # Затем здоровые системы
        if healthy_systems:
            message += "Здоровые системы:\n"
            message += "\n".join(healthy_systems)
        
        if self.telegram_bot:
            try:
                self.telegram_bot.send_message(
                    chat_id="monitoring_chat",  # ID чата мониторинга
                    text=message
                )
                logger.info("Status report sent successfully")
                
            except Exception as e:
                logger.error(f"Error sending status report: {e}")
    
    def _test_api_connection(self, api_client) -> bool:
        """
        Проверка подключения к API
        
        Args:
            api_client: Клиент API для проверки
            
        Returns:
            bool: True если API доступно
        """
        if not api_client:
            return False
            
        try:
            # Пытаемся выполнить тестовый запрос
            if hasattr(api_client, 'test_connection'):
                return api_client.test_connection()
            
            # Для Telegram бота проверяем метод send_message
            if hasattr(api_client, 'send_message'):
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"API connection test failed: {e}")
            return False
    
    def _test_db_connection(self) -> bool:
        """
        Проверка подключения к базе данных
        
        Returns:
            bool: True если БД доступна
        """
        if not self.database:
            return False
            
        try:
            # Выполняем простой запрос для проверки
            self.database.execute("SELECT 1")
            return True
            
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def _get_agent_processes(self) -> List:
        """
        Получение списка процессов агента
        
        Returns:
            List: Список процессов
        """
        agent_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if 'agent' in proc.info['name'].lower():
                    agent_processes.append(proc)
        except Exception as e:
            logger.error(f"Error getting agent processes: {e}")
        
        return agent_processes
    
    def _recover_process(self, process_name: str, status: Dict) -> bool:
        """
        Восстановление процесса
        
        Args:
            process_name (str): Имя процесса
            status (Dict): Статус процесса
            
        Returns:
            bool: True если восстановление успешно
        """
        try:
            pid = int(process_name.split('_')[1])
            process = psutil.Process(pid)
            
            if process.status() != 'running':
                process.resume()  # Пытаемся возобновить процесс
                
            return process.status() == 'running'
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, ValueError) as e:
            logger.error(f"Error recovering process: {e}")
            return False
    
    def _recover_database(self) -> bool:
        """
        Восстановление подключения к БД
        
        Returns:
            bool: True если восстановление успешно
        """
        try:
            # Пытаемся переподключиться к БД
            return self._test_db_connection()
            
        except Exception as e:
            logger.error(f"Error recovering database connection: {e}")
            return False
    
    def _recover_api_integration(self, api_client) -> bool:
        """
        Восстановление API интеграции
        
        Args:
            api_client: Клиент API для восстановления
            
        Returns:
            bool: True если восстановление успешно
        """
        try:
            # Пытаемся переподключиться к API
            return self._test_api_connection(api_client)
            
        except Exception as e:
            logger.error(f"Error recovering API integration: {e}")
            return False
