"""
Тесты для цикла мониторинга заявок
"""
import pytest
from datetime import datetime, timedelta
from src.agents.agent_4.cycles.cycle_1_monitoring import MonitoringCycle

def test_monitoring_cycle_initialization(mock_telegram_bot, mock_database):
    """Тест инициализации цикла мониторинга"""
    cycle = MonitoringCycle(
        telegram_bot=mock_telegram_bot,
        database=mock_database
    )
    
    assert cycle.name == "Monitoring Cycle"
    assert cycle.interval == 600
    assert cycle.telegram_bot == mock_telegram_bot
    assert cycle.database == mock_database
    assert cycle.stuck_threshold == timedelta(hours=2)
    assert not cycle.is_running
    assert cycle.last_run is None
    assert cycle.error_count == 0

def test_check_new_requests(mock_database):
    """Тест проверки новых заявок"""
    cycle = MonitoringCycle(database=mock_database)
    
    # Подготавливаем тестовые данные
    test_requests = [
        {
            'id': 'REQ-001',
            'status': 'NEW',
            'source': 'telegram',
            'created_at': datetime.now()
        },
        {
            'id': 'REQ-002',
            'status': 'NEW',
            'source': 'email',
            'created_at': datetime.now()
        }
    ]
    
    # Добавляем заявки в мок БД
    mock_database.data['requests'] = test_requests
    
    # Проверяем получение новых заявок
    new_requests = cycle._check_new_requests()
    assert len(new_requests) == 2
    assert new_requests[0]['id'] == 'REQ-001'
    assert new_requests[1]['id'] == 'REQ-002'

def test_process_new_requests(mock_telegram_bot, mock_database):
    """Тест обработки новых заявок"""
    cycle = MonitoringCycle(
        telegram_bot=mock_telegram_bot,
        database=mock_database
    )
    
    # Подготавливаем тестовые заявки
    test_requests = [
        {
            'id': 'REQ-001',
            'status': 'NEW',
            'source': 'telegram'
        }
    ]
    
    # Обрабатываем заявки
    cycle._process_new_requests(test_requests)
    
    # Проверяем отправку уведомления
    last_message = mock_telegram_bot.get_last_message()
    assert last_message is not None
    assert 'REQ-001' in last_message['text']
    assert '🆕 Новая заявка!' in last_message['text']
    
    # Проверяем обновление статуса
    assert mock_database.get_last_query() is not None

def test_check_stuck_requests(mock_database):
    """Тест проверки застрявших заявок"""
    cycle = MonitoringCycle(database=mock_database)
    
    # Подготавливаем тестовые данные
    old_time = datetime.now() - timedelta(hours=3)
    test_requests = [
        {
            'id': 'REQ-001',
            'status': 'IN_PROGRESS',
            'assignee': 'operator1',
            'started_at': old_time,
            'time_in_progress': '3 hours'
        }
    ]
    
    # Добавляем заявки в мок БД
    mock_database.data['requests'] = test_requests
    
    # Проверяем получение застрявших заявок
    stuck_requests = cycle._check_stuck_requests()
    assert len(stuck_requests) == 1
    assert stuck_requests[0]['id'] == 'REQ-001'
    assert stuck_requests[0]['assignee'] == 'operator1'

def test_process_stuck_requests(mock_telegram_bot, mock_database):
    """Тест обработки застрявших заявок"""
    cycle = MonitoringCycle(
        telegram_bot=mock_telegram_bot,
        database=mock_database
    )
    
    # Подготавливаем тестовые заявки
    test_requests = [
        {
            'id': 'REQ-001',
            'status': 'IN_PROGRESS',
            'assignee': 'operator1',
            'time_in_progress': '3 hours'
        }
    ]
    
    # Обрабатываем заявки
    cycle._process_stuck_requests(test_requests)
    
    # Проверяем отправку уведомления
    last_message = mock_telegram_bot.get_last_message()
    assert last_message is not None
    assert 'REQ-001' in last_message['text']
    assert '⚠️ Застрявшая заявка!' in last_message['text']
    assert 'operator1' in last_message['text']
    
    # Проверяем обновление статуса
    assert mock_database.get_last_query() is not None

def test_update_request_status(mock_database):
    """Тест обновления статуса заявки"""
    cycle = MonitoringCycle(database=mock_database)
    
    test_request = {
        'id': 'REQ-001',
        'status': 'NEW'
    }
    
    # Обновляем статус
    cycle._update_request_status(test_request, "IN_PROGRESS")
    
    # Проверяем запрос к БД
    last_query = mock_database.get_last_query()
    assert last_query is not None
    assert 'REQ-001' in str(last_query['params'])
    assert 'IN_PROGRESS' in str(last_query['params'])

def test_send_notification(mock_telegram_bot):
    """Тест отправки уведомлений"""
    cycle = MonitoringCycle(telegram_bot=mock_telegram_bot)
    
    # Отправляем обычное уведомление
    test_message = "Test notification"
    cycle._send_notification(test_message)
    
    last_message = mock_telegram_bot.get_last_message()
    assert last_message is not None
    assert last_message['text'] == test_message
    
    # Отправляем срочное уведомление
    urgent_message = "Urgent notification"
    cycle._send_notification(urgent_message, is_urgent=True)
    
    last_message = mock_telegram_bot.get_last_message()
    assert last_message is not None
    assert last_message['text'] == urgent_message

def test_execute_full_cycle(mock_telegram_bot, mock_database):
    """Тест полного выполнения цикла мониторинга"""
    cycle = MonitoringCycle(
        telegram_bot=mock_telegram_bot,
        database=mock_database
    )
    
    # Подготавливаем тестовые данные
    old_time = datetime.now() - timedelta(hours=3)
    test_requests = [
        {
            'id': 'REQ-001',
            'status': 'NEW',
            'source': 'telegram',
            'created_at': datetime.now()
        },
        {
            'id': 'REQ-002',
            'status': 'IN_PROGRESS',
            'assignee': 'operator1',
            'started_at': old_time,
            'time_in_progress': '3 hours'
        }
    ]
    
    # Добавляем заявки в мок БД
    mock_database.data['requests'] = test_requests
    
    # Запускаем полный цикл
    cycle.execute()
    
    # Проверяем результаты
    messages = mock_telegram_bot.messages
    assert len(messages) >= 2  # Минимум 2 уведомления
    
    # Проверяем обновления в БД
    queries = mock_database.queries
    assert len(queries) >= 2  # Минимум 2 обновления статуса

if __name__ == '__main__':
    pytest.main([__file__])
