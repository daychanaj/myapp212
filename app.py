import pandas as pd
import plotly.express as px
import streamlit as st


DATA_URL = (
    "https://krabi.gdcatalog.go.th/dataset/"
    "0a8a80f7-2337-4e11-8c61-50a5c03c4e9b/resource/"
    "b7ac6e4d-70fe-4cb5-95f5-00b984393bcb/download/dopa_04.csv"
)

AGE_COLUMNS = [
    "วัยเด็ก (อายุ 0-14 ปี)",
    "วัยทำงาน (15-59 ปี)",
    "วัยสูงอายุ (60 ปีขึ้นไป)",
]


@st.cache_data(ttl=3600)
def load_data() -> pd.DataFrame:
    data = pd.read_csv(DATA_URL)
    data.columns = data.columns.str.replace("\ufeff", "", regex=False).str.strip()

    for column in ["ปี", *AGE_COLUMNS]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.dropna(subset=["ปี", "จังหวัด", *AGE_COLUMNS]).copy()
    data["ปี"] = data["ปี"].astype(int)
    data["ประชากรรวม"] = data[AGE_COLUMNS].sum(axis=1)
    return data


st.set_page_config(
    page_title="ข้อมูลประชากรไทย",
    page_icon="📊",
    layout="wide",
)

st.title("แดชบอร์ดข้อมูลประชากรไทย")
st.write(
    "วิเคราะห์ประชากรจากการทะเบียน จำแนกตามจังหวัด ปี และช่วงวัย "
    "โดยใช้ข้อมูลเปิดจาก data.go.th"
)

try:
    df = load_data()
except Exception as error:
    st.error(f"ไม่สามารถโหลดข้อมูลได้: {error}")
    st.stop()

years = sorted(df["ปี"].unique(), reverse=True)
selected_year = st.sidebar.selectbox("เลือกปี พ.ศ.", years)

year_df = df[df["ปี"] == selected_year].copy()
provinces = sorted(year_df["จังหวัด"].unique())
selected_province = st.sidebar.selectbox("เลือกจังหวัด", provinces)

province_row = year_df[year_df["จังหวัด"] == selected_province].iloc[0]

metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("ประชากรรวม", f"{province_row['ประชากรรวม']:,.0f} คน")
metric_2.metric("วัยทำงาน", f"{province_row[AGE_COLUMNS[1]]:,.0f} คน")
metric_3.metric("วัยสูงอายุ", f"{province_row[AGE_COLUMNS[2]]:,.0f} คน")

top_provinces = year_df.nlargest(10, "ประชากรรวม").sort_values("ประชากรรวม")
population_chart = px.bar(
    top_provinces,
    x="ประชากรรวม",
    y="จังหวัด",
    orientation="h",
    title=f"10 จังหวัดที่มีประชากรมากที่สุด ปี {selected_year}",
    labels={"ประชากรรวม": "จำนวนประชากร (คน)"},
    color="ประชากรรวม",
    color_continuous_scale="Blues",
)
population_chart.update_layout(coloraxis_showscale=False)

age_df = pd.DataFrame(
    {
        "ช่วงวัย": ["วัยเด็ก", "วัยทำงาน", "วัยสูงอายุ"],
        "จำนวนประชากร": [province_row[column] for column in AGE_COLUMNS],
    }
)
age_chart = px.pie(
    age_df,
    names="ช่วงวัย",
    values="จำนวนประชากร",
    title=f"สัดส่วนประชากรตามช่วงวัย จังหวัด{selected_province}",
    hole=0.4,
)

left, right = st.columns(2)
with left:
    st.plotly_chart(population_chart, use_container_width=True)
with right:
    st.plotly_chart(age_chart, use_container_width=True)

st.subheader("ตัวอย่างข้อมูล")
st.dataframe(
    year_df[["จังหวัด", *AGE_COLUMNS, "ประชากรรวม"]]
    .sort_values("ประชากรรวม", ascending=False),
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "แหล่งข้อมูล: กรมการปกครอง ผ่านเว็บไซต์ data.go.th "
    "(ประชากรจากการทะเบียน จำแนกรายจังหวัดและช่วงวัย)"
)
