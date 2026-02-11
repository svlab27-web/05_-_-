"""
Конфигурация pytest и общие фикстуры для тестов
"""
import os
import pytest
import logging
from datetime import datetime
from typing import Dict, Optional

# Настройка базового логирования для тестов
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@pytest.fixture
def mock_config() -> Dict:
    """
    Фикстура с тестовой конфигурацией
    """
    return {
        'cycles': {
            'monitoring': 600,
            'time_audit': 3600,
            'healthcheck': 1800,
            'optimization': 86400,
            'planning': 604800
        },
        'thresholds': {
            'stuck_request_time': 7200,
            'critical_response_time': 3600,
            'high_load_threshold': 100
        },
        'kpi': {
            'response_time': 3600,
            'automation_rate': 0.7,
            'success_rate': 0.95,
            'time_saving': 20
        },
        'notifications': {
            'enable_telegram': True,
            'enable_email': True,
            'urgent_retry_count': 3
        },
        'paths': {
            'logs_dir': 'tests/data/logs',
            'db_dir': 'tests/data/databases',
            'temp_dir': 'tests/data/temp'
        }
    }

@pytest.fixture
def mock_telegram_bot():
    """
    Фикстура, имитирующая Telegram бота
    """
    class MockTelegramBot:
        def __init__(self):
            self.messages = []
        
        def send_message(self, chat_id: str, text: str):
            self.messages.append({
                'chat_id': chat_id,
                'text': text,
                'timestamp': datetime.now()
            })
            
        def get_last_message(self) -> Optional[Dict]:
            return self.messages[-1] if self.messages else None
    
    return MockTelegramBot()

@pytest.fixture
def mock_database():
    """
    Фикстура, имитирующая базу данных
    """
    class MockDatabase:
        def __init__(self):
            self.data = {}
            self.queries = []
        
        def execute(self, query: str, params: Dict = None):
            self.queries.append({
                'query': query,
                'params': params,
                'timestamp': datetime.now()
            })
            
        def get_data(self, key: str) -> Optional[Dict]:
            return self.data.get(key)
        
        def set_data(self, key: str, value: Dict):
            self.data[key] = value
            
        def get_last_query(self) -> Optional[Dict]:
            return self.queries[-1] if self.queries else None
    
    return MockDatabase()

@pytest.fixture
def mock_task_manager():
    """
    Фикстура, имитирующая систему управления задачами
    """
    class MockTaskManager:
        def __init__(self):
            self.tasks = []
        
        def create_task(self, title: str, description: str, priority: str = 'medium'):
            task = {
                'id': len(self.tasks) + 1,
                'title': title,
                'description': description,
                'priority': priority,
                'status': 'new',
                'created_at': datetime.now()
            }
            self.tasks.append(task)
            return task
        
        def get_task(self, task_id: int) -> Optional[Dict]:
            for task in self.tasks:
                if task['id'] == task_id:
                    return task
            return None
        
        def update_task(self, task_id: int, status: str):
            task = self.get_task(task_id)
            if task:
                task['status'] = status
                task['updated_at'] = datetime.now()
    
    return MockTaskManager()

@pytest.fixture(autouse=True)
def setup_test_environment(tmp_path):
    """
    Фикстура для настройки тестового окружения
    Создает временные директории для тестов
    """
    # Создаем временные директории
    test_dirs = ['logs', 'databases', 'temp']
    for dir_name in test_dirs:
        os.makedirs(tmp_path / dir_name, exist_ok=True)
    
    # Устанавливаем переменные окружения для тестов
    os.environ['TEST_MODE'] = 'true'
    os.environ['TEST_DATA_DIR'] = str(tmp_path)
    
    yield
    
    # Очистка после тестов
    os.environ.pop('TEST_MODE', None)
    os.environ.pop('TEST_DATA_DIR', None)

@pytest.fixture
def sample_request_data() -> Dict:
    """
    Фикстура с тестовыми данными заявки
    """
    return {
        'id': 'REQ-001',
        'title': 'Test Request',
        'description': 'This is a test request',
        'status': 'new',
        'priority': 'medium',
        'created_at': datetime.now(),
        'source': 'telegram',
        'assignee': None,
        'time_spent': 0
    }

@pytest.fixture
def sample_metrics_data() -> Dict:
    """
    Фикстура с тестовыми метриками
    """
    return {
        'response_times': [120, 180, 240, 300],  # в секундах
        'automation_rate': 0.75,
        'success_rate': 0.95,
        'processed_requests': 100,
        'automated_requests': 75,
        'errors': 5,
        'time_saved': 120  # в минутах
    }

def pytest_configure(config):
    """
    Конфигурация pytest
    """
    # Добавляем пользовательские маркеры
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )

def pytest_collection_modifyitems(config, items):
    """
    Модификация тестовых item'ов
    Пропускает медленные тесты если не указан флаг --runslow
    """
    if not config.getoption("--runslow"):
        skip_slow = pytest.mark.skip(reason="need --runslow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)

def pytest_addoption(parser):
    """
    Добавление пользовательских опций pytest
    """
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests"
    )
