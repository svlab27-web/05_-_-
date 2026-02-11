import pytest
from datetime import datetime, timedelta
from src.agents.agent_4.cycles.cycle_1_monitoring import MonitoringCycle

@pytest.fixture
def mock_alert_system():
    class MockAlertSystem:
        def __init__(self):
            self.last_alert = None
            
        def send_alert(self, message):
            self.last_alert = {
                'text': message,
                'timestamp': datetime.now()
            }
            
    return MockAlertSystem()

def test_monitoring_cycle_initialization():
    cycle = MonitoringCycle()
    assert cycle.name == "Monitoring Cycle"
    assert cycle.interval == 300
    assert isinstance(cycle.thresholds, dict)

def test_check_metrics():
    cycle = MonitoringCycle()
    metrics = {
        'cpu': 75,
        'memory': 85,
        'disk': 90
    }
    
    status = cycle._check_metrics(metrics)
    
    assert 'cpu' in status
    assert 'memory' in status
    assert 'disk' in status
    assert status['cpu']['value'] == 75
    assert status['memory']['value'] == 85
    assert status['disk']['value'] == 90

def test_detect_anomalies():
    cycle = MonitoringCycle()
    metrics = {
        'cpu': 95,
        'memory': 98,
        'disk': 99
    }
    
    anomalies = cycle._detect_anomalies(metrics)
    
    assert len(anomalies) == 3
    assert all(a['critical'] for a in anomalies)

def test_generate_alert_message():
    cycle = MonitoringCycle()
    anomaly = {
        'metric': 'cpu',
        'value': 95,
        'threshold': 90,
        'critical': True
    }
    
    message = cycle._generate_alert_message(anomaly)
    assert "🔴 СРОЧНО! Превышение порога CPU: 95% (порог: 90%)" in message

def test_send_notification(mock_alert_system):
    cycle = MonitoringCycle(alert_system=mock_alert_system)
    alert = {
        'metric': 'memory',
        'value': 98,
        'threshold': 90,
        'critical': True
    }
    
    cycle._send_notification(alert)
    assert mock_alert_system.last_alert is not None
    assert "🔴 СРОЧНО! Превышение порога памяти" in mock_alert_system.last_alert['text']

def test_save_monitoring_data():
    cycle = MonitoringCycle()
    metrics = {
        'cpu': 75,
        'memory': 85
    }
    
    result = cycle._save_monitoring_data(metrics)
    assert result is True

def test_execute_full_cycle(mock_alert_system):
    cycle = MonitoringCycle(alert_system=mock_alert_system)
    cycle.metrics_provider = lambda: {
        'cpu': 95,
        'memory': 98
    }
    
    cycle.execute()
    
    assert mock_alert_system.last_alert is not None
    assert "🔴 СРОЧНО!" in mock_alert_system.last_alert['text']

if __name__ == '__main__':
    pytest.main([__file__])
