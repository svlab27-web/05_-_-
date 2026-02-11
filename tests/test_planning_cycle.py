"""
Тесты для цикла планирования
"""
import pytest
from datetime import datetime, timedelta
import pandas as pd
from src.agents.agent_4.cycles.cycle_5_planning import PlanningCycle

@pytest.fixture
def mock_task_manager():
    """Фикстура для мока системы управления задачами"""
    class MockTaskManager:
        def __init__(self):
            self.tasks = []
            
        def create_task(self, title, description, priority='medium'):
            task = {
                'id': len(self.tasks) + 1,
                'title': title,
                'description': description,
                'priority': priority,
                'created_at': datetime.now()
            }
            self.tasks.append(task)
            return task
            
        def get_tasks(self):
            return self.tasks
    
    return MockTaskManager()

@pytest.fixture
def sample_weekly_analysis():
    """Фикстура с тестовым недельным анализом"""
    return {
        'time_stats': {
            'total_time': 168000,  # 40 часов в секундах
            'by_category': {
                'development': 72000,
                'meetings': 36000,
                'support': 60000
            },
            'by_process': {
                'code_review': 28800,
                'bug_fixing': 43200,
                'documentation': 14400
            },
            'trends': {
                'increasing': ['meetings'],
                'decreasing': ['development']
            }
        },
        'automation_candidates': [
            {
                'name': 'Daily Reports',
                'frequency': 5,
                'time_cost': 1800,
                'complexity': 'easy'
            },
            {
                'name': 'Code Reviews',
                'frequency': 10,
                'time_cost': 3600,
                'complexity': 'medium'
            }
        ],
        'performance_metrics': {
            'total_tasks': 150,
            'avg_response_time': '2h',
            'automation_rate': 65,
            'success_rate': 0.92
        },
        'bottlenecks': [
            {
                'process': 'Code Review',
                'impact': 'high',
                'delay': '2d'
            }
        ]
    }

@pytest.fixture
def sample_automation_plan():
    """Фикстура с тестовым планом автоматизации"""
    return {
        'quick_wins': [
            {
                'name': 'Daily Reports Automation',
                'estimated_time': '4h',
                'expected_outcome': 'Автоматическая генерация отчетов',
                'metrics': ['Время на отчеты', 'Точность данных']
            }
        ],
        'medium_term': [
            {
                'name': 'Code Review Assistant',
                'estimated_time': '3d',
                'expected_outcome': 'Автоматическая проверка кода',
                'metrics': ['Время ревью', 'Количество найденных ошибок']
            }
        ],
        'long_term': [
            {
                'name': 'AI Support Bot',
                'estimated_time': '2w',
                'expected_outcome': 'Автоматизация поддержки',
                'metrics': ['Время ответа', 'Удовлетворенность']
            }
        ],
        'estimated_savings': {
            'time_per_week': 20,
            'money_per_month': 50000,
            'efficiency_gain': 15
        }
    }

def test_planning_cycle_initialization(mock_database, mock_telegram_bot, mock_task_manager):
    """Тест инициализации цикла планирования"""
    cycle = PlanningCycle(
        database=mock_database,
        telegram_bot=mock_telegram_bot,
        task_manager=mock_task_manager
    )
    
    assert cycle.name == "Planning Cycle"
    assert cycle.interval == 604800
    assert cycle.database == mock_database
    assert cycle.telegram_bot == mock_telegram_bot
    assert cycle.task_manager == mock_task_manager

def test_analyze_previous_week(mock_database, sample_weekly_analysis):
    """Тест анализа прошлой недели"""
    cycle = PlanningCycle(database=mock_database)
    
    # Подготавливаем тестовые данные
    mock_database.data['weekly_stats'] = sample_weekly_analysis
    
    # Анализируем неделю
    analysis = cycle._analyze_previous_week()
    
    assert 'time_stats' in analysis
    assert 'automation_candidates' in analysis
    assert 'performance_metrics' in analysis
    assert 'bottlenecks' in analysis

def test_plan_automations(sample_weekly_analysis):
    """Тест планирования автоматизаций"""
    cycle = PlanningCycle()
    
    plan = cycle._plan_automations(sample_weekly_analysis)
    
    assert 'quick_wins' in plan
    assert 'medium_term' in plan
    assert 'long_term' in plan
    assert 'estimated_savings' in plan

def test_create_tasks(mock_task_manager, sample_automation_plan):
    """Тест создания задач"""
    cycle = PlanningCycle(task_manager=mock_task_manager)
    
    tasks = cycle._create_tasks(sample_automation_plan)
    
    assert len(tasks) > 0
    for task in tasks:
        assert 'title' in task
        assert 'description' in task
        assert 'priority' in task

