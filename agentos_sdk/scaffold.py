import re, shutil
from pathlib import Path

TEMPLATES = Path(__file__).parent / "templates"

def _pkg_name(name):
    p = re.sub(r"[^0-9a-zA-Z_]", "_", name).lower()
    return ("a_"+p) if p[0].isdigit() else p

def new_agent(name, type_="headless", target_dir="."):
    src = TEMPLATES / type_
    if not src.exists():
        raise SystemExit(f"unknown template type: {type_}")
    pkg = _pkg_name(name)
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    dest = Path(target_dir) / slug
    if dest.exists(): raise SystemExit(f"{dest} already exists")
    shutil.copytree(src, dest)
    
    # Rename package directory if it exists
    if (dest / "pkg").exists():
        (dest / "pkg").rename(dest / pkg)
    if (dest / "backend" / "pkg").exists():
        (dest / "backend" / "pkg").rename(dest / "backend" / pkg)
        
    for f in dest.rglob("*"):
        if f.is_file():
            try:
                content = f.read_text(encoding="utf-8")
                new_content = content.replace("__AGENT_ID__", name).replace("__PKG__", pkg).replace("__SLUG__", slug)
                if new_content != content:
                    f.write_text(new_content, encoding="utf-8")
            except UnicodeDecodeError:
                # Skip binary files if any
                pass
    return dest, pkg
