import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib.animation import FuncAnimation

g = 9.80665  # 중력가속도 (m/s^2)
rho = 1.225  # 공기 밀도 (kg/m^3)


def velocity(t: float) -> float:
    """자유낙하운동의 속도를 계산합니다. (m/s)"""
    return g * t


def height(h: int, t: float) -> float:
    """자유낙하운동의 높이를 계산합니다. (m)"""
    return h - 0.5 * velocity(t) * t


def terminal_velocity_with_air_resistance(Cd: float, A: float, m: int) -> float:
    """공기저항을 고려한 낙하운동의 종단속도를 계산합니다. (m/s)"""
    return (2 * m * g / (rho * Cd * A)) ** 0.5


def velocity_with_air_resistance(Cd: float, A: float, m: int, t: float) -> float:
    """공기저항을 고려한 낙하운동의 속도를 계산합니다. (m/s)"""
    v_t = terminal_velocity_with_air_resistance(Cd, A, m)

    return v_t * (np.e ** (2 * g * t / v_t) - 1) / (np.e ** (2 * g * t / v_t) + 1)


def height_with_air_resistance(Cd: float, A: float, h: int, m: int, t: float) -> float:
    """공기저항을 고려한 낙하운동의 높이를 계산합니다. (m)"""
    v_t = terminal_velocity_with_air_resistance(Cd, A, m)

    return h + (
        v_t * t
        - v_t**2 / g * np.log(np.e ** (2 * g * t / v_t) + 1)
        + v_t**2 / g * np.log(2)
    )


def simulate(
    Cd: float,
    A: float,
    h: int,
    m: int,
    air_resistance: bool,
    mode: str,
    seconds: int,
    fps: int,
) -> None:
    x = np.linspace(0, seconds, fps * seconds + 1)

    if air_resistance:
        if mode == "속도":
            y = velocity_with_air_resistance(Cd, A, m, x)

        else:
            y = height_with_air_resistance(Cd, A, h, m, x)

    else:
        if mode == "속도":
            y = velocity(x)

        else:
            y = height(h, x)

    fig, ax = plt.subplots()
    ax: plt.Axes
    (line,) = ax.plot([], [])

    ax.set_xlim(x[0], x[-1] * 1.1)
    ax.set_xlabel("Time (s)")

    if mode == "속도":
        ax.set_ylim(0, y[-1] * 1.1)
        ax.set_ylabel("Velocity (m/s)")

    else:
        ax.set_ylim(y[-1] * 1.1, y[-0] * 1.1)
        ax.set_ylabel("Height (m)")

    def update(frame: int) -> tuple[plt.Line2D]:
        line.set_data(x[:frame], y[:frame])

        return (line,)

    if air_resistance:
        ax.set_title("Fall Motion with Air Resistance")

    else:
        ax.set_title("Free Fall Motion")

    ani = FuncAnimation(
        fig,
        update,
        frames=len(x),
        interval=1000 / fps,
        blit=True,
    )

    ani.save("video.mp4", "ffmpeg", fps)


def format_quality(quality: int) -> str:
    if quality == 20:
        return "낮음"

    if quality == 30:
        return "중간"

    return "높음"


st.set_page_config(
    page_title="낙하운동 시뮬레이터",
    page_icon=":apple:",
    menu_items={
        "About": "낙하운동 시뮬레이터",
    },
)

state = st.session_state

st.title("낙하운동 시뮬레이터", anchor=False)

placeholder = st.empty()
col1, col2, col3, col4 = st.columns(4)
col5, col6, col7, col8 = st.columns(4)
placeholder_button = st.empty()

state["Cd"] = col1.number_input("항력계수", value=0.42)
state["A"] = col2.number_input("단면적 (m^2)", value=19.25)
state["h"] = col3.number_input("초기 높이 (m)", value=70)
state["m"] = col4.number_input("질량 (kg)", value=1000)

col5.write(
    "<p style='font-size: 14px; margin-top: 1px; margin-bottom: 4.5px;'>공기저항</p>",
    unsafe_allow_html=True,
)
state["air_resistance"] = col5.toggle(
    "공기저항", value=True, label_visibility="collapsed"
)
state["mode"] = col6.radio("그래프 종류", ["속도", "높이"], horizontal=True)
state["seconds"] = col7.number_input("시간 (s)", 1, 60, 10)
state["fps"] = col8.selectbox("품질", [20, 30, 60], 1, format_quality)

if placeholder_button.button("시뮬레이션 시작", key="simulation"):
    with st.spinner("시뮬레이션 중..."):
        placeholder_button.button(
            "시뮬레이션 시작",
            key="simulating",
            disabled=True,
        )

        simulate(
            state["Cd"],
            state["A"],
            state["h"],
            state["m"],
            state["air_resistance"],
            state["mode"],
            state["seconds"],
            state["fps"],
        )

    placeholder.video("video.mp4")

    placeholder_button.button("돌아가기")
