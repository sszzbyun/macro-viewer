import os
import json
import shutil
import hashlib
import subprocess
from datetime import datetime

def find_executable(name, default_path):
    which_path = shutil.which(name)
    if which_path:
        return which_path
    if os.path.exists(default_path):
        return default_path
    return name

def get_file_hash(filepath):
    """파일의 MD5 해시 반환"""
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def load_cache(cache_path):
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_cache(cache_path, cache):
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def sync_from_google_drive(folder_url, output_dir, cache_path):
    """구글 드라이브에서 전체 다운로드 후, 실제 변경된 파일만 보관 (하위폴더 재귀 지원)"""
    try:
        import gdown
    except ImportError:
        print("  [오류] gdown이 설치되어 있지 않습니다. `pip install -r requirements.txt` 실행 필요.")
        return 0
    import tempfile

    os.makedirs(output_dir, exist_ok=True)

    # 임시 폴더에 일단 다운로드
    tmp_dir = tempfile.mkdtemp(prefix="gdrive_sync_")
    print("  → 구글 드라이브 파일 목록 확인 중 (임시 폴더 활용)...")

    try:
        gdown.download_folder(url=folder_url, output=tmp_dir, quiet=True, use_cookies=False)
    except Exception as e:
        print(f"  [경고] 다운로드 오류: {e}")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return 0

    # 다운로드된 모든 HTML 재귀 수집 (하위폴더 포함, basename 기준 평탄화)
    downloaded = {}  # basename -> src 경로
    for root, _dirs, filenames in os.walk(tmp_dir):
        for fname in filenames:
            if not fname.lower().endswith(".html"):
                continue
            src = os.path.join(root, fname)
            if fname in downloaded:
                print(f"  [경고] 동명 파일 충돌, 첫 번째만 유지: {fname} ({src} 무시)")
                continue
            downloaded[fname] = src

    cache = load_cache(cache_path)
    new_count = 0
    skip_count = 0

    for fname in sorted(downloaded.keys()):
        src = downloaded[fname]
        dst = os.path.join(output_dir, fname)
        try:
            src_hash = get_file_hash(src)
        except OSError as e:
            print(f"  [경고] 해시 실패, 건너뜀: {fname} ({e})")
            continue

        # 캐시와 비교하여 변경 없으면 건너뜀
        if fname in cache and cache[fname] == src_hash and os.path.exists(dst):
            skip_count += 1
            continue

        # 신규 또는 변경된 파일만 복사
        shutil.copy2(src, dst)
        cache[fname] = src_hash
        new_count += 1
        print(f"  → [업데이트] {fname}")

    # Drive에 없는 로컬 잔류 파일 정리 + 캐시 pruning
    downloaded_names = set(downloaded.keys())
    for stale in [k for k in list(cache.keys()) if k not in downloaded_names]:
        del cache[stale]
    for local in os.listdir(output_dir):
        if local.lower().endswith(".html") and local not in downloaded_names:
            os.remove(os.path.join(output_dir, local))
            print(f"  → [삭제] Drive에 없어 로컬에서 제거: {local}")

    save_cache(cache_path, cache)
    shutil.rmtree(tmp_dir, ignore_errors=True)

    if new_count == 0:
        print(f"  → 새 파일 없음 ({skip_count}개 파일 이미 최신 상태)")
    else:
        print(f"  → 신규/변경 파일 {new_count}개 반영 완료! ({skip_count}개 건너뜀)")

    return new_count

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    print("=" * 60)
    print("  매크로 리포트 아카이브 - 자동 동기화 & 배포 시스템")
    print("=" * 60)

    git_bin = find_executable("git", r"C:\Program Files\Git\cmd\git.exe")
    node_bin = find_executable("node", r"C:\Program Files\nodejs\node.exe")

    folder_url = "https://drive.google.com/drive/folders/1LBzd_bb6UjL6fcAIW2B1cUmWFG6RBtQu"
    output_dir = os.path.join(base_dir, "public", "reports")
    cache_path = os.path.join(base_dir, ".sync_cache.json")

    # 1. 구글 드라이브 동기화 (변경 파일만 반영)
    print("\n[1/3] 구글 드라이브에서 변경된 리포트 확인 중...")
    new_count = sync_from_google_drive(folder_url, output_dir, cache_path)

    # 2. 인덱싱 (shell=False: 경로 공백 문제 방지)
    print("\n[2/3] 리포트 목록 인덱싱 중...")
    try:
        subprocess.run(
            [node_bin, os.path.join("scripts", "build-index.js")],
            check=True, shell=False
        )
    except Exception as e:
        print(f"[오류] 빌드 스크립트 실패: {e}")
        return

    # 3. Git 커밋 & 푸시
    print("\n[3/3] 변경 사항 확인 및 Vercel로 전송 중...")
    try:
        subprocess.run([git_bin, "add", "public/reports/", "public/reports.json", ".sync_cache.json"], check=True)

        diff_res = subprocess.run([git_bin, "diff", "--cached", "--quiet"])
        if diff_res.returncode == 0:
            print("\n" + "=" * 60)
            print("  [안내] 새로 추가된 리포트가 없습니다. 이미 최신 상태입니다.")
            print("=" * 60)
            return

        today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        subprocess.run([git_bin, "commit", "-m", f"Auto Update: {today_str} 구글 드라이브 리포트 동기화"], check=True)
        subprocess.run([git_bin, "push", "origin", "main"], check=True)

        print("\n" + "=" * 60)
        print("  [성공] 배포 완료! 약 20~30초 후 웹사이트에 반영됩니다.")
        print("=" * 60)
    except Exception as e:
        print(f"\n[오류] Git 전송 중 오류 발생: {e}")

if __name__ == "__main__":
    main()
