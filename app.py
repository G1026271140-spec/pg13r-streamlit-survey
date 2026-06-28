from __future__ import annotations

import csv
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st


APP_TITLE = "延长哀伤-13-修改版（PG-13-R）在线问卷"
TRANSLATOR = "译：刘新宪，周宁宁"
DATA_DIR = Path(os.environ.get("PG13R_DATA_DIR", "data"))
RESPONSES_FILE = DATA_DIR / "pg13r_responses.csv"

YES = "是"
NO = "否"
YES_NO_OPTIONS = [YES, NO]

SCALE_LABELS = {
    1: "不符合 1",
    2: "稍微符合 2",
    3: "比较符合 3",
    4: "非常符合 4",
    5: "完全符合 5",
}

SCORE_QUESTIONS = [
    {"id": "Q3", "text": "您感到自己怀念并渴望见到逝者吗？"},
    {"id": "Q4", "text": "您因为过于想念逝者而在做日常事务时有困难吗？"},
    {
        "id": "Q5",
        "text": "您对自己的在生活中的角色感到困惑，或者感到不知道自己是谁（即感到失去了自己的一部分）吗？",
    },
    {"id": "Q6", "text": "您难以相信逝者真的去世了吗？"},
    {"id": "Q7", "text": "您回避提示逝者离世的线索吗？"},
    {"id": "Q8", "text": "您感到与逝者离世有关的情绪痛苦（例如愤怒、苦楚、悲伤）吗？"},
    {
        "id": "Q9",
        "text": "您觉得难以让生活继续前进（例如，难以与朋友交往、培养兴趣、规划未来）吗？",
    },
    {"id": "Q10", "text": "您感到情感麻木或与他人疏远了吗？"},
    {"id": "Q11", "text": "您觉得没有逝者，生活就毫无意义吗？"},
    {"id": "Q12", "text": "没有逝者，您感到孤单或孤独吗？"},
]


