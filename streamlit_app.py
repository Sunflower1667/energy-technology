import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os
import io
from PIL import Image

font_path = os.path.join("fonts", "NanumGothic-Regular.ttf")
fm.fontManager.addfont(font_path)
fontprop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = 'NanumGothic'

import matplotlib.pyplot as plt
import matplotlib

matplotlib.rc('font', family='NanumGothic-Regular')

import streamlit as st
import pandas as pd

st.set_page_config(page_title="친환경 에너지 발전 동향 파악하기", page_icon=":seedling:")
st.title("친환경 에너지 발전 동향 파악하기")

# 학생 학번, 이름 입력
student_id = st.text_input("학생 학번을 입력하세요")
student_name = st.text_input("학생 이름을 입력하세요")

# 최근 5년
years = [2021, 2022, 2023, 2024, 2025]
energy_types = ["원자력", "화력", "수력", "신재생"]

# 표 형태로 입력: editable dataframe
st.subheader("최근 5년간 에너지 사용량 입력")
default_data = {"연도": years}
for energy in energy_types:
	default_data[energy] = [0.0]*len(years)
input_df = pd.DataFrame(default_data)
edited_df = st.data_editor(input_df, num_rows="dynamic", use_container_width=True)

# melt하여 분석용 데이터프레임 생성
df = edited_df.melt(id_vars=["연도"], value_vars=energy_types, var_name="에너지", value_name="사용량")
df["학생"] = student_name
df["학번"] = student_id





# 꺾은선 그래프: 에너지별, 연도별 사용량 (matplotlib)
st.subheader("에너지 사용량 꺾은선 그래프")
fig, ax = plt.subplots(figsize=(8, 5))
for energy in energy_types:
	ax.plot(df[df["에너지"] == energy]["연도"], df[df["에너지"] == energy]["사용량"], marker='o', label=energy)
ax.set_xlabel("연도", fontproperties=fontprop)
ax.set_ylabel("사용량", fontproperties=fontprop)
ax.set_title("에너지 사용량 꺾은선 그래프", fontproperties=fontprop)
ax.legend(prop=fontprop)
st.pyplot(fig)




# 연도별 차이 계산 및 막대그래프 표시 (matplotlib)
st.subheader("연도별 에너지 사용량 변화 막대그래프")
diff_data = []
for energy in energy_types:
	energy_df = df[df["에너지"] == energy].sort_values("연도")
	for idx in range(1, len(years)):
		prev = energy_df[energy_df["연도"] == years[idx-1]]["사용량"].values
		curr = energy_df[energy_df["연도"] == years[idx]]["사용량"].values
		if len(prev) and len(curr):
			diff = curr[0] - prev[0]
			diff_data.append({
				"에너지": energy,
				"연도 변화": f"{years[idx-1]}→{years[idx]}",
				"사용량 변화": diff
			})
diff_df = pd.DataFrame(diff_data)
bar_df = diff_df.pivot(index="연도 변화", columns="에너지", values="사용량 변화")

fig2, ax2 = plt.subplots(figsize=(8, 5))
bar_df.plot(kind='bar', ax=ax2)
ax2.set_xlabel("연도 변화", fontproperties=fontprop)
ax2.set_ylabel("사용량 변화", fontproperties=fontprop)
ax2.set_title("연도별 에너지 사용량 변화 막대그래프", fontproperties=fontprop)
ax2.legend(prop=fontprop)
st.pyplot(fig2)


# 전체 결과 JPG/PDF 저장 기능 (학생 정보, 표, 그래프 모두 포함)
st.subheader("전체 결과 저장")
fig_all, axs = plt.subplots(2, 2, figsize=(16, 10))

# 학생 정보 텍스트
axs[0, 0].axis('off')
student_info = f"학번: {student_id}\n이름: {student_name}"
axs[0, 0].text(0, 1, student_info, fontsize=16, va='top', fontproperties=fontprop)

# 입력 표
axs[0, 1].axis('off')
table_data = [input_df.columns.tolist()] + input_df.values.tolist()
table = axs[0, 1].table(cellText=table_data, loc='center', cellLoc='center', colWidths=[0.15]*len(input_df.columns))
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1, 2)
axs[0, 1].set_title('입력 데이터', fontsize=14, fontproperties=fontprop)

# 꺾은선 그래프
for energy in energy_types:
	axs[1, 0].plot(df[df["에너지"] == energy]["연도"], df[df["에너지"] == energy]["사용량"], marker='o', label=energy)
axs[1, 0].set_xlabel("연도", fontproperties=fontprop)
axs[1, 0].set_ylabel("사용량", fontproperties=fontprop)
axs[1, 0].set_title("에너지 사용량 꺾은선 그래프", fontproperties=fontprop)
axs[1, 0].legend(prop=fontprop)

# 막대그래프
bar_df.plot(kind='bar', ax=axs[1, 1])
axs[1, 1].set_xlabel("연도 변화", fontproperties=fontprop)
axs[1, 1].set_ylabel("사용량 변화", fontproperties=fontprop)
axs[1, 1].set_title("연도별 에너지 사용량 변화 막대그래프", fontproperties=fontprop)
axs[1, 1].legend(prop=fontprop)

plt.tight_layout()

# JPG 저장
img_buf = io.BytesIO()
fig_all.savefig(img_buf, format='jpeg')
img_buf.seek(0)
st.download_button("전체 결과 JPG 다운로드", data=img_buf, file_name="energy_result.jpg", mime="image/jpeg")

# PDF 저장
pdf_buf = io.BytesIO()
fig_all.savefig(pdf_buf, format='pdf')
pdf_buf.seek(0)
st.download_button("전체 결과 PDF 다운로드", data=pdf_buf, file_name="energy_result.pdf", mime="application/pdf")


