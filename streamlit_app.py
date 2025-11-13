import altair as alt
import pandas as pd
import streamlit as st

DATA_PATH = "data/yearly_deaths_by_clinic-1.csv"

st.title("Yearly births and deaths by clinic")


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # ensure types
    df["Year"] = df["Year"].astype(int)
    df["Birth"] = pd.to_numeric(df["Birth"], errors="coerce")
    df["Deaths"] = pd.to_numeric(df["Deaths"], errors="coerce")
    return df


df = load_data(DATA_PATH)

st.sidebar.header("Controls")
clinics = sorted(df["Clinic"].unique())
selected_clinics = st.sidebar.multiselect("Select clinics", clinics, default=clinics)
year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
year_range = st.sidebar.slider("Year range", year_min, year_max, (year_min, year_max))

filtered = df.loc[
    df["Clinic"].isin(selected_clinics) & df["Year"].between(year_range[0], year_range[1])
]

st.markdown("### Data sample")
st.dataframe(filtered.reset_index(drop=True))

st.markdown("---")

st.markdown("#### Deaths over time (line chart)")
line = (
    alt.Chart(filtered)
    .mark_line(point=True)
    .encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Deaths:Q", title="Deaths"),
        color=alt.Color("Clinic:N", title="Clinic"),
        tooltip=["Year", "Clinic", "Birth", "Deaths"],
    )
    .properties(height=400, width=700)
)
st.altair_chart(line, use_container_width=True)

st.markdown("#### Deaths by year and clinic (grouped bars)")
bar = (
    alt.Chart(filtered)
    .mark_bar()
    .encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Deaths:Q", title="Deaths"),
        color=alt.Color("Clinic:N", title="Clinic"),
        column=alt.Column("Clinic:N", header=alt.Header(labelAngle=0, title=None)),
        tooltip=["Year", "Clinic", "Deaths"],
    )
    .properties(height=300)
)
st.altair_chart(bar, use_container_width=True)

st.markdown("#### Births vs Deaths (scatter)")
scatter = (
    alt.Chart(filtered)
    .mark_circle(opacity=0.7)
    .encode(
        x=alt.X("Birth:Q", title="Births"),
        y=alt.Y("Deaths:Q", title="Deaths"),
        size=alt.Size("Birth:Q", title="Births", scale=alt.Scale(range=[30, 400])),
        color=alt.Color("Clinic:N", title="Clinic"),
        tooltip=["Year", "Clinic", "Birth", "Deaths"],
    )
    .properties(height=400)
)
st.altair_chart(scatter, use_container_width=True)

st.markdown("\n---\n\nTip: adjust the clinic selection and year range in the sidebar to update the charts.")
