"""
Цикл 4: Обучение и оптимизация
Анализирует эффективность и выполняет самооптимизацию
Запускается каждый день в 23:00
"""
from datetime import datetime, timedelta
import logging
import pandas as pd
from typing import Dict, List
from .base_cycle import BaseCycle

logger = logging.getLogger(__name__)

class OptimizationCycle(BaseCycle):
    def __init__(self, database=None, telegram_bot=None):
        """
        Инициализация цикла оптимизации
        
        Args:
            database: Объект для работы с базой данных
            telegram_bot: Клиент для отправки уведомлений в Telegram
        """
        super().__init__(name="Optimization Cycle", interval=86400)  # 86400 секунд = 24 часа
        self.database = database
        self.telegram_bot = telegram_bot
        self.kpi_targets = {
            'response_time': 3600,  # 1 час
            'automation_rate': 0.7,  # 70%
            'success_rate': 0.95    # 95%
        }
    
    def execute(self):
        """Выполнение цикла оптимизации"""
        try:
            # 1. Анализ дневной работы
            daily_stats = self._analyze_daily_work()
            
            # 2. Машинное обучение
            learning_results = self._perform_machine_learning(daily_stats)
            
            # 3. Генерация отчетов
            report = self._generate_reports(daily_stats, learning_results)
            
            # 4. Отправка результатов
            self._send_results(report)
            
            logger.info("Optimization cycle completed successfully")
            
        except Exception as e:
            logger.error(f"Error in optimization cycle: {e}")
            raise
    
    def _analyze_daily_work(self) -> Dict:
        """
        Анализ работы за день
        
        Returns:
            Dict: Статистика за день
        """
        stats = {
            'requests': {
                'total': 0,
                'automated': 0,
                'manual': 0
            },
            'response_times': [],
            'automation_rate': 0.0,
            'success_rate': 0.0,
            'time_saved': 0.0
        }
        
        try:
            if self.database:
                # Получаем статистику из БД
                stats = self.database.data.get('daily_stats', stats)
                
                # Расчет ключевых метрик
                if stats['requests']['total'] > 0:
                    stats['automation_rate'] = (
                        stats['requests']['automated'] / stats['requests']['total']
                    )
                
                # Сравнение с KPI
                stats['kpi_comparison'] = self._compare_with_kpi(stats)
                
                logger.info(f"Analyzed daily work: {stats['requests']['total']} requests")
                
        except Exception as e:
            logger.error(f"Error analyzing daily work: {e}")
            stats['error'] = str(e)
        
        return stats
    
    def _perform_machine_learning(self, daily_stats: Dict) -> Dict:
        """
        Выполнение машинного обучения на основе собранных данных
        
        Args:
            daily_stats (Dict): Статистика за день
            
        Returns:
            Dict: Результаты обучения
        """
        learning_results = {
            'patterns': [],
            'improvements': [],
            'rules_updated': False
        }
        
        try:
            # 1. Анализ успешных и неуспешных паттернов
            if daily_stats['requests']['total'] > 0:
                patterns = self._analyze_patterns(daily_stats)
                learning_results['patterns'] = patterns
                
                # 2. Обновление правил приоритизации
                if patterns:
                    self._update_prioritization_rules(patterns)
                    learning_results['rules_updated'] = True
                
                # 3. Улучшение шаблонов ответов
                template_improvements = self._improve_response_templates(daily_stats)
                learning_results['improvements'] = template_improvements
                
                logger.info(
                    f"Machine learning completed: {len(patterns)} patterns, "
                    f"{len(template_improvements)} improvements"
                )
                
        except Exception as e:
            logger.error(f"Error in machine learning: {e}")
            learning_results['error'] = str(e)
        
        return learning_results
    
    def _generate_reports(self, daily_stats: Dict, learning_results: Dict) -> Dict:
        """
        Генерация отчетов на основе анализа
        
        Args:
            daily_stats (Dict): Статистика за день
            learning_results (Dict): Результаты обучения
            
        Returns:
            Dict: Сгенерированные отчеты
        """
        reports = {
            'daily_dashboard': {},
            'roi_report': {},
            'recommendations': []
        }
        
        try:
            # 1. Формирование дневного дашборда
            reports['daily_dashboard'] = {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'metrics': {
                    'total_requests': daily_stats['requests']['total'],
                    'automation_rate': f"{daily_stats['automation_rate']*100:.1f}%",
                    'avg_response_time': self._format_duration(
                        sum(daily_stats['response_times']) / len(daily_stats['response_times'])
                        if daily_stats['response_times'] else 0
                    ),
                    'success_rate': f"{daily_stats['success_rate']*100:.1f}%"
                },
                'kpi_status': daily_stats.get('kpi_comparison', {})
            }
            
            # 2. Расчет ROI автоматизаций
            reports['roi_report'] = self._calculate_roi(daily_stats)
            
            # 3. Формирование рекомендаций
            reports['recommendations'] = self._generate_recommendations(
                daily_stats,
                learning_results
            )
            
            logger.info("Reports generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating reports: {e}")
            reports['error'] = str(e)
        
        return reports
    
    def _send_results(self, report: Dict):
        """
        Отправка результатов анализа
        
        Args:
            report (Dict): Отчет для отправки
        """
        if self.telegram_bot:
            try:
                # Формирование сообщения
                message = self._format_report_message(report)
                
                # Отправка отчета
                self.telegram_bot.send_message(
                    chat_id="analytics_chat",  # ID чата аналитики
                    text=message
                )
                
                logger.info("Results sent successfully")
                
            except Exception as e:
                logger.error(f"Error sending results: {e}")
    
    def _compare_with_kpi(self, stats: Dict) -> Dict:
        """
        Сравнение результатов с целевыми KPI
        
        Args:
            stats (Dict): Текущая статистика
            
        Returns:
            Dict: Результаты сравнения
        """
        comparison = {}
        
        for metric, target in self.kpi_targets.items():
            current = stats.get(metric, 0)
            difference = ((current - target) / target) * 100 if target > 0 else 0
            
            comparison[metric] = {
                'target': target,
                'current': current,
                'achieved': current >= target,
                'difference': difference
            }
        
        return comparison
    
    def _analyze_patterns(self, stats: Dict) -> List[Dict]:
        """
        Анализ паттернов обработки заявок
        
        Args:
            stats (Dict): Статистика за день
            
        Returns:
            List[Dict]: Выявленные паттерны
        """
        patterns = []
        
        try:
            # Анализ времени ответа
            if stats['response_times']:
                avg_time = sum(stats['response_times']) / len(stats['response_times'])
                if avg_time > self.kpi_targets['response_time']:
                    patterns.append({
                        'type': 'response_time',
                        'condition': 'high_load',
                        'avg_time': avg_time,
                        'frequency': len(stats['response_times'])
                    })
            
            # Анализ автоматизации
            if 'templates_used' in stats:
                for template in stats['templates_used']:
                    if template['success_rate'] >= 0.9:
                        patterns.append({
                            'type': 'automation',
                            'category': template['name'],
                            'success_rate': template['success_rate'],
                            'usage_count': template['uses']
                        })
            
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
        
        return patterns
    
    def _update_prioritization_rules(self, patterns: List[Dict]):
        """
        Обновление правил приоритизации на основе паттернов
        
        Args:
            patterns (List[Dict]): Выявленные паттерны
        """
        if self.database:
            try:
                # Формируем правила на основе паттернов
                rules = []
                for pattern in patterns:
                    if pattern['type'] == 'response_time':
                        rules.append({
                            'condition': pattern['condition'],
                            'priority': 'high',
                            'threshold': pattern['avg_time']
                        })
                
                # Сохраняем правила в БД
                self.database.execute(
                    "UPDATE prioritization_rules SET rules = :rules",
                    {'rules': rules}
                )
                
                logger.info(f"Updated {len(rules)} prioritization rules")
                
            except Exception as e:
                logger.error(f"Error updating prioritization rules: {e}")
    
    def _improve_response_templates(self, stats: Dict) -> List[Dict]:
        """
        Улучшение шаблонов ответов
        
        Args:
            stats (Dict): Статистика использования шаблонов
            
        Returns:
            List[Dict]: Улучшения для шаблонов
        """
        improvements = []
        
        try:
            if 'templates_used' in stats:
                for template in stats['templates_used']:
                    # Анализируем успешность шаблона
                    if template['success_rate'] < 0.9:
                        improvements.append({
                            'template_id': template['id'],
                            'suggestion': 'Пересмотреть формулировки',
                            'expected_improvement': 0.1
                        })
                    elif template['uses'] > 50:
                        improvements.append({
                            'template_id': template['id'],
                            'suggestion': 'Добавить вариации ответа',
                            'expected_improvement': 0.05
                        })
        
        except Exception as e:
            logger.error(f"Error improving templates: {e}")
        
        return improvements
    
    def _calculate_roi(self, stats: Dict) -> Dict:
        """
        Расчет ROI автоматизаций
        
        Args:
            stats (Dict): Статистика за день
            
        Returns:
            Dict: Расчет ROI
        """
        roi = {
            'time_saved': stats.get('time_saved', 0),
            'money_saved': 0,
            'efficiency_increase': 0
        }
        
        try:
            # Расчет сэкономленных денег (условно 1000 руб/час)
            roi['money_saved'] = (stats.get('time_saved', 0) / 3600) * 1000
            
            # Расчет повышения эффективности
            if stats['requests']['total'] > 0:
                manual_time = sum(stats['response_times']) / len(stats['response_times'])
                automated_time = manual_time * 0.2  # Автоматизация экономит 80% времени
                
                time_without_automation = manual_time * stats['requests']['total']
                time_with_automation = (
                    automated_time * stats['requests']['automated'] +
                    manual_time * stats['requests']['manual']
                )
                
                if time_without_automation > 0:
                    roi['efficiency_increase'] = (
                        (time_without_automation - time_with_automation) /
                        time_without_automation * 100
                    )
            
        except Exception as e:
            logger.error(f"Error calculating ROI: {e}")
        
        return roi
    
    def _generate_recommendations(self, stats: Dict, learning_results: Dict) -> List[str]:
        """
        Генерация рекомендаций на основе анализа
        
        Args:
            stats (Dict): Статистика за день
            learning_results (Dict): Результаты обучения
            
        Returns:
            List[str]: Список рекомендаций
        """
        recommendations = []
        
        try:
            # 1. Рекомендации по времени ответа
            if stats['response_times']:
                avg_time = sum(stats['response_times']) / len(stats['response_times'])
                if avg_time > self.kpi_targets['response_time']:
                    recommendations.append(
                        "⏱ Оптимизировать время ответа: текущее среднее "
                        f"{self._format_duration(avg_time)}"
                    )
            
            # 2. Рекомендации по автоматизации
            if stats['automation_rate'] < self.kpi_targets['automation_rate']:
                recommendations.append(
                    "🤖 Увеличить уровень автоматизации: текущий "
                    f"{stats['automation_rate']*100:.1f}%"
                )
            
            # 3. Рекомендации по шаблонам
            for improvement in learning_results['improvements']:
                recommendations.append(
                    f"📝 {improvement['suggestion']} "
                    f"(ожидаемое улучшение: {improvement['expected_improvement']*100:.1f}%)"
                )
            
            # 4. Рекомендации по эффективности
            roi = self._calculate_roi(stats)
            if roi['efficiency_increase'] < 50:
                recommendations.append(
                    "📈 Повысить эффективность: текущий прирост "
                    f"{roi['efficiency_increase']:.1f}%"
                )
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            recommendations.append("⚠️ Ошибка при генерации рекомендаций")
        
        return recommendations
    
    def _format_report_message(self, report: Dict) -> str:
        """
        Форматирование отчета для отправки
        
        Args:
            report (Dict): Отчет для форматирования
            
        Returns:
            str: Отформатированное сообщение
        """
        dashboard = report['daily_dashboard']
        roi = report['roi_report']
        
        message = (
            f"📊 Дневной отчет ({dashboard['date']})\n\n"
            f"Основные метрики:\n"
            f"- Всего заявок: {dashboard['metrics']['total_requests']}\n"
            f"- Уровень автоматизации: {dashboard['metrics']['automation_rate']}\n"
            f"- Среднее время ответа: {dashboard['metrics']['avg_response_time']}\n"
            f"- Успешность: {dashboard['metrics']['success_rate']}\n\n"
            
            f"💰 ROI автоматизации:\n"
            f"- Сэкономлено времени: {self._format_duration(roi['time_saved'])}\n"
            f"- Сэкономлено денег: {roi['money_saved']:.0f} руб\n"
            f"- Прирост эффективности: {roi['efficiency_increase']:.1f}%\n"
        )
        
        if report['recommendations']:
            message += "\n🎯 Рекомендации на завтра:\n"
            for i, rec in enumerate(report['recommendations'], 1):
                message += f"{i}. {rec}\n"
        
        return message
    
    def _format_duration(self, seconds: float) -> str:
        """
        Форматирование длительности из секунд в читаемый формат
        
        Args:
            seconds (float): Количество секунд
            
        Returns:
            str: Отформатированная строка
        """
        if seconds < 60:
            return f"{seconds:.0f}с"
        elif seconds < 3600:
            return f"{seconds/60:.1f}м"
        else:
            return f"{seconds/3600:.1f}ч"
