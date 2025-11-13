import altair as alt
import pandas as pd
import streamlit as st

DATA_PATH = "data/yearly_deaths_by_clinic-1.csv"

# year when hand-washing was introduced in Semmelweis' analysis
HANDWASH_YEAR = 1847

st.title("Yearly births and deaths by clinic")

st.markdown(
    "Sonia Chavelas Gonzalez  \n"
    "Emanuel Stanescu Moloman  \n"
    "Priyal Vyas  \n"
    "Nina Myers"
)

st.markdown(
    "This notebook visualizes yearly births and deaths from two clinics in the 1840s."
    " The dataset is the classic Semmelweis case used to study how hand-washing changed outcomes."
)


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

# Findings and quick metrics in the sidebar so they're always visible
st.sidebar.header("Findings")
st.sidebar.markdown(
    "- Clinic 1 shows a large drop in deaths around 1847 (hand-washing introduction).\n"
    "- Clinic 2 has lower mortality across the period.\n\n"
    "Use the filters above to refine by year or clinic."
)

sel_for_metrics = df[df["Clinic"].isin(selected_clinics) & df["Year"].between(year_range[0], year_range[1])]
pre = sel_for_metrics[sel_for_metrics["Year"] < HANDWASH_YEAR]["Deaths"].mean()
post = sel_for_metrics[sel_for_metrics["Year"] >= HANDWASH_YEAR]["Deaths"].mean()

# compute percent change (post vs pre)
pct_change = None
if (not pd.isna(pre)) and (pre != 0) and (not pd.isna(post)):
    pct_change = (post - pre) / pre * 100

st.sidebar.markdown("**Quick metrics (selected clinics & years)**")
st.sidebar.metric("Avg deaths (before 1847)", f"{pre:.1f}" if not pd.isna(pre) else "N/A")
if pct_change is None:
    st.sidebar.metric("Avg deaths (from 1847)", f"{post:.1f}" if not pd.isna(post) else "N/A")
else:
    # show percent change as delta
    st.sidebar.metric("Avg deaths (from 1847)", f"{post:.1f}", delta=f"{pct_change:+.1f}%")

st.markdown("### Data sample")
st.dataframe(filtered.reset_index(drop=True))

st.markdown("---")

st.markdown("#### Deaths over time (line chart)")

base_line = (
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

rule = alt.Chart(pd.DataFrame({"Year": [HANDWASH_YEAR]})).mark_rule(color="red", strokeDash=[4, 4]).encode(
    x=alt.X("Year:O")
)

rule_text = alt.Chart(pd.DataFrame({"Year": [HANDWASH_YEAR], "label": [f"Hand-washing: {HANDWASH_YEAR}"]})).mark_text(
    align="left", dx=5, dy=-10, color="red"
).encode(x=alt.X("Year:O"), text="label:N")

st.altair_chart(alt.layer(base_line, rule, rule_text), use_container_width=True)

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
st.markdown("\n---\n\nTip: adjust the clinic selection and year range in the sidebar to update the charts.")
