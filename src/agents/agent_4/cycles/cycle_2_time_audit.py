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
        self.last_run = None
        
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
            
            # 5. Сохраняем время последнего запуска
            self.last_run = datetime.now()
            
            logger.info("Time audit cycle completed successfully")
            
            # Возвращаем результаты для тестирования
            return {
                'time_data': time_data,
                'patterns': patterns,
                'insights': insights
            }
            
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
        
        if time_data.get('task_durations') and len(time_data['task_durations']) > 0:
            try:
                # Преобразование в DataFrame для удобного анализа
                df = pd.DataFrame(time_data['task_durations'])
                
                # Проверка наличия необходимых колонок
                required_columns = ['task_id', 'title', 'duration']
                if not all(col in df.columns for col in required_columns):
                    logger.warning(f"Missing required columns. Available: {df.columns.tolist()}")
                    return patterns
                
                # Поиск задач, занимающих больше времени чем планировалось
                patterns['time_wasters'] = self._find_time_wasters(df)
                
                # Поиск повторяющихся действий
                patterns['automation_candidates'] = self._find_automation_candidates(df)
                
                # Сравнение с прошлой неделей
                patterns['weekly_comparison'] = self._compare_with_previous_week(df)
                
            except Exception as e:
                logger.error(f"Error analyzing patterns: {e}")
        
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
        time_wasters = patterns.get('time_wasters', [])
        if time_wasters:
            raw_wasters = sorted(
                time_wasters,
                key=lambda x: x.get('excess_time', 0),
                reverse=True
            )[:5]
            for item in raw_wasters:
                insights['top_time_wasters'].append({
                    'title': 'Пожиратель времени',
                    'text': f"Лишняя активность: {item.get('title', 'Неизвестно')}",
                    'excess_time': item.get('excess_time', 0)
                })
        
        # 2. Предложения по оптимизации
        automation_candidates = patterns.get('automation_candidates', [])
        if automation_candidates:
            insights['optimization_suggestions'] = self._generate_optimization_suggestions(
                automation_candidates
            )
        
        # 3. Расчет потенциальной экономии времени
        insights['potential_time_savings'] = self._calculate_potential_savings(
            time_wasters,
            automation_candidates
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
                    'patterns': str(patterns),
                    'insights': str(insights),
                    'savings': insights.get('potential_time_savings', 0)
                })
                
                logger.info("Time audit results saved to database")
                
            except Exception as e:
                logger.error(f"Error saving time audit results: {e}")
        
        # Логирование основных результатов
        logger.info(
            f"Time audit results:\n"
            f"- Top time wasters: {len(insights.get('top_time_wasters', []))}\n"
            f"- Optimization suggestions: {len(insights.get('optimization_suggestions', []))}\n"
            f"- Potential time savings: {insights.get('potential_time_savings', 0)} hours"
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
            # Проверяем наличие необходимых колонок
            required_columns = ['task_id', 'title', 'duration', 'planned_duration']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.warning(f"Missing columns for time wasters analysis: {missing_columns}")
                return []
            
            # Создаем копию для избежания SettingWithCopyWarning
            df_copy = df[required_columns].copy()
            
            # Обрабатываем NaN значения
            df_copy['duration'] = pd.to_numeric(df_copy['duration'], errors='coerce').fillna(0)
            df_copy['planned_duration'] = pd.to_numeric(df_copy['planned_duration'], errors='coerce').fillna(0)
            df_copy['task_id'] = df_copy['task_id'].fillna('unknown')
            df_copy['title'] = df_copy['title'].fillna('Без названия')
            
            # Вычисляем превышение времени
            df_copy['excess_time'] = df_copy['duration'] - df_copy['planned_duration']
            
            # Фильтруем задачи с превышением времени
            time_wasters_df = df_copy[df_copy['excess_time'] > 0]
            
            if time_wasters_df.empty:
                return []
            
            # Формируем результат используя to_dict вместо iterrows
            time_wasters = time_wasters_df[['task_id', 'title', 'excess_time']].to_dict('records')
            
            # Приводим к нужному формату
            result = []
            for waster in time_wasters:
                result.append({
                    'task_id': str(waster.get('task_id', 'unknown')),
                    'excess_time': float(waster.get('excess_time', 0)),
                    'title': str(waster.get('title', 'Без названия'))
                })
            
            return result
            
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
            # Проверяем наличие необходимых колонок
            required_columns = ['task_id', 'title', 'duration']
            if not all(col in df.columns for col in required_columns):
                logger.warning("Missing required columns for automation candidates analysis")
                return []
            
            # Создаем копию и обрабатываем данные
            df_copy = df[required_columns].copy()
            
            # Обрабатываем NaN значения
            df_copy['duration'] = pd.to_numeric(df_copy['duration'], errors='coerce').fillna(0)
            df_copy['task_id'] = df_copy['task_id'].fillna('unknown')
            df_copy['title'] = df_copy['title'].fillna('Без названия')
            
            # Удаляем строки с нулевой длительностью
            df_copy = df_copy[df_copy['duration'] > 0]
            
            if df_copy.empty:
                return []
            
            # Группируем задачи по task_id и title и считаем повторения
            task_counts = df_copy.groupby(['task_id', 'title'], as_index=False, dropna=False).agg(
                repetition_count=('duration', 'count'),
                avg_duration=('duration', 'mean')
            )
            
            # Фильтруем задачи с частыми повторениями
            automation_candidates_df = task_counts[task_counts['repetition_count'] >= 3]
            
            if automation_candidates_df.empty:
                return []
            
            # Формируем результат
            automation_candidates = automation_candidates_df.to_dict('records')
            
            # Приводим к нужному формату
            result = []
            for candidate in automation_candidates:
                result.append({
                    'task_id': str(candidate.get('task_id', 'unknown')),
                    'title': str(candidate.get('title', 'Без названия')),
                    'repetition_count': int(candidate.get('repetition_count', 0)),
                    'avg_duration': float(candidate.get('avg_duration', 0))
                })
            
            return result
            
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
            # Проверяем наличие необходимых колонок
            if 'date' not in df.columns:
                logger.warning("Column 'date' not found, skipping weekly comparison")
                return {}
            
            if 'duration' not in df.columns:
                logger.warning("Column 'duration' not found, skipping weekly comparison")
                return {}
            
            # Создаем копию
            df_copy = df[['date', 'duration']].copy()
            
            # Обрабатываем разные форматы дат
            try:
                df_copy['date'] = pd.to_datetime(df_copy['date'], errors='coerce')
                # Удаляем строки с невалидными датами
                df_copy = df_copy.dropna(subset=['date'])
                
                if df_copy.empty:
                    logger.warning("No valid dates found after conversion")
                    return {}
                    
                df_copy['date'] = df_copy['date'].dt.date
            except Exception as e:
                logger.error(f"Error converting dates: {e}")
                return {}
            
            # Обрабатываем NaN в duration ДО разделения на недели
            df_copy['duration'] = pd.to_numeric(df_copy['duration'], errors='coerce').fillna(0)
            
            # Определяем границы недель
            current_date = datetime.now().date()
            week_ago = current_date - timedelta(days=7)
            
            # Разделяем данные по неделям
            current_week = df_copy[df_copy['date'] >= week_ago]
            previous_week = df_copy[df_copy['date'] < week_ago]
            
            # Считаем метрики
            current_total = float(current_week['duration'].sum()) if not current_week.empty else 0
            previous_total = float(previous_week['duration'].sum()) if not previous_week.empty else 0
            
            # Вычисляем изменения
            if previous_total > 0:
                efficiency_change = ((current_total - previous_total) / previous_total) * 100
            else:
                efficiency_change = 0
                
            return {
                'total_time_change': round(efficiency_change, 2),
                'efficiency_change': round(efficiency_change, 2),
                'current_week_total': round(current_total, 2),
                'previous_week_total': round(previous_total, 2)
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
            repetition_count = candidate.get('repetition_count', 0)
            title = candidate.get('title', 'Неизвестная задача')
            avg_duration = candidate.get('avg_duration', 0)
            
            if repetition_count >= 5:
                suggestions.append(
                    f"Автоматизировать задачу '{title}' "
                    f"(выполняется {repetition_count} раз, "
                    f"среднее время: {avg_duration:.1f} мин)"
                )
            elif repetition_count >= 3:
                suggestions.append(
                    f"Создать шаблон для задачи '{title}' "
                    f"(повторяется {repetition_count} раза)"
                )
        
        return suggestions
    
    def _calculate_potential_savings(self, time_wasters: list, automation_candidates: list) -> float:
        """
        Расчет потенциальной экономии времени
        Предполагается, что все данные о времени в минутах
        
        Args:
            time_wasters (list): Список пожирателей времени
            automation_candidates (list): Список кандидатов на автоматизацию
            
        Returns:
            float: Потенциальная экономия в часах
        """
        total_savings = 0
        
        # 1. Экономия от оптимизации пожирателей времени (данные в минутах)
        for waster in time_wasters:
            excess_time = float(waster.get('excess_time', 0))
            total_savings += excess_time
        
        # 2. Экономия от автоматизации
        for candidate in automation_candidates:
            repetition_count = int(candidate.get('repetition_count', 0))
            avg_duration = float(candidate.get('avg_duration', 0))
            
            if repetition_count >= 5:
                # Предполагаем, что автоматизация сэкономит 80% времени
                potential_saving = repetition_count * avg_duration * 0.8
                total_savings += potential_saving
            elif repetition_count >= 3:
                # Шаблоны сэкономят 40% времени
                potential_saving = repetition_count * avg_duration * 0.4
                total_savings += potential_saving
        
        # Переводим минуты в часы
        return round(total_savings / 60, 1)