def setup_page() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.markdown(
        """
        <style>
        :root {
            --warm-bg: #fff7ee;
            --warm-panel: #fffdf9;
            --warm-panel-strong: #fff1e1;
            --warm-line: #ecd2bd;
            --warm-text: #402a1f;
            --warm-muted: #7d6253;
            --warm-accent: #c46a3a;
            --warm-accent-dark: #9f4f2b;
            --warm-rose: #d88478;
            --warm-sage: #7d9a7b;
        }
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(249, 204, 166, 0.42), transparent 34rem),
                linear-gradient(135deg, #fff8f1 0%, #fff2e7 45%, #fffaf4 100%);
            color: var(--warm-text);
        }
        .block-container {
            max-width: 1080px;
            padding-top: 2rem;
            padding-bottom: 3.5rem;
        }
        [data-testid="stSidebar"] {
            background: #fff0e3;
            border-right: 1px solid var(--warm-line);
        }
        [data-testid="stForm"] {
            background: rgba(255, 253, 249, 0.94);
            border: 1px solid var(--warm-line);
            border-radius: 8px;
            box-shadow: 0 18px 48px rgba(137, 85, 49, 0.11);
            padding: 1.2rem 1.25rem 1.35rem;
        }
        h1, h2, h3, h4 {
            color: var(--warm-text);
            letter-spacing: 0;
        }
        .hero-panel {
            border: 1px solid var(--warm-line);
            border-radius: 8px;
            background: linear-gradient(135deg, rgba(255, 253, 249, 0.96), rgba(255, 239, 224, 0.94));
            box-shadow: 0 18px 54px rgba(137, 85, 49, 0.12);
            padding: 1.45rem 1.5rem;
            margin: 0.4rem 0 1.4rem;
        }
        .eyebrow {
            color: var(--warm-accent-dark);
            font-size: 0.84rem;
            font-weight: 700;
            margin-bottom: 0.35rem;
        }
        .hero-title {
            font-size: clamp(1.95rem, 4vw, 3.2rem);
            line-height: 1.12;
            font-weight: 800;
            margin: 0;
        }
        .hero-copy {
            color: var(--warm-muted);
            font-size: 1rem;
            line-height: 1.8;
            margin: 0.95rem 0 0;
        }
        .soft-note {
            border: 1px solid #f0d4bf;
            border-left: 4px solid var(--warm-rose);
            background: #fff8ef;
            border-radius: 8px;
            padding: 0.9rem 1rem;
            color: #5e4234;
            margin: 1rem 0 1.2rem;
        }
        .scale-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(110px, 1fr));
            border: 1px solid #dfc2ac;
            border-radius: 8px;
            margin: 0.8rem 0 1.1rem;
            overflow: hidden;
        }
        .scale-cell {
            min-height: 64px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-weight: 750;
            color: #3d281f;
            border-right: 1px solid #dfc2ac;
        }
        .scale-cell:last-child {
            border-right: none;
        }
        .scale-1 { background: #fffdf9; }
        .scale-2 { background: #fff1df; }
        .scale-3 { background: #f6cfb1; }
        .scale-4 { background: #e9aa86; }
        .scale-5 { background: #cf7b59; color: #fffaf5; }
        .result-hero {
            border: 1px solid var(--warm-line);
            border-radius: 8px;
            background: linear-gradient(135deg, #fffaf4 0%, #ffe9d8 100%);
            box-shadow: 0 20px 60px rgba(137, 85, 49, 0.14);
            padding: 1.7rem;
            margin: 0.3rem 0 1.1rem;
        }
        .result-kicker {
            color: var(--warm-accent-dark);
            font-weight: 800;
            font-size: 0.9rem;
            margin-bottom: 0.35rem;
        }
        .result-title {
            color: var(--warm-text);
            font-size: clamp(2rem, 5vw, 3.7rem);
            line-height: 1.06;
            font-weight: 850;
            margin: 0;
        }
        .result-message {
            color: #5f4435;
            font-size: 1.08rem;
            line-height: 1.85;
            margin: 1rem 0 0;
        }
        .score-band {
            display: grid;
            grid-template-columns: minmax(140px, 0.55fr) minmax(220px, 1.45fr);
            gap: 1rem;
            align-items: stretch;
            margin: 1rem 0;
        }
        .score-box, .guidance-box {
            border: 1px solid var(--warm-line);
            border-radius: 8px;
            background: rgba(255, 253, 249, 0.94);
            padding: 1.1rem;
        }
        .score-number {
            font-size: clamp(3.1rem, 8vw, 5rem);
            line-height: 1;
            font-weight: 900;
            color: var(--warm-accent-dark);
        }
        .score-label {
            color: var(--warm-muted);
            font-weight: 700;
            margin-top: 0.3rem;
        }
        .guidance-box strong {
            color: var(--warm-accent-dark);
        }
        .gentle-list {
            color: #684b3b;
            line-height: 1.85;
            margin-top: 0.85rem;
        }
        .stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button {
            background: linear-gradient(135deg, var(--warm-accent), var(--warm-accent-dark));
            color: #fffaf5;
            border: 0;
            border-radius: 8px;
            font-weight: 800;
            box-shadow: 0 10px 22px rgba(159, 79, 43, 0.18);
        }
        .stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
            border: 0;
            color: #ffffff;
            filter: brightness(0.98);
        }
        [data-testid="stMetric"] {
            background: #fffdf9;
            border: 1px solid var(--warm-line);
            border-radius: 8px;
            padding: 0.85rem 1rem;
        }
        @media (max-width: 760px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }
            .scale-grid, .score-band {
                grid-template-columns: 1fr;
            }
            .scale-cell {
                min-height: 42px;
                border-right: none;
                border-bottom: 1px solid #dfc2ac;
            }
            .scale-cell:last-child {
                border-bottom: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def get_secret(name: str, default: str = "") -> str:
    try:
        return str(st.secrets.get(name, default))
    except Exception:
        return default


def format_scale(value: int) -> str:
    return SCALE_LABELS[value]


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def rerun_app() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


def evaluate_result(q1: str, months: int, q13: str, ratings: dict[str, int]) -> dict[str, object]:
    total_score = sum(ratings.values())
    criteria = {
        "Q1 重要他人丧失": q1 == YES,
        "Q2 离世时间至少 6 个月": months >= 6,
        "Q3-Q12 总分不少于 30 分": total_score >= 30,
        "Q13 功能明显下降": q13 == YES,
    }
    positive = all(criteria.values())
    return {
        "total_score": total_score,
        "criteria": criteria,
        "positive": positive,
    }


def build_submission_row(
    respondent_code: str,
    q1: str,
    months: int,
    q13: str,
    consent: bool,
    ratings: dict[str, int],
    result: dict[str, object],
) -> dict[str, object]:
    criteria = result["criteria"]
    row: dict[str, object] = {
        "submission_id": uuid.uuid4().hex[:12],
        "submitted_at": utc_timestamp(),
        "respondent_code": respondent_code,
        "consent": consent,
        "Q1_lost_important_person": q1,
        "Q2_months_since_death": months,
        "Q13_functional_impairment": q13,
        "total_score_Q3_Q12": result["total_score"],
        "screening_positive": result["positive"],
    }
    for key, value in criteria.items():
        row[f"criterion_{key}"] = value
    for question in SCORE_QUESTIONS:
        qid = question["id"]
        row[f"{qid}_score"] = ratings[qid]
        row[f"{qid}_label"] = SCALE_LABELS[ratings[qid]]
    return row


def save_submission(row: dict[str, object]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_exists = RESPONSES_FILE.exists()
    with RESPONSES_FILE.open("a", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=list(row.keys()))
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def load_submissions() -> pd.DataFrame:
    if not RESPONSES_FILE.exists():
        return pd.DataFrame()
    return pd.read_csv(RESPONSES_FILE)


def render_header() -> None:
    st.markdown(
        f"""
        <section class="hero-panel">
            <div class="eyebrow">PG-13-R 在线自评</div>
            <h1 class="hero-title">{APP_TITLE}</h1>
            <p class="hero-copy">
                {TRANSLATOR}<br>
                这是一份关于失去重要他人后的哀伤体验自评。请在一个安静的时刻作答，
                不需要追求“正确答案”，只需选择最贴近您当前感受的一项。
            </p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="soft-note">
        本问卷仅用于延长哀伤相关症状的自评与筛查参考，不作为正式诊断。
        如果您正在经历强烈痛苦，或出现伤害自己或他人的想法，请立即联系当地急救服务、
        危机干预热线或可信赖的人。
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_scale_legend() -> None:
    st.markdown("#### Q3-Q12 作答说明")
    st.markdown("自从 ta 离世后，或者由于 ta 的离世，请选择最符合您近况的一项。")
    st.markdown(
        """
        <div class="scale-grid">
            <div class="scale-cell scale-1">不符合<br>1</div>
            <div class="scale-cell scale-2">稍微符合<br>2</div>
            <div class="scale-cell scale-3">比较符合<br>3</div>
            <div class="scale-cell scale-4">非常符合<br>4</div>
            <div class="scale-cell scale-5">完全符合<br>5</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def validate_submission(
    q1: str | None,
    months: int | None,
    q13: str | None,
    consent: bool,
    ratings: dict[str, int | None],
) -> list[str]:
    missing: list[str] = []
    if not consent:
        missing.append("请先勾选知情同意。")
    if q1 is None:
        missing.append("请回答 Q1。")
    if months is None:
        missing.append("请填写 Q2 的月份。")
    for question in SCORE_QUESTIONS:
        if ratings.get(question["id"]) is None:
            missing.append(f"请回答 {question['id']}。")
    if q13 is None:
        missing.append("请回答 Q13。")
    return missing


def result_title_and_message(result: dict[str, object]) -> tuple[str, str, str]:
    total_score = int(result["total_score"])
    positive = bool(result["positive"])
    if positive:
        return (
            "哀伤指数较高",
            "当前您的哀伤指数较高。请先慢慢呼吸一下，您愿意完成这份问卷，本身就是在认真照顾自己。",
            "建议您在方便的时候前往专业医院或心理健康机构，进行更准确、更完整的评估。让专业人员陪您一起梳理这些感受，会比一个人承受轻一些。",
        )
    if total_score >= 30:
        return (
            "需要多给自己一些照顾",
            "您的哀伤指数有些偏高，说明这段经历可能仍在占据您很多心力。",
            "如果这些感受已经影响到睡眠、工作、学习、人际关系或日常生活，建议您寻求专业医院或心理健康机构的进一步支持。",
        )
    return (
        "请继续温柔地照顾自己",
        "从本次作答来看，您的哀伤指数暂时没有处在较高范围。",
        "这并不代表您的难过不重要。请允许自己有起伏，也可以在需要时和可信赖的人聊一聊。",
    )


def render_result_page() -> None:
    result = st.session_state.get("latest_result")

    if not result:
        st.markdown(
            """
            <section class="result-hero">
                <div class="result-kicker">尚无结果</div>
                <h1 class="result-title">请先完成问卷</h1>
                <p class="result-message">完成提交后，系统会自动跳转到这里显示您的测试结果。</p>
            </section>
            """,
            unsafe_allow_html=True,
        )
        if st.button("去填写问卷", use_container_width=True):
            st.session_state.current_page = "填写问卷"
            rerun_app()
        return

    title, main_message, supporting_message = result_title_and_message(result)
    total_score = int(result["total_score"])

    st.markdown(
        f"""
        <section class="result-hero">
            <div class="result-kicker">您的测试结果</div>
            <h1 class="result-title">{title}</h1>
            <p class="result-message">{main_message}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="score-band">
            <div class="score-box">
                <div class="score-number">{total_score}</div>
                <div class="score-label">您的哀伤指数 / 50</div>
            </div>
            <div class="guidance-box">
                <strong>给您的建议</strong>
                <p>{supporting_message}</p>
                <div class="gentle-list">
                如果您近期感到难以承受，或出现伤害自己/他人的想法，请立即联系当地急救服务、
                危机干预热线，或身边可信赖的人。
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(min(total_score / 50, 1.0), text=f"哀伤指数：{total_score}/50")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("重新填写", use_container_width=True):
            st.session_state.current_page = "填写问卷"
            rerun_app()
    with col2:
        if st.button("返回问卷首页", use_container_width=True):
            st.session_state.current_page = "填写问卷"
            rerun_app()


def render_questionnaire() -> None:
    render_header()

    with st.form("pg13r_form", clear_on_submit=True):
        st.subheader("基本问题")
        respondent_code = st.text_input(
            "受访者编号（可选，不建议填写身份证号、手机号等敏感信息）",
            placeholder="例如：A001",
        )
        q1 = st.radio(
            "Q1. 您是否失去了对您很重要的人？",
            YES_NO_OPTIONS,
            index=None,
            horizontal=True,
        )
        months = st.number_input(
            "Q2. 您的重要他人去世已有几个月了？",
            min_value=0,
            max_value=1200,
            value=None,
            step=1,
            placeholder="例如：8",
        )

        render_scale_legend()
        ratings: dict[str, int | None] = {}
        for question in SCORE_QUESTIONS:
            ratings[question["id"]] = st.radio(
                f"{question['id']}. {question['text']}",
                options=list(SCALE_LABELS.keys()),
                index=None,
                format_func=format_scale,
                horizontal=True,
                key=f"rating_{question['id']}",
            )

        st.subheader("功能影响")
        q13 = st.radio(
            "Q13. 上述症状，是否对您的社交、职业或其他重要领域的功能造成明显下降？",
            YES_NO_OPTIONS,
            index=None,
            horizontal=True,
        )
        consent = st.checkbox("我理解本问卷仅用于筛查参考，不作为正式诊断，并同意提交本次作答。")
        submitted = st.form_submit_button("提交并查看结果", use_container_width=True)

    if not submitted:
        return

    missing = validate_submission(q1, months, q13, consent, ratings)
    if missing:
        st.error("提交前请补全以下内容：")
        for item in missing:
            st.write(f"- {item}")
        return

    completed_ratings = {key: int(value) for key, value in ratings.items() if value is not None}
    result = evaluate_result(str(q1), int(months), str(q13), completed_ratings)
    row = build_submission_row(
        respondent_code=respondent_code.strip(),
        q1=str(q1),
        months=int(months),
        q13=str(q13),
        consent=consent,
        ratings=completed_ratings,
        result=result,
    )
    save_submission(row)
    st.session_state.latest_result = result
    st.session_state.latest_answers = {
        "respondent_code": respondent_code.strip(),
        "q1": str(q1),
        "months": int(months),
        "q13": str(q13),
        "ratings": completed_ratings,
        "submitted_at": row["submitted_at"],
    }
    st.session_state.current_page = "测试结果"
    rerun_app()


def render_admin() -> None:
    st.title("结果管理")
    st.caption("此页面用于查看和下载本应用本地保存的问卷提交记录。")

    admin_password = get_secret("ADMIN_PASSWORD", os.environ.get("ADMIN_PASSWORD", ""))
    if not admin_password:
        st.warning(
            "尚未配置 ADMIN_PASSWORD。为保护问卷数据，结果管理页暂不开放。"
            "部署到 Streamlit Cloud 后，请在 App secrets 中配置 ADMIN_PASSWORD。"
        )
        st.code('ADMIN_PASSWORD = "请替换为足够复杂的管理口令"', language="toml")
        return

    password = st.text_input("管理员口令", type="password")
    if password != admin_password:
        st.info("请输入管理员口令后查看结果。")
        return

    submissions = load_submissions()
    if submissions.empty:
        st.info("还没有收到问卷提交。")
        return

    st.metric("提交数量", len(submissions))
    st.dataframe(submissions, use_container_width=True, hide_index=True)
    csv_data = submissions.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "下载 CSV",
        data=csv_data,
        file_name="pg13r_responses.csv",
        mime="text/csv",
        use_container_width=True,
    )


def render_reference_note() -> None:
    with st.expander("量表说明与数据来源"):
        st.markdown(
            """
            - 此量表的 Cronbach's α = 0.83～0.93。
            - 图片中的延长哀伤障碍建议规则：总分 ≥ 30 分，以及第 1 和第 13 项都选择“是”，第 2 项至少为 6 个月。
            - 此量表适合作为延长哀伤障碍症状评估，但不宜用作正式诊断。
            - 数据来源：Prigerson H G, Boelen P A, Xu J, et al. Validation of the new DSM-5-TR criteria for prolonged grief disorder and the PG-13-Revised (PG-13-R) scale[J]. World Psychiatry, 2021, 20(1): 96-106.
            - 图片来源标注：哀伤疗愈之家 https://mp.weixin.qq.com/s/WolYX3Ey6LkdsCL2OCjjw
            """
        )


def get_sidebar_page() -> str:
    if "current_page" not in st.session_state:
        st.session_state.current_page = "填写问卷"

    pages = ["填写问卷"]
    if st.session_state.get("latest_result") is not None:
        pages.append("测试结果")
    pages.append("结果管理")

    current_page = st.session_state.current_page
    if current_page not in pages:
        current_page = "填写问卷"

    selected_page = st.sidebar.radio("页面", pages, index=pages.index(current_page))
    st.session_state.current_page = selected_page
    st.sidebar.markdown("---")
    st.sidebar.caption("PG-13-R 在线问卷")
    return selected_page


def main() -> None:
    setup_page()
    page = get_sidebar_page()

    if page == "填写问卷":
        render_questionnaire()
        render_reference_note()
    elif page == "测试结果":
        render_result_page()
    else:
        render_admin()


if __name__ == "__main__":
    main()
