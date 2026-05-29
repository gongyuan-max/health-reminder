"""
提醒管理器模块
"""

from datetime import datetime, time
from typing import Callable, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.core.database import Database
from src.core.notification import Notification
from src.utils.config import Config
from src.utils.logger import logger


class ReminderManager:
    """提醒管理器"""
    
    def __init__(self):
        """初始化提醒管理器"""
        self.scheduler = BackgroundScheduler()
        self.database = Database()
        self.water_callback: Optional[Callable] = None
        self.rest_callback: Optional[Callable] = None
        self.is_running = False
    
    def start(self) -> None:
        """启动提醒服务"""
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                self.is_running = True
                self._schedule_reminders()
                logger.info("提醒管理器已启动")
        except Exception as e:
            logger.error(f"启动提醒管理器失败: {e}")
    
    def stop(self) -> None:
        """停止提醒服务"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                self.is_running = False
                logger.info("提醒管理器已停止")
        except Exception as e:
            logger.error(f"停止提醒管理器失败: {e}")
    
    def restart(self) -> None:
        """重启提醒服务"""
        self.stop()
        self.start()
    
    def _schedule_reminders(self) -> None:
        """配置提醒任务"""
        # 移除现有的所有任务
        self.scheduler.remove_all_jobs()
        
        # 配置饮水提醒
        self._schedule_water_reminder()
        
        # 配置休息提醒
        self._schedule_rest_reminder()
        
        logger.info("提醒任务已配置")
    
    def _schedule_water_reminder(self) -> None:
        """配置饮水提醒"""
        water_config = Config.get_section('water_reminder')
        
        if water_config.get('enabled'):
            interval = water_config.get('interval', 30)
            
            self.scheduler.add_job(
                self._trigger_water_reminder,
                IntervalTrigger(minutes=interval),
                id='water_reminder',
                name='Water Reminder',
                replace_existing=True
            )
            logger.info(f"饮水提醒已配置: {interval} 分钟间隔")
    
    def _schedule_rest_reminder(self) -> None:
        """配置休息提醒"""
        rest_config = Config.get_section('rest_reminder')
        
        if rest_config.get('enabled'):
            interval = rest_config.get('interval', 45)
            
            self.scheduler.add_job(
                self._trigger_rest_reminder,
                IntervalTrigger(minutes=interval),
                id='rest_reminder',
                name='Rest Reminder',
                replace_existing=True
            )
            logger.info(f"休息提醒已配置: {interval} 分钟间隔")
    
    def _should_remind(self) -> bool:
        """检查是否应该提醒（考虑工作时间设置）"""
        work_time_config = Config.get_section('work_time')
        
        if not work_time_config.get('enabled'):
            return True
        
        try:
            now = datetime.now().time()
            start_time = datetime.strptime(work_time_config['start'], "%H:%M").time()
            end_time = datetime.strptime(work_time_config['end'], "%H:%M").time()
            
            # 只在工作时间内提醒
            return start_time <= now <= end_time
        except Exception as e:
            logger.error(f"检查工作时间失败: {e}")
            return True
    
    def _trigger_water_reminder(self) -> None:
        """触发饮水提醒"""
        if not self._should_remind():
            return
        
        water_config = Config.get_section('water_reminder')
        
        # 显示通知
        message = Notification.get_water_reminder_message()
        Notification.show_notification(
            '💧 饮水提醒',
            message,
            duration=Config.get('notification.notification_duration', 5)
        )
        
        # 播放音效
        Notification.play_water_reminder(water_config.get('sound_enabled', True))
        
        # 记录提醒历史
        self.database.add_reminder_history('water', 'shown')
        
        # 调用回调函数
        if self.water_callback:
            self.water_callback()
        
        logger.info("饮水提醒已触发")
    
    def _trigger_rest_reminder(self) -> None:
        """触发休息提醒"""
        if not self._should_remind():
            return
        
        rest_config = Config.get_section('rest_reminder')
        rest_types = rest_config.get('rest_types', ['eyes', 'stand'])
        
        # 随机选择一种休息类型
        import random
        rest_type = random.choice(rest_types)
        
        # 获取提醒消息
        title, message = Notification.get_rest_reminder_message(rest_type)
        
        # 显示通知
        Notification.show_notification(
            title,
            message,
            duration=Config.get('notification.notification_duration', 5)
        )
        
        # 播放音效
        Notification.play_rest_reminder(rest_config.get('sound_enabled', True))
        
        # 记录提醒历史
        self.database.add_reminder_history('rest', 'shown')
        
        # 调用回调函数
        if self.rest_callback:
            self.rest_callback(rest_type)
        
        logger.info(f"休息提醒已触发: {rest_type}")
    
    def record_water(self, amount: int = 1) -> bool:
        """记录饮水"""
        success = self.database.add_water_record(amount=amount)
        if success and self.water_callback:
            self.water_callback()
        return success
    
    def record_rest(self, rest_type: str) -> bool:
        """记录休息"""
        success = self.database.add_rest_record(rest_type)
        if success and self.rest_callback:
            self.rest_callback(rest_type)
        return success
    
    def set_water_callback(self, callback: Callable) -> None:
        """设置饮水记录回调"""
        self.water_callback = callback
    
    def set_rest_callback(self, callback: Callable) -> None:
        """设置休息记录回调"""
        self.rest_callback = callback
    
    def get_today_stats(self) -> dict:
        """获取今日统计"""
        return self.database.get_daily_stats()
    
    def get_water_records_today(self) -> list:
        """获取今天的饮水记录"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.database.get_water_records(today)
    
    def get_rest_records_today(self) -> list:
        """获取今天的休息记录"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.database.get_rest_records(today)
