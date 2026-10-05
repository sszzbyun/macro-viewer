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
    // 날짜가 전혀 없을 경우 파일 생성/수정 시간 기준으로 fallback (비결정적이므로 경고)
    const stats = fs.statSync(filePath);
    dateStr = stats.mtime.toISOString().split('T')[0];
    console.warn(`[Warn] 날짜 없음, mtime 사용: ${filename} -> ${dateStr}`);
  }

  reports.push({
    filename,
    title,
    date: dateStr,
    url: `reports/${encodeURIComponent(filename)}`
  });
}

// 최신 일자순 정렬 (동일 일자면 파일명순 → 장전/장마감 순서 안정화)
reports.sort((a, b) => b.date.localeCompare(a.date) || a.filename.localeCompare(b.filename, 'ko'));

fs.writeFileSync(outputFile, JSON.stringify(reports, null, 2), 'utf-8');
console.log(`[Success] Indexed ${reports.length} report(s) into ${outputFile}`);
