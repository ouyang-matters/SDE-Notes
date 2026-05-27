"""Pull SDE project from Overleaf into the local working tree.

Strategy: additive merge.
  - For each file present on Overleaf: write/overwrite the local file.
  - Files only in local (e.g. WIP drafts not yet on Overleaf, .git, .olauth,
    backups, build artifacts) are left untouched.
  - Deletions on Overleaf are NOT propagated to local; if you want to drop a
    file locally, do it by hand or via git.

Usage:
  py scripts/sync_pull.py            # dry run (show what would change)
  py scripts/sync_pull.py --apply    # actually pull
"""
import pickle, sys, os, pathlib, hashlib, zipfile, io

os.environ['PYTHONIOENCODING'] = 'utf-8'
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import pyoverleaf

ROOT = pathlib.Path(__file__).resolve().parent.parent
OLAUTH = ROOT / '.olauth'
PROJECT_ID = '688782544e7f993835152bb7'
APPLY = '--apply' in sys.argv


def load_api():
    with open(OLAUTH, 'rb') as f:
        data = pickle.load(f)
    api = pyoverleaf.Api()
    api.login_from_cookies({"overleaf_session2": data['cookie']['overleaf_session2']})
    return api


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:12]


def main():
    api = load_api()

    print(f'Downloading project {PROJECT_ID} ...')
    zip_bytes = api.download_project(PROJECT_ID)

    new_files = []     # not present locally
    changed_files = [] # present, content differs
    same_files = 0

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            # Overleaf paths are like "SDE/01-brownian-motion/I.tex"
            # The leading SDE/ wraps everything; strip it.
            rel = info.filename
            if rel.startswith('SDE/'):
                rel = rel[len('SDE/'):]
            elif rel == 'SDE':
                continue
            local_path = ROOT / rel
            remote_content = zf.read(info)
            if local_path.exists():
                local_content = local_path.read_bytes()
                if local_content == remote_content:
                    same_files += 1
                else:
                    changed_files.append((rel, local_content, remote_content))
            else:
                new_files.append((rel, remote_content))

    print()
    print(f'=== Pull plan ({"APPLY" if APPLY else "DRY RUN"}) ===')
    print(f'  unchanged: {same_files}')
    print(f'  changed:   {len(changed_files)}')
    for rel, lc, rc in changed_files:
        print(f'    M  {rel}  (local sha {sha256(lc)} -> remote sha {sha256(rc)})')
    print(f'  new (only on Overleaf): {len(new_files)}')
    for rel, rc in new_files:
        print(f'    +  {rel}  (sha {sha256(rc)})')

    if not APPLY:
        print('\n(dry run — re-run with --apply to write changes)')
        return

    print('\n=== Writing ===')
    for rel, _, rc in changed_files:
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(rc)
        print(f'  M  {rel}')
    for rel, rc in new_files:
        p = ROOT / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(rc)
        print(f'  +  {rel}')
    print('Done.')


if __name__ == '__main__':
    main()
