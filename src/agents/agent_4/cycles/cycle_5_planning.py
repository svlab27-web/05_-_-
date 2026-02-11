"""
Цикл 5: Проактивное планирование
Планирование оптимизаций на неделю
Запускается каждый понедельник в 08:00
"""
from datetime import datetime, timedelta
import logging
from typing import Dict, List
import pandas as pd
from .base_cycle import BaseCycle

logger = logging.getLogger(__name__)

class PlanningCycle(BaseCycle):
    def __init__(self, database=None, telegram_bot=None, task_manager=None):
        """
        Инициализация цикла планирования
        
        Args:
            database: Объект для работы с базой данных
            telegram_bot: Клиент для отправки уведомлений в Telegram
            task_manager: Клиент для работы с системой управления задачами
        """
        super().__init__(name="Planning Cycle", interval=604800)  # 604800 секунд = 1 неделя
        self.database = database
        self.telegram_bot = telegram_bot
        self.task_manager = task_manager
        
    def execute(self):
        """Выполнение цикла планирования"""
        try:
            # 1. Анализ прошлой недели
            weekly_analysis = self._analyze_previous_week()
            
            # 2. Планирование автоматизаций
            automation_plan = self._plan_automations(weekly_analysis)
            
            # 3. Создание задач
            tasks = self._create_tasks(automation_plan)
            
            # 4. Отправка плана команде
            self._send_weekly_plan(weekly_analysis, automation_plan, tasks)
            
            logger.info("Planning cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Error in planning cycle: {e}")
            raise
    
    def _analyze_previous_week(self) -> Dict:
        """
        Анализ статистики за прошлую неделю
        
        Returns:
            Dict: Результаты анализа прошлой недели
        """
        analysis = {
            'time_stats': {},
            'automation_candidates': [],
            'performance_metrics': {},
            'bottlenecks': []
        }
        
        try:
            if self.database:
                # Получаем статистику из БД
                analysis = self.database.data.get('weekly_stats', analysis)
                
                # Дополнительный анализ, если нужно
                if not analysis.get('bottlenecks'):
                    analysis['bottlenecks'] = self._identify_bottlenecks(
                        analysis.get('time_stats', {})
                    )
                
                logger.info("Weekly analysis completed successfully")
                
        except Exception as e:
            logger.error(f"Error analyzing previous week: {e}")
            analysis['error'] = str(e)
        
        return analysis
    
    def _plan_automations(self, weekly_analysis: Dict) -> Dict:
        """
        Планирование автоматизаций на основе анализа
        
        Args:
            weekly_analysis (Dict): Результаты анализа прошлой недели
            
        Returns:
            Dict: План автоматизаций
        """
        plan = {
            'quick_wins': [],
            'medium_term': [],
            'long_term': [],
            'estimated_savings': {}
        }
        
        try:
            # 1. Приоритизация кандидатов
            candidates = self._prioritize_automation_candidates(
                weekly_analysis.get('automation_candidates', [])
            )
            
            # 2. Категоризация по сложности
            categorized = self._categorize_by_complexity(candidates)
            plan.update(categorized)
            
            # 3. Расчет приоритетов
            plan = self._calculate_priorities(plan)
            
            # 4. Оценка экономии
            plan['estimated_savings'] = self._estimate_savings(plan)
            
            logger.info(
                f"Automation plan created: {len(plan['quick_wins'])} quick wins, "
                f"{len(plan['medium_term'])} medium tasks, "
                f"{len(plan['long_term'])} long term tasks"
            )
            
        except Exception as e:
            logger.error(f"Error planning automations: {e}")
            plan['error'] = str(e)
        
        return plan
    
    def _create_tasks(self, automation_plan: Dict) -> List[Dict]:
        """
        Создание задач в системе управления проектами
        
        Args:
            automation_plan (Dict): План автоматизаций
            
        Returns:
            List[Dict]: Созданные задачи
        """
        tasks = []
        
        if self.task_manager:
            try:
                # 1. Создание quick wins
                for task in automation_plan['quick_wins']:
                    task_data = self._prepare_task_data(task, priority='high')
                    created_task = self.task_manager.create_task(
                        title=task_data['title'],
                        description=task_data['description'],
                        priority=task_data['priority']
                    )
                    tasks.append(created_task)
                
                # 2. Создание средних задач
                for task in automation_plan['medium_term']:
                    task_data = self._prepare_task_data(task, priority='medium')
                    created_task = self.task_manager.create_task(
                        title=task_data['title'],
                        description=task_data['description'],
                        priority=task_data['priority']
                    )
                    tasks.append(created_task)
                
                # 3. Создание долгосрочных задач
                for task in automation_plan['long_term']:
                    task_data = self._prepare_task_data(task, priority='low')
                    created_task = self.task_manager.create_task(
                        title=task_data['title'],
                        description=task_data['description'],
                        priority=task_data['priority']
                    )
                    tasks.append(created_task)
                
                logger.info(f"Created {len(tasks)} tasks in task manager")
                
            except Exception as e:
                logger.error(f"Error creating tasks: {e}")
        
        return tasks
    
    def _send_weekly_plan(self, analysis: Dict, plan: Dict, tasks: List[Dict]):
        """
        Отправка недельного плана команде
        
        Args:
            analysis (Dict): Результаты анализа
            plan (Dict): План автоматизаций
            tasks (List[Dict]): Созданные задачи
        """
        if self.telegram_bot:
            try:
                message = self._format_weekly_plan(analysis, plan, tasks)
                
                self.telegram_bot.send_message(
                    chat_id="team_chat",  # ID чата команды
                    text=message
                )
                
                logger.info("Weekly plan sent successfully")
                
            except Exception as e:
                logger.error(f"Error sending weekly plan: {e}")
    
    def _collect_time_statistics(self, start_date: datetime) -> Dict:
        """
        Сбор статистики по времени за период
        
        Args:
            start_date (datetime): Начальная дата периода
            
        Returns:
            Dict: Статистика по времени
        """
        stats = {
            'total_time': 0,
            'by_category': {},
            'by_process': {},
            'trends': {}
        }
        
        if self.database:
            try:
                # Получаем данные из БД
                time_data = self.database.data.get('time_data', [])
                
                # Фильтруем данные за период
                period_data = [
                    entry for entry in time_data
                    if entry['date'] >= start_date
                ]
                
                # Агрегируем данные
                for entry in period_data:
                    stats['total_time'] += entry.get('duration', 0)
                    
                    # По категориям
                    category = entry.get('category')
                    if category:
                        stats['by_category'][category] = (
                            stats['by_category'].get(category, 0) +
                            entry.get('duration', 0)
                        )
                    
                    # По процессам
                    process = entry.get('process')
                    if process:
                        stats['by_process'][process] = (
                            stats['by_process'].get(process, 0) +
                            entry.get('duration', 0)
                        )
                
                # Анализ трендов
                stats['trends'] = self._analyze_trends(period_data)
                
            except Exception as e:
                logger.error(f"Error collecting time statistics: {e}")
        
        return stats
    
    def _identify_bottlenecks(self, time_stats: Dict) -> List[Dict]:
        """
        Выявление узких мест в процессах
        
        Args:
            time_stats (Dict): Статистика по времени
            
        Returns:
            List[Dict]: Список узких мест
        """
        bottlenecks = []
        
        try:
            # Анализируем процессы
            for process, time in time_stats.get('by_process', {}).items():
                # Если процесс занимает более 20% общего времени
                if time > 0.2 * time_stats.get('total_time', 0):
                    bottlenecks.append({
                        'process': process,
                        'impact': 'high',
                        'delay': f"{time/3600:.1f}h"
                    })
                
        except Exception as e:
            logger.error(f"Error identifying bottlenecks: {e}")
        
        return bottlenecks
    
    def _analyze_trends(self, time_data: List[Dict]) -> Dict:
        """
        Анализ трендов во временных данных
        
        Args:
            time_data (List[Dict]): Данные о времени
            
        Returns:
            Dict: Тренды
        """
        trends = {
            'increasing': [],
            'decreasing': []
        }
        
        try:
            if len(time_data) >= 2:
                # Группируем данные по дням
                daily_data = {}
                for entry in time_data:
                    date = entry['date'].date()
                    daily_data[date] = daily_data.get(date, 0) + entry.get('duration', 0)
                
                # Анализируем тренд
                dates = sorted(daily_data.keys())
                first_day = daily_data[dates[0]]
                last_day = daily_data[dates[-1]]
                
                # Если разница больше 10%
                if abs(last_day - first_day) / first_day > 0.1:
                    if last_day > first_day:
                        trends['increasing'].append('total_time')
                    else:
                        trends['decreasing'].append('total_time')
                
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
        
        return trends
    
    def _prioritize_automation_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """
        Приоритизация кандидатов на автоматизацию
        
        Args:
            candidates (List[Dict]): Список кандидатов
            
        Returns:
            List[Dict]: Приоритизированный список
        """
        if not candidates:
            return []
            
        try:
            # Расчет score для каждого кандидата
            for candidate in candidates:
                frequency = candidate.get('frequency', 0)
                time_cost = candidate.get('time_cost', 0)
                complexity = 1
                
                if candidate.get('complexity') == 'easy':
                    complexity = 1
                elif candidate.get('complexity') == 'medium':
                    complexity = 2
                else:
                    complexity = 3
                
                # Score = (частота * время) / сложность
                candidate['score'] = (frequency * time_cost) / complexity
            
            # Сортировка по score
            return sorted(candidates, key=lambda x: x['score'], reverse=True)
            
        except Exception as e:
            logger.error(f"Error prioritizing candidates: {e}")
            return candidates
    
    def _categorize_by_complexity(self, candidates: List[Dict]) -> Dict:
        """
        Категоризация задач по сложности
        
        Args:
            candidates (List[Dict]): Список кандидатов
            
        Returns:
            Dict: Задачи по категориям
        """
        categorized = {
            'quick_wins': [],    # Легкие задачи
            'medium_term': [],   # Средние задачи
            'long_term': []      # Сложные задачи
        }
        
        for task in candidates:
            complexity = task.get('complexity', 'medium')
            if complexity == 'easy':
                categorized['quick_wins'].append(task)
            elif complexity == 'medium':
                categorized['medium_term'].append(task)
            else:
                categorized['long_term'].append(task)
        
        return categorized
    
    def _calculate_priorities(self, plan: Dict) -> Dict:
        """
        Расчет приоритетов для задач
        
        Args:
            plan (Dict): План автоматизаций
            
        Returns:
            Dict: План с рассчитанными приоритетами
        """
        try:
            # Сортируем задачи по score внутри каждой категории
            for category in ['quick_wins', 'medium_term', 'long_term']:
                plan[category] = sorted(
                    plan[category],
                    key=lambda x: x.get('score', 0),
                    reverse=True
                )
            
            # Ограничиваем количество задач в каждой категории
            plan['quick_wins'] = plan['quick_wins'][:5]  # Топ-5 быстрых побед
            plan['medium_term'] = plan['medium_term'][:3]  # Топ-3 средних задачи
            plan['long_term'] = plan['long_term'][:2]  # Топ-2 долгосрочные задачи
            
        except Exception as e:
            logger.error(f"Error calculating priorities: {e}")
        
        return plan
    
    def _estimate_savings(self, plan: Dict) -> Dict:
        """
        Оценка потенциальной экономии
        
        Args:
            plan (Dict): План автоматизаций
            
        Returns:
            Dict: Оценка экономии
        """
        savings = {
            'time_per_week': 0,
            'money_per_month': 0,
            'efficiency_gain': 0
        }
        
        try:
            # 1. Расчет экономии времени
            for category in ['quick_wins', 'medium_term', 'long_term']:
                for task in plan[category]:
                    weekly_time = (
                        task.get('frequency', 0) *
                        task.get('time_cost', 0) / 3600  # переводим в часы
                    )
                    savings['time_per_week'] += weekly_time
            
            # 2. Расчет экономии денег (условно 1000 руб/час)
            savings['money_per_month'] = (
                savings['time_per_week'] * 4 * 1000  # 4 недели в месяце
            )
            
            # 3. Оценка повышения эффективности
            total_tasks = len(plan['quick_wins']) + len(plan['medium_term']) + len(plan['long_term'])
            if total_tasks > 0:
                savings['efficiency_gain'] = (
                    savings['time_per_week'] * 100 / (40 * total_tasks)  # 40 часов в неделю
                )
            
        except Exception as e:
            logger.error(f"Error estimating savings: {e}")
        
        return savings
    
    def _prepare_task_data(self, task: Dict, priority: str) -> Dict:
        """
        Подготовка данных задачи для создания в системе управления проектами
        
        Args:
            task (Dict): Данные задачи
            priority (str): Приоритет задачи
            
        Returns:
            Dict: Подготовленные данные задачи
        """
        return {
            'title': f"Автоматизация: {task.get('name', 'Новая задача')}",
            'description': self._generate_task_description(task),
            'priority': priority,
            'estimated_time': task.get('estimated_time', '0h'),
            'expected_outcome': task.get('expected_outcome', ''),
            'metrics': task.get('metrics', [])
        }
    
    def _generate_task_description(self, task: Dict) -> str:
        """
        Генерация описания задачи
        
        Args:
            task (Dict): Данные задачи
            
        Returns:
            str: Описание задачи
        """
        description = [
            f"# Задача автоматизации\n",
            f"## Текущий процесс",
            task.get('current_process', 'Нет описания'),
            f"\n## Проблема",
            task.get('problem', 'Не указана'),
            f"\n## Ожидаемый результат",
            task.get('expected_outcome', 'Не указан'),
            f"\n## Метрики успеха",
            "\n".join([f"- {m}" for m in task.get('metrics', ['Не указаны'])]),
            f"\n## Оценка экономии",
            f"- Время: {task.get('estimated_time_saving', '0')} часов в неделю",
            f"- ROI: {task.get('estimated_roi', 'Не рассчитан')}"
        ]
        
        return "\n".join(description)
    
    def _format_weekly_plan(self, analysis: Dict, plan: Dict, tasks: List[Dict]) -> str:
        """
        Форматирование недельного плана для отправки
        
        Args:
            analysis (Dict): Результаты анализа
            plan (Dict): План автоматизаций
            tasks (List[Dict]): Созданные задачи
            
        Returns:
            str: Отформатированное сообщение
        """
        message = [
            "📅 План автоматизации на неделю\n",
            "\n📊 Итоги прошлой недели:",
            f"- Обработано задач: {analysis['performance_metrics'].get('total_tasks', 0)}",
            f"- Среднее время ответа: {analysis['performance_metrics'].get('avg_response_time', '0')}",
            f"- Уровень автоматизации: {analysis['performance_metrics'].get('automation_rate', '0')}%\n",
            "\n🎯 План на неделю:",
            "\n1️⃣ Quick Wins (быстрые победы):"
        ]
        
        # Добавление quick wins
        for task in tasks:
            if task['priority'] == 'high':
                message.append(f"- {task['title']}")
        
        message.extend([
            "\n2️⃣ Средний приоритет:"
        ])
        
        # Добавление средних задач
        for task in tasks:
            if task['priority'] == 'medium':
                message.append(f"- {task['title']}")
        
        message.extend([
            f"\n💰 Ожидаемая экономия:",
            f"- Время: {plan['estimated_savings'].get('time_per_week', 0)} часов в неделю",
            f"- Деньги: {plan['estimated_savings'].get('money_per_month', 0):,.0f} руб/месяц",
            f"- Эффективность: +{plan['estimated_savings'].get('efficiency_gain', 0):.1f}%"
        ])
        
        return "\n".join(message)