def test_prioritize_automation_candidates():
    """Тест приоритизации кандидатов на автоматизацию"""
    cycle = PlanningCycle()
    
    candidates = [
        {
            'name': 'Task 1',
            'frequency': 10,
            'time_cost': 1800,
            'complexity': 1
        },
        {
            'name': 'Task 2',
            'frequency': 5,
            'time_cost': 3600,
            'complexity': 2
        }
    ]
    
    prioritized = cycle._prioritize_automation_candidates(candidates)
    
    assert len(prioritized) == 2
    assert all('score' in task for task in prioritized)
    assert prioritized[0]['score'] >= prioritized[1]['score']

def test_categorize_by_complexity():
    """Тест категоризации задач по сложности"""
    cycle = PlanningCycle()
    
    tasks = [
        {'name': 'Task 1', 'complexity': 'easy'},
        {'name': 'Task 2', 'complexity': 'medium'},
        {'name': 'Task 3', 'complexity': 'hard'}
    ]
    
    categorized = cycle._categorize_by_complexity(tasks)
    
    assert len(categorized['quick_wins']) == 1
    assert len(categorized['medium_term']) == 1
    assert len(categorized['long_term']) == 1

def test_estimate_savings(sample_automation_plan):
    """Тест оценки потенциальной экономии"""
    cycle = PlanningCycle()
    
    savings = cycle._estimate_savings(sample_automation_plan)
    
    assert 'time_per_week' in savings
    assert 'money_per_month' in savings
    assert 'efficiency_gain' in savings
    assert isinstance(savings['time_per_week'], (int, float))
    assert isinstance(savings['money_per_month'], (int, float))
    assert isinstance(savings['efficiency_gain'], (int, float))

def test_prepare_task_data():
    """Тест подготовки данных задачи"""
    cycle = PlanningCycle()
    
    task = {
        'name': 'Test Task',
        'estimated_time': '4h',
        'expected_outcome': 'Expected result',
        'metrics': ['Metric 1', 'Metric 2']
    }
    
    task_data = cycle._prepare_task_data(task, priority='high')
    
    assert 'title' in task_data
    assert 'description' in task_data
    assert 'priority' in task_data
    assert task_data['priority'] == 'high'
    assert 'Test Task' in task_data['title']

def test_generate_task_description():
    """Тест генерации описания задачи"""
    cycle = PlanningCycle()
    
    task = {
        'name': 'Test Task',
        'current_process': 'Current process description',
        'problem': 'Problem description',
        'expected_outcome': 'Expected outcome',
        'metrics': ['Metric 1', 'Metric 2'],
        'estimated_time_saving': '10',
        'estimated_roi': '200%'
    }
    
    description = cycle._generate_task_description(task)
    
    assert 'Задача автоматизации' in description
    assert 'Текущий процесс' in description
    assert 'Проблема' in description
    assert 'Ожидаемый результат' in description
    assert 'Метрики успеха' in description
    assert 'Оценка экономии' in description

def test_format_weekly_plan(sample_weekly_analysis, sample_automation_plan):
    """Тест форматирования недельного плана"""
    cycle = PlanningCycle()
    
    tasks = [
        {
            'title': 'Task 1',
            'priority': 'high'
        },
        {
            'title': 'Task 2',
            'priority': 'medium'
        }
    ]
    
    message = cycle._format_weekly_plan(
        sample_weekly_analysis,
        sample_automation_plan,
        tasks
    )
    
    assert '📅 План автоматизации на неделю' in message
    assert 'Итоги прошлой недели' in message
    assert 'План на неделю' in message
    assert 'Quick Wins' in message
    assert 'Ожидаемая экономия' in message

def test_execute_full_cycle(
    mock_database,
    mock_telegram_bot,
    mock_task_manager,
    sample_weekly_analysis
):
    """Тест полного выполнения цикла"""
    cycle = PlanningCycle(
        database=mock_database,
        telegram_bot=mock_telegram_bot,
        task_manager=mock_task_manager
    )
    
    # Подготавливаем тестовые данные
    mock_database.data['weekly_stats'] = sample_weekly_analysis
    
    # Запускаем полный цикл
    cycle.execute()
    
    # Проверяем результаты
    assert len(mock_database.queries) > 0  # Были запросы к БД
    assert len(mock_telegram_bot.messages) > 0  # Были отправлены уведомления
    assert len(mock_task_manager.tasks) > 0  # Были созданы задачи

if __name__ == '__main__':
    pytest.main([__file__])
