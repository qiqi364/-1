"""解析器工厂"""
from backend.parsers.bin_parser import BinLogParser
from backend.parsers.ulog_parser import ULogParser

PARSERS = {
    "bin": BinLogParser,
    "log": BinLogParser,
    "ulg": ULogParser,
}

SUPPORTED_FORMATS = list(PARSERS.keys())

def create_parser(format_type):
    """根据格式类型创建解析器实例"""
    cls = PARSERS.get(format_type.lower())
    if not cls:
        raise ValueError(f"不支持的格式: {format_type}。支持的格式: {', '.join(SUPPORTED_FORMATS)}")
    return cls()

def supported_formats():
    """返回支持的格式列表"""
    return SUPPORTED_FORMATS