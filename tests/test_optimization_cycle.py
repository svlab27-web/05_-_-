"""
Тесты для цикла оптимизации
"""
import pytest
from datetime import datetime, timedelta
import pandas as pd
from src.agents.agent_4.cycles.cycle_4_optimization import OptimizationCycle

@pytest.fixture
def sample_daily_stats():
    """Фикстура с тестовой дневной статистикой"""
    return {
        'requests': {
            'total': 100,
            'automated': 75,
            'manual': 25
        },
        'response_times': [1800, 2400, 3000, 3600],  # в секундах
        'automation_rate': 0.75,
        'success_rate': 0.95,
        'time_saved': 7200,  # 2 часа в секундах
        'templates_used': [
            {'id': 1, 'name': 'greeting', 'uses': 30, 'success_rate': 0.9},
            {'id': 2, 'name': 'farewell', 'uses': 25, 'success_rate': 0.95}
        ]
    }

@pytest.fixture
def sample_learning_results():
    """Фикстура с тестовыми результатами обучения"""
    return {
        'patterns': [
            {
                'type': 'response_time',
                'condition': 'high_load',
                'avg_time': 3600,
                'frequency': 10
            },
            {
                'type': 'automation',
                'category': 'greeting',
                'success_rate': 0.95,
                'usage_count': 50
            }
        ],
        'improvements': [
            {
                'template_id': 1,
                'suggestion': 'Добавить вариации приветствия',
                'expected_improvement': 0.1
            }
        ],
        'rules_updated': True
    }

def test_optimization_cycle_initialization(mock_database, mock_telegram_bot):
    """Тест инициализации цикла оптимизации"""
    cycle = OptimizationCycle(
        database=mock_database,
        telegram_bot=mock_telegram_bot
    )
    
    assert cycle.name == "Optimization Cycle"
    assert cycle.interval == 86400
    assert cycle.database == mock_database
    assert cycle.telegram_bot == mock_telegram_bot
    assert isinstance(cycle.kpi_targets, dict)
    assert 'response_time' in cycle.kpi_targets
    assert 'automation_rate' in cycle.kpi_targets
    assert 'success_rate' in cycle.kpi_targets

def test_analyze_daily_work(mock_database, sample_daily_stats):
    """Тест анализа дневной работы"""
    cycle = OptimizationCycle(database=mock_database)
    
    # Подготавливаем тестовые данные
    mock_database.data['daily_stats'] = sample_daily_stats
    
    # Анализируем работу
    stats = cycle._analyze_daily_work()
    
    assert 'requests' in stats
    assert 'automation_rate' in stats
    assert 'success_rate' in stats
    assert 'kpi_comparison' in stats
    assert stats['automation_rate'] == 0.75
    assert stats['success_rate'] == 0.95

def test_perform_machine_learning(sample_daily_stats):
    """Тест выполнения машинного обучения"""
    cycle = OptimizationCycle()
    
    results = cycle._perform_machine_learning(sample_daily_stats)
    
    assert 'patterns' in results
    assert 'improvements' in results
    assert 'rules_updated' in results
    assert isinstance(results['patterns'], list)
    assert isinstance(results['improvements'], list)
    assert isinstance(results['rules_updated'], bool)

def test_generate_reports(sample_daily_stats, sample_learning_results):
    """Тест генерации отчетов"""
    cycle = OptimizationCycle()
    
    reports = cycle._generate_reports(sample_daily_stats, sample_learning_results)
    
    assert 'daily_dashboard' in reports
    assert 'roi_report' in reports
    assert 'recommendations' in reports
    
    dashboard = reports['daily_dashboard']
    assert 'date' in dashboard
    assert 'metrics' in dashboard
    assert 'kpi_status' in dashboard

def test_compare_with_kpi(sample_daily_stats):
    """Тест сравнения с KPI"""
    cycle = OptimizationCycle()
    
    comparison = cycle._compare_with_kpi(sample_daily_stats)
    
    for metric in ['response_time', 'automation_rate', 'success_rate']:
        assert metric in comparison
        assert 'target' in comparison[metric]
        assert 'current' in comparison[metric]
        assert 'achieved' in comparison[metric]
        assert 'difference' in comparison[metric]

def test_analyze_patterns(sample_daily_stats):
    """Тест анализа паттернов"""
    cycle = OptimizationCycle()
    
    patterns = cycle._analyze_patterns(sample_daily_stats)
    
    assert isinstance(patterns, list)
    for pattern in patterns:
        assert isinstance(pattern, dict)
        assert 'type' in pattern

def test_improve_response_templates(sample_daily_stats):
    """Тест улучшения шаблонов ответов"""
    cycle = OptimizationCycle()
    
    improvements = cycle._improve_response_templates(sample_daily_stats)
    
    assert isinstance(improvements, list)
    for improvement in improvements:
        assert isinstance(improvement, dict)
        assert 'template_id' in improvement
        assert 'suggestion' in improvement

def test_calculate_roi(sample_daily_stats):
    """Тест расчета ROI"""
    cycle = OptimizationCycle()
    
    roi = cycle._calculate_roi(sample_daily_stats)
    
    assert 'time_saved' in roi
    assert 'money_saved' in roi
    assert 'efficiency_increase' in roi
    assert isinstance(roi['time_saved'], (int, float))
    assert isinstance(roi['money_saved'], (int, float))
    assert isinstance(roi['efficiency_increase'], (int, float))

def test_generate_recommendations(sample_daily_stats, sample_learning_results):
    """Тест генерации рекомендаций"""
    cycle = OptimizationCycle()
    
    recommendations = cycle._generate_recommendations(
        sample_daily_stats,
        sample_learning_results
    )
    
    assert isinstance(recommendations, list)
    assert len(recommendations) > 0
    for rec in recommendations:
        assert isinstance(rec, str)

def test_format_report_message():
    """Тест форматирования отчета"""
    cycle = OptimizationCycle()
    
    report = {
        'daily_dashboard': {
            'date': '2024-01-01',
            'metrics': {
                'total_requests': 100,
                'automation_rate': '75%',
                'avg_response_time': '30м',
                'success_rate': '95%'
            }
        },
        'recommendations': [
            'Увеличить автоматизацию',
            'Улучшить шаблоны'
        ]
    }
    
    message = cycle._format_report_message(report)
    
    assert '📊 Дневной отчет' in message
    assert 'Основные метрики:' in message
    assert '🎯 Рекомендации на завтра:' in message
    assert 'Увеличить автоматизацию' in message

def test_format_duration():
    """Тест форматирования длительности"""
    cycle = OptimizationCycle()
    
    assert cycle._format_duration(30) == '30с'
    assert cycle._format_duration(90) == '1.5м'
    assert cycle._format_duration(3600) == '1.0ч'
    assert cycle._format_duration(5400) == '1.5ч'

def test_execute_full_cycle(mock_database, mock_telegram_bot, sample_daily_stats):
    """Тест полного выполнения цикла"""
    cycle = OptimizationCycle(
        database=mock_database,
        telegram_bot=mock_telegram_bot
    )
    
    # Подготавливаем тестовые данные
    mock_database.data['daily_stats'] = sample_daily_stats
    
    # Запускаем полный цикл
    cycle.execute()
    
    # Проверяем результаты
    assert len(mock_database.queries) > 0  # Были запросы к БД
    assert len(mock_telegram_bot.messages) > 0  # Были отправлены уведомления

if __name__ == '__main__':
    pytest.main([__file__])
