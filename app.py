from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


DATA_FILE = Path(__file__).with_name("dopa_04.csv")
DATASET_URL = "https://data.go.th/dataset/dopa_04"

AGE_COLUMNS = [
    "วัยเด็ก (อายุ 0-14 ปี)",
    "วัยทำงาน (15-59 ปี)",
    "วัยสูงอายุ (60 ปีขึ้นไป)",
]

AGE_LABELS = {
    "วัยเด็ก (อายุ 0-14 ปี)": "วัยเด็ก",
    "วัยทำงาน (15-59 ปี)": "วัยทำงาน",
    "วัยสูงอายุ (60 ปีขึ้นไป)": "วัยสูงอายุ",
}


@st.cache_data
def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_FILE)
    data.columns = data.columns.str.replace("\ufeff", "", regex=False).str.strip()

    for column in ["ปี", *AGE_COLUMNS]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=["ปี", "จังหวัด", *AGE_COLUMNS]).copy()
    data["ปี"] = data["ปี"].astype(int)
    data["ประชากรรวม"] = data[AGE_COLUMNS].sum(axis=1)
    return data


def format_people(value: float) -> str:
    return f"{value:,.0f} คน"


def clean_chart_layout(figure, height: int = 420):
    figure.update_layout(
        height=height,
        margin=dict(l=12, r=12, t=18, b=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", color="#334155", size=13),
        hoverlabel=dict(bgcolor="#0F172A", font_color="white", bordercolor="#0F172A"),
    )
    return figure


st.set_page_config(
    page_title="ข้อมูลประชากรไทย",
    page_icon="◌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stAppViewContainer"] {
            background: #F6F8FB;
        }

        .block-container {
            max-width: 1180px;
            padding-top: 2.6rem;
            padding-bottom: 3rem;
        }

        .hero-kicker {
            color: #2563EB;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            margin-bottom: 0.55rem;
            text-transform: uppercase;
        }

        .hero-title {
            color: #0F172A;
            font-size: clamp(2rem, 4vw, 3.25rem);
            font-weight: 750;
            letter-spacing: -0.04em;
            line-height: 1.08;
            margin: 0;
        }

        .hero-subtitle {
            color: #64748B;
            font-size: 1rem;
            line-height: 1.7;
            margin: 0.85rem 0 2rem 0;
            max-width: 720px;
        }

        .section-title {
            color: #0F172A;
            font-size: 1.05rem;
            font-weight: 700;
            margin: 0.25rem 0 0.7rem 0;
        }

        .chart-title {
            color: #0F172A;
            font-size: 1rem;
            font-weight: 700;
            margin: 0.15rem 0 0 0;
        }

        .chart-subtitle {
            color: #94A3B8;
            font-size: 0.78rem;
            margin: 0.15rem 0 0.35rem 0;
        }

        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E6EAF0;
            border-radius: 16px;
            box-shadow: 0 8px 28px rgba(15, 23, 42, 0.045);
            padding: 1.05rem 1.2rem;
        }

        div[data-testid="stMetricLabel"] {
            color: #64748B;
        }

        div[data-testid="stMetricValue"] {
            color: #0F172A;
            font-size: 1.7rem;
        }

        div[data-testid="stVerticalBlockBorderWrapper"] {
            background: #FFFFFF;
            border-color: #E6EAF0;
            border-radius: 18px;
            box-shadow: 0 8px 28px rgba(15, 23, 42, 0.04);
        }

        div[data-baseweb="select"] > div {
            background: #FFFFFF;
            border-color: #DDE3EC;
            border-radius: 12px;
        }

        .source-note {
            color: #94A3B8;
            font-size: 0.78rem;
            line-height: 1.6;
            margin-top: 1.5rem;
        }

        .source-note a {
            color: #64748B;
            text-decoration: none;
        }

        .source-note a:hover {
            color: #2563EB;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="hero-kicker">Thailand Open Data</div>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">ภาพรวมประชากรไทย</h1>', unsafe_allow_html=True)
st.markdown(
    """
    <p class="hero-subtitle">
        สำรวจจำนวนประชากรจากการทะเบียนในแต่ละจังหวัด
        พร้อมเปรียบเทียบโครงสร้างประชากรตามช่วงวัย
    </p>
    """,
    unsafe_allow_html=True,
)

try:
    df = load_data()
except Exception as error:
    st.error(f"ไม่สามารถโหลดข้อมูลได้: {error}")
    st.stop()

years = sorted(df["ปี"].unique(), reverse=True)

st.markdown('<div class="section-title">เลือกมุมมองข้อมูล</div>', unsafe_allow_html=True)
year_filter, province_filter, filter_space = st.columns([1, 1.5, 2.5])

with year_filter:
    selected_year = st.selectbox("ปี พ.ศ.", years)

year_df = df[df["ปี"] == selected_year].copy()
provinces = sorted(year_df["จังหวัด"].unique())
default_province = provinces.index("กรุงเทพมหานคร") if "กรุงเทพมหานคร" in provinces else 0

with province_filter:
    selected_province = st.selectbox("จังหวัด", provinces, index=default_province)

province_row = year_df[year_df["จังหวัด"] == selected_province].iloc[0]
total_population = province_row["ประชากรรวม"]
working_share = province_row[AGE_COLUMNS[1]] / total_population * 100
elderly_share = province_row[AGE_COLUMNS[2]] / total_population * 100

metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("ประชากรรวม", format_people(total_population))
metric_2.metric(
    "ประชากรวัยทำงาน",
    format_people(province_row[AGE_COLUMNS[1]]),
    f"{working_share:.1f}% ของทั้งหมด",
    delta_color="off",
)
metric_3.metric(
    "ประชากรวัยสูงอายุ",
    format_people(province_row[AGE_COLUMNS[2]]),
    f"{elderly_share:.1f}% ของทั้งหมด",
    delta_color="off",
)

st.write("")

top_provinces = year_df.nlargest(10, "ประชากรรวม").sort_values("ประชากรรวม")
population_chart = px.bar(
    top_provinces,
    x="ประชากรรวม",
    y="จังหวัด",
    orientation="h",
    labels={"ประชากรรวม": "จำนวนประชากร", "จังหวัด": ""},
    color_discrete_sequence=["#2563EB"],
)
population_chart.update_traces(
    marker_line_width=0,
    hovertemplate="<b>%{y}</b><br>%{x:,.0f} คน<extra></extra>",
)
population_chart.update_xaxes(
    showgrid=True,
    gridcolor="#EEF2F7",
    zeroline=False,
    tickformat="~s",
    title_text="จำนวนประชากร (คน)",
)
population_chart.update_yaxes(showgrid=False, title_text="")
clean_chart_layout(population_chart)

age_df = pd.DataFrame(
    {
        "ช่วงวัย": [AGE_LABELS[column] for column in AGE_COLUMNS],
        "จำนวนประชากร": [province_row[column] for column in AGE_COLUMNS],
    }
)
age_chart = px.pie(
    age_df,
    names="ช่วงวัย",
    values="จำนวนประชากร",
    hole=0.66,
    color="ช่วงวัย",
    color_discrete_map={
        "วัยเด็ก": "#93C5FD",
        "วัยทำงาน": "#2563EB",
        "วัยสูงอายุ": "#F59E0B",
    },
)
age_chart.update_traces(
    textposition="inside",
    textinfo="percent",
    hovertemplate="<b>%{label}</b><br>%{value:,.0f} คน<br>%{percent}<extra></extra>",
    marker=dict(line=dict(color="#FFFFFF", width=3)),
)
age_chart.add_annotation(
    text=f"{total_population / 1_000_000:.2f}M<br><span style='font-size:11px;color:#94A3B8'>คนทั้งหมด</span>",
    x=0.5,
    y=0.5,
    showarrow=False,
    font=dict(size=20, color="#0F172A"),
)
clean_chart_layout(age_chart)

left, right = st.columns([1.35, 1])
with left:
    with st.container(border=True):
        st.markdown(
            f'<div class="chart-title">10 จังหวัดที่มีประชากรมากที่สุด</div>'
            f'<div class="chart-subtitle">ข้อมูลปี พ.ศ. {selected_year}</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(population_chart, width="stretch")

with right:
    with st.container(border=True):
        st.markdown(
            f'<div class="chart-title">โครงสร้างประชากรตามช่วงวัย</div>'
            f'<div class="chart-subtitle">จังหวัด{selected_province}</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(age_chart, width="stretch")

with st.expander("ดูข้อมูลรายจังหวัดทั้งหมด"):
    display_df = (
        year_df[["จังหวัด", *AGE_COLUMNS, "ประชากรรวม"]]
        .sort_values("ประชากรรวม", ascending=False)
        .reset_index(drop=True)
    )
    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True,
        column_config={
            column: st.column_config.NumberColumn(column, format="%,d")
            for column in [*AGE_COLUMNS, "ประชากรรวม"]
        },
    )

st.markdown(
    f"""
    <p class="source-note">
        แหล่งข้อมูล: กรมการปกครอง ผ่าน
        <a href="{DATASET_URL}" target="_blank">data.go.th</a>
        · ครอบคลุมปี พ.ศ. {min(years)}–{max(years)} · {df['จังหวัด'].nunique()} จังหวัด
    </p>
    """,
    unsafe_allow_html=True,
)
