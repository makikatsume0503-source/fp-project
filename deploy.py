#!/usr/bin/env python3
"""Xserver FTP自動デプロイスクリプト"""
import ftplib
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

FTP_HOST = os.getenv("FTP_HOST", "")
FTP_USER = os.getenv("FTP_USER", "")
FTP_PASS = os.getenv("FTP_PASS", "")
FTP_REMOTE_DIR = os.getenv("FTP_REMOTE_DIR", "/public_html")

LOCAL_ROOT = Path(__file__).parent

DEPLOY_FILES = [
    "index.html",
    "style.css",
    "favicon.svg",
    "blog/nisa-fufu-katsuyo.html",
    "blog/ideco-setsuzei.html",
    "blog/kyoiku-hi-tsumitatate.html",
    "blog/kakei-kanri.html",
    "blog/kodomo-okane.html",
    "blog/credit-card-points.html",
]


def ensure_remote_dir(ftp: ftplib.FTP, remote_path: str):
    parts = remote_path.strip("/").split("/")
    current = ""
    for part in parts:
        current += f"/{part}"
        try:
            ftp.mkd(current)
        except ftplib.error_perm:
            pass


def deploy():
    if not all([FTP_HOST, FTP_USER, FTP_PASS]):
        print("エラー: .envにFTP_HOST, FTP_USER, FTP_PASSを設定してください")
        sys.exit(1)

    print(f"接続中: {FTP_HOST}")
    ftp = ftplib.FTP()
    ftp.connect(FTP_HOST, 21)
    ftp.login(FTP_USER, FTP_PASS)
    ftp.set_pasv(True)
    print("接続成功")

    uploaded = 0
    for rel_path in DEPLOY_FILES:
        local_file = LOCAL_ROOT / rel_path
        if not local_file.exists():
            print(f"スキップ（ファイルなし）: {rel_path}")
            continue

        remote_dir = FTP_REMOTE_DIR
        if "/" in rel_path:
            subdir = rel_path.rsplit("/", 1)[0]
            remote_dir = f"{FTP_REMOTE_DIR}/{subdir}"
            ensure_remote_dir(ftp, remote_dir)

        remote_file = f"{FTP_REMOTE_DIR}/{rel_path}"
        with open(local_file, "rb") as f:
            ftp.storbinary(f"STOR {remote_file}", f)
        print(f"✓ {rel_path}")
        uploaded += 1

    ftp.quit()
    print(f"\n完了: {uploaded}ファイルをアップロードしました")
    print(f"サイト確認: https://fp-makikatsume.com/")


if __name__ == "__main__":
    deploy()
