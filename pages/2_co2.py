import streamlit as st
from PIL import Image
import math, os
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.utils import ImageReader

st.title("🌿 탄소 절감 효과 계산기")

# ✅ 사용자 정보 입력
st.sidebar.header("👤 사용자 정보 입력")
name = st.sidebar.text_input("이름")
sid = st.sidebar.text_input("학번")
if not name or not sid:
    st.warning("👈 왼쪽에서 이름과 학번을 입력하세요.")
    st.stop()

tree_path = os.path.join(os.path.dirname(__file__), "tree.png")
try:
    tree_img = Image.open(tree_path)
except FileNotFoundError:
    st.error("⚠️ tree.png 파일이 없습니다.")
    st.stop()

energy = st.number_input("누적 발전량 (kWh)", min_value=0, value=10000)
CO2_saved = energy * 0.424
trees = CO2_saved / 22
st.metric("절감된 CO₂량 (kg)", f"{CO2_saved:.2f}")
st.metric("상응하는 나무 수", f"{trees:.2f} 그루")

def generate_forest(img, n):
    size = 500
    base = Image.new("RGB", (size, size), (232, 245, 233))
    cx, cy = size//2, size//2
    max_t = min(int(n), 60)
    a, b = size*0.35, size*0.28
    count = 0
    for r in range(int(math.sqrt(max_t)) + 1):
        if count >= max_t: break
        n_ring = min(6 + r*6, max_t - count)
        for i in range(n_ring):
            angle = 2*math.pi*i/n_ring
            x = cx + a*(r+1)/(math.sqrt(max_t))*math.cos(angle)
            y = cy + b*(r+1)/(math.sqrt(max_t))*math.sin(angle)
            s = 30 + int(10*(r+1)/(math.sqrt(max_t)))
            resized = img.resize((s, s))
            base.paste(resized, (int(x-s/2), int(y-s/2)), mask=resized.split()[3] if resized.mode=="RGBA" else None)
            count += 1
    return base

forest = generate_forest(tree_img, trees)
st.image(forest, caption="CO₂ 절감 효과")

if st.button("📄 PDF로 저장"):
    buffer = BytesIO()
    pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("HYSMyeongJo-Medium", 16)
    c.drawCentredString(105*mm, 280*mm, "탄소 절감 효과 계산 결과")
    c.setFont("HYSMyeongJo-Medium", 12)
    c.drawString(25*mm, 270*mm, f"이름: {name} / 학번: {sid}")
    c.drawString(25*mm, 260*mm, f"누적 발전량: {energy:.0f} kWh")
    c.drawString(25*mm, 250*mm, f"절감된 CO₂: {CO2_saved:.2f} kg")
    c.drawString(25*mm, 240*mm, f"상응 나무 수: {trees:.2f} 그루")

    img_buf = BytesIO()
    forest.save(img_buf, format="PNG")
    img_buf.seek(0)
    c.drawImage(ImageReader(img_buf), 35*mm, 50*mm, width=120*mm, preserveAspectRatio=True)
    c.save()
    buffer.seek(0)
    st.download_button("📥 PDF 다운로드", data=buffer, file_name=f"{name}_co2.pdf", mime="application/pdf")
