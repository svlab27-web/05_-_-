"""
Конфигурация Агента 4
"""
from typing import Dict

# Интервалы выполнения циклов (в секундах)
CYCLE_INTERVALS = {
    'monitoring': 600,     # 10 минут
    'time_audit': 3600,    # 1 час
    'healthcheck': 1800,   # 30 минут
    'optimization': 86400, # 24 часа
    'planning': 604800     # 1 неделя
}

# Пороговые значения для мониторинга
MONITORING_THRESHOLDS = {
    'stuck_request_time': 7200,  # 2 часа для "застрявших" заявок
    'critical_response_time': 3600,  # 1 час максимального времени ответа
    'high_load_threshold': 100  # количество заявок для высокой нагрузки
}

# Настройки KPI
KPI_TARGETS = {
    'response_time': 3600,  # среднее время ответа - 1 час
    'automation_rate': 0.7,  # уровень автоматизации - 70%
    'success_rate': 0.95,   # успешность обработки - 95%
    'time_saving': 20       # целевая экономия времени в часах в неделю
}

# Настройки уведомлений
NOTIFICATION_SETTINGS = {
    'enable_telegram': True,
    'enable_email': True,
    'urgent_retry_count': 3,
    'notification_levels': ['info', 'warning', 'error', 'critical']
}

# Настройки восстановления
RECOVERY_SETTINGS = {
    'max_retry_attempts': 3,
    'retry_delay': 300,  # 5 минут между попытками
    'backup_systems': ['secondary_db', 'failover_api']
}

# Пути к важным файлам и директориям
PATHS = {
    'logs_dir': 'data/logs',
    'db_dir': 'data/databases',
    'temp_dir': 'data/temp',
    'reports_dir': 'data/reports'
}

# Настройки логирования
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_rotation': '1 day',
    'max_log_files': 30
}

# Интеграции
INTEGRATIONS = {
    'telegram': {
        'enabled': True,
        'token': None,  # Будет загружен из переменных окружения
        'admin_chat_id': None  # Будет загружен из переменных окружения
    },
    'email': {
        'enabled': True,
        'smtp_host': None,
        'smtp_port': 587,
        'username': None,
        'password': None
    },
    'calendar': {
        'enabled': True,
        'type': 'google',  # или 'outlook'
        'credentials_file': 'config/calendar_credentials.json'
    },
    'task_manager': {
        'enabled': True,
        'type': 'jira',  # или 'trello', 'asana'
        'api_key': None,
        'project_key': None
    }
}

def load_config() -> Dict:
    """
    Загрузка конфигурации с учетом переменных окружения
    
    Returns:
        Dict: Полная конфигурация агента
    """
    import os
    from dotenv import load_dotenv
    
    # Загрузка переменных окружения из .env файла
    load_dotenv()
    
    config = {
        'cycles': CYCLE_INTERVALS,
        'thresholds': MONITORING_THRESHOLDS,
        'kpi': KPI_TARGETS,
        'notifications': NOTIFICATION_SETTINGS,
        'recovery': RECOVERY_SETTINGS,
        'paths': PATHS,
        'logging': LOGGING_CONFIG,
        'integrations': INTEGRATIONS
    }
    
    # Загрузка секретных данных из переменных окружения
    config['integrations']['telegram']['token'] = os.getenv('TELEGRAM_BOT_TOKEN')
    config['integrations']['telegram']['admin_chat_id'] = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
    config['integrations']['email']['smtp_host'] = os.getenv('EMAIL_SMTP_HOST')
    config['integrations']['email']['username'] = os.getenv('EMAIL_USERNAME')
    config['integrations']['email']['password'] = os.getenv('EMAIL_PASSWORD')
    config['integrations']['task_manager']['api_key'] = os.getenv('TASK_MANAGER_API_KEY')
    
    return config

def validate_config(config: Dict) -> bool:
    """
    Проверка корректности конфигурации
    
    Args:
        config (Dict): Конфигурация для проверки
        
    Returns:
        bool: True если конфигурация валидна
        
    Raises:
        ValueError: Если найдены ошибки в конфигурации
    """
    # Проверка обязательных параметров
    required_sections = ['cycles', 'thresholds', 'kpi', 'notifications', 'paths']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required config section: {section}")
    
    # Проверка интервалов циклов
    for cycle, interval in config['cycles'].items():
        if not isinstance(interval, int) or interval <= 0:
            raise ValueError(f"Invalid interval for cycle {cycle}: {interval}")
    
    # Проверка порогов
    for threshold, value in config['thresholds'].items():
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"Invalid threshold value for {threshold}: {value}")
    
    # Проверка KPI
    for kpi, value in config['kpi'].items():
        if not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"Invalid KPI value for {kpi}: {value}")
    
    return True
