#!/usr/bin/env python3
"""Reject invalid CMS articles before replacing the published site."""
import datetime, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def validate(data):
    if not isinstance(data, dict) or not isinstance(data.get('posts'), list):
        raise ValueError('blog/posts.json must contain a posts list')
    slugs = set()
    for index, post in enumerate(data['posts'], 1):
        if not isinstance(post, dict):
            raise ValueError(f'Post {index}: invalid entry')
        slug = post.get('slug', '')
        if not isinstance(slug, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug) or len(slug) > 200:
            raise ValueError(f'Post {index}: URL名は半角英小文字・数字・ハイフンで入力してください')
        if slug in slugs:
            raise ValueError(f'Post {index}: URL名 {slug} が重複しています')
        slugs.add(slug)
        for key in ('title', 'excerpt', 'body'):
            if not isinstance(post.get(key), str) or not post[key].strip():
                raise ValueError(f'Post {index}: {key} を入力してください')
        date = post.get('date', '')
        if not isinstance(date, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date):
            raise ValueError(f'Post {index}: 日付は YYYY-MM-DD 形式にしてください')
        datetime.date.fromisoformat(date)
    return len(slugs)

if __name__ == '__main__':
    count = validate(json.loads((ROOT / 'blog/posts.json').read_text()))
    print(f'Validated {count} blog posts')
