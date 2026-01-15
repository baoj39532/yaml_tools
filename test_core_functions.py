"""
核心功能测试脚本
测试三大核心功能的后端逻辑
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.yaml_parser import YAMLParser
from core.command_generator import CommandGenerator
from core.yaml_comparator import YAMLComparator
from core.info_extractor import InfoExtractor
from utils.excel_exporter import ExcelExporter

def print_section(title):
    """打印分隔线"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_yaml_parser():
    """测试1: YAML解析器"""
    print_section("测试1: YAML解析器")
    
    parser = YAMLParser()
    cluster_path = "test_data/cluster1"
    
    print(f"解析集群文件夹: {cluster_path}")
    resources = parser.parse_cluster_folder(cluster_path)
    
    print(f"\n✓ 成功解析 {len(resources)} 个资源:")
    for r in resources:
        print(f"  - {r.kind:25s} | {r.namespace:20s} | {r.name}")
    
    # 测试路径提取
    print("\n测试路径提取功能:")
    if resources:
        test_resource = resources[0]
        replicas = parser.extract_value_by_path(test_resource.yaml_content, "spec.replicas")
        print(f"  提取 spec.replicas = {replicas}")

    # 测试带特殊字符的key解析（单引号包裹）
    print("\n测试带特殊字符的key解析:")
    sample_yaml = {
        "metadata": {
            "annotations": {
                "app.cebpaas.io/last-replicas": "6"
            }
        }
    }
    special_key_path = "metadata.annotations.'app.cebpaas.io/last-replicas'"
    special_value = parser.extract_value_by_path(sample_yaml, special_key_path)
    print(f"  提取 {special_key_path} = {special_value}")
    
    if parser.get_errors():
        print("\n警告:")
        for error in parser.get_errors():
            print(f"  ⚠ {error}")
    
    return len(resources) > 0

def test_command_generator():
    """测试2: 命令生成器"""
    print_section("测试2: 命令生成器")
    
    parser = YAMLParser()
    cmd_gen = CommandGenerator()
    
    resources = parser.parse_cluster_folder("test_data/cluster1")
    print(f"已解析 {len(resources)} 个资源\n")
    
    # 生成部署命令
    print("生成部署命令:")
    deploy_commands = cmd_gen.generate_deploy_commands(resources)
    print(f"✓ 生成 {len(deploy_commands)} 条部署命令:")
    for i, cmd in enumerate(deploy_commands[:5], 1):  # 只显示前5条
        print(f"  {i}. {cmd}")
    if len(deploy_commands) > 5:
        print(f"  ... 还有 {len(deploy_commands)-5} 条")
    
    # 生成删除命令
    print("\n生成删除命令:")
    delete_commands = cmd_gen.generate_delete_commands(resources)
    print(f"✓ 生成 {len(delete_commands)} 条删除命令:")
    for i, cmd in enumerate(delete_commands[:5], 1):
        print(f"  {i}. {cmd}")
    if len(delete_commands) > 5:
        print(f"  ... 还有 {len(delete_commands)-5} 条")
    
    # 保存到文件
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    deploy_file = f"{output_dir}/deploy_commands.sh"
    delete_file = f"{output_dir}/delete_commands.sh"
    
    cmd_gen.save_commands_to_file(deploy_commands, deploy_file)
    cmd_gen.save_commands_to_file(delete_commands, delete_file)
    
    print(f"\n✓ 命令已保存:")
    print(f"  - {deploy_file}")
    print(f"  - {delete_file}")
    
    return len(deploy_commands) > 0 and len(delete_commands) > 0

