"""
Тесты для цикла проверки здоровья систем
"""
import pytest
from datetime import datetime
from src.agents.agent_4.cycles.cycle_3_healthcheck import HealthCheckCycle

@pytest.fixture
def mock_api_client():
    """Фикстура для мока API клиента"""
    class MockApiClient:
        def __init__(self):
            self.is_healthy = True
            self.error_message = None
            
        def set_health(self, is_healthy: bool, error_message: str = None):
            self.is_healthy = is_healthy
            self.error_message = error_message
            
        def test_connection(self):
            if not self.is_healthy:
                raise Exception(self.error_message or "API недоступен")
            return True
    
    return MockApiClient()

def test_healthcheck_cycle_initialization(mock_telegram_bot, mock_database):
    """Тест инициализации цикла проверки здоровья"""
    cycle = HealthCheckCycle(
        telegram_bot=mock_telegram_bot,
        database=mock_database
    )
    
    assert cycle.name == "Health Check Cycle"
    assert cycle.interval == 1800
    assert cycle.telegram_bot == mock_telegram_bot
    assert cycle.database == mock_database
    assert isinstance(cycle.recovery_attempts, dict)
    assert cycle.max_recovery_attempts == 3

def test_check_api_integrations(mock_telegram_bot, mock_api_client):
    """Тест проверки API интеграций"""
    cycle = HealthCheckCycle(telegram_bot=mock_telegram_bot)
    
    # Проверка здоровой системы
    mock_api_client.set_health(True)
    status = cycle._check_api_integrations()
    
    assert 'telegram_bot' in status
    assert status['telegram_bot']['healthy']
    assert status['telegram_bot']['message'] == 'OK'
    
    # Проверка нездоровой системы
    mock_api_client.set_health(False, "Connection timeout")
    status = cycle._check_api_integrations()
    
    assert 'telegram_bot' in status
    assert not status['telegram_bot']['healthy']
    assert "Connection timeout" in status['telegram_bot']['message']

def test_check_databases(mock_database):
    """Тест проверки баз данных"""
    cycle = HealthCheckCycle(database=mock_database)
    
    # Проверка работающей БД
    status = cycle._check_databases()
    
    assert 'main_db' in status
    assert status['main_db']['healthy']
    assert status['main_db']['message'] == 'OK'
    
    # Проверка с ошибкой БД
    mock_database.execute = lambda *args: exec('raise Exception("DB Error")')
    status = cycle._check_databases()
    
    assert 'main_db' in status
    assert not status['main_db']['healthy']
    assert "DB Error" in status['main_db']['message']

def test_check_running_processes():
    """Тест проверки запущенных процессов"""
    cycle = HealthCheckCycle()
    
    status = cycle._check_running_processes()
    assert isinstance(status, dict)

def test_should_attempt_recovery():
    """Тест логики попыток восстановления"""
    cycle = HealthCheckCycle()
    
    # Первая попытка
    assert cycle._should_attempt_recovery('test_system')
    
    # Увеличиваем счетчик попыток
    cycle.recovery_attempts['test_system'] = 2
    assert cycle._should_attempt_recovery('test_system')
    
    # Превышаем лимит попыток
    cycle.recovery_attempts['test_system'] = 3
    assert not cycle._should_attempt_recovery('test_system')

def test_attempt_recovery():
    """Тест попытки восстановления системы"""
    cycle = HealthCheckCycle()
    
    system_name = 'test_system'
    status = {
        'healthy': False,
        'message': 'System down',
        'timestamp': datetime.now()
    }
    
    # Первая попытка восстановления
    cycle._attempt_recovery(system_name, status)
    assert cycle.recovery_attempts[system_name] == 1
    
    # Вторая попытка
    cycle._attempt_recovery(system_name, status)
    assert cycle.recovery_attempts[system_name] == 2

def test_escalate_issue(mock_telegram_bot):
    """Тест эскалации проблемы"""
    cycle = HealthCheckCycle(telegram_bot=mock_telegram_bot)
    
    system_name = 'critical_system'
    status = {
        'healthy': False,
        'message': 'Critical error',
        'timestamp': datetime.now()
    }
    
    # Эскалация проблемы
    cycle._escalate_issue(system_name, status)
    
    # Проверяем отправку уведомления
    last_message = mock_telegram_bot.get_last_message()
    assert last_message is not None
    assert '🚨 Критическая ошибка!' in last_message['text']
    assert system_name in last_message['text']

def test_save_health_check_results(mock_database):
    """Тест сохранения результатов проверки"""
    cycle = HealthCheckCycle(database=mock_database)
    
    health_status = {
        'system1': {
            'healthy': True,
            'message': 'OK',
            'timestamp': datetime.now()
        },
        'system2': {
            'healthy': False,
            'message': 'Error',
            'timestamp': datetime.now()
        }
    }
    
    cycle._save_health_check_results(health_status)
    
    # Проверяем сохранение в БД
    last_query = mock_database.get_last_query()
    assert last_query is not None

def test_send_status_report(mock_telegram_bot):
    """Тест отправки отчета о статусе"""
    cycle = HealthCheckCycle(telegram_bot=mock_telegram_bot)
    
    health_status = {
        'system1': {
            'healthy': True,
            'message': 'OK',
            'timestamp': datetime.now()
        },
        'system2': {
            'healthy': False,
            'message': 'Error',
            'timestamp': datetime.now()
        }
    }
    
    cycle._send_status_report(health_status)
    
    # Проверяем отправку отчета
    last_message = mock_telegram_bot.get_last_message()
    assert last_message is not None
    assert 'Отчет о состоянии систем' in last_message['text']
    assert 'Здоровых систем: 1/2' in last_message['text']

def test_execute_full_cycle(mock_telegram_bot, mock_database, mock_api_client):
    """Тест полного выполнения цикла"""
    cycle = HealthCheckCycle(
        telegram_bot=mock_telegram_bot,
        database=mock_database
    )
    
    # Настраиваем состояние систем
    mock_api_client.set_health(True)
    
    # Запускаем полный цикл
    cycle.execute()
    
    # Проверяем результаты
    assert len(mock_database.queries) > 0  # Были запросы к БД
    assert len(mock_telegram_bot.messages) > 0  # Были отправлены уведомления

def test_handle_failures():
    """Тест обработки сбоев"""
    cycle = HealthCheckCycle()
    
    health_status = {
        'system1': {
            'healthy': False,
            'message': 'Error 1',
            'timestamp': datetime.now()
        },
        'system2': {
            'healthy': True,
            'message': 'OK',
            'timestamp': datetime.now()
        },
        'system3': {
            'healthy': False,
            'message': 'Error 2',
            'timestamp': datetime.now()
        }
    }
    
    # Обрабатываем сбои
    cycle._handle_failures(health_status)
    
    # Проверяем попытки восстановления
    assert 'system1' in cycle.recovery_attempts
    assert 'system3' in cycle.recovery_attempts
    assert 'system2' not in cycle.recovery_attempts

if __name__ == '__main__':
    pytest.main([__file__])
