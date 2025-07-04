#!/usr/bin/env python3

import sys, argparse, json
from pathlib import Path
from utils import get_articles, Article, load_template, ENCODE

RSS_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>静カニのブログ</title>
  <link>https://shizukani-cp.github.io/blog/</link>
  <language>ja-jp</language>
  <description>静カニのブログ</description>
  {items}
</channel>
</rss>
"""

def execute(arg):

    if arg.template is None:
        arg.template = open(Path(arg.top_dir) / "template.html", "r", encoding=ENCODE)

    template = load_template(arg.template)

    articles = [Article(Path(fname)) for fname in get_articles(arg.top_dir)]

    if len(articles) == 0:
        sys.exit("記事がありません")

    configs = []
    for article in articles:
        article.html_save(template)
        configs.append(article.config)

    with open(Path(arg.top_dir) / "scripts" / "articles.json.js", "w", encoding=ENCODE) as f:
        f.write(f"window.articles = JSON.parse('{json.dumps(configs, ensure_ascii=False)}');")

    with open(Path(arg.top_dir) / "rss.xml", "w", encoding=ENCODE) as f:
        f.write(RSS_TEMPLATE.format(items="\n".join([article.get_rss() for article in articles])))

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("top_dir", default=".")
    parser.add_argument("--template", "-t", type=argparse.FileType("r", encoding=ENCODE))

    args = parser.parse_args()

    execute(args)
