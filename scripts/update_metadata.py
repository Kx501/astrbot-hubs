# scripts/update_metadata.py
import json
import os
import sys
import yaml
from datetime import datetime
from pathlib import Path

def load_yaml_content(yaml_content):
    """从YAML字符串加载内容"""
    try:
        return yaml.safe_load(yaml_content)
    except:
        # 如果传入的是字典
        if isinstance(yaml_content, dict):
            return yaml_content
        return {}

def convert_to_official_format(plugin_data):
    """将metadata.yaml格式转换为官方插件格式"""
    
    # 插件ID生成逻辑
    if "name" in plugin_data:
        # 从name字段生成ID
        name = plugin_data["name"]
        if name.startswith("astrbot_plugin_"):
            plugin_id = name
        else:
            plugin_id = f"astrbot_plugin_{name}_fork"
    else:
        # 从仓库URL提取
        repo_url = plugin_data.get("repo", "")
        if "github.com" in repo_url:
            repo_name = repo_url.split("/")[-1]
            plugin_id = f"astrbot_plugin_{repo_name}_fork"
        else:
            plugin_id = f"astrbot_plugin_unknown_fork"
    
    # 构建官方格式
    formatted = {
        "display_name": plugin_data.get("name", "").replace("_fork", "").replace("_", " ").title(),
        "desc": plugin_data.get("desc", ""),
        "author": plugin_data.get("author", "Kx501"),
        "repo": plugin_data.get("repo", ""),
        "tags": plugin_data.get("tags", []),
        "social_link": f"https://github.com/{plugin_data.get('author', 'Kx501')}",
        "stars": plugin_data.get("stars", 0),
        "version": plugin_data.get("version", "v1.0.0"),
        "updated_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "logo": plugin_data.get("logo", "")
    }
    
    return plugin_id, formatted

def update_plugin_metadata(plugin_yaml):
    """更新或添加插件元数据"""
    
    # 加载YAML数据
    plugin_data = load_yaml_content(plugin_yaml)
    
    # 读取现有的plugins.json
    plugins_file = Path("plugins.json")
    if plugins_file.exists():
        with open(plugins_file, 'r', encoding='utf-8') as f:
            all_plugins = json.load(f)
    else:
        all_plugins = {}
    
    # 转换为官方格式
    plugin_id, formatted_data = convert_to_official_format(plugin_data)
    
    # 更新数据
    all_plugins[plugin_id] = formatted_data
    
    # 保存
    with open(plugins_file, 'w', encoding='utf-8') as f:
        json.dump(all_plugins, f, ensure_ascii=False, indent=2)
    
    return plugin_id, formatted_data

if __name__ == "__main__":
    # 从环境变量或参数获取YAML数据
    if len(sys.argv) > 1:
        plugin_yaml = sys.argv[1]
    else:
        plugin_yaml = os.environ.get('PLUGIN_YAML', '{}')
    
    plugin_id, updated_data = update_plugin_metadata(plugin_yaml)
    
    print(f"Updated plugin: {plugin_id}")
    print(json.dumps({plugin_id: updated_data}, ensure_ascii=False, indent=2))
