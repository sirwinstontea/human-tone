import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from writeit.check import check
r = check(open(sys.argv[1], encoding='utf-8').read(), 'casual')
print(json.dumps(r, indent=2)); sys.exit(0 if r['ok'] else 1)
