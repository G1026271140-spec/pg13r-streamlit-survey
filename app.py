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

YES_NO_OPTIONS = ["是", "否"]
SCALE_LABELS = {
    1: "不符合 1",
    2: "稍微符合 2",
    3: "比较符合 3",
    4: "非常符合 4",
    5: "完全符合 5",
}

SCORE_QUESTIONS = [
    {
        "id": "Q3",
        "text": "您感到自己怀念并渴望见到逝者吗？",
    },
    {
        "id": "Q4",
        "text": "您因为过于想念逝者而在做日常事务时有困难吗？",
    },
    {
        "id": "Q5",
        "text": "您对自己的在生活中的角色感到困惑，或者感到不知道自己是谁（即感到失去了自己的一部分）吗？",
    },
    {
        "id": "Q6",
        "text": "您难以相信逝者真的去世了吗？",
    },
    {
        "id": "Q7",
        "text": "您回避提示逝者离世的线索吗？",
    },
    {
        "id": "Q8",
        "text": "您感到与逝者离世有关的情绪痛苦（例如愤怒、苦楚、悲伤）吗？",
    },
    {
        "id": "Q9",
        "text": "您觉得难以让生活继续前进（例如，难以与朋友交往、培养兴趣、规划未来）吗？",
    },
    {
        "id": "Q10",
        "text": "您感到情感麻木或与他人疏远了吗？",
    },
    {
        "id": "Q11",
        "text": "您觉得没有逝者，生活就毫无意义吗？",
    },
    {
        "id": "Q12",
        "text": "没有逝者，您感到孤单或孤独吗？",
    },
]


def setup_page() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 1120px;
            padding-top: 2.2rem;
            padding-bottom: 3rem;
        }
        .intro-note {
            border-left: 4px solid #2c9f7a;
            background: #eef8f4;
            padding: 0.9rem 1rem;
            color: #18362e;
            margin: 1rem 0 1.2rem;
        }
        .scale-grid {
            display: grid;
            grid-template-columns: repeat(5, minmax(110px, 1fr));
            border: 1px solid #b7c9c0;
            margin: 0.8rem 0 1.1rem;
            overflow: hidden;
        }
        .scale-cell {
            min-height: 64px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            font-weight: 700;
            color: #10231e;
            border-right: 1px solid #9db8ad;
        }
        .scale-cell:last-child {
            border-right: none;
        }
        .scale-1 { background: #ffffff; }
        .scale-2 { background: #c9f2df; }
        .scale-3 { background: #9fe2c8; }
        .scale-4 { background: #70cda9; }
        .scale-5 { background: #53b58f; }
        .result-positive {
            border: 1px solid #bd6b28;
            background: #fff6ed;
            padding: 1rem;
            color: #5e310e;
        }
        .result-negative {
            border: 1px solid #68a98f;
            background: #f0faf6;
            padding: 1rem;
            color: #174536;
        }
        @media (max-width: 760px) {
            .scale-grid {
                grid-template-columns: 1fr;
            }
            .scale-cell {
                min-height: 42px;
                border-right: none;
                border-bottom: 1px solid #9db8ad;
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


def evaluate_result(q1: str, months: int, q13: str, ratings: dict[str, int]) -> dict[str, object]:
    total_score = sum(ratings.values())
    criteria = {
        "Q1 重要他人丧失": q1 == "是",
        "Q2 离世时间至少 6 个月": months >= 6,
        "Q3-Q12 总分不少于 30 分": total_score >= 30,
        "Q13 功能明显下降": q13 == "是",
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
    st.title(APP_TITLE)
    st.caption(TRANSLATOR)
    st.markdown(
        """
        <div class="intro-note">
        本问卷适合作为延长哀伤相关症状的自评与筛查参考，不宜用作正式诊断。
        如果您正在经历强烈痛苦，或出现伤害自己/他人的想法，请立即联系当地急救服务、
        危机干预热线或可信赖的人。
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_scale_legend() -> None:
    st.markdown("#### Q3-Q12 作答说明")
    st.markdown("自从 ta 离世后，或者由于 ta 的离世……请选择最符合您近况的一项。")
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


def render_result(result: dict[str, object]) -> None:
    criteria = result["criteria"]
    total_score = result["total_score"]
    positive = result["positive"]

    st.subheader("提交结果")
    st.metric("Q3-Q12 总分", f"{total_score} / 50")
    if positive:
        st.markdown(
            """
            <div class="result-positive">
            按本问卷图片中的规则，当前结果达到延长哀伤障碍筛查阳性提示：
            总分 ≥ 30，Q1 和 Q13 均选择“是”，且 Q2 至少为 6 个月。
            该结果不能替代专业诊断，建议在需要时联系专业心理健康服务。
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="result-negative">
            按本问卷图片中的规则，当前结果未同时满足延长哀伤障碍筛查阳性条件。
            如果痛苦持续影响生活，仍建议寻求专业支持。
            </div>
            """,
            unsafe_allow_html=True,
        )

    criteria_frame = pd.DataFrame(
        [{"规则": key, "是否满足": "是" if value else "否"} for key, value in criteria.items()]
    )
    st.dataframe(criteria_frame, hide_index=True, use_container_width=True)


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
        submitted = st.form_submit_button("提交问卷", use_container_width=True)

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
    st.success("问卷已提交。")
    render_result(result)


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


def main() -> None:
    setup_page()
    page = st.sidebar.radio("页面", ["填写问卷", "结果管理"])
    st.sidebar.markdown("---")
    st.sidebar.caption("PG-13-R 在线问卷原型")

    if page == "填写问卷":
        render_questionnaire()
        render_reference_note()
    else:
        render_admin()


if __name__ == "__main__":
    main()
