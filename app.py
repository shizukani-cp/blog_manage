import sys, re, glob, json, argparse
from io import StringIO
from pathlib import Path
import yaml, markdown
from jinja2 import Template

ENCODE = "utf-8"
EXTENSIONS = ["tables"]

def get_articles(top):
    return glob.glob(f"{top}/articles/[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]/index.md")

class Article:
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self._split_config_content()
        self.md = markdown.Markdown(extensions=EXTENSIONS)

    def _split_config_content(self):
        self.mdstr = ""
        config_str = ""
        n = 0
        with open(self.filepath, "r", encoding=ENCODE) as f:
            for line in f.readlines():
                if re.fullmatch("^---+[\r\n]+", line):
                    n += 1
                    continue
                if n == 1:
                    config_str += line
                else:
                    self.mdstr += line

        with StringIO() as st:
            st.write(config_str)
            st.seek(0)
            self.config =  yaml.safe_load(st)

    def _to_html_with_template(self, template: Template) -> str :
        return template.render(
                               content=self.md.convert(self.mdstr),
                               config=self.config)

    def _get_html_file_name(self) -> Path :
        return Path(str(self.filepath.parent / self.filepath.stem) + ".html")

    def html_save(self, template: Template):
        print("saving", str(self.filepath))
        with open(self._get_html_file_name(), "w", encoding=ENCODE) as f:
            f.write(self._to_html_with_template(template))

def load_template(templatefile):
    return Template(templatefile.read())

def main(arg):
    template = load_template(arg.template)

    articles = [Article(Path(fname)) for fname in get_articles(arg.top_dir)]

    if len(articles) == 0:
        sys.exit("記事がありません")

    configs = []
    for article in articles:
        article.html_save(template)
        configs.append(article.config)

    with open(Path(arg.top_dir) / "articles.json", "w", encoding=ENCODE) as f:
        f.write(json.dumps(configs, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("top_dir")
    parser.add_argument("--template", "-t", type=argparse.FileType("r", encoding=ENCODE), default="template.html")

    args = parser.parse_args()

    main(args)
