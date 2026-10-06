"""
CI 환경(GitHub Actions)에서 실행되는 구글 드라이브 동기화 스크립트
로컬 sync.py와 별도로 경량화된 버전
"""
import os
import json
import hashlib
import shutil
import tempfile

def get_hash(filepath):
    h = hashlib.md5()
    with open(filepath, "rb") as f:
        h.update(f.read())
    return h.hexdigest()

def main():
    output_dir = "public/reports"
    cache_path = ".sync_cache.json"
    folder_url = "https://drive.google.com/drive/folders/1LBzd_bb6UjL6fcAIW2B1cUmWFG6RBtQu"

    os.makedirs(output_dir, exist_ok=True)

    # 캐시 로드
    cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    print(f"[1] 구글 드라이브에서 파일 다운로드 중: {folder_url}")

    try:
        import gdown
    except ImportError:
        print("[오류] gdown 미설치. requirements.txt 확인 필요.")
        raise SystemExit(1)

    tmp_dir = tempfile.mkdtemp(prefix="gdrive_")
    try:
        gdown.download_folder(
            url=folder_url,
            output=tmp_dir,
            quiet=False,
            use_cookies=False
        )
    except Exception as e:
        print(f"[오류] 다운로드 실패: {e}")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return

    # 다운로드된 모든 HTML 재귀 수집 (하위폴더 포함, basename 기준 평탄화)
    downloaded = {}
    for root, _dirs, filenames in os.walk(tmp_dir):
        for fname in filenames:
            if not fname.lower().endswith(".html"):
                continue
            if fname in downloaded:
                print(f"  [경고] 동명 파일 충돌, 첫 번째만 유지: {fname}")
                continue
            downloaded[fname] = os.path.join(root, fname)

    print("\n[2] 변경 파일 비교 중...")
    new_count = 0
    skip_count = 0

    for fname in sorted(downloaded.keys()):
        src = downloaded[fname]
        dst = os.path.join(output_dir, fname)
        try:
            file_hash = get_hash(src)
        except OSError as e:
            print(f"  [경고] 해시 실패, 건너뜀: {fname} ({e})")
            continue

        if fname in cache and cache[fname] == file_hash and os.path.exists(dst):
            skip_count += 1
            continue

        shutil.copy2(src, dst)
        cache[fname] = file_hash
        new_count += 1
        print(f"  [업데이트] {fname}")

    # Drive에 없는 로컬 파일은 자동 삭제하지 않고 후보로만 보고
    # (gdown 부분 다운로드 실패 시误删 방지)
    downloaded_names = set(downloaded.keys())
    for local in sorted(os.listdir(output_dir)):
        if local.lower().endswith(".html") and local not in downloaded_names:
            print(f"  [확인필요] Drive에 없음 (로컬 유지): {local}")

    shutil.rmtree(tmp_dir, ignore_errors=True)

    # 캐시 저장
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

    print(f"\n[완료] 신규/변경: {new_count}개 | 스킵: {skip_count}개")

if __name__ == "__main__":
    main()
