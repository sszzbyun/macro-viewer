"""마크다운 → doc-to-web 스킬 양식 단일 HTML 변환.
사용법: python scripts/md-to-web.py <입력.md> <출력.html> [제목]
"""
import re
import sys
import html as H

def inline(text):
    text = H.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener" class="text-blue-600 dark:text-blue-400 hover:underline">\1</a>', text)
    text = re.sub(r"`([^`]+)`", r'<code class="px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-800 text-sm font-mono">\1</code>', text)
    return text

def is_table_sep(line):
    return bool(re.match(r"^\s*\|?[\s:\-|]+\|?\s*$", line)) and "-" in line

def md_to_html(md):
    lines = md.split("\n")
    out, toc = [], []
    i, sec = 0, 0
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    while i < len(lines):
        line = lines[i].rstrip()
        s = line.strip()

        if not s:
            close_list()
            i += 1
            continue
        if re.match(r"^---+$", s):
            close_list()
            out.append('<hr class="my-8 border-slate-200 dark:border-slate-700">')
            i += 1
            continue

        m = re.match(r"^(#{1,4})\s+(.*)", s)
        if m:
            close_list()
            lv, text = len(m.group(1)), inline(m.group(2))
            if lv == 1:
                out.append(f'<h1 class="text-2xl font-extrabold tracking-tight mt-2 mb-4">{text}</h1>')
            elif lv == 2:
                aid = f"sec-{sec}"; sec += 1
                toc.append((2, re.sub(r"<[^>]+>", "", m.group(2))[:60], aid))
                out.append(f'<h2 id="{aid}" class="text-xl font-bold mt-10 mb-4 pb-2 border-b border-slate-200 dark:border-slate-700 scroll-mt-24">{text}</h2>')
            elif lv == 3:
                aid = f"sec-{sec}"; sec += 1
                toc.append((3, re.sub(r"<[^>]+>", "", m.group(2))[:60], aid))
                out.append(f'<h3 id="{aid}" class="text-lg font-semibold mt-8 mb-3 scroll-mt-24">{text}</h3>')
            else:
                out.append(f'<h4 class="font-semibold mt-6 mb-2">{text}</h4>')
            i += 1
            continue

        # 테이블
        if "|" in s and i + 1 < len(lines) and is_table_sep(lines[i + 1]):
            close_list()
            headers = [c.strip() for c in s.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and "|" in lines[i].strip() and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in headers)
            tr = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            out.append(f'<div class="overflow-x-auto my-6 rounded-xl border border-slate-200 dark:border-slate-700"><table class="w-full text-sm min-w-[720px]"><thead class="bg-slate-100 dark:bg-slate-800"><tr>{th}</tr></thead><tbody class="divide-y divide-slate-200 dark:divide-slate-700">{tr}</tbody></table></div>')
            continue

        m = re.match(r"^[*\-]\s+(.*)", s)
        if m:
            if not in_list:
                out.append('<ul class="my-4 space-y-2">')
                in_list = True
            out.append(f'<li class="leading-relaxed">{inline(m.group(1))}</li>')
            i += 1
            continue

        close_list()
        out.append(f'<p class="my-3 leading-7 text-[0.95rem]">{inline(s)}</p>')
        i += 1

    close_list()
    return "\n".join(out), toc

TEMPLATE_TOP = """<!DOCTYPE html>
<html lang="ko" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>__TITLE__</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = { darkMode: 'class', theme: { extend: { fontFamily: { sans: ['Pretendard','-apple-system','BlinkMacSystemFont','system-ui','Roboto','sans-serif'] } } } };
  </script>
  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
  <style>table th,table td{padding:.65rem .8rem;text-align:left;vertical-align:top}table tbody tr:nth-child(even){background:rgba(148,163,184,.08)}</style>
</head>
<body class="bg-slate-50 text-slate-800 dark:bg-slate-900 dark:text-slate-100 min-h-screen transition-colors duration-200 antialiased font-sans">
  <header class="sticky top-0 z-50 backdrop-blur-md bg-white/80 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800">
    <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between gap-3">
      <div class="font-bold text-base sm:text-lg tracking-tight truncate">__TITLE__</div>
      <div class="flex items-center gap-2 shrink-0">
        <button onclick="copyDocument()" class="px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition">내용 복사</button>
        <button onclick="toggleTheme()" class="p-2 rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition" aria-label="테마 전환">🌓</button>
      </div>
    </div>
  </header>
  <div class="max-w-6xl mx-auto px-4 py-8 flex flex-col lg:flex-row gap-8">
    <aside class="lg:block w-full lg:w-64 shrink-0 order-2 lg:order-1">
      <nav class="lg:sticky lg:top-24 space-y-1.5 text-sm text-slate-600 dark:text-slate-400 bg-white dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-xl p-4" id="toc-nav">
        <div class="font-bold text-slate-800 dark:text-slate-100 mb-2">목차</div>
__TOC__
      </nav>
    </aside>
    <main id="document-content" class="flex-1 max-w-3xl order-1 lg:order-2 min-w-0">
__BODY__
    </main>
  </div>
  <div id="toast" class="fixed bottom-5 right-5 bg-slate-900 text-white dark:bg-white dark:text-slate-900 px-4 py-2 rounded-lg shadow-lg text-sm transition-opacity duration-300 opacity-0 pointer-events-none">클립보드에 복사되었습니다.</div>
  <script>
    function toggleTheme(){const h=document.documentElement;if(h.classList.contains('dark')){h.classList.remove('dark');localStorage.setItem('theme','light');}else{h.classList.add('dark');localStorage.setItem('theme','dark');}}
    if(localStorage.getItem('theme')==='dark'||(!('theme' in localStorage)&&window.matchMedia('(prefers-color-scheme: dark)').matches)){document.documentElement.classList.add('dark');}
    function copyDocument(){const t=document.getElementById('document-content').innerText;navigator.clipboard.writeText(t).then(()=>showToast('문서 본문이 복사되었습니다.'));}
    function showToast(m){const t=document.getElementById('toast');t.innerText=m;t.classList.remove('opacity-0');setTimeout(()=>t.classList.add('opacity-0'),2000);}
  </script>
</body>
</html>
"""

def convert(src, dst, title=None):
    md = open(src, encoding="utf-8").read()
    if not title:
        m = re.search(r"^#\s+(.*)", md, re.M)
        title = m.group(1).strip()[:80] if m else "브리핑"
    body, toc = md_to_html(md)
    toc_html = "\n".join(
        f'<a href="#{a}" class="block hover:text-blue-600 dark:hover:text-blue-400 transition{" ml-3" if lv==3 else ""}">{H.escape(x)}</a>'
        for lv, x, a in toc)
    page = TEMPLATE_TOP.replace("__TITLE__", H.escape(title)).replace("__TOC__", toc_html).replace("__BODY__", body)
    open(dst, "w", encoding="utf-8").write(page)
    print(f"[Success] {dst} ({len(page)} chars, TOC {len(toc)}개)")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python scripts/md-to-web.py <입력.md> <출력.html> [제목]")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
