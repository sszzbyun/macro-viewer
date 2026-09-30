const fs = require('fs');
const path = require('path');

const reportsDir = path.join(__dirname, '../public/reports');
const outputFile = path.join(__dirname, '../public/reports.json');

if (!fs.existsSync(reportsDir)) {
  fs.mkdirSync(reportsDir, { recursive: true });
}

const files = fs.readdirSync(reportsDir).filter(file => file.toLowerCase().endsWith('.html'));

const reports = files.map(filename => {
  const filePath = path.join(reportsDir, filename);
  const content = fs.readFileSync(filePath, 'utf-8');

  // 1. <title> 태그 추출 (없으면 파일명에서 확장자 제거)
  const titleMatch = content.match(/<title[^>]*>(.*?)<\/title>/i);
  const title = titleMatch ? titleMatch[1].trim() : filename.replace(/\.html$/i, '');

  // 2. 날짜 추출 (YYYY.MM.DD, YYYY-MM-DD, YYYY_MM_DD 등 지원)
  const dateMatch = (filename + " " + title).match(/(20\d{2})[.\-_\s]*(\d{1,2})[.\-_\s]*(\d{1,2})/);
  let dateStr = "";

  if (dateMatch) {
    const year = dateMatch[1];
    const month = dateMatch[2].padStart(2, '0');
    const day = dateMatch[3].padStart(2, '0');
    dateStr = `${year}-${month}-${day}`;
  } else {
    // 날짜가 전혀 없을 경우 파일 생성/수정 시간 기준으로 fallback
    const stats = fs.statSync(filePath);
    dateStr = stats.mtime.toISOString().split('T')[0];
  }

  return {
    filename,
    title,
    date: dateStr,
    url: `reports/${encodeURIComponent(filename)}`
  };
});

// 최신 일자순 정렬 (동일 일자면 제목순)
reports.sort((a, b) => b.date.localeCompare(a.date) || a.title.localeCompare(b.title));

fs.writeFileSync(outputFile, JSON.stringify(reports, null, 2), 'utf-8');
console.log(`[Success] Indexed ${reports.length} report(s) into ${outputFile}`);
