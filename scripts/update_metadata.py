# scripts/update_metadata.py
import json
import os
import sys
from datetime import datetime

def update_plugin_metadata(plugin_data):
    """更新或添加插件元数据"""
    
    # 读取现有的plugins.json
    try:
        with open('plugins.json', 'r', encoding='utf-8') as f:
            all_plugins = json.load(f)
    except FileNotFoundError:
        all_plugins = {}
    
    # 确保插件ID符合官方格式
    plugin_id = plugin_data.get("plugin_id")
    if not plugin_id:
        # 自动生成ID
        repo_url = plugin_data.get("repo", "")
        if "github.com" in repo_url:
            repo_name = repo_url.split("/")[-1]
            plugin_id = f"astrbot_plugin_{repo_name}_fork"
        else:
            plugin_id = f"astrbot_plugin_{plugin_data.get('name', 'unknown')}_fork"
    
    # 转换为你提供的官方格式
    formatted_data = {
        "display_name": plugin_data.get("display_name") or plugin_data.get("name", ""),
        "desc": plugin_data.get("desc") or plugin_data.get("description", ""),
        "author": plugin_data.get("author", "Kx501"),
        "repo": plugin_data.get("repo", ""),
        "tags": plugin_data.get("tags", []),
        "social_link": plugin_data.get("social_link", f"https://github.com/{plugin_data.get('author', 'Kx501')}"),
        "stars": plugin_data.get("stars", 0),
        "version": plugin_data.get("version", "v1.0.0"),
        "updated_at": datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "logo": plugin_data.get("logo", "")
    }
    
    # 更新数据
    all_plugins[plugin_id] = formatted_data
    
    # 保存
    with open('plugins.json', 'w', encoding='utf-8') as f:
        json.dump(all_plugins, f, ensure_ascii=False, indent=2)
    
    return plugin_id, formatted_data

if __name__ == "__main__":
    # 从环境变量或参数获取插件数据
    if len(sys.argv) > 1:
        plugin_json = sys.argv[1]
    else:
        plugin_json = os.environ.get('PLUGIN_DATA', '{}')
    
    plugin_data = json.loads(plugin_json)
    plugin_id, updated_data = update_plugin_metadata(plugin_data)
    
    print(f"Updated plugin: {plugin_id}")
    print(json.dumps({plugin_id: updated_data}, ensure_ascii=False, indent=2))
