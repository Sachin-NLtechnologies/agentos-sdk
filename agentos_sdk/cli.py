import argparse, importlib, sys
from . import AgentOS
from . import config as C

def load_agent(package):
    if not package:
        raise SystemExit("agentos.toml [agent].package missing")
    mod = importlib.import_module(package)
    manifest = getattr(mod, 'MANIFEST', None)
    dispatch = getattr(mod, 'dispatch', None)
    if manifest is None or dispatch is None:
        raise SystemExit(f"package '{package}' must export MANIFEST and dispatch")
    return manifest, dispatch

def cmd_login(a):
    path = C.save_credentials(a.url.rstrip('/'), a.key)
    print(f"saved credentials -> {path}")

def cmd_status(a):
    r = C.resolve(a.config)
    print(f"url={r['url']} key={'set' if r['key'] else 'MISSING'} package={r['package']}")

def cmd_run(a):
    r = C.resolve(a.config)
    if not r['key']: raise SystemExit("no key. run: agentos login --url <u> --key aos_...")
    manifest, dispatch = load_agent(r['package'])
    print(f"[agentos] running {manifest.get('agent_id')} -> {r['url']}")
    AgentOS(url=r['url'], key=r['key']).run(manifest, dispatch)

def cmd_new(a):
    from .scaffold import new_agent
    dest, pkg = new_agent(a.name, a.type, a.dir)
    print(f"scaffolded {a.name} -> {dest} (package {pkg})")
    if a.type == "headless":
        print(
            f"\nnext:\n"
            f"  cd {dest}\n"
            f"  pip install -e .\n"
            f"  python -m agentos_sdk login --url <platform-url> --key aos_...\n"
            f"  python -m agentos_sdk run\n"
            f"\n(tip: 'agentos' is an alias for 'python -m agentos_sdk' — use the latter if agentos isn't on PATH)"
        )
    else:  # full / full-ai
        print(
            f"\nnext:\n"
            f"  1. cd {dest}                        <- IMPORTANT: run compose from INSIDE this folder\n"
            f"  2. copy your provisioned .env into {dest}/.env\n"
            f"  3. local dev: docker compose --env-file .env up -d --build\n"
            f"     deploy:    docker compose -f docker-compose.prod.yml --env-file .env up -d --build\n"
            f"  4. platform dashboard -> '{a.name}' turns ONLINE within ~30s -> click Run\n"
            f"\n(tip: if 'agentos' isn't found, use: python -m agentos_sdk ...)\n"
            f"(tip: see README.md in {dest}/ for full setup and troubleshooting)"
        )

def build_parser():
    p = argparse.ArgumentParser(prog='agentos')
    p.add_argument('--config', default='agentos.toml')
    sub = p.add_subparsers(dest='cmd', required=True)
    lp = sub.add_parser('login'); lp.add_argument('--url', required=True); lp.add_argument('--key', required=True); lp.set_defaults(fn=cmd_login)
    sp = sub.add_parser('status'); sp.set_defaults(fn=cmd_status)
    rp = sub.add_parser('run'); rp.set_defaults(fn=cmd_run)
    
    np = sub.add_parser('new')
    np.add_argument('name')
    np.add_argument('--type', default='headless')   # headless | full | full-ai
    np.add_argument('--dir', default='.')
    np.set_defaults(fn=cmd_new)
    
    return p

def main(argv=None):
    args = build_parser().parse_args(argv)
    args.fn(args)

if __name__ == '__main__':
    main(sys.argv[1:])