def test_yaml_comparator():
    """测试3: YAML比较器"""
    print_section("测试3: YAML比较器")
    
    comparator = YAMLComparator()
    
    cluster1 = "test_data/cluster1"
    cluster2 = "test_data/cluster2"
    
    print(f"比较集群:")
    print(f"  集群1: {cluster1}")
    print(f"  集群2: {cluster2}")
    
    # 配置比较Key
    compare_keys = [
        {'key_path': 'spec.replicas', 'is_configmap_file': False},
        {'key_path': 'spec.image', 'is_configmap_file': False},
    ]
    
    print(f"\n比较Key: spec.replicas, spec.image")
    
    results = comparator.compare_clusters(cluster1, cluster2, compare_keys)
    
    print(f"\n✓ 发现 {len(results)} 个差异项:")
    for result in results:
        print(f"\n  资源: {result.resource_left.kind}/{result.resource_left.name}")
        if result.resource_right is None:
            print(f"    状态: 仅存在于集群1")
        else:
            for diff in result.differences:
                print(f"    - {diff['key_path']}: {diff['left_value']} -> {diff['right_value']}")
    
    # 测试ConfigMap文件比较
    print("\n\n测试ConfigMap文件内容比较:")
    configmap_keys = [
        {
            'is_configmap_file': True,
            'file_key': 'application.yaml',
            'file_type': 'yaml',
            'compare_key': 'server.port'
        },
        {
            'is_configmap_file': True,
            'file_key': 'application.yaml',
            'file_type': 'yaml',
            'compare_key': 'logging.level'
        }
    ]
    
    cm_results = comparator.compare_clusters(cluster1, cluster2, configmap_keys)
    
    print(f"✓ 发现 {len(cm_results)} 个ConfigMap差异:")
    for result in cm_results:
        if result.resource_left.kind == "ConfigMap":
            print(f"\n  ConfigMap: {result.resource_left.name}")
            for diff in result.differences:
                print(f"    - {diff['key_path']}: {diff['left_value']} -> {diff['right_value']}")
    
    return len(results) > 0

def test_info_extractor():
    """测试4: 信息提取器"""
    print_section("测试4: 信息提取器")
    
    extractor = InfoExtractor()
    
    path = "test_data/cluster1"
    
    print(f"提取路径: {path}")
    
    # 配置提取Key
    extract_configs = [
        {'key_path': 'spec.replicas', 'alias': '副本数', 'is_configmap_file': False},
        {'key_path': 'spec.image', 'alias': '镜像', 'is_configmap_file': False},
    ]
    
    print(f"提取Key: spec.replicas (副本数), spec.image (镜像)")
    
    results = extractor.extract_from_path(path, extract_configs)
    
    print(f"\n✓ 提取 {len(results)} 个资源的信息:")
    for result in results[:5]:  # 只显示前5个
        print(f"\n  资源: {result.resource.kind}/{result.resource.name}")
        for key, value in result.extracted_values.items():
            print(f"    {key}: {value}")
    
    if len(results) > 5:
        print(f"\n  ... 还有 {len(results)-5} 个资源")
    
    return len(results) > 0

def test_excel_export():
    """测试5: Excel导出"""
    print_section("测试5: Excel导出")
    
    parser = YAMLParser()
    exporter = ExcelExporter()
    
    resources = parser.parse_cluster_folder("test_data/cluster1")
    
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = f"{output_dir}/资源表.xlsx"
    
    print(f"导出资源表到Excel: {output_file}")
    success = exporter.export_resource_table(resources, output_file)
    
    if success:
        print(f"✓ 成功导出 {len(resources)} 个资源")
        print(f"  文件大小: {os.path.getsize(output_file)} 字节")
    else:
        print(f"✗ 导出失败")
        for error in exporter.get_errors():
            print(f"  {error}")
    
    return success

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("  K8s YAML管理工具 - 核心功能测试")
    print("="*60)
    
    results = []
    
    # 检查测试数据
    if not os.path.exists("test_data/cluster1"):
        print("\n✗ 错误: 测试数据不存在")
        print("  请先创建测试数据")
        return 1
    
    # 运行测试
    try:
        results.append(("YAML解析器", test_yaml_parser()))
        results.append(("命令生成器", test_command_generator()))
        results.append(("YAML比较器", test_yaml_comparator()))
        results.append(("信息提取器", test_info_extractor()))
        results.append(("Excel导出", test_excel_export()))
    except Exception as e:
        print(f"\n✗ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 总结
    print_section("测试总结")
    
    for name, passed in results:
        status = "✓ 通过" if passed else "✗ 失败"
        print(f"  {name:20s}: {status}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("  ✓ 所有测试通过！")
        print(f"  测试输出目录: test_output/")
    else:
        print("  ✗ 部分测试失败")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
