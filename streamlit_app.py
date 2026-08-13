# -*- coding: utf-8 -*-
"""留白製造所 · 商務形象頁 — 照片管理小後台（獨立 Streamlit app）
角色卡照片 → assets/roster/<名>.jpg；首頁封面 → assets/hero/1~4.jpg。
選 → 上傳 → 拖框 3:4 → 存檔，commit 回本倉庫，GitHub Pages 約一分鐘內同步。
部署自 txba1826-bot/roster。"""
import streamlit as st
import os, io
from PIL import Image

st.set_page_config(page_title="形象頁 · 照片管理", page_icon="📸", layout="centered")
st.markdown("""<style>[data-testid="stAppViewContainer"]{background:#0e0e0e}
h1,h2,h3,p,label,span,div{color:#eaeaea}</style>""", unsafe_allow_html=True)

st.title("📸 商務形象頁 · 照片管理")
st.caption("選要換的位置 → 上傳 → 拖框調 3:4 → 存檔發布。約一分鐘後 "
           "https://txba1826-bot.github.io/roster/ 同步。")

BASE = os.path.dirname(os.path.abspath(__file__))
ROSTER_DIR = os.path.join(BASE, "assets", "roster")
HERO_DIR = os.path.join(BASE, "assets", "hero")

def to34(im):
    cw, ch = im.size
    want = cw * 4 // 3
    if ch > want:
        im = im.crop((0, 0, cw, want))
    elif ch < want:
        nw = ch * 3 // 4
        off = max(0, (cw - nw) // 2)
        im = im.crop((off, 0, off + nw, ch))
    return im

mode = st.radio("① 要換哪裡？", ["角色卡照片", "首頁封面（4 格）", "角色庫卡面（大總表）"], horizontal=True)

if mode == "角色卡照片":
    try:
        names = sorted(f[:-4] for f in os.listdir(ROSTER_DIR) if f.lower().endswith(".jpg"))
    except Exception:
        names = []
    # 依 女 → 男 → 其他 分組排序（讀 assets/roster_meta.json）
    meta = {}
    try:
        import json as _json
        with open(os.path.join(BASE, "assets", "roster_meta.json"), encoding="utf-8") as _f:
            meta = _json.load(_f)
    except Exception:
        pass
    _ORDER = {"女": 0, "男": 1, "其他": 2}
    def _key(n):
        g = (meta.get(n) or {}).get("g", "女")
        return (_ORDER.get(g, 3), n)
    names = sorted(names, key=_key)
    def _fmt(n):
        info = meta.get(n) or {}
        g = info.get("g", "")
        en = info.get("e", "")
        tag = {"女": "👩", "男": "👨", "其他": "🐾"}.get(g, "")
        return f"{tag} {n}" + (f"　{en}" if en and en != "（待定）" else "")
    label = st.selectbox("② 選擇角色", names, format_func=_fmt) if names else None
    repo_path = f"assets/roster/{label}.jpg" if label else None
    local_path = os.path.join(ROSTER_DIR, f"{label}.jpg") if label else None
    if names:
        _nf = sum(1 for n in names if (meta.get(n) or {}).get("g") == "女")
        _nm = sum(1 for n in names if (meta.get(n) or {}).get("g") == "男")
        _no = len(names) - _nf - _nm
        st.caption(f"共 {len(names)} 張：女 {_nf} · 男 {_nm} · 其他/真人 {_no}")
    else:
        st.error("找不到 assets/roster/ 圖檔。")
elif mode == "首頁封面（4 格）":
    slot = st.selectbox("② 選擇封面圖（最多 12 張，一次輪播顯示 4 張）",
                        [f"封面 {i}" for i in range(1, 13)])
    n = slot.split()[-1]
    label = slot
    repo_path = f"assets/hero/{n}.jpg"
    local_path = os.path.join(HERO_DIR, f"{n}.jpg")
else:
    # 角色庫卡面：大總表卡片墙的首圖（assets/dashthumbs/<名>.jpg），
    # 不影響形象頁與概念圖。發布後大總表約一分鐘自動更新。
    DASH_DIR = os.path.join(BASE, "assets", "dashthumbs")
    try:
        names = sorted(f[:-4] for f in os.listdir(ROSTER_DIR) if f.lower().endswith(".jpg"))
    except Exception:
        names = []
    meta = {}
    try:
        import json as _json
        with open(os.path.join(BASE, "assets", "roster_meta.json"), encoding="utf-8") as _f:
            meta = _json.load(_f)
    except Exception:
        pass
    _ORDER = {"女": 0, "男": 1, "其他": 2}
    names = sorted(names, key=lambda n: (_ORDER.get((meta.get(n) or {}).get("g", "女"), 3), n))
    def _fmt2(n):
        info = meta.get(n) or {}
        tag = {"女": "👩", "男": "👨", "其他": "🐾"}.get(info.get("g", ""), "")
        en = info.get("e", "")
        return f"{tag} {n}" + (f"　{en}" if en and en != "（待定）" else "")
    label = st.selectbox("② 選擇角色", names, format_func=_fmt2) if names else None
    st.caption("此模式只換『大總表』卡片首圖，不會動到形象頁照片與概念圖。")
    repo_path = f"assets/dashthumbs/{label}.jpg" if label else None
    local_path = os.path.join(DASH_DIR, f"{label}.jpg") if label else None

if label:
    if local_path and os.path.exists(local_path):
        st.image(local_path, width=200, caption=f"目前：{label}")

    up = st.file_uploader("③ 上傳新照片（jpg / png）", type=["jpg", "jpeg", "png"])
    if up is not None:
        img = Image.open(up).convert("RGB")
        st.markdown("**④ 拖框調整（固定 3:4 比例）**")
        try:
            from streamlit_cropper import st_cropper
            crop = st_cropper(img, aspect_ratio=(3, 4), box_color="#C2485A", realtime_update=True)
        except Exception:
            st.info("裁切元件未載入，改為自動置中裁成 3:4。")
            crop = img

        final = to34(crop)
        if final.width > 440:
            final = final.resize((440, round(final.height * 440 / final.width)), Image.LANCZOS)
        st.markdown("**發布預覽**")
        st.image(final, width=180)

        if st.button("✅ 存檔並發布", type="primary"):
            buf = io.BytesIO()
            final.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
            data = buf.getvalue()
            try:
                token = st.secrets["github"]["token"]
                repo_name = st.secrets["github"].get("repo", "txba1826-bot/roster")
            except Exception:
                st.error("尚未設定 GitHub 權杖（secrets [github] token）。")
                st.stop()
            try:
                from github import Github
                repo = Github(token).get_repo(repo_name)
                try:
                    ex = repo.get_contents(repo_path)
                    repo.update_file(repo_path, f"update {label}", data, ex.sha)
                except Exception:
                    repo.create_file(repo_path, f"add {label}", data)
                try:
                    with open(local_path, "wb") as f:
                        f.write(data)
                except Exception:
                    pass
                st.success(f"✅ 已發布「{label}」！約一分鐘後刷新形象頁即見新圖。")
                st.balloons()
            except Exception as e:
                st.error(f"發布失敗：{e}")
