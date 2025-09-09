#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
process.py — 读取 ../raw/ 下的 MovieLens 100k 原始文件，输出到当前目录 ./ ：
1) behavior.csv  -> 每个用户的按时间排序的高分(>=4)交互序列（列: user_id, behavior）
2) user.csv      -> 用户信息（列: user_id, gender, age, occupation）
3) item.csv      -> 物品信息（列: item_id, metadata(JSON: title, release_date, imdb_url, genres)）
"""

import os
import sys
import json
import pandas as pd
from typing import List

# --- 固定路径（以脚本所在目录为基准） ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, "../raw"))   # 输入目录
OUT_DIR = BASE_DIR                                             # 输出目录 ./


# ---------- 读取原始文件 ----------
def read_ratings() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "u.data")
    if not os.path.exists(path):
        _missing(path)
    df = pd.read_csv(
        path,
        sep=r"\t",
        header=None,
        names=["user_id", "item_id", "rating", "timestamp"],
        engine="python",
    )
    return df


def read_users() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "u.user")
    if not os.path.exists(path):
        _missing(path)
    df = pd.read_csv(
        path,
        sep="|",
        header=None,
        names=["user_id", "age", "gender", "occupation", "zip_code"],
        engine="python",
    )
    df = df[["user_id", "gender", "age", "occupation"]].copy()
    df["user_id"] = df["user_id"].astype(int)
    return df


def read_genres() -> List[str]:
    path = os.path.join(DATA_DIR, "u.genre")
    if not os.path.exists(path):
        _missing(path)
    g = pd.read_csv(path, sep="|", header=None, names=["genre", "genre_id"], engine="python")
    g = g.dropna().sort_values("genre_id")
    return g["genre"].tolist()


def read_items(genres: List[str]) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "u.item")
    if not os.path.exists(path):
        _missing(path)

    base_cols = ["item_id", "title", "release_date", "video_release_date", "imdb_url"]
    genre_cols = [f"g_{i}" for i in range(len(genres))]
    names = base_cols + genre_cols

    df = pd.read_csv(
        path,
        sep="|",
        header=None,
        names=names,
        encoding="latin-1",
        engine="python",
    )

    # one-hot -> genre 名称列表
    def row_genres(r):
        present = []
        for i, g in enumerate(genres):
            v = r.get(f"g_{i}")
            try:
                if int(v) == 1:
                    present.append(g)
            except Exception:
                pass
        return present

    df["genres"] = df.apply(row_genres, axis=1)
    return df[["item_id", "title", "release_date", "imdb_url", "genres"]].copy()


# ---------- 生成输出 ----------
def build_behavior_csv(ratings: pd.DataFrame) -> None:
    """behavior.csv: user_id, behavior(按时间升序，仅 rating>=4 的 item_id，用空格分隔)"""
    hi = ratings[ratings["rating"] >= 4].copy()
    hi = hi.sort_values(["user_id", "timestamp"])
    seq = (
        hi.groupby("user_id")["item_id"]
        .apply(lambda s: " ".join(map(str, s.tolist())))
        .reset_index()
        .rename(columns={"item_id": "behavior"})
    )
    out_path = os.path.join(OUT_DIR, "behavior.csv")
    seq.to_csv(out_path, index=False)


def build_user_csv(users: pd.DataFrame) -> None:
    out_path = os.path.join(OUT_DIR, "user.csv")
    users.to_csv(out_path, index=False)


def build_item_csv(items: pd.DataFrame) -> None:
    """item.csv: item_id, metadata(JSON: title, release_date, imdb_url, genres)"""
    def to_meta(row):
        meta = {
            "title": row["title"],
            "release_date": None if pd.isna(row["release_date"]) else str(row["release_date"]),
            "imdb_url": None if pd.isna(row["imdb_url"]) else str(row["imdb_url"]),
            "genres": row["genres"] if isinstance(row["genres"], list) else [],
        }
        return json.dumps(meta, ensure_ascii=False)

    out = pd.DataFrame({
        "item_id": items["item_id"].astype(int),
        "metadata": items.apply(to_meta, axis=1),
    })
    out_path = os.path.join(OUT_DIR, "item.csv")
    out.to_csv(out_path, index=False)


# ---------- 工具 ----------
def _missing(path: str):
    print(f"[ERROR] Missing file: {path}", file=sys.stderr)
    sys.exit(1)


# ---------- 入口 ----------
def main():
    # 基本文件检查
    required = ["u.data", "u.item", "u.user", "u.genre"]
    miss = [f for f in required if not os.path.exists(os.path.join(DATA_DIR, f))]
    if miss:
        print(f"[ERROR] Files not found in {DATA_DIR}: {', '.join(miss)}", file=sys.stderr)
        sys.exit(1)

    ratings = read_ratings()
    users = read_users()
    genres = read_genres()
    items = read_items(genres)

    os.makedirs(OUT_DIR, exist_ok=True)
    build_behavior_csv(ratings)
    build_user_csv(users)
    build_item_csv(items)

    print("Done. Wrote files to ./")
    print(" - behavior.csv")
    print(" - user.csv")
    print(" - item.csv")


if __name__ == "__main__":
    main()
