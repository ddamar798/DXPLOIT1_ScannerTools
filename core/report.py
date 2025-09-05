from core.utils import save_json, now_iso, ensure_dir
import os


RESULTS_DIR = os.path.join('data', 'results')




def store_result(target: str, phase: str, data: dict) -> str:
ensure_dir(RESULTS_DIR)
filename = f"{target.replace(':','_')}_{phase}_{now_iso().replace(':','-')}.json"
path = os.path.join(RESULTS_DIR, filename)
save_json(path, data)
return path