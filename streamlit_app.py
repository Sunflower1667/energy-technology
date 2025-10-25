import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import matplotlib
import os
import io
from datetime import datetime

# -------------------------------
# ✅ 한글 폰트 설정 (NanumGothic 사용)
# -------------------------------
font_path = os.path.join("fonts", "NanumGothic-Regular.ttf")
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    fontprop = fm.FontProperties(fname=font_path)
    plt.rcParams['font.family'] = 'NanumGothic'
    matplotlib.rc('font', family='NanumGothic-Regular')
else:
    fontprop = None
    st.warning("⚠️ 폰트 파일이 없습니다. 'fonts/NanumGothic-Regular.ttf' 경로에 폰트를 추가하세요.")

# -------------------------------
# ✅ 페이지 설정
# -------------------------------
st.set_page_config(page_title="생각 정리 및 에너지 발전 추이", page_icon="📝", layout="wide")
st.title("에너지 발전량 변화 확인하기")

st.markdown("""
최근 5년간 발전량을 직접 입력하고, **왜 이런 변화가 나타났는지** 자신의 생각을 정리해 보세요.
""")

# -------------------------------
# ✅ 학번/이름 입력 (전역 공유)
# -------------------------------
st.sidebar.header("👤 사용자 정보")
st.sidebar.info("입력한 학번과 이름은 모든 페이지에서 자동으로 적용됩니다.")

st.sidebar.text_input("이름", key="student_name")
st.sidebar.text_input("학번", key="student_id")

# 값이 입력되지 않으면 경고
if not st.session_state.get("student_name") or not st.session_state.get("student_id"):
    st.warning("👈 왼쪽 사이드바에서 이름과 학번을 입력해주세요.")
    st.stop()

# 변수로 가져오기 (코드 가독성 위해)
student_name = st.session_state.student_name
student_id = st.session_state.student_id

# -------------------------------
# ✅ 발전량 입력
# -------------------------------
st.subheader("최근 5년간 에너지 발전량 입력 (단위: 천kW)")
years = [2021, 2022, 2023, 2024, 2025]
energy_types = ["원자력", "화력", "수력", "신재생"]

default_data = {"연도": years}
for e in energy_types:
    default_data[e] = [0.0] * len(years)

input_df = pd.DataFrame(default_data)
edited_df = st.data_editor(input_df, num_rows="dynamic", use_container_width=True)

# 분석용 데이터 변환
df = edited_df.melt(id_vars=["연도"], value_vars=energy_types, var_name="에너지", value_name="발전량")
df["학번"] = student_id
df["이름"] = student_name

# -------------------------------
# ✅ 꺾은선 그래프
# -------------------------------
st.subheader("에너지 발전량 추이 그래프")

fig, ax = plt.subplots(figsize=(8, 5))
for e in energy_types:
    ax.plot(df[df["에너지"] == e]["연도"], df[df["에너지"] == e]["발전량"], marker='o', label=e)

ax.set_xlabel("연도", fontproperties=fontprop)
ax.set_ylabel("발전량(천kW)", fontproperties=fontprop)
ax.set_title("에너지 발전량 추이", fontproperties=fontprop)
ax.legend(prop=fontprop)
st.pyplot(fig)

# -------------------------------
# ✅ 개인 생각 작성 섹션
# -------------------------------
st.markdown("---")
st.subheader("생각 정리")

with st.form("reflection"):
    q1 = st.text_area("① 어떤 발전원이 늘거나 줄었나요? 그 이유는 무엇이라고 생각하나요?", height=120)
    q2 = st.text_area("② 이러한 변화가 환경과 사회에 미치는 영향은 무엇일까요?", height=120)
    q3 = st.text_area("③ 우리 지역/학교에서 실천할 수 있는 것은 무엇이 있을까요?", height=120)
    submitted = st.form_submit_button("저장")

if "responses" not in st.session_state:
    st.session_state["responses"] = []

if submitted:
    st.session_state["responses"].append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "학번": student_id,
        "이름": student_name or "무명",
        "q1": q1,
        "q2": q2,
        "q3": q3
    })
    st.success("✅ 저장되었습니다. 아래 표에서 확인하고 CSV로 내려받을 수 있습니다.")

if st.session_state["responses"]:
    df_resp = pd.DataFrame(st.session_state["responses"])
    st.dataframe(df_resp, use_container_width=True)
    st.download_button(
        "🧾 생각 정리 CSV 다운로드",
        data=df_resp.to_csv(index=False).encode("utf-8-sig"),
        file_name="학생_생각정리_응답.csv",
        mime="text/csv"
    )
else:
    st.info("아직 저장된 응답이 없습니다. 위 폼을 작성해 주세요.")

# -------------------------------
# ✅ 전체 결과 저장 (JPG/PDF)
# -------------------------------
st.markdown("---")
st.subheader("전체 결과 저장 (입력 + 그래프 + 생각 요약)")

fig_all, axs = plt.subplots(2, 2, figsize=(16, 10))

# 1️⃣ 학생 정보
axs[0, 0].axis('off')
student_info = f"학번: {student_id}\n이름: {student_name}\n날짜: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
axs[0, 0].text(0, 1, student_info, fontsize=16, va='top', fontproperties=fontprop)

# 2️⃣ 입력 데이터 표
axs[0, 1].axis('off')
table_data = [edited_df.columns.tolist()] + edited_df.values.tolist()
table = axs[0, 1].table(cellText=table_data, loc='center', cellLoc='center', colWidths=[0.15]*len(edited_df.columns))
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1, 2)
axs[0, 1].set_title('입력 데이터', fontsize=14, fontproperties=fontprop)
for key, cell in table.get_celld().items():
    cell.get_text().set_fontproperties(fontprop)

# 3️⃣ 발전량 그래프
for e in energy_types:
    axs[1, 0].plot(df[df["에너지"] == e]["연도"], df[df["에너지"] == e]["발전량"], marker='o', label=e)
axs[1, 0].set_xlabel("연도", fontproperties=fontprop)
axs[1, 0].set_ylabel("발전량(천kW)", fontproperties=fontprop)
axs[1, 0].set_title("에너지 발전량 추이", fontproperties=fontprop)
axs[1, 0].legend(prop=fontprop)

# 4️⃣ 학생 생각 요약
axs[1, 1].axis('off')
thoughts = f"① {q1}\n\n② {q2}\n\n③ {q3}"
axs[1, 1].text(0, 1, thoughts, fontsize=12, va='top', fontproperties=fontprop)
axs[1, 1].set_title('생각 정리', fontsize=14, fontproperties=fontprop)

# JPG 다운로드
img_buf = io.BytesIO()
fig_all.savefig(img_buf, format='jpeg', bbox_inches='tight')
img_buf.seek(0)
st.download_button("📸 전체 결과 JPG 다운로드", data=img_buf, file_name="energy_result.jpg", mime="image/jpeg")

# PDF 다운로드
pdf_buf = io.BytesIO()
fig_all.savefig(pdf_buf, format='pdf', bbox_inches='tight')
pdf_buf.seek(0)
st.download_button("📄 전체 결과 PDF 다운로드", data=pdf_buf, file_name="energy_result.pdf", mime="application/pdf")

st.caption("※ NanumGothic 폰트를 /fonts 폴더에 넣으면 한글 깨짐 없이 출력됩니다.")
