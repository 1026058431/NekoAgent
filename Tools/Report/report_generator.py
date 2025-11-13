"""
🐱 修复版报告生成器 - 解决路径问题
"""

import json
import os
from typing import Dict, Any, List
from pathlib import Path


class SimpleReportGenerator:
    """简化版报告生成器 - 直接文件引用"""

    def __init__(self, templates_dir: str = None):
        # 使用绝对路径，确保能找到模板文件
        if templates_dir is None:
            # 获取当前文件所在目录的绝对路径
            current_dir = Path(__file__).parent
            self.templates_dir = current_dir / "templates"
        else:
            self.templates_dir = Path(templates_dir)

        self.template_files = {}
        self._scan_template_files()

    def _scan_template_files(self):
        """扫描模板目录中的文件"""
        # 确保模板目录存在
        self.templates_dir.mkdir(exist_ok=True)

        print(f"🐱 扫描模板目录: {self.templates_dir}")

        # 扫描所有文件
        for file_path in self.templates_dir.glob("*"):
            if file_path.is_file():
                self.template_files[file_path.stem] = {
                    "name": file_path.stem,
                    "path": str(file_path),
                    "extension": file_path.suffix
                }
                # print(f"🐱 找到模板文件: {file_path.stem}{file_path.suffix}")

    def get_report_guide(self, template_type: str, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """获取报告生成指南"""

        # 内置模板映射
        builtin_templates = {
            "ctf_report": "ctf_report_template.md",
            "development_report": "development_report_template.md",
            "crawling_report": "crawling_report_template.md",
            "task_report": "task_report_template.md",
            "plan_report": "plan_report_template.md",
            "security_audit_report": "security_audit_report_template.md"
        }

        # 查找模板文件
        template_file = None

        # 1. 先检查内置映射
        if template_type in builtin_templates:
            template_file = builtin_templates[template_type]

        # 2. 检查模板目录中的文件
        elif template_type in self.template_files:
            template_file = self.template_files[template_type]["name"] + self.template_files[template_type]["extension"]

        # 3. 检查是否有对应的文件
        else:
            # 检查是否有类似名称的文件
            for file_info in self.template_files.values():
                if template_type.lower() in file_info["name"].lower():
                    template_file = file_info["name"] + file_info["extension"]
                    break

        if template_file:
            # 返回文件引用提示
            return {
                "template_type": template_type,
                "instruction": f"请仿照 '{template_file}' 文件的格式和风格生成报告",
                "available_files": list(self.template_files.keys()),
                "context": context_data
            }
        else:
            # 返回可用文件列表
            return {
                "template_type": template_type,
                "error": f"未找到 '{template_type}' 对应的模板文件",
                "instruction": "请从以下可用模板中选择一个文件进行模仿:",
                "available_files": list(self.template_files.keys()),
                "suggestion": "使用 get_report_guide('文件名') 来指定具体文件",
                "context": context_data
            }

    def list_available_templates(self) -> List[str]:
        """列出所有可用的模板文件"""
        return list(self.template_files.keys())

    def add_template_file(self, file_path: str, template_name: str = None) -> bool:
        """添加模板文件到模板目录"""
        try:
            source_path = Path(file_path)
            if not source_path.exists():
                return False

            target_name = template_name or source_path.stem
            target_path = self.templates_dir / source_path.name

            # 复制文件到模板目录
            import shutil
            shutil.copy2(source_path, target_path)

            # 更新文件列表
            self._scan_template_files()

            return True

        except Exception as e:
            print(f"❌ 添加模板文件失败: {e}")
            return False


# 全局实例 - 使用绝对路径
_simple_generator = SimpleReportGenerator()


# 工具函数
def get_report_guide(template_type: str, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """获取报告生成指南"""
    return _simple_generator.get_report_guide(template_type, context_data)


def list_available_templates() -> List[str]:
    """列出所有可用的模板文件"""
    return _simple_generator.list_available_templates()


def add_template_file(file_path: str, template_name: str = None) -> bool:
    """添加模板文件"""
    return _simple_generator.add_template_file(file_path, template_name)


# 快捷工具函数
def get_ctf_report_guide(context_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """获取CTF报告生成指南"""
    return get_report_guide("ctf_report", context_data)


def get_development_report_guide(context_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """获取开发报告生成指南"""
    return get_report_guide("development_report", context_data)


def get_task_report_guide(context_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """获取任务报告生成指南"""
    return get_report_guide("task_report", context_data)


def get_plan_report_guide(context_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """获取计划报告生成指南"""
    return get_report_guide("plan_report", context_data)


if __name__ == "__main__":
    # 测试代码
    print("🐱 修复版报告生成器测试")
    print("=" * 50)
    
    # 列出可用模板
    templates = list_available_templates()
    print(f"可用模板文件: {templates}")
    print()
    
    # 获取CTF报告指南
    ctf_guide = get_ctf_report_guide({"题目": "测试SQLi", "状态": "成功"})
    print("CTF报告指南:")
    print(json.dumps(ctf_guide, ensure_ascii=False, indent=2))
    print()
    
    # 获取开发报告指南
    dev_guide = get_development_report_guide({"项目": "CTFAgent", "阶段": "开发"})
    print("开发报告指南:")
    print(json.dumps(dev_guide, ensure_ascii=False, indent=2))
    print()
    
    # 测试不存在的模板
    unknown_guide = get_report_guide("unknown_report")
    print("未知模板指南:")
    print(json.dumps(unknown_guide, ensure_ascii=False, indent=2))