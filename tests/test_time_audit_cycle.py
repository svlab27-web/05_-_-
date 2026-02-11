"""
Тесты для цикла аудита времени
"""
import pytest
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from src.agents.agent_4.cycles.cycle_2_time_audit import TimeAuditCycle

@pytest.fixture
def mock_calendar_client():
    """Фикстура для мока календаря"""
    class MockCalendarClient:
        def __init__(self):
            self.events = []
            
        def get_events(self, start_date, end_date):
            return [
                event for event in self.events
                if start_date <= event['start'] <= end_date
            ]
            
        def add_test_event(self, event):
            self.events.append(event)
    
    return MockCalendarClient()

@pytest.fixture
def sample_time_data():
    """Фикстура с тестовыми данными о времени"""
    return {
        'calendar_events': [
            {
                'id': 'evt1',
                'title': 'Daily Standup',
                'start': datetime.now(),
                'duration': timedelta(minutes=15)
            }
        ],
        'task_durations': [
            {
                'task_id': 'TSK-001',
                'title': 'Code Review',
                'duration': 45,  # минуты
                'planned_duration': 30,
                'category': 'Development',
                'date': datetime.now().date()
            },
            {
                'task_id': 'TSK-002',
                'title': 'Bug Fix',
                'duration': 120,
                'planned_duration': 60,
                'category': 'Development',
                'date': datetime.now().date()
            }
        ],
        'activity_logs': [
            {
                'timestamp': datetime.now(),
                'activity': 'Code Review',
                'duration': 45
            }
        ]
    }

def test_time_audit_cycle_initialization(mock_calendar_client, mock_database):
    """Тест инициализации цикла аудита времени"""
    cycle = TimeAuditCycle(
        calendar_client=mock_calendar_client,
        database=mock_database
    )
    
    assert cycle.name == "Time Audit Cycle"
    assert cycle.interval == 3600
    assert cycle.calendar_client == mock_calendar_client
    assert cycle.database == mock_database
    assert isinstance(cycle.time_data, list)

def test_collect_time_data(mock_calendar_client, mock_database, sample_time_data):
    """Тест сбора данных о времени"""
    cycle = TimeAuditCycle(
        calendar_client=mock_calendar_client,
        database=mock_database
    )
    
    # Подготавливаем тестовые данные
    mock_database.data['tasks'] = sample_time_data['task_durations']
    for event in sample_time_data['calendar_events']:
        mock_calendar_client.add_test_event(event)
    
    # Собираем данные
    time_data = cycle._collect_time_data()
    
    assert 'calendar_events' in time_data
    assert 'task_durations' in time_data
    assert 'activity_logs' in time_data
    assert len(time_data['calendar_events']) > 0
    assert len(time_data['task_durations']) > 0

def test_analyze_patterns(mock_calendar_client, mock_database, sample_time_data):
    """Тест анализа паттернов времени"""
    cycle = TimeAuditCycle(
        calendar_client=mock_calendar_client,
        database=mock_database
    )
    
    patterns = cycle._analyze_patterns(sample_time_data)
    
    assert 'time_wasters' in patterns
    assert 'automation_candidates' in patterns
    assert 'weekly_comparison' in patterns

def test_generate_insights(mock_calendar_client, mock_database):
    """Тест генерации инсайтов"""
    cycle = TimeAuditCycle(
        calendar_client=mock_calendar_client,
        database=mock_database
    )
    
    patterns = {
        'time_wasters': [
            {
                'task_id': 'TSK-001',
                'excess_time': 45,
                'frequency': 'daily'
            }
        ],
        'automation_candidates': [
            {
                'task_id': 'TSK-002',
                'repetition_count': 5,
                'avg_duration': 30
            }
        ],
        'weekly_comparison': {
            'total_time': '+10%',
            'efficiency': '-5%'
        }
    }
    
    insights = cycle._generate_insights(patterns)
    
    assert 'top_time_wasters' in insights
    assert 'optimization_suggestions' in insights
    assert 'potential_time_savings' in insights
    assert isinstance(insights['potential_time_savings'], (int, float))

