"""解析器基类"""
from abc import ABC, abstractmethod

class BaseParser(ABC):
    """飞行日志解析器基类"""
    
    @abstractmethod
    def parse(self, filepath):
        """解析日志文件，返回结构化数据"""
        pass
    
    @abstractmethod
    def get_supported_formats(self):
        """返回支持的文件扩展名"""
        pass