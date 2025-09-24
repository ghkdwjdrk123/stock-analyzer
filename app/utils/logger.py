"""
로깅 설정 및 유틸리티
"""
import logging
import logging.handlers
import os
import re
from typing import Dict, Any

class SensitiveDataFilter(logging.Filter):
    """민감정보 마스킹 필터"""
    
    def filter(self, record):
        if hasattr(record, 'msg'):
            record.msg = self.mask_sensitive_data(record.msg)
        return True
    
    def mask_sensitive_data(self, message):
        """민감정보 마스킹"""
        if not isinstance(message, str):
            return message
        
        # 패스워드, 토큰, 키 등 마스킹
        patterns = [
            (r'password["\']?\s*[:=]\s*["\']?([^"\']+)["\']?', r'password="***"'),
            (r'token["\']?\s*[:=]\s*["\']?([^"\']+)["\']?', r'token="***"'),
            (r'key["\']?\s*[:=]\s*["\']?([^"\']+)["\']?', r'key="***"'),
            (r'secret["\']?\s*[:=]\s*["\']?([^"\']+)["\']?', r'secret="***"'),
        ]
        
        for pattern, replacement in patterns:
            message = re.sub(pattern, replacement, message, flags=re.IGNORECASE)
        
        return message

def setup_logging(config: Dict[str, Any]):
    """로깅 설정"""
    log_level = config.get('logging.level', 'INFO')
    log_file = config.get('logging.file_path', './logs/stock_analyzer.log')
    max_size = config.get('logging.max_size_mb', 10) * 1024 * 1024
    backup_count = config.get('logging.backup_count', 5)
    console_output = config.get('logging.console_output', True)
    sensitive_masking = config.get('logging.sensitive_data_masking', True)
    
    # 로그 디렉토리 생성
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # 로거 설정
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 파일 핸들러 (로테이션)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_size, backupCount=backup_count
    )
    file_handler.setLevel(getattr(logging, log_level))
    
    # 콘솔 핸들러
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level))
    
    # 포맷터
    formatter = logging.Formatter(
        config.get('logging.format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    file_handler.setFormatter(formatter)
    if console_output:
        console_handler.setFormatter(formatter)
    
    # 민감정보 마스킹 필터 추가
    if sensitive_masking:
        sensitive_filter = SensitiveDataFilter()
        file_handler.addFilter(sensitive_filter)
        if console_output:
            console_handler.addFilter(sensitive_filter)
    
    logger.addHandler(file_handler)
    if console_output:
        logger.addHandler(console_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """로거 인스턴스 반환"""
    return logging.getLogger(name)
