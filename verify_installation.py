"""
安装验证脚本
检查所有依赖是否正确安装
"""

import sys

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✓ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("  需要: Python 3.9 或更高版本")
        return False

def check_dependencies():
    """检查依赖包"""
    print("\n检查依赖包...")
    dependencies = {
        'PyQt5': '5.15.10',
        'yaml': '6.0.1',  # PyYAML导入时使用yaml
        'openpyxl': '3.1.2',
    }
    
    all_ok = True
    
    for module_name, expected_version in dependencies.items():
        try:
            if module_name == 'yaml':
                import yaml
                module = yaml
                actual_name = 'PyYAML'
            else:
                module = __import__(module_name)
                actual_name = module_name
            
            # 尝试获取版本
            try:
                if hasattr(module, '__version__'):
                    version = module.__version__
                else:
                    version = "未知版本"
                print(f"✓ {actual_name}: {version}")
            except:
                print(f"✓ {actual_name}: 已安装")
                
        except ImportError:
            if module_name == 'yaml':
                actual_name = 'PyYAML'
            else:
                actual_name = module_name
            print(f"✗ {actual_name}: 未安装")
            all_ok = False
    
    return all_ok

def check_project_structure():
    """检查项目结构"""
    print("\n检查项目结构...")
    import os
    
    required_files = [
        'main.py',
        'config.py',
        'requirements.txt',
        'core/__init__.py',
        'core/yaml_parser.py',
        'core/command_generator.py',
        'core/yaml_comparator.py',
        'core/info_extractor.py',
        'ui/__init__.py',
        'ui/main_window.py',
        'ui/tab_command_gen.py',
        'ui/tab_comparator.py',
        'ui/tab_extractor.py',
        'models/__init__.py',
        'models/resource.py',
        'utils/__init__.py',
        'utils/excel_exporter.py',
        'utils/file_utils.py',
        'utils/validators.py',
    ]
    
    all_ok = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - 缺失")
            all_ok = False
    
    return all_ok

def main():
    """主函数"""
    print("="*50)
    print("K8s YAML管理工具 - 安装验证")
    print("="*50)
    
    results = []
    
    # 检查Python版本
    results.append(check_python_version())
    
    # 检查依赖包
    results.append(check_dependencies())
    
    # 检查项目结构
    results.append(check_project_structure())
    
    # 总结
    print("\n" + "="*50)
    if all(results):
        print("✓ 所有检查通过！")
        print("您可以运行以下命令启动程序：")
        print("  python main.py")
        print("\n或者打包成可执行文件：")
        print("  python build.py")
        return 0
    else:
        print("✗ 存在问题，请检查上述错误信息")
        print("\n安装依赖：")
        print("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
