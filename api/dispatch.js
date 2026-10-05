// POST /api/dispatch → GitHub Actions "Auto Sync from Google Drive" 수동 실행
// 필요 환경변수(Vercel Dashboard → Settings → Environment Variables): GH_TOKEN
//   - Fine-grained PAT, 대상 repo(macro-viewer)에 Actions: Read and write
const OWNER = "sszzbyun";
const REPO = "macro-viewer";
const WORKFLOW = "deploy.yml";
const COOLDOWN_MS = 5 * 60 * 1000; // 5분 내 중복 실행 방지

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.status(405).json({ ok: false, error: "POST only" });
    return;
  }

  const token = process.env.GH_TOKEN;
  if (!token) {
    res.status(500).json({ ok: false, error: "GH_TOKEN 미설정 (Vercel 환경변수 확인)" });
    return;
  }

  const apiBase = `https://api.github.com/repos/${OWNER}/${REPO}/actions`;
  const headers = {
    Authorization: `Bearer ${token}`,
    Accept: "application/vnd.github+json",
    "Content-Type": "application/json",
  };

  try {
    // 최근 실행 확인 → 쿨다운 중이면 실행 없이 안내
    const runsRes = await fetch(`${apiBase}/workflows/${WORKFLOW}/runs?per_page=1`, { headers });
    if (runsRes.ok) {
      const runs = await runsRes.json();
      const latest = runs.workflow_runs && runs.workflow_runs[0];
      if (latest && latest.created_at) {
        const age = Date.now() - new Date(latest.created_at).getTime();
        if (age < COOLDOWN_MS) {
          const waitSec = Math.ceil((COOLDOWN_MS - age) / 1000);
          res.status(200).json({ ok: false, cooldown: true, waitSec });
          return;
        }
      }
    }

    const r = await fetch(`${apiBase}/workflows/${WORKFLOW}/dispatches`, {
      method: "POST",
      headers,
      body: JSON.stringify({ ref: "main" }),
    });

    if (r.status === 204) {
      res.status(200).json({ ok: true });
    } else {
      res.status(502).json({ ok: false, error: `GitHub API ${r.status}: ${await r.text()}` });
    }
  } catch (e) {
    res.status(502).json({ ok: false, error: String(e && e.message || e) });
  }
};
