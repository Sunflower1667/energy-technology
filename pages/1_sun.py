import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib
import os
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.utils import ImageReader

# ✅ 한글 폰트 설정 (Matplotlib용)
font_path = os.path.join("fonts", "NanumGothic-Regular.ttf")
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    plt.rcParams["font.family"] = "NanumGothic"
    matplotlib.rc("font", family="NanumGothic")
else:
    st.warning("⚠️ 'fonts/NanumGothic-Regular.ttf' 파일이 없어 기본 폰트로 표시됩니다.")

# ✅ ReportLab 폰트 등록 (PDF용)
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont("NanumGothic", font_path))
    font_name = "NanumGothic"
else:
    pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))
    font_name = "HYSMyeongJo-Medium"

# --------------------
# 🌞 메인 화면
# --------------------
st.title("🔆 태양광 에너지 발전 통합 실습")

# 사용자 입력
st.sidebar.header("👤 사용자 정보 입력")
name = st.sidebar.text_input("이름")
sid = st.sidebar.text_input("학번")

if not name or not sid:
    st.warning("👈 왼쪽에서 이름과 학번을 입력하세요.")
    st.stop()

# 탭 구성
tab1, tab2 = st.tabs(["발전 시뮬레이터", "날씨 기반 예측"])

# --------------------------
# 🌞 1. 발전 시뮬레이터 탭
# --------------------------
with tab1:
    st.header("🌞 태양광 발전 원리 시뮬레이터")

    E = st.slider("일사량 (W/m²)", 0, 1000, 500)
    A = st.slider("전지판 면적 (m²)", 0.01, 1.0, 0.1)
    eta = st.slider("전지 효율 (%)", 1, 25, 15)
    theta = st.slider("입사각 (°)", 0, 90, 30)

    P = E * A * (eta / 100) * np.cos(np.radians(theta))
    st.metric("발전 전력 (W)", f"{P:.2f}")

    # ✅ Matplotlib 그래프
    angles = np.linspace(0, 90, 100)
    power_curve = E * A * (eta / 100) * np.cos(np.radians(angles))

    fig, ax = plt.subplots()
    ax.plot(angles, power_curve, label="발전 전력 (W)")
    ax.set_xlabel("입사각(°)")
    ax.set_ylabel("발전 전력(W)")
    ax.set_title("입사각에 따른 발전 전력 변화")
    ax.legend()
    st.pyplot(fig)

    # ✅ PDF 저장
    if st.button("📄 PDF 저장 (그래프 포함)", key="sim_pdf"):
        img_buf = BytesIO()
        fig.savefig(img_buf, format="png", bbox_inches="tight")
        img_buf.seek(0)
        img_reader = ImageReader(img_buf)

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.setFont(font_name, 16)
        c.drawCentredString(105 * mm, 280 * mm, "태양광 발전 시뮬레이터 결과")

        c.setFont(font_name, 12)
        c.drawString(25 * mm, 265 * mm, f"이름: {name} / 학번: {sid}")
        c.drawString(25 * mm, 255 * mm, f"일사량: {E} W/m², 면적: {A} m², 효율: {eta}%")
        c.drawString(25 * mm, 245 * mm, f"입사각: {theta}°, 발전 전력: {P:.2f} W")

        # 그래프 삽입
        c.drawImage(img_reader, 25 * mm, 80 * mm, width=160 * mm, preserveAspectRatio=True)
        c.save()
        buffer.seek(0)

        st.download_button(
            "📥 PDF 다운로드",
            data=buffer,
            file_name=f"{name}_발전시뮬레이터.pdf",
            mime="application/pdf"
        )

# --------------------------
# ☁️ 2. 날씨 기반 예측 탭
# --------------------------
with tab2:
    st.header("☁️ 날씨 조건 기반 태양광 발전 출력 예측기")

    weather = st.selectbox("날씨 상태 선택", ["맑음", "약간 흐림", "흐림", "매우 흐림"])
    temp = st.slider("기온 (℃)", -10, 40, 25)
    area = st.slider("전지판 면적 (m²)", 0.05, 0.5, 0.1)
    eff = st.slider("전지 효율 (%)", 5, 25, 15)

    weather_factor = {
        "맑음": 1.0,
        "약간 흐림": 0.7,
        "흐림": 0.4,
        "매우 흐림": 0.2
    }

    E = 1000 * weather_factor[weather]
    P = E * area * (eff / 100)

    st.metric("예상 발전 전력 (W)", f"{P:.2f}")
    st.write(f"날씨: {weather}, 기온: {temp}℃")
    st.write(f"일사량 추정치: {E:.0f} W/m²")

    # ✅ 간단한 막대그래프 시각화
    fig2, ax2 = plt.subplots()
    ax2.bar(["예상 발전 전력"], [P], color="orange")
    ax2.set_ylabel("발전 전력 (W)")
    ax2.set_title(f"{weather} 조건에서의 예상 출력")
    st.pyplot(fig2)

    # ✅ PDF 저장
    if st.button("📄 PDF 저장 (결과 포함)", key="weather_pdf"):
        img_buf2 = BytesIO()
        fig2.savefig(img_buf2, format="png", bbox_inches="tight")
        img_buf2.seek(0)
        img_reader2 = ImageReader(img_buf2)

        buffer2 = BytesIO()
        c = canvas.Canvas(buffer2, pagesize=A4)
        c.setFont(font_name, 16)
        c.drawCentredString(105 * mm, 280 * mm, "날씨 기반 태양광 발전 결과")

        c.setFont(font_name, 12)
        c.drawString(25 * mm, 265 * mm, f"이름: {name} / 학번: {sid}")
        c.drawString(25 * mm, 255 * mm, f"날씨: {weather}, 기온: {temp}℃")
        c.drawString(25 * mm, 245 * mm, f"전지 효율: {eff}%, 면적: {area} m²")
        c.drawString(25 * mm, 235 * mm, f"예상 발전 전력: {P:.2f} W")
        c.drawString(25 * mm, 225 * mm, f"일사량 추정치: {E:.0f} W/m²")

        # 그래프 삽입
        c.drawImage(img_reader2, 25 * mm, 90 * mm, width=160 * mm, preserveAspectRatio=True)
        c.save()
        buffer2.seek(0)

        st.download_button(
            "📥 PDF 다운로드",
            data=buffer2,
            file_name=f"{name}_날씨기반예측.pdf",
            mime="application/pdf"
        )
