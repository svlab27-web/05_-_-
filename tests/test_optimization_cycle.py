import pytest
from datetime import datetime
from src.agents.agent_4.cycles.cycle_4_optimization import OptimizationCycle

@pytest.fixture
def mock_database():
    class MockDatabase:
        def __init__(self):
            self.data = {
                'daily_stats': {
                    'requests': {'total': 10, 'automated': 7, 'manual': 3},
                    'response_times': [3000, 4000, 3500],
                    'automation_rate': 0.7,
                    'success_rate': 0.95,
                    'time_saved': 7200
                }
            }
            
        def execute(self, query, params=None):
            pass
            
    return MockDatabase()

def test_format_report_message():
    cycle = OptimizationCycle()
    report = {
        'daily_dashboard': {
            'date': '2023-10-01',
            'metrics': {
                'total_requests': 10,
                'automation_rate': '70.0%',
                'avg_response_time': '1.0ч',
                'success_rate': '95.0%'
            },
            'kpi_status': {}
        },
        'roi_report': {
            'time_saved': 7200,
            'money_saved': 2000,
            'efficiency_increase': 30.5
        },
        'recommendations': [
            "Оптимизировать время ответа",
            "Увеличить уровень автоматизации"
        ]
    }
    
    message = cycle._format_report_message(report)
    assert 'Дневной отчет' in message
    assert '70.0%' in message
    assert '1.0ч' in message
    assert '95.0%' in message
    assert '2000 руб' in message
    assert '30.5%' in message
    assert 'Рекомендации' in message

def test_generate_reports(mock_database):
    cycle = OptimizationCycle(database=mock_database)
    daily_stats = {
        'requests': {'total': 10, 'automated': 7, 'manual': 3},
        'response_times': [3000, 4000, 3500],
        'automation_rate': 0.7,
        'success_rate': 0.95,
        'time_saved': 7200
    }
    
    learning_results = {
        'patterns': [],
        'improvements': [],
        'rules_updated': False
    }
    
    report = cycle._generate_reports(daily_stats, learning_results)
    assert 'daily_dashboard' in report
    assert 'roi_report' in report
    assert 'recommendations' in report
    assert isinstance(report['recommendations'], list)

if __name__ == '__main__':
    pytest.main([__file__])
