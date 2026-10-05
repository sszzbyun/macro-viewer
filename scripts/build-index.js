const fs = require('fs');
const path = require('path');

const reportsDir = path.join(__dirname, '../public/reports');
const outputFile = path.join(__dirname, '../public/reports.json');

if (!fs.existsSync(reportsDir)) {
  fs.mkdirSync(reportsDir, { recursive: true });
}

// HTML 엔티티 디코드 (reports.json에는 디코드된 원문을 저장, 표시는 index.html escapeHtml이 담당)
function decodeEntities(str) {
  return str
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(Number(n)));
}

const files = fs.readdirSync(reportsDir).filter(file => file.toLowerCase().endsWith('.html'));

const reports = [];
for (const filename of files) {
  const filePath = path.join(reportsDir, filename);
  let content;
  try {
    content = fs.readFileSync(filePath, 'utf-8');
  } catch (e) {
    console.warn(`[Warn] 읽기 실패, 건너뜀: ${filename} (${e.message})`);
    continue;
  }

  // 1. <title> 태그 추출 (없으면 파일명에서 확장자 제거)
  //    태그 제거 + 엔티티 디코드 + 공백 정규화
  const titleMatch = content.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  let title = titleMatch ? titleMatch[1].replace(/<[^>]*>/g, '') : filename.replace(/\.html$/i, '');
  title = decodeEntities(title).replace(/\s+/g, ' ').trim() || filename.replace(/\.html$/i, '');

  // 2. 날짜 추출 (YYYY.MM.DD, YYYY-MM-DD, YYYY_MM_DD 등 지원, 월 1-12 / 일 1-31 검증)
  //    날짜가 없으면 빈 문자열 → 목록 하단 "상시자료"로 표시 (mtime fallback 폐지: 재빌드마다 날짜가 바뀌는 문제)
  const dateMatch = (filename + " " + title).match(/(20\d{2})[.\-_\s]*(\d{1,2})[.\-_\s]*(\d{1,2})/);
  let dateStr = "";

  if (dateMatch) {
    const month = Number(dateMatch[2]);
    const day = Number(dateMatch[3]);
    if (month >= 1 && month <= 12 && day >= 1 && day <= 31) {
      dateStr = `${dateMatch[1]}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    }
  }
  if (!dateStr) {
    console.warn(`[Warn] 날짜 없음 → 상시자료로 분류: ${filename}`);
  }

  // 3. 시리즈 추출 ([미장이], [따블] 등 접두 → 필터 칩용, 없으면 "기타")
  const seriesMatch = filename.match(/^\s*\[([^\]]+)\]/) || title.match(/^\s*\[([^\]]+)\]/);
  const series = seriesMatch ? seriesMatch[1].trim() : "기타";

  reports.push({
    filename,
    title,
    date: dateStr,
    series,
    url: `reports/${encodeURIComponent(filename)}`
  });
}

// 정렬: 날짜 있는 것 최신순 → 날짜 없는 것(상시)은 하단에 파일명순
reports.sort((a, b) => {
  if (a.date && b.date) return b.date.localeCompare(a.date) || a.filename.localeCompare(b.filename, 'ko');
  if (a.date) return -1;
  if (b.date) return 1;
  return a.filename.localeCompare(b.filename, 'ko');
});

fs.writeFileSync(outputFile, JSON.stringify(reports, null, 2), 'utf-8');
console.log(`[Success] Indexed ${reports.length} report(s) into ${outputFile}`);
