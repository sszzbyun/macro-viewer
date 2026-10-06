---
name: doc-to-web
description: Converts raw text, markdown, meeting notes, reports, and planning documents into an interactive, single-file HTML web page. Use when the user invokes /doc2web, /html, "웹페이지로 만들어줘", or "단일 HTML로 변환해줘", or wants any written content as a shareable HTML file.
---

# Doc to Web

Converts raw text, markdown, meeting notes, reports, and planning documents into an interactive, beautifully designed, single-file HTML web page that can be opened directly in any browser without build tools.

## When to Use

- When the user wants to convert markdown, text, or reports into a web page or HTML file.
- When the user invokes triggers such as `/doc2web`, `/html`, "웹페이지로 만들어줘", or "단일 HTML로 변환해줘".
- When an immediate, shareable, single-file HTML presentation of written content is needed.

## Guidelines and Execution Rules

### 1. Persona and Execution
- Act as a senior full-stack web publisher and UI/UX designer.
- Execute directly without asking redundant clarifying questions. Analyze the document context (technical doc, proposal, report, blog post) and determine the optimal layout automatically.
- Output clean, production-ready, valid HTML.

### 2. Required Tech Stack
- Styling: Tailwind CSS via CDN (`https://cdn.tailwindcss.com`).
- Typography: Pretendard font via CDN (`https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css`).
- Icons: Inline SVG or Lucide Icons CDN.
- Portability: Must be completely self-contained in a single file with zero build step, fully functional when opened locally.

### 3. Layout and Key UI Features
- Sticky Header: Displays document title, dark/light mode toggle switch, and clipboard copy utility button with toast feedback.
- Dark Mode Support: Seamless theme toggling with Tailwind's `dark` class, localStorage persistence, and system preference detection.
- Navigation / TOC: For lengthy documents, generate a sticky table of contents based on H2 and H3 tags (sidebar on desktop, responsive layout on mobile).
- Visual Hierarchy: Professional typography scale, callout boxes for notes or highlights, responsive tables, and styled code blocks.

### 4. Boilerplate Architecture

```html
<!DOCTYPE html>
<html lang="ko" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>문서 제목</title>

  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Pretendard', '-apple-system', 'BlinkMacSystemFont', 'system-ui', 'Roboto', 'sans-serif'],
          }
        }
      }
    }
  </script>

  <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css" />
</head>
<body class="bg-slate-50 text-slate-800 dark:bg-slate-900 dark:text-slate-100 min-h-screen transition-colors duration-200 antialiased font-sans">

  <header class="sticky top-0 z-50 backdrop-blur-md bg-white/80 dark:bg-slate-900/80 border-b border-slate-200 dark:border-slate-800">
    <div class="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
      <div class="font-bold text-lg tracking-tight truncate max-w-md">문서 제목</div>
      <div class="flex items-center gap-2">
        <button id="copyBtn" onclick="copyDocument()" class="px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition">
          내용 복사
        </button>
        <button id="themeToggle" onclick="toggleTheme()" class="p-2 rounded-lg border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition" aria-label="테마 전환">
          🌓
        </button>
      </div>
    </div>
  </header>

  <div class="max-w-6xl mx-auto px-4 py-8 flex flex-col lg:flex-row gap-8">
    <aside class="hidden lg:block w-64 shrink-0">
      <nav class="sticky top-24 space-y-2 text-sm text-slate-600 dark:text-slate-400" id="toc-nav">
      </nav>
    </aside>

    <main id="document-content" class="flex-1 max-w-3xl prose prose-slate dark:prose-invert">
    </main>
  </div>

  <div id="toast" class="fixed bottom-5 right-5 bg-slate-900 text-white dark:bg-white dark:text-slate-900 px-4 py-2 rounded-lg shadow-lg text-sm transition-opacity duration-300 opacity-0 pointer-events-none">
    클립보드에 복사되었습니다.
  </div>

  <script>
    function toggleTheme() {
      const html = document.documentElement;
      if (html.classList.contains('dark')) {
        html.classList.remove('dark');
        localStorage.setItem('theme', 'light');
      } else {
        html.classList.add('dark');
        localStorage.setItem('theme', 'dark');
      }
    }
    if (localStorage.getItem('theme') === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    }

    function copyDocument() {
      const text = document.getElementById('document-content').innerText;
      navigator.clipboard.writeText(text).then(() => {
        showToast('문서 본문이 복사되었습니다.');
      });
    }

    function showToast(msg) {
      const toast = document.getElementById('toast');
      toast.innerText = msg;
      toast.classList.remove('opacity-0');
      setTimeout(() => toast.classList.add('opacity-0'), 2000);
    }
  </script>
</body>
</html>
```

## Gotchas

- External build dependencies must not be used; all libraries should be loaded via lightweight CDNs.
- Avoid breaking layouts on smaller viewports; ensure tables and code snippets have horizontal scrolling if needed.
- Ensure dark mode color contrast satisfies accessibility standards.
