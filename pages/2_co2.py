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
from reportlab.lib import colors

# 🌳 제목
st.title("🌿 탄소 절감 효과 계산기 (PDF 포함)")

# 1️⃣ 트리 이미지 로드
tree_path = os.path.join(os.path.dirname(__file__), "tree.png")
try:
    tree_img = Image.open(tree_path)
except FileNotFoundError:
    st.error("⚠️ tree.png 파일을 찾을 수 없습니다. 같은 폴더에 tree.png를 두세요.")
    st.stop()

# 2️⃣ 입력값
energy = st.number_input("누적 발전량 (kWh)", min_value=0, value=10000)
CO2_saved = energy * 0.424
trees = CO2_saved / 22

st.metric("절감된 CO₂량 (kg)", f"{CO2_saved:.2f}")
st.metric("상응하는 나무 수", f"{trees:.2f} 그루")

# 3️⃣ 타원형 균일 배치 숲 이미지 함수
def generate_elliptical_forest(tree_img, num_trees):
    img_size = 500
    forest_img = Image.new("RGB", (img_size, img_size), (232, 245, 233))
    center_x, center_y = img_size // 2, img_size // 2

    max_trees = min(int(num_trees), 60)
    a = img_size * 0.35   # 가로 반경
    b = img_size * 0.28   # 세로 반경
    rings = int(math.sqrt(max_trees)) + 1
    placed = 0

    for r in range(rings):
        if placed >= max_trees:
            break
        radius_scale = (r + 1) / rings
        trees_in_ring = min(6 + r * 6, max_trees - placed)
        angle_step = 2 * math.pi / trees_in_ring

        for i in range(trees_in_ring):
            if placed >= max_trees:
                break
            angle = i * angle_step
            x = center_x + a * radius_scale * math.cos(angle)
            y = center_y + b * radius_scale * math.sin(angle)
            size = 30 + int(10 * radius_scale)
            resized = tree_img.resize((size, size))
            forest_img.paste(
                resized,
                (int(x - size / 2), int(y - size / 2)),
                mask=resized.split()[3] if resized.mode == "RGBA" else None
            )
            placed += 1

    return forest_img

# 4️⃣ 숲 이미지 생성 및 표시
forest_img = generate_elliptical_forest(tree_img, trees)
st.image(forest_img, caption="CO₂ 절감 효과 시각화 (타원형 균일 배치)", use_container_width=True)

# 5️⃣ PDF 저장 버튼
if st.button("📄 PDF로 저장"):
    buffer = BytesIO()

    # ✅ 한글 폰트 등록 (ReportLab 내장)
    pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))

    # PDF 생성
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("HYSMyeongJo-Medium", 16)
    c.drawCentredString(105 * mm, 280 * mm, "탄소 절감 효과 계산 결과")

    # 작성일
    c.setFont("HYSMyeongJo-Medium", 12)
    c.drawString(25 * mm, 265 * mm, f"작성일: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # ✅ 표 형식으로 결과 표시
    x_start = 25 * mm
    y_start = 250 * mm
    row_height = 10 * mm
    col_widths = [60 * mm, 60 * mm]

    # 배경색
    c.setFillColorRGB(0.95, 0.95, 0.95)
    c.rect(x_start, y_start - 3 * row_height, sum(col_widths), 3 * row_height, fill=True, stroke=False)
    c.setFillColorRGB(0, 0, 0)

    # 테두리
    c.setLineWidth(0.5)
    c.rect(x_start, y_start - 3 * row_height, sum(col_widths), 3 * row_height, stroke=True, fill=False)
    c.line(x_start, y_start - row_height, x_start + sum(col_widths), y_start - row_height)
    c.line(x_start, y_start - 2 * row_height, x_start + sum(col_widths), y_start - 2 * row_height)
    c.line(x_start + col_widths[0], y_start, x_start + col_widths[0], y_start - 3 * row_height)

    # 텍스트
    c.setFont("HYSMyeongJo-Medium", 12)
    c.drawCentredString(x_start + col_widths[0] / 2, y_start - 8, "항목")
    c.drawCentredString(x_start + col_widths[0] + col_widths[1] / 2, y_start - 8, "값")

    c.drawString(x_start + 5, y_start - row_height + 3, "누적 발전량 (kWh)")
    c.drawString(x_start + col_widths[0] + 5, y_start - row_height + 3, f"{energy:.0f} kWh")

    c.drawString(x_start + 5, y_start - 2 * row_height + 3, "절감된 CO₂량 (kg)")
    c.drawString(x_start + col_widths[0] + 5, y_start - 2 * row_height + 3, f"{CO2_saved:.2f} kg")

    c.drawString(x_start + 5, y_start - 3 * row_height + 3, "상응하는 나무 수 (그루)")
    c.drawString(x_start + col_widths[0] + 5, y_start - 3 * row_height + 3, f"{trees:.2f} 그루")

    # ✅ 숲 이미지 삽입 (크기 축소 + 중앙 정렬)
    img_buffer = BytesIO()
    forest_img.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    img_reader = ImageReader(img_buffer)

    c.drawImage(
    img_reader,
    35 * mm,        # 좌측 여백
    40 * mm,        # ⬅️ 이미지 세로 위치 (낮춰서 표 아래로)
    width=120 * mm, # 이미지 크기
    preserveAspectRatio=True
)
    # ✅ 페이지를 넘기지 않고 저장
    c.save()
    buffer.seek(0)

    # ✅ 다운로드 버튼
    st.download_button(
        label="📥 PDF 다운로드",
        data=buffer,
        file_name="co2_savings.pdf",
        mime="application/pdf"
    )

    st.success("✅ 표와 숲 이미지가 한 페이지에 포함된 PDF가 생성되었습니다.")