def test_find_time_wasters():
    """Тест поиска пожирателей времени"""
    cycle = TimeAuditCycle()
    
    # Создаем тестовый DataFrame
    data = {
        'task_id': ['TSK-001', 'TSK-002', 'TSK-003'],
        'duration': [120, 60, 30],
        'planned_duration': [60, 60, 30],
        'title': ['Long Task', 'Normal Task', 'Quick Task']
    }
    df = pd.DataFrame(data)
    
    time_wasters = cycle._find_time_wasters(df)
    
    assert len(time_wasters) > 0
    assert time_wasters[0]['task_id'] == 'TSK-001'
    assert time_wasters[0]['excess_time'] == 60

def test_find_automation_candidates():
    """Тест поиска кандидатов на автоматизацию"""
    cycle = TimeAuditCycle()
    
    # Создаем тестовый DataFrame с повторяющимися задачами
    data = {
        'task_id': ['TSK-001', 'TSK-001', 'TSK-001', 'TSK-002'],
        'title': ['Daily Report', 'Daily Report', 'Daily Report', 'Unique Task'],
        'duration': [30, 30, 30, 45]
    }
    df = pd.DataFrame(data)
    
    candidates = cycle._find_automation_candidates(df)
    
    assert len(candidates) > 0
    assert candidates[0]['task_id'] == 'TSK-001'
    assert candidates[0]['repetition_count'] == 3

def test_compare_with_previous_week():
    """Тест сравнения с предыдущей неделей"""
    cycle = TimeAuditCycle()
    
    # Создаем тестовые данные для двух недель
    current_week = pd.DataFrame({
        'date': [datetime.now().date()] * 3,
        'duration': [60, 45, 30]
    })
    
    previous_week = pd.DataFrame({
        'date': [(datetime.now() - timedelta(days=7)).date()] * 3,
        'duration': [50, 40, 25]
    })
    
    # Объединяем данные
    df = pd.concat([current_week, previous_week])
    
    comparison = cycle._compare_with_previous_week(df)
    
    assert 'total_time_change' in comparison
    assert 'efficiency_change' in comparison
    assert isinstance(comparison['total_time_change'], (int, float))

def test_save_results(mock_database, sample_time_data):
    """Тест сохранения результатов"""
    cycle = TimeAuditCycle(database=mock_database)
    
    patterns = {
        'time_wasters': [{'task_id': 'TSK-001', 'excess_time': 45}],
        'automation_candidates': [{'task_id': 'TSK-002', 'repetition_count': 3}],
        'weekly_comparison': {'total_time_change': 10}
    }
    
    insights = {
        'top_time_wasters': [{'task_id': 'TSK-001'}],
        'optimization_suggestions': ['Автоматизировать ежедневные отчеты'],
        'potential_time_savings': 120
    }
    
    cycle._save_results(sample_time_data, patterns, insights)
    
    # Проверяем, что данные были сохранены в БД
    assert len(mock_database.queries) > 0
    last_query = mock_database.get_last_query()
    assert last_query is not None

def test_execute_full_cycle(mock_calendar_client, mock_database, sample_time_data):
    """Тест полного выполнения цикла"""
    cycle = TimeAuditCycle(
        calendar_client=mock_calendar_client,
        database=mock_database
    )
    
    # Подготавливаем тестовые данные
    mock_database.data['tasks'] = sample_time_data['task_durations']
    for event in sample_time_data['calendar_events']:
        mock_calendar_client.add_test_event(event)
    
    # Запускаем полный цикл
    cycle.execute()
    
    # Проверяем, что данные были обработаны и сохранены
    assert len(mock_database.queries) > 0
    assert cycle.last_run is not None

if __name__ == '__main__':
    pytest.main([__file__])
