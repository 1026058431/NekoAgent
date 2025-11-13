"""
🐱 通用报告生成器模块 - 简化版
支持直接文件引用："请仿照XXX文件的格式"
"""

from .report_generator import (
    get_report_guide,
    list_available_templates,
    add_template_file,
    get_ctf_report_guide,
    get_development_report_guide,
    get_task_report_guide,
    get_plan_report_guide
)

from .report_tools import (
    get_report_template,
    list_all_templates,
    add_new_template
)

__all__ = [
    # 核心生成器函数
    'get_report_guide',
    'list_available_templates', 
    'add_template_file',
    'get_ctf_report_guide',
    'get_development_report_guide',
    'get_task_report_guide',
    'get_plan_report_guide',
    
    # 工具接口函数
    'get_report_template',
    'list_all_templates',
    'add_new_template'
]