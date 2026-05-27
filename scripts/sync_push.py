"""Push local-only or locally-changed files up to Overleaf.

Use this after editing locally (or when Claude/another tool writes files) and
you want those changes to appear in Overleaf too. Pull first if you've also
been editing on Overleaf.

Strategy:
  - Walk local SDE working tree, skipping .git, scripts/, .olauth, backups,
    LaTeX build artifacts.
  - For each local file: compare against Overleaf's copy.
    * If Overleaf has the same content, do nothing.
    * If Overleaf has a different version, delete remote then re-upload.
    * If Overleaf doesn't have it at all, create parent folders as needed
      and upload.
  - Files that exist on Overleaf but not locally are NOT deleted on Overleaf.
    (If you actually want a remote delete, do it in the Overleaf UI.)

Usage:
  py scripts/sync_push.py            # dry run
  py scripts/sync_push.py --apply    # do it
"""
import pickle, sys, os, pathlib, hashlib

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

# Skip these from local walk — not lecture content, shouldn't be on Overleaf
SKIP_DIRS = {'.git', 'scripts', '__pycache__'}
SKIP_FILE_PREFIXES = ('.olauth', '.overleaf-backup-')
SKIP_FILE_NAMES = {'.gitignore', 'sync.ps1'}
SKIP_EXTS = {'.aux', '.log', '.out', '.toc', '.bbl', '.bcf', '.blg', '.run.xml',
             '.synctex.gz', '.fls', '.fdb_latexmk', '.pyc'}

# Text extensions where CRLF vs LF should be normalized when comparing
TEXT_EXTS = {'.tex', '.md', '.bib', '.sty', '.py', '.cls', '.bst', '.txt'}


def _undo_mojibake(b: bytes) -> bytes:
    """pyoverleaf decodes doc text as Latin-1 then re-encodes UTF-8, double-encoding
    multi-byte chars (e.g. local UTF-8 `\\xe5\\xb8\\x83` becomes remote `\\xc3\\xa5\\xc2\\xb8\\xc2\\x83`).
    Reverse it: decode-utf8 then encode-latin1. ASCII is unaffected (round-trips).
    Real binary (images) fails decode-utf8 and is returned as-is."""
    try:
        return b.decode('utf-8').encode('latin-1')
    except (UnicodeDecodeError, UnicodeEncodeError):
        return b


def normalize_for_compare(content: bytes, suffix: str) -> bytes:
    """For text files, undo pyoverleaf's mojibake then normalize line endings."""
    if suffix.lower() in TEXT_EXTS:
        return _undo_mojibake(content).replace(b'\r\n', b'\n').replace(b'\r', b'\n')
    return content


def load_api():
    with open(OLAUTH, 'rb') as f:
        data = pickle.load(f)
    api = pyoverleaf.Api()
    api.login_from_cookies({"overleaf_session2": data['cookie']['overleaf_session2']})
    return api


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()[:12]


def walk_local():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        # Mutate dirnames to skip
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        for fn in filenames:
            if fn in SKIP_FILE_NAMES:
                continue
            if any(fn.startswith(p) for p in SKIP_FILE_PREFIXES):
                continue
            if pathlib.Path(fn).suffix in SKIP_EXTS:
                continue
            full = pathlib.Path(dirpath) / fn
            rel = full.relative_to(ROOT).as_posix()
            yield rel, full


def find_child(folder, name):
    for c in folder.children:
        if c.name == name:
            return c
    return None


def find_by_path(start, path):
    parts = [p for p in path.split('/') if p]
    cur = start
    for p in parts:
        nxt = find_child(cur, p)
        if nxt is None:
            return None
        cur = nxt
    return cur


def ensure_folder_path(api, root, sde_folder, relpath):
    """Create folders as needed; return the final folder entity."""
    parts = relpath.split('/')
    cur = sde_folder
    for part in parts:
        nxt = find_child(cur, part)
        if nxt is None:
            print(f'  MKDIR {part} in {cur.name}')
            api.project_create_folder(PROJECT_ID, cur.id, part)
            # Refresh
            root_new = api.project_get_files(PROJECT_ID)
            sde_new = find_child(root_new, 'SDE')
            cur_new = find_by_path(sde_new, '/'.join(parts[:parts.index(part)+1]) if parts.index(part) >= 0 else '')
            # Just re-resolve from scratch
            root = root_new
            sde_folder = sde_new
            cur = find_by_path(sde_folder, '/'.join(parts[:parts.index(part)+1]))
        else:
            cur = nxt
    return root, sde_folder, cur


def main():
    api = load_api()
    root = api.project_get_files(PROJECT_ID)
    sde_folder = find_child(root, 'SDE')
    if sde_folder is None:
        print('ERROR: SDE/ folder not found at Overleaf root.')
        sys.exit(1)

    to_upload = []   # (rel, full_path, remote_entity_or_None, parent_path)
    unchanged = 0

    for rel, full in walk_local():
        local_content = full.read_bytes()
        remote = find_by_path(sde_folder, rel)
        parent_path = '/'.join(rel.split('/')[:-1])  # may be ''
        if remote is None:
            to_upload.append((rel, full, None, parent_path, local_content))
        else:
            # Download remote and compare
            try:
                remote_content = api.project_download_file(PROJECT_ID, remote)
            except Exception:
                remote_content = None
            suffix = pathlib.Path(rel).suffix
            if remote_content is not None and \
               normalize_for_compare(remote_content, suffix) == \
                   normalize_for_compare(local_content, suffix):
                unchanged += 1
            else:
                to_upload.append((rel, full, remote, parent_path, local_content))

    print()
    print(f'=== Push plan ({"APPLY" if APPLY else "DRY RUN"}) ===')
    print(f'  unchanged: {unchanged}')
    print(f'  to upload: {len(to_upload)}')
    for rel, full, remote, parent_path, content in to_upload:
        action = 'replace' if remote else 'create'
        print(f'    {action:7s} {rel}  ({len(content)} bytes, sha {sha256(content)})')

    if not APPLY:
        print('\n(dry run — re-run with --apply to upload)')
        return

    print('\n=== Executing ===')
    for rel, full, remote, parent_path, content in to_upload:
        # Delete old version first if it exists
        if remote is not None:
            print(f'  delete  {rel}')
            api.project_delete_entity(PROJECT_ID, remote)
        # Re-fetch
        root = api.project_get_files(PROJECT_ID)
        sde_folder = find_child(root, 'SDE')
        # Ensure parent folder chain
        if parent_path:
            root, sde_folder, parent_obj = ensure_folder_path(api, root, sde_folder, parent_path)
        else:
            parent_obj = sde_folder
        print(f'  upload  {rel}  -> folder {parent_obj.name} (id {parent_obj.id})')
        api.project_upload_file(PROJECT_ID, parent_obj.id, pathlib.Path(rel).name, content)

    print('\nDone.')


if __name__ == '__main__':
    main()
