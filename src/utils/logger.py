import logging
import sys
from typing import Optional


class Logger:
    """Centralized logging configuration for the portfolio generator"""
    
    _logger: Optional[logging.Logger] = None
    
    @classmethod
    def get_logger(cls, name: str = "portfolio_generator") -> logging.Logger:
        """Get configured logger instance"""
        if cls._logger is None:
            cls._logger = cls._setup_logger(name)
        return cls._logger
    
    @classmethod
    def _setup_logger(cls, name: str) -> logging.Logger:
        """Set up logger with appropriate configuration"""
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(console_handler)
        
        return logger
    
    @classmethod
    def set_debug_mode(cls, debug: bool = True) -> None:
        """Enable or disable debug mode"""
        if cls._logger:
            level = logging.DEBUG if debug else logging.INFO
            cls._logger.setLevel(level)
            for handler in cls._logger.handlers:
                handler.setLevel(level)