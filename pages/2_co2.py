import streamlit as st
from PIL import Image
import base64
from io import BytesIO
import math, os
import streamlit.components.v1 as components

st.title("🌍 탄소 절감 효과 계산기")

# 1️⃣ 이미지 로드
tree_path = os.path.join(os.path.dirname(__file__), "tree.png")
try:
    tree_img = Image.open(tree_path)
except FileNotFoundError:
    st.error("⚠️ tree.png 파일을 찾을 수 없습니다. 같은 폴더에 두세요.")
    st.stop()

# 2️⃣ base64 인코딩
buf = BytesIO()
tree_img.save(buf, format="PNG")
b64_tree = base64.b64encode(buf.getvalue()).decode()

# 3️⃣ 계산
energy = st.number_input("누적 발전량 (Wh)", min_value=0, value=10000)
energy_kWh = energy / 1000
CO2_saved = energy_kWh * 0.424
trees = CO2_saved / 22
st.metric("절감된 CO₂량 (kg)", f"{CO2_saved:.2f}")
st.metric("상응하는 나무 수", f"{trees:.2f} 그루")

# 4️⃣ 중심부터 채워지는 원형 배치
tree_count = int(trees)
max_trees = min(tree_count, 60)  # 렌더링 제한

center_x, center_y = 50, 50
max_radius = 35   # 전체 숲 반지름 비율 (%)
rings = int(math.sqrt(max_trees)) + 1  # 몇 겹의 원으로 채울지
html_trees = ""
tree_index = 0

for r in range(rings):
    # 각 링의 반지름
    radius = max_radius * (r / rings)
    # 해당 링에 들어갈 나무 수 (안쪽 링은 적고, 바깥쪽 링은 많게)
    trees_in_ring = 6 + r * 6
    for i in range(trees_in_ring):
        if tree_index >= max_trees:
            break
        angle = 2 * math.pi * i / trees_in_ring
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        size = 50 + r * 3  # 바깥쪽일수록 조금 크게
        html_trees += f"""
            <img src="data:image/png;base64,{b64_tree}" 
                 style="position:absolute;
                        left:{x}%;
                        top:{y}%;
                        width:{size}px;
                        transform:translate(-50%,-50%);
                        opacity:0.95;">
        """
        tree_index += 1

# 5️⃣ HTML 컨테이너
html_container = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="margin:0;padding:0;">
  <div style="
      position:relative;
      width:100%;
      height:400px;
      background-color:#e8f5e9;
      border-radius:15px;
      box-shadow:inset 0 0 10px rgba(0,0,0,0.1);
      overflow:hidden;">
    {html_trees}
  </div>
</body>
</html>
"""

# 6️⃣ Streamlit에서 렌더링
components.html(html_container, height=420, scrolling=False)

if tree_count > max_trees:
    st.caption(f"표시 제한: {max_trees}그루 (총 {tree_count}그루 중)")


