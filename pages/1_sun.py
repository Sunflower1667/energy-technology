import streamlit as st

st.title("🔆 태양광 에너지 발전")
tab1, tab2 = st.tabs(["발전 시뮬레이터", "날씨 기반 예측"])

with tab1:
    # (1번 코드)
    import streamlit as st
    import numpy as np
    import plotly.express as px

    st.title("🌞 태양광 발전 원리 시뮬레이터")

    E = st.slider("일사량 (W/m²)", 0, 1000, 500)
    A = st.slider("전지판 면적 (m²)", 0.01, 1.0, 0.1)
    eta = st.slider("전지 효율 (%)", 1, 25, 15)
    theta = st.slider("입사각 (°)", 0, 90, 30)

    P = E * A * (eta / 100) * np.cos(np.radians(theta))
    st.metric("발전 전력 (W)", f"{P:.2f}")

    angles = np.linspace(0, 90, 100)
    power_curve = E * A * (eta / 100) * np.cos(np.radians(angles))
    fig = px.line(x=angles, y=power_curve, labels={'x':'입사각(°)', 'y':'발전전력(W)'})
    st.plotly_chart(fig)

 
with tab2:
    # (3번 코드)
    import streamlit as st
    import numpy as np

    st.title("☁️ 날씨 조건 기반 태양광 출력 예측기")

    # 사용자 입력
    weather = st.selectbox("날씨 상태 선택", ["맑음", "약간 흐림", "흐림", "매우 흐림"])
    temp = st.slider("기온 (℃)", -10, 40, 25)
    area = st.slider("전지판 면적 (m²)", 0.05, 0.5, 0.1)
    eff = st.slider("전지 효율 (%)", 5, 25, 15)

    # 날씨에 따른 일사량 가정
    weather_factor = {
        "맑음": 1.0,
        "약간 흐림": 0.7,
        "흐림": 0.4,
        "매우 흐림": 0.2
    }
    E = 1000 * weather_factor[weather]  # 단순화된 일사량 모델

    # 발전 전력 계산
    P = E * area * (eff / 100)
    st.metric("예상 발전 전력 (W)", f"{P:.2f}")

    # 상세 출력
    st.write(f"날씨: {weather}, 기온: {temp}℃")
    st.write(f"일사량 추정치: {E:.0f} W/m²")
