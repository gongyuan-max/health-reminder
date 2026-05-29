"""
系统通知模块
"""

import sys
import winsound
from pathlib import Path
from typing import Optional
from datetime import datetime
from src.utils.logger import logger

class Notification:
    """系统通知管理"""
    
    # 休息建议
    REST_TIPS = {
        'eyes': [
            '👀 眼睛休息时间！',
            '看看远方，让眼睛放松5秒钟',
            '遵循 20-20-20 法则：每20分钟，看20秒远处，距离20英尺外'
        ],
        'stand': [
            '🚶 是时候站起来活动活动了！',
            '站起来，走走，放松双腿和腰部',
            '活动一下身体，促进血液循环'
        ],
        'stretch': [
            '💪 肩颈拉伸时间',
            '做些简单的颈部和肩膀拉伸',
            '轻轻转动头部，放松肩部肌肉'
        ],
        'breathe': [
            '🌬️ 深呼吸放松',
            '做5次深呼吸，吸气4秒，呼气4秒',
            '放松身心，缓解压力'
        ]
    }
    
    @staticmethod
    def show_notification(title: str, message: str, duration: int = 5) -> None:
        """
        显示系统通知
        
        Args:
            title: 标题
            message: 消息内容
            duration: 显示时长（秒）
        """
        try:
            if sys.platform == 'win32':
                Notification._show_windows_notification(title, message, duration)
            elif sys.platform == 'darwin':
                Notification._show_mac_notification(title, message)
            else:
                Notification._show_linux_notification(title, message, duration)
            
            logger.info(f"显示通知: {title} - {message}")
        except Exception as e:
            logger.error(f"显示通知失败: {e}")
    
    @staticmethod
    def _show_windows_notification(title: str, message: str, duration: int) -> None:
        """Windows 系统通知"""
        try:
            from win10toast import ToastNotifier
            notifier = ToastNotifier()
            notifier.show_toast(
                title=title,
                msg=message,
                duration=duration,
                threaded=True
            )
        except ImportError:
            logger.warning("win10toast 未安装，使用备用通知方式")
            # 备用方案：使用弹窗
            Notification._show_fallback_notification(title, message)
    
    @staticmethod
    def _show_mac_notification(title: str, message: str) -> None:
        """macOS 系统通知"""
        import os
        script = f'display notification "{message}" with title "{title}"'
        os.system(f'osascript -e \'{script}\'')
    
    @staticmethod
    def _show_linux_notification(title: str, message: str, duration: int) -> None:
        """Linux 系统通知"""
        try:
            import subprocess
            subprocess.run([
                'notify-send',
                title,
                message,
                f'--expire-time={duration * 1000}'
            ])
        except Exception as e:
            logger.error(f"Linux 通知失败: {e}")
    
    @staticmethod
    def _show_fallback_notification(title: str, message: str) -> None:
        """备用通知方式"""
        print(f"\n{'=' * 50}")
        print(f"🔔 {title}")
        print(f"{message}")
        print(f"{'=' * 50}\n")
    
    @staticmethod
    def play_sound(sound_type: str = 'normal') -> None:
        """
        播放提醒音效
        
        Args:
            sound_type: 音效类型 (normal, important, silent)
        """
        if sound_type == 'silent':
            return
        
        try:
            if sys.platform == 'win32':
                if sound_type == 'normal':
                    winsound.Beep(1000, 500)  # 1000Hz, 500ms
                elif sound_type == 'important':
                    winsound.Beep(1500, 300)
                    winsound.Beep(1500, 300)
            else:
                # 其他平台使用系统声音
                import os
                os.system('afplay /System/Library/Sounds/Glass.aiff' if sys.platform == 'darwin'
                         else 'paplay /usr/share/sounds/freedesktop/stereo/complete.oga')
        except Exception as e:
            logger.error(f"播放音效失败: {e}")
    
    @staticmethod
    def get_water_reminder_message() -> str:
        """获取饮水提醒消息"""
        messages = [
            '💧 是时候喝水了！保持水分充足',
            '🚰 喝一杯水，保持健康',
            '💦 提醒：现在应该喝水了',
            '🥤 水润肌肤，健康生活，现在就喝一杯吧'
        ]
        import random
        return random.choice(messages)
    
    @staticmethod
    def get_rest_reminder_message(rest_type: str = 'general') -> tuple:
        """
        获取休息提醒消息
        
        Returns:
            (标题, 消息内容)
        """
        import random
        
        if rest_type in Notification.REST_TIPS:
            tips = Notification.REST_TIPS[rest_type]
            return tips[0], tips[1]
        else:
            return '🧘 是时候休息了！', '站起来活动活动，放松一下身心'
    
    @staticmethod
    def play_water_reminder(sound_enabled: bool = True) -> None:
        """播放饮水提醒"""
        if sound_enabled:
            Notification.play_sound('normal')
    
    @staticmethod
    def play_rest_reminder(sound_enabled: bool = True) -> None:
        """播放休息提醒"""
        if sound_enabled:
            Notification.play_sound('important')


# Windows 额外支持 - 需要安装 win10toast
# pip install win10toast
