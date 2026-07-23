# -*- coding: utf-8 -*-
"""留白製造所 · 商務形象頁 — 照片管理小後台（獨立 Streamlit app）
選角色 → 上傳 → 拖框 3:4 → 存檔，commit 回本倉庫 assets/roster/<名>.jpg，
GitHub Pages 形象頁約一分鐘內同步。部署自 txba1826-bot/roster。"""
import streamlit as st
import os, io
from PIL import Image

st.set_page_config(page_title="形象頁 · 照片管理", page_icon="📸", layout="centered")

st.markdown("""
<style>
[data-testid="stAppViewContainer"]{background:#0e0e0e}
h1,h2,h3,p,label,span,div{color:#eaeaea}
</style>
""", unsafe_allow_html=True)

st.title("📸 商務形象頁 · 照片管理")
st.caption("選角色 → 上傳 → 拖框調 3:4 → 存檔發布。圖檔會 commit 回本倉庫，"
           "形象頁 https://txba1826-bot.github.io/roster/ 約一分鐘內同步。")

ROSTER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "roster")
try:
    existing = sorted(f[:-4] for f in os.listdir(ROSTER_DIR) if f.lower().endswith(".jpg"))
except Exception:
    existing = []

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

if not existing:
    st.error("找不到 assets/roster/ 圖檔。請確認本倉庫含 assets/roster/*.jpg。")
else:
    name = st.selectbox("① 選擇角色", existing)
    cur = os.path.join(ROSTER_DIR, name + ".jpg")
    if os.path.exists(cur):
        st.image(cur, width=200, caption=f"目前照片：{name}")

    up = st.file_uploader("② 上傳新照片（jpg / png）", type=["jpg", "jpeg", "png"])
    if up is not None:
        img = Image.open(up).convert("RGB")
        st.markdown("**③ 拖框調整（固定 3:4 比例）**")
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
                st.error("尚未設定 GitHub 權杖。請在 Streamlit secrets 加入 "
                         "[github] token=\"ghp_...\" repo=\"txba1826-bot/roster\"。")
                st.stop()
            try:
                from github import Github
                repo = Github(token).get_repo(repo_name)
                path = f"assets/roster/{name}.jpg"
                try:
                    ex = repo.get_contents(path)
                    repo.update_file(path, f"update roster photo: {name}", data, ex.sha)
                except Exception:
                    repo.create_file(path, f"add roster photo: {name}", data)
                try:
                    with open(cur, "wb") as f:
                        f.write(data)
                except Exception:
                    pass
                st.success(f"✅ 已發布「{name}」的新照片！約一分鐘後刷新 "
                           "https://txba1826-bot.github.io/roster/ 即見新圖。")
                st.balloons()
            except Exception as e:
                st.error(f"發布失敗：{e}")
