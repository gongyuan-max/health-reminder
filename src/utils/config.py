"""
配置管理模块
"""

import json
from pathlib import Path
from typing import Any, Dict

class Config:
    """应用配置管理"""
    
    # 配置目录
    CONFIG_DIR = Path.home() / ".health_reminder"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    
    # 默认配置
    DEFAULT_CONFIG = {
        # 饮水提醒设置
        "water_reminder": {
            "enabled": True,
            "interval": 30,  # 分钟
            "daily_goal": 8,  # 杯数
            "sound_enabled": True,
            "sound_type": "normal"  # normal, important, silent
        },
        # 休息提醒设置
        "rest_reminder": {
            "enabled": True,
            "interval": 45,  # 分钟
            "duration": 5,  # 分钟
            "sound_enabled": True,
            "rest_types": ["eyes", "stand", "stretch"]  # 休息类型
        },
        # 工作时间设置
        "work_time": {
            "enabled": False,
            "start": "09:00",
            "end": "18:00"
        },
        # 应用设置
        "app": {
            "theme": "light",  # light, dark
            "auto_start": False,
            "minimize_to_tray": True,
            "window_geometry": None
        },
        # 通知设置
        "notification": {
            "show_notification": True,
            "notification_duration": 5  # 秒
        }
    }
    
    _config: Dict[str, Any] = {}
    
    @classmethod
    def init_config(cls) -> None:
        """初始化配置"""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        if cls.CONFIG_FILE.exists():
            cls.load()
        else:
            cls._config = cls.DEFAULT_CONFIG.copy()
            cls.save()
    
    @classmethod
    def load(cls) -> None:
        """从文件加载配置"""
        try:
            with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                cls._config = json.load(f)
                # 合并默认配置，确保所有键都存在
                cls._merge_defaults()
        except Exception as e:
            print(f"加载配置失败: {e}")
            cls._config = cls.DEFAULT_CONFIG.copy()
    
    @classmethod
    def save(cls) -> None:
        """保存配置到文件"""
        try:
            with open(cls.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(cls._config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持 "section.key" 格式
            default: 默认值
            
        Returns:
            配置值
        """
        if not cls._config:
            cls.init_config()
        
        if '.' in key:
            section, sub_key = key.split('.', 1)
            return cls._config.get(section, {}).get(sub_key, default)
        else:
            return cls._config.get(key, default)
    
    @classmethod
    def set(cls, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键，支持 "section.key" 格式
            value: 配置值
        """
        if not cls._config:
            cls.init_config()
        
        if '.' in key:
            section, sub_key = key.split('.', 1)
            if section not in cls._config:
                cls._config[section] = {}
            cls._config[section][sub_key] = value
        else:
            cls._config[key] = value
        
        cls.save()
    
    @classmethod
    def get_section(cls, section: str) -> Dict[str, Any]:
        """获取整个配置节"""
        if not cls._config:
            cls.init_config()
        return cls._config.get(section, {})
    
    @classmethod
    def set_section(cls, section: str, values: Dict[str, Any]) -> None:
        """设置整个配置节"""
        if not cls._config:
            cls.init_config()
        cls._config[section] = values
        cls.save()
    
    @classmethod
    def _merge_defaults(cls) -> None:
        """合并默认配置"""
        for section, defaults in cls.DEFAULT_CONFIG.items():
            if section not in cls._config:
                cls._config[section] = defaults
            elif isinstance(defaults, dict):
                for key, value in defaults.items():
                    if key not in cls._config[section]:
                        cls._config[section][key] = value
    
    @classmethod
    def reset(cls) -> None:
        """重置为默认配置"""
        cls._config = cls.DEFAULT_CONFIG.copy()
        cls.save()
    
    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """获取所有配置"""
        if not cls._config:
            cls.init_config()
        return cls._config.copy()
