"""
Тесты для базового класса HD циклов
"""
import pytest
from datetime import datetime
import time
from src.agents.agent_4.cycles.base_cycle import BaseCycle

class TestCycle(BaseCycle):
    """Тестовый цикл для проверки базового функционала"""
    def __init__(self, name="Test Cycle", interval=1):
        super().__init__(name=name, interval=interval)
        self.execute_count = 0
        
    def execute(self):
        """Тестовая реализация метода execute"""
        self.execute_count += 1

def test_cycle_initialization():
    """Тест инициализации цикла"""
    cycle = TestCycle(name="Test", interval=5)
    assert cycle.name == "Test"
    assert cycle.interval == 5
    assert not cycle.is_running
    assert cycle.last_run is None
    assert cycle.error_count == 0

def test_cycle_start_stop():
    """Тест запуска и остановки цикла"""
    cycle = TestCycle(interval=1)
    
    # Проверка запуска
    cycle.start()
    assert cycle.is_running
    
    # Ждем немного, чтобы цикл выполнился
    time.sleep(1.5)
    
    # Проверка остановки
    cycle.stop()
    assert not cycle.is_running
    assert cycle.execute_count > 0

def test_cycle_error_handling():
    """Тест обработки ошибок"""
    class ErrorCycle(BaseCycle):
        def execute(self):
            raise Exception("Test error")
    
    cycle = ErrorCycle(name="Error Cycle", interval=1)
    cycle.start()
    
    # Ждем, чтобы произошло несколько ошибок
    time.sleep(2)
    
    # Проверяем, что ошибки подсчитываются
    assert cycle.error_count > 0
    
    cycle.stop()

def test_cycle_status():
    """Тест получения статуса цикла"""
    cycle = TestCycle(name="Status Test", interval=60)
    
    # Проверка начального статуса
    status = cycle.get_status()
    assert status['name'] == "Status Test"
    assert not status['running']
    assert status['last_run'] is None
    assert status['error_count'] == 0
    assert status['interval'] == 60
    
    # Запускаем цикл и проверяем обновление статуса
    cycle.start()
    time.sleep(1)  # Даем время на выполнение
    cycle.stop()
    
    status = cycle.get_status()
    assert status['last_run'] is not None
    assert isinstance(status['last_run'], str)  # Проверяем, что дата преобразована в строку

def test_cycle_max_errors():
    """Тест максимального количества ошибок"""
    class MaxErrorCycle(BaseCycle):
        def execute(self):
            self.error_count += 1
            raise Exception("Test error")
    
    cycle = MaxErrorCycle(name="Max Error Test", interval=1)
    cycle.max_errors = 2  # Устанавливаем низкий порог для теста
    
    cycle.start()
    time.sleep(3)  # Даем время на накопление ошибок
    
    # Проверяем, что цикл остановился после превышения max_errors
    assert not cycle.is_running
    assert cycle.error_count >= cycle.max_errors

def test_cycle_interval_execution():
    """Тест интервала выполнения"""
    cycle = TestCycle(interval=2)
    cycle.start()
    
    # Проверяем количество выполнений за определенный период
    time.sleep(5)
    cycle.stop()
    
    # За 5 секунд с интервалом 2 секунды должно быть 2-3 выполнения
    assert 2 <= cycle.execute_count <= 3

def test_cycle_concurrent_start():
    """Тест повторного запуска цикла"""
    cycle = TestCycle()
    
    # Первый запуск
    cycle.start()
    assert cycle.is_running
    
    # Повторный запуск не должен вызывать ошибок
    cycle.start()
    assert cycle.is_running
    
    cycle.stop()

if __name__ == '__main__':
    pytest.main([__file__])
