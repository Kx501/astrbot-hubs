#!/usr/bin/env python3
"""
验证和修复插件元数据
"""
import json
import os
import re
import sys
import yaml
from typing import Dict, Any, Optional

def validate_and_fix_metadata(metadata: Dict[str, Any], github_repo: str = "", github_ref: str = "") -> Dict[str, Any]:
    """
    验证和修复metadata，返回修复后的数据
    """
    if metadata is None:
        metadata = {}
    
    # 从GitHub仓库信息提取数据
    if github_repo:
        owner, repo_name = github_repo.split('/', 1) if '/' in github_repo else ('', github_repo)
    else:
        repo_url = metadata.get('repo', '') or metadata.get('repo_url', '')
        if repo_url:
            match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
            if match:
                owner, repo_name = match.groups()
            else:
                owner, repo_name = '', ''
        else:
            owner, repo_name = '', ''
    
    # 字段别名配置
    FIELD_ALIASES = {
        'repo': ['repo_url', 'repository', 'github'],
        'display_name': ['displayname', 'name'],
        'name': ['plugin_name'],
        'desc': ['description', 'summary'],
        'author': ['authors', 'author_name'],
        'version': ['ver', 'v'],
        'tags': ['tag', 'labels', 'categories'],
    }
    
    # 字段自动生成规则
    AUTO_GENERATE_RULES = {
        'repo': lambda: f"https://github.com/{github_repo}" if github_repo else None,
        'display_name': lambda: repo_name,
        'name': lambda: (
            (repo_name and re.sub(r'^(astrbot_plugin_|astrbot-plugin-|plugin-)', '', repo_name))
            or None
        ),
        'author': lambda: owner or None,
        'version': lambda: github_ref[10:] if github_ref and github_ref.startswith('refs/tags/') else None,
        'desc': lambda: '一个AstrBot插件',
        'tags': lambda: [],
    }
    
    changes_made = False
    
    # 1. 处理字段别名
    for correct_field, wrong_aliases in FIELD_ALIASES.items():
        for wrong_field in wrong_aliases:
            if wrong_field in metadata:
                if correct_field not in metadata:
                    metadata[correct_field] = metadata[wrong_field]
                    print(f"✅ 将错误字段 {wrong_field} 替换为正确字段 {correct_field}", file=sys.stderr)
                del metadata[wrong_field]
                changes_made = True
    
    # 2. 自动生成缺失字段
    for field, generator_func in AUTO_GENERATE_RULES.items():
        if field not in metadata or metadata[field] is None or metadata[field] == '':
            generated_value = generator_func()
            if generated_value:
                metadata[field] = generated_value
                print(f"✅ 自动生成 {field} 字段: {generated_value}", file=sys.stderr)
                changes_made = True
    
    # 3. 字段类型转换
    if 'tags' in metadata:
        tags = metadata['tags']
        if not isinstance(tags, list):
            if isinstance(tags, str):
                # 处理逗号分隔的字符串或JSON字符串
                if tags.startswith('[') and tags.endswith(']'):
                    try:
                        tags = json.loads(tags)
                    except:
                        tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
                else:
                    tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
            else:
                tags = [str(tags)] if tags else []
            metadata['tags'] = tags
            if changes_made:
                print(f"✅ 转换 tags 字段为 list 类型", file=sys.stderr)
    
    if not changes_made:
        print("✅ 元数据文件完整，无需修改", file=sys.stderr)
    
    return metadata

if __name__ == '__main__':
    # 从环境变量或参数读取
    if len(sys.argv) > 1:
        metadata_str = sys.argv[1]
    else:
        metadata_str = os.environ.get('PLUGIN_METADATA', '{}')
    
    github_repo = os.environ.get('GITHUB_REPOSITORY', '')
    github_ref = os.environ.get('GITHUB_REF', '')
    
    # 解析输入（可能是JSON或YAML）
    try:
        if metadata_str.startswith('{') or metadata_str.startswith('['):
            metadata = json.loads(metadata_str)
        else:
            metadata = yaml.safe_load(metadata_str) or {}
    except:
        metadata = {}
    
    # 验证和修复
    fixed_metadata = validate_and_fix_metadata(metadata, github_repo, github_ref)
    
    # 输出JSON格式
    print(json.dumps(fixed_metadata, ensure_ascii=False))
