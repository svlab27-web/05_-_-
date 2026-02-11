"""
Цикл 2: Аудит времени
Отслеживает время на задачи и выявляет узкие места
Запускается каждый час
"""
from datetime import datetime, timedelta
import logging
import pandas as pd
import numpy as np
from .base_cycle import BaseCycle

logger = logging.getLogger(__name__)

class TimeAuditCycle(BaseCycle):
    def __init__(self, calendar_client=None, database=None):
        """
        Инициализация цикла аудита времени
        
        Args:
            calendar_client: Клиент для работы с календарем (Google Calendar/Outlook)
            database: Объект для работы с базой данных
        """
        super().__init__(name="Time Audit Cycle", interval=3600)  # 3600 секунд = 1 час
        self.calendar_client = calendar_client
        self.database = database
        self.time_data = []
        
    def execute(self):
        """Выполнение цикла аудита времени"""
        try:
            # 1. Сбор данных о времени
            time_data = self._collect_time_data()
            
            # 2. Анализ паттернов
            patterns = self._analyze_patterns(time_data)
            
            # 3. Генерация инсайтов
            insights = self._generate_insights(patterns)
            
            # 4. Сохранение результатов
            self._save_results(time_data, patterns, insights)
            
            logger.info("Time audit cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Error in time audit cycle: {e}")
            raise
    
    def _collect_time_data(self) -> dict:
        """
        Сбор данных о времени из разных источников
        
        Returns:
            dict: Собранные данные о времени
        """
        time_data = {
            'calendar_events': [],
            'task_durations': [],
            'activity_logs': []
        }
        
        # 1. Получение данных из календаря
        if self.calendar_client:
            try:
                time_data['calendar_events'] = self._get_calendar_events()
            except Exception as e:
                logger.error(f"Error getting calendar events: {e}")
        
        # 2. Получение времени выполнения задач
        if self.database:
            try:
                time_data['task_durations'] = self._get_task_durations()
            except Exception as e:
                logger.error(f"Error getting task durations: {e}")
        
        return time_data
    
    def _analyze_patterns(self, time_data: dict) -> dict:
        """
        Анализ паттернов использования времени
        
        Args:
            time_data (dict): Собранные данные о времени
            
        Returns:
            dict: Выявленные паттерны
        """
        patterns = {
            'time_wasters': [],
            'automation_candidates': [],
            'weekly_comparison': {}
        }
        
        if time_data['task_durations']:
            # Преобразование в DataFrame для удобного анализа
            df = pd.DataFrame(time_data['task_durations'])
            
            # Поиск задач, занимающих больше времени чем планировалось
            patterns['time_wasters'] = self._find_time_wasters(df)
            
            # Поиск повторяющихся действий
            patterns['automation_candidates'] = self._find_automation_candidates(df)
            
            # Сравнение с прошлой неделей
            patterns['weekly_comparison'] = self._compare_with_previous_week(df)
        
        return patterns
    
    def _generate_insights(self, patterns: dict) -> dict:
        """
        Генерация инсайтов на основе анализа
        
        Args:
            patterns (dict): Проанализированные паттерны
            
        Returns:
            dict: Сгенерированные инсайты
        """
        insights = {
            'top_time_wasters': [],
            'optimization_suggestions': [],
            'potential_time_savings': 0
        }
        
        # 1. Топ-5 пожирателей времени
        if patterns['time_wasters']:
            insights['top_time_wasters'] = sorted(
                patterns['time_wasters'],
                key=lambda x: x['excess_time'],
                reverse=True
            )[:5]
        
        # 2. Предложения по оптимизации
        if patterns['automation_candidates']:
            insights['optimization_suggestions'] = self._generate_optimization_suggestions(
                patterns['automation_candidates']
            )
        
        # 3. Расчет потенциальной экономии времени
        insights['potential_time_savings'] = self._calculate_potential_savings(
            patterns['time_wasters'],
            patterns['automation_candidates']
        )
        
        return insights
    
    def _save_results(self, time_data: dict, patterns: dict, insights: dict):
        """
        Сохранение результатов анализа
        
        Args:
            time_data (dict): Исходные данные о времени
            patterns (dict): Выявленные паттерны
            insights (dict): Сгенерированные инсайты
        """
        if self.database:
            try:
                # Сохраняем результаты анализа
                query = """
                INSERT INTO time_audit_results 
                (date, patterns, insights, potential_savings) 
                VALUES (:date, :patterns, :insights, :savings)
                """
                
                self.database.execute(query, {
                    'date': datetime.now(),
                    'patterns': patterns,
                    'insights': insights,
                    'savings': insights['potential_time_savings']
                })
                
                logger.info("Time audit results saved to database")
                
            except Exception as e:
                logger.error(f"Error saving time audit results: {e}")
        
        # Логирование основных результатов
        logger.info(
            f"Time audit results:\n"
            f"- Top time wasters: {len(insights['top_time_wasters'])}\n"
            f"- Optimization suggestions: {len(insights['optimization_suggestions'])}\n"
            f"- Potential time savings: {insights['potential_time_savings']} hours"
        )
    
    def _get_calendar_events(self) -> list:
        """
        Получение событий из календаря
        
        Returns:
            list: Список событий календаря
        """
        if not self.calendar_client:
            return []
            
        try:
            # Получаем события за последнюю неделю
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            events = self.calendar_client.get_events(start_date, end_date)
            logger.info(f"Retrieved {len(events)} calendar events")
            
            return events
            
        except Exception as e:
            logger.error(f"Error retrieving calendar events: {e}")
            return []
    
    def _get_task_durations(self) -> list:
        """
        Получение длительности выполнения задач
        
        Returns:
            list: Список задач с длительностью
        """
        if not self.database:
            return []
            
        try:
            # Получаем задачи из БД
            tasks = self.database.data.get('tasks', [])
            logger.info(f"Retrieved {len(tasks)} tasks with durations")
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error retrieving task durations: {e}")
            return []
    
    def _find_time_wasters(self, df: pd.DataFrame) -> list:
        """
        Поиск задач, занимающих много времени
        
        Args:
            df (pd.DataFrame): DataFrame с данными о задачах
            
        Returns:
            list: Список задач-пожирателей времени
        """
        if df.empty:
            return []
            
        try:
            # Вычисляем превышение времени
            df['excess_time'] = df['duration'] - df['planned_duration']
            
            # Фильтруем задачи с превышением времени
            time_wasters = df[df['excess_time'] > 0].to_dict('records')
            
            return [
                {
                    'task_id': task['task_id'],
                    'excess_time': task['excess_time'],
                    'title': task['title']
                }
                for task in time_wasters
            ]
            
        except Exception as e:
            logger.error(f"Error finding time wasters: {e}")
            return []
    
    def _find_automation_candidates(self, df: pd.DataFrame) -> list:
        """
        Поиск кандидатов на автоматизацию
        
        Args:
            df (pd.DataFrame): DataFrame с данными о задачах
            
        Returns:
            list: Список задач-кандидатов на автоматизацию
        """
        if df.empty:
            return []
            
        try:
            # Группируем задачи по названию и считаем повторения
            task_counts = df.groupby(['task_id', 'title']).agg({
                'duration': ['count', 'mean']
            }).reset_index()
            
            # Переименовываем колонки
            task_counts.columns = ['task_id', 'title', 'repetition_count', 'avg_duration']
            
            # Фильтруем задачи с частыми повторениями
            automation_candidates = task_counts[
                task_counts['repetition_count'] >= 3
            ].to_dict('records')
            
            return automation_candidates
            
        except Exception as e:
            logger.error(f"Error finding automation candidates: {e}")
            return []
    
    def _compare_with_previous_week(self, df: pd.DataFrame) -> dict:
        """
        Сравнение с предыдущей неделей
        
        Args:
            df (pd.DataFrame): DataFrame с данными о задачах
            
        Returns:
            dict: Результаты сравнения
        """
        if df.empty:
            return {}
            
        try:
            # Определяем границы недель
            current_date = datetime.now().date()
            week_ago = current_date - timedelta(days=7)
            
            # Разделяем данные по неделям
            current_week = df[df['date'] >= week_ago]
            previous_week = df[df['date'] < week_ago]
            
            # Считаем метрики
            current_total = current_week['duration'].sum()
            previous_total = previous_week['duration'].sum()
            
            # Вычисляем изменения
            if previous_total > 0:
                total_change = ((current_total - previous_total) / previous_total) * 100
            else:
                total_change = 0
                
            return {
                'total_time_change': total_change,
                'current_week_total': current_total,
                'previous_week_total': previous_total
            }
            
        except Exception as e:
            logger.error(f"Error comparing with previous week: {e}")
            return {}
    
    def _generate_optimization_suggestions(self, candidates: list) -> list:
        """
        Генерация предложений по оптимизации
        
        Args:
            candidates (list): Список кандидатов на автоматизацию
            
        Returns:
            list: Список предложений по оптимизации
        """
        suggestions = []
        
        for candidate in candidates:
            if candidate['repetition_count'] >= 5:
                suggestions.append(
                    f"Автоматизировать задачу '{candidate['title']}' "
                    f"(выполняется {candidate['repetition_count']} раз, "
                    f"среднее время: {candidate['avg_duration']:.1f} мин)"
                )
            elif candidate['repetition_count'] >= 3:
                suggestions.append(
                    f"Создать шаблон для задачи '{candidate['title']}' "
                    f"(повторяется {candidate['repetition_count']} раза)"
                )
        
        return suggestions
    
    def _calculate_potential_savings(self, time_wasters: list, automation_candidates: list) -> float:
        """
        Расчет потенциальной экономии времени
        
        Args:
            time_wasters (list): Список пожирателей времени
            automation_candidates (list): Список кандидатов на автоматизацию
            
        Returns:
            float: Потенциальная экономия в часах
        """
        total_savings = 0
        
        # 1. Экономия от оптимизации пожирателей времени
        for waster in time_wasters:
            total_savings += waster['excess_time']
        
        # 2. Экономия от автоматизации
        for candidate in automation_candidates:
            if candidate['repetition_count'] >= 5:
                # Предполагаем, что автоматизация сэкономит 80% времени
                potential_saving = (
                    candidate['repetition_count'] * 
                    candidate['avg_duration'] * 
                    0.8
                )
                total_savings += potential_saving
            elif candidate['repetition_count'] >= 3:
                # Шаблоны сэкономят 40% времени
                potential_saving = (
                    candidate['repetition_count'] * 
                    candidate['avg_duration'] * 
                    0.4
                )
                total_savings += potential_saving
        
        # Переводим минуты в часы
        return round(total_savings / 60, 1)
