"""구글 문서 export HTML → 반응형 단일 웹페이지 변환.
사용법: python scripts/convert-gdoc.py <입력.html> <출력.html> [제목]
"""
import re
import sys
import html as H
from html.parser import HTMLParser

KEEP = {"h1", "h2", "h3", "p", "ul", "ol", "li", "table", "thead", "tbody",
        "tr", "th", "td", "strong", "b", "em", "i", "u", "a", "br", "hr",
        "blockquote", "sup", "sub"}

class Sanitizer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.skip = 0  # style/script 건너뜀

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self.skip += 1
            return
        if tag in KEEP:
            if tag == "a":
                href = dict(attrs).get("href", "")
                href = H.escape(href, quote=True)
                self.out.append(f'<a href="{href}" target="_blank" rel="noopener">')
            elif tag in ("br", "hr"):
                self.out.append(f"<{tag}>")
            else:
                self.out.append(f"<{tag}>")

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self.skip = max(0, self.skip - 1)
            return
        if tag in KEEP and tag not in ("br", "hr"):
            self.out.append(f"</{tag}>")

    def handle_data(self, data):
        if self.skip:
            return
        if data.strip():
            self.out.append(H.escape(data))

def convert(src_path, dst_path, title=None):
    raw = open(src_path, encoding="utf-8").read()
    m = re.search(r"<body.*?>(.*)</body>", raw, re.S)
    body = m.group(1) if m else raw

    s = Sanitizer()
    s.feed(body)
    content = "".join(s.out)

    # 빈 문단 정리 + 테이블 반응형 래핑
    content = re.sub(r"<p>\s*</p>", "", content)
    content = content.replace("<table>", '<div class="table-wrap"><table>')
    content = content.replace("</table>", "</table></div>")

    # 제목: 인자 > 첫 번째 h1 텍스트 > 파일명
    if not title:
        h1 = re.search(r"<h1>(.*?)</h1>", content, re.S)
        if h1:
            title = H.unescape(re.sub(r"<[^>]+>", "", h1.group(1))).strip()[:80]
    if not title:
        title = "브리핑"

    # 목차 (h1/h2 기준)
    toc_items = []
    def add_id(m):
        tag, inner = m.group(1), m.group(2)
        text = H.unescape(re.sub(r"<[^>]+>", "", inner)).strip()
        aid = f"sec-{len(toc_items)}"
        toc_items.append((tag, text, aid))
        return f"<{tag} id=\"{aid}\">{inner}</{tag}>"
    content = re.sub(r"<(h[12])>(.*?)</\1>", add_id, content, flags=re.S)

    toc = ""
    if toc_items:
        toc = '<nav class="toc"><div class="toc-title">목차</div><ul>' + "".join(
            f'<li class="toc-{t}"><a href="#{a}">{H.escape(x[:60])}</a></li>'
            for t, x, a in toc_items) + "</ul></nav>"

    page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{H.escape(title)}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; background: #f1f5f9; color: #0f172a;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR", sans-serif;
    line-height: 1.75; }}
  .page {{ max-width: 880px; margin: 0 auto; padding: 24px 20px 64px; }}
  .doc-head {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: #fff;
    border-radius: 16px; padding: 28px 24px; margin-bottom: 20px; }}
  .doc-head h1 {{ margin: 0; font-size: 1.35rem; line-height: 1.5; }}
  .doc-head .date {{ display: inline-block; margin-top: 10px; font-size: 0.8rem;
    background: rgba(255,255,255,.2); padding: 3px 10px; border-radius: 9999px; }}
  .toc {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 16px 20px; margin-bottom: 20px; }}
  .toc-title {{ font-weight: 700; font-size: 0.9rem; margin-bottom: 8px; }}
  .toc ul {{ margin: 0; padding-left: 18px; }}
  .toc li {{ margin: 4px 0; font-size: 0.88rem; }}
  .toc-h2 {{ margin-left: 12px; }}
  .toc a {{ color: #1d4ed8; text-decoration: none; }}
  .toc a:hover {{ text-decoration: underline; }}
  .card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 20px 22px; margin-bottom: 16px; }}
  .card h1 {{ font-size: 1.2rem; margin: 0 0 12px; padding-bottom: 10px;
    border-bottom: 2px solid #dbeafe; color: #1e3a8a; }}
  .card h2 {{ font-size: 1.02rem; margin: 18px 0 8px; color: #1e40af; }}
  .card h3 {{ font-size: 0.95rem; margin: 14px 0 6px; }}
  .card p {{ margin: 8px 0; font-size: 0.93rem; }}
  .card ul, .card ol {{ padding-left: 20px; margin: 8px 0; font-size: 0.93rem; }}
  .card li {{ margin: 4px 0; }}
  .table-wrap {{ overflow-x: auto; margin: 12px 0; border: 1px solid #e2e8f0; border-radius: 8px; }}
  table {{ border-collapse: collapse; width: 100%; min-width: 560px; font-size: 0.85rem; }}
  th, td {{ border: 1px solid #e2e8f0; padding: 8px 10px; text-align: left; }}
  th {{ background: #eff6ff; font-weight: 700; white-space: nowrap; }}
  tr:nth-child(even) td {{ background: #f8fafc; }}
  a {{ color: #1d4ed8; }}
  @media (max-width: 640px) {{
    .page {{ padding: 12px 12px 48px; }}
    .doc-head {{ padding: 20px 16px; border-radius: 12px; }}
    .doc-head h1 {{ font-size: 1.1rem; }}
    .card {{ padding: 14px 15px; }}
  }}
</style>
</head>
<body>
<div class="page">
  <header class="doc-head"><h1>{H.escape(title)}</h1></header>
  {toc}
  <article class="card">
  {content}
  </article>
</div>
</body>
</html>"""

    # 본문을 섹션 카드로 분할 (h1 기준)
    parts = re.split(r"(?=<h1[^>]*>)", content)
    if len(parts) > 1:
        body_html = "".join(
            f'<section class="card">{p}</section>' if p.strip().startswith("<h1") else p
            for p in parts if p.strip()
        )
        page = page.replace(f"<article class=\"card\">\n  {content}\n  </article>",
                            body_html)

    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"[Success] {dst_path} ({len(page)} chars, TOC {len(toc_items)}개)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python scripts/convert-gdoc.py <입력.html> <출력.html> [제목]")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
