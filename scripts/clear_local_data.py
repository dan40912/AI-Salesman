"""Explicit local reset. Stop the web server first. Never touches Codex credentials."""
import argparse,shutil
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--confirm',action='store_true');args=p.parse_args()
root=Path(__file__).resolve().parents[1]/'backend/data'
if not args.confirm:raise SystemExit('請先停止伺服器。加上 --confirm 將永久刪除本專案角色、設定、對話、上傳與音訊快取；不會更動原 V2 或 Codex 登入。')
if root.is_symlink():raise SystemExit('資料路徑不可為符號連結。')
if root.exists():shutil.rmtree(root)
print('本專案資料已清除，下次啟動會重建四個預設角色。')
