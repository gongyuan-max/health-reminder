"""
数据库管理模块
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Any
from src.utils.logger import logger

class Database:
    """SQLite 数据库操作"""
    
    DB_DIR = Path.home() / ".health_reminder"
    DB_FILE = DB_DIR / "health_reminder.db"
    
    def __init__(self):
        """初始化数据库连接"""
        self.DB_DIR.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.DB_FILE))
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self) -> None:
        """初始化数据库表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 饮水记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS water_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                amount INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 休息记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rest_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                rest_type TEXT NOT NULL,
                duration INTEGER DEFAULT 5,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 每日统计表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT UNIQUE NOT NULL,
                water_count INTEGER DEFAULT 0,
                rest_count INTEGER DEFAULT 0,
                water_goal INTEGER DEFAULT 8,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 提醒历史表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminder_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                reminder_type TEXT NOT NULL,
                status TEXT DEFAULT 'shown',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    
    # ==================== 饮水记录相关 ====================
    
    def add_water_record(self, date: str = None, amount: int = 1) -> bool:
        """
        添加饮水记录
        
        Args:
            date: 日期 (YYYY-MM-DD)
            amount: 饮水量（杯数）
            
        Returns:
            是否成功
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        time = datetime.now().strftime("%H:%M:%S")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO water_records (date, time, amount)
                VALUES (?, ?, ?)
            ''', (date, time, amount))
            
            # 更新每日统计
            self._update_daily_stats(date)
            
            conn.commit()
            conn.close()
            logger.info(f"添加饮水记录: {date} {time}")
            return True
        except Exception as e:
            logger.error(f"添加饮水记录失败: {e}")
            return False
    
    def get_water_records(self, date: str) -> List[Dict[str, Any]]:
        """
        获取指定日期的饮水记录
        
        Args:
            date: 日期 (YYYY-MM-DD)
            
        Returns:
            饮水记录列表
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, date, time, amount, created_at
                FROM water_records
                WHERE date = ?
                ORDER BY time
            ''', (date,))
            
            records = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return records
        except Exception as e:
            logger.error(f"获取饮水记录失败: {e}")
            return []
    
    def get_water_count_today(self) -> int:
        """获取今天的饮水次数"""
        today = datetime.now().strftime("%Y-%m-%d")
        records = self.get_water_records(today)
        return sum(r['amount'] for r in records)
    
    def delete_water_record(self, record_id: int) -> bool:
        """删除饮水记录"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 先获取日期
            cursor.execute('SELECT date FROM water_records WHERE id = ?', (record_id,))
            row = cursor.fetchone()
            
            if row:
                date = row['date']
                cursor.execute('DELETE FROM water_records WHERE id = ?', (record_id,))
                self._update_daily_stats(date)
                conn.commit()
                logger.info(f"删除饮水记录: {record_id}")
                return True
            
            conn.close()
            return False
        except Exception as e:
            logger.error(f"删除饮水记录失败: {e}")
            return False
    
    # ==================== 休息记录相关 ====================
    
    def add_rest_record(self, rest_type: str, date: str = None, duration: int = 5) -> bool:
        """
        添加休息记录
        
        Args:
            rest_type: 休息类型 (eyes, stand, stretch, breathe)
            date: 日期 (YYYY-MM-DD)
            duration: 休息时长（分钟）
            
        Returns:
            是否成功
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        time = datetime.now().strftime("%H:%M:%S")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO rest_records (date, time, rest_type, duration)
                VALUES (?, ?, ?, ?)
            ''', (date, time, rest_type, duration))
            
            # 更新每日统计
            self._update_daily_stats(date)
            
            conn.commit()
            conn.close()
            logger.info(f"添加休息记录: {date} {rest_type}")
            return True
        except Exception as e:
            logger.error(f"添加休息记录失败: {e}")
            return False
    
    def get_rest_records(self, date: str) -> List[Dict[str, Any]]:
        """获取指定日期的休息记录"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, date, time, rest_type, duration, created_at
                FROM rest_records
                WHERE date = ?
                ORDER BY time
            ''', (date,))
            
            records = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return records
        except Exception as e:
            logger.error(f"获取休息记录失败: {e}")
            return []
    
    def get_rest_count_today(self) -> int:
        """获取今天的休息次数"""
        today = datetime.now().strftime("%Y-%m-%d")
        records = self.get_rest_records(today)
        return len(records)
    
    def delete_rest_record(self, record_id: int) -> bool:
        """删除休息记录"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT date FROM rest_records WHERE id = ?', (record_id,))
            row = cursor.fetchone()
            
            if row:
                date = row['date']
                cursor.execute('DELETE FROM rest_records WHERE id = ?', (record_id,))
                self._update_daily_stats(date)
                conn.commit()
                logger.info(f"删除休息记录: {record_id}")
                return True
            
            conn.close()
            return False
        except Exception as e:
            logger.error(f"删除休息记录失败: {e}")
            return False
    
    # ==================== 每日统计相关 ====================
    
    def _update_daily_stats(self, date: str) -> None:
        """更新每日统计"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # 获取该日期的饮水和休息记录数
            cursor.execute('SELECT SUM(amount) FROM water_records WHERE date = ?', (date,))
            water_count = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT COUNT(*) FROM rest_records WHERE date = ?', (date,))
            rest_count = cursor.fetchone()[0]
            
            # 更新或插入统计
            cursor.execute('''
                INSERT INTO daily_stats (date, water_count, rest_count)
                VALUES (?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    water_count = ?,
                    rest_count = ?,
                    updated_at = CURRENT_TIMESTAMP
            ''', (date, water_count, rest_count, water_count, rest_count))
            
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"更新每日统计失败: {e}")
    
    def get_daily_stats(self, date: str = None) -> Dict[str, Any]:
        """获取每日统计"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT water_count, rest_count, water_goal
                FROM daily_stats
                WHERE date = ?
            ''', (date,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'date': date,
                    'water_count': row['water_count'],
                    'rest_count': row['rest_count'],
                    'water_goal': row['water_goal']
                }
            else:
                return {
                    'date': date,
                    'water_count': 0,
                    'rest_count': 0,
                    'water_goal': 8
                }
        except Exception as e:
            logger.error(f"获取每日统计失败: {e}")
            return {}
    
    def get_stats_range(self, days: int = 7) -> List[Dict[str, Any]]:
        """获取指定天数范围内的统计"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            cursor.execute('''
                SELECT date, water_count, rest_count, water_goal
                FROM daily_stats
                WHERE date >= ?
                ORDER BY date
            ''', (start_date,))
            
            records = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return records
        except Exception as e:
            logger.error(f"获取统计范围失败: {e}")
            return []
    
    # ==================== 提醒历史相关 ====================
    
    def add_reminder_history(self, reminder_type: str, status: str = 'shown') -> bool:
        """记录提醒历史"""
        date = datetime.now().strftime("%Y-%m-%d")
        time = datetime.now().strftime("%H:%M:%S")
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO reminder_history (date, time, reminder_type, status)
                VALUES (?, ?, ?, ?)
            ''', (date, time, reminder_type, status))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"记录提醒历史失败: {e}")
            return False
    
    def get_reminder_history(self, date: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取提醒历史"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, date, time, reminder_type, status
                FROM reminder_history
                WHERE date = ?
                ORDER BY time DESC
                LIMIT ?
            ''', (date, limit))
            
            records = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return records
        except Exception as e:
            logger.error(f"获取提醒历史失败: {e}")
            return []
    
    def cleanup_old_data(self, days: int = 90) -> bool:
        """��理旧数据（保留最近N天）"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            cursor.execute('DELETE FROM water_records WHERE date < ?', (cutoff_date,))
            cursor.execute('DELETE FROM rest_records WHERE date < ?', (cutoff_date,))
            cursor.execute('DELETE FROM daily_stats WHERE date < ?', (cutoff_date,))
            cursor.execute('DELETE FROM reminder_history WHERE date < ?', (cutoff_date,))
            
            conn.commit()
            conn.close()
            logger.info(f"清理旧数据完成: 删除{cutoff_date}之前的数据")
            return True
        except Exception as e:
            logger.error(f"清理旧数据失败: {e}")
            return False
