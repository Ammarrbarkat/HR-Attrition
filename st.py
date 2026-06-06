import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(
    page_title="HR Attrition Dashboard",
    page_icon="logo.png",
    layout="wide"
)

# Colors
UNI_COLORS  = ['pink', 'purple']
BIVA_COLORS = ['purple', 'blue']

# Load Data
@st.cache_data
def load_data():
    train = pd.read_csv('train.csv', encoding='utf-8-sig')
    test  = pd.read_csv('test.csv',  encoding='utf-8-sig')
    df = pd.concat([train, test], ignore_index=True)
    df.columns = (df.columns
                   .str.strip()
                   .str.lower()
                   .str.replace(' ', '_')
                   .str.replace('-', '_'))
    df['company_tenure'] = df['company_tenure'].clip(upper=60)
    return df

df = load_data()

# Sidebar
with st.sidebar:
    col1, col2, col3 = st.columns([0.5, 9, 0.5])
    with col2:
        st.image('logo.png', use_container_width=True)

    st.markdown("<h3 style='text-align: center;'>HR Attrition Dashboard</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("**NAVIGATION**")
    page = st.radio(
        "Navigation",
        ["🏠 Overview", "📊 Univariate", "📈 Bivariate", "🔥 Multivariate", "📄 Data"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**FILTERS**")
    job_roles = ['All'] + sorted(df['job_role'].unique().tolist())
    selected_role = st.selectbox("🏢 Job Role", job_roles)

    attrition_options = ['All', 'Stayed', 'Left']
    selected_attrition = st.selectbox("👥 Attrition", attrition_options)

# Apply Filters
filtered = df.copy()
if selected_role != 'All':
    filtered = filtered[filtered['job_role'] == selected_role]
if selected_attrition != 'All':
    filtered = filtered[filtered['attrition'] == selected_attrition]

# KPIs
st.title("🏢 HR Attrition Dashboard")
st.markdown("---")

total      = len(filtered)
left_count = len(filtered[filtered['attrition'] == 'Left'])
stayed     = len(filtered[filtered['attrition'] == 'Stayed'])
left_rate  = round((left_count / total * 100), 1) if total > 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("👥 Total Employees", f"{total:,}")
with col2:
    st.metric("🚪 Employees Left", f"{left_count:,}", f"{left_rate}%")
with col3:
    st.metric("✅ Employees Stayed", f"{stayed:,}")

st.markdown("---")

# ══════════════════════════════════════════════
# Page: Overview
# ══════════════════════════════════════════════
if page == "🏠 Overview":
    st.subheader("🏠 Overview")

    att_data = filtered['attrition'].value_counts().reset_index()
    att_data.columns = ['attrition', 'count']
    fig = px.pie(
        att_data,
        names='attrition', values='count',
        title='Employee Attrition Distribution',
        color_discrete_sequence=UNI_COLORS
    )
    st.plotly_chart(fig, use_container_width=True)

    if left_rate > 50:
        st.error(f"🚨 **Insight:** {left_rate}% of employees left the company — a high rate that requires immediate HR intervention!")
    elif left_rate > 40:
        st.warning(f"⚠️ **Insight:** {left_rate}% of employees left — a concerning rate. HR should investigate the root causes of attrition.")
    else:
        st.info(f"💡 **Insight:** {left_rate}% of employees left — a reasonable rate, but continuous monitoring is recommended.")

# ══════════════════════════════════════════════
# Page: Univariate
# ══════════════════════════════════════════════
elif page == "📊 Univariate":
    st.subheader("📊 Univariate Analysis")

    # Chart 1 — Attrition Distribution
    att_data = filtered['attrition'].value_counts().reset_index()
    att_data.columns = ['attrition', 'count']
    fig1 = px.pie(
        att_data,
        names='attrition', values='count',
        title='Employee Attrition Distribution',
        color_discrete_sequence=UNI_COLORS
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.info(f"💡 **Insight:** {left_rate}% of {total:,} employees left the company, while {100 - left_rate}% stayed.")

    # Chart 2 — Age Distribution
    age_data = filtered[['age', 'attrition']].copy()
    fig2 = px.histogram(
        age_data,
        x='age', color='attrition',
        title='Age Distribution by Attrition',
        barmode='overlay', opacity=0.7,
        color_discrete_sequence=UNI_COLORS
    )
    st.plotly_chart(fig2, use_container_width=True)

    avg_age_left   = round(filtered[filtered['attrition'] == 'Left']['age'].mean(), 1)
    avg_age_stayed = round(filtered[filtered['attrition'] == 'Stayed']['age'].mean(), 1)
    if abs(avg_age_left - avg_age_stayed) < 2:
        st.info(f"💡 **Insight:** Average age of employees who left ({avg_age_left}) is very close to those who stayed ({avg_age_stayed}) — age is not a significant driver of attrition.")
    elif avg_age_left < avg_age_stayed:
        st.error(f"🚨 **Insight:** Younger employees (avg age {avg_age_left}) are leaving more than older ones (avg age {avg_age_stayed}).")
    else:
        st.error(f"🚨 **Insight:** Older employees (avg age {avg_age_left}) are leaving more than younger ones (avg age {avg_age_stayed}).")

    # Chart 3 — Monthly Income Distribution
    income_data = filtered[['monthly_income', 'attrition']].copy()
    fig3 = px.histogram(
        income_data,
        x='monthly_income', color='attrition',
        title='Monthly Income Distribution by Attrition',
        barmode='overlay', opacity=0.7,
        color_discrete_sequence=['purple', 'blue']
    )
    st.plotly_chart(fig3, use_container_width=True)

    avg_inc_left   = round(filtered[filtered['attrition'] == 'Left']['monthly_income'].mean(), 0)
    avg_inc_stayed = round(filtered[filtered['attrition'] == 'Stayed']['monthly_income'].mean(), 0)
    diff = round(avg_inc_stayed - avg_inc_left, 0)
    if abs(diff) < 200:
        st.info(f"💡 **Insight:** The income difference between employees who left (${avg_inc_left:,.0f}) and stayed (${avg_inc_stayed:,.0f}) is minimal — salary alone is not the main driver of attrition.")
    else:
        st.error(f"🚨 **Insight:** Employees who left earned on average ${avg_inc_left:,.0f} vs ${avg_inc_stayed:,.0f} for those who stayed — a gap of ${diff:,.0f}.")

# ══════════════════════════════════════════════
# Page: Bivariate
# ══════════════════════════════════════════════
elif page == "📈 Bivariate":
    st.subheader("📈 Bivariate Analysis")

    # Chart 1 — Attrition by Job Role
    role_data = (filtered.groupby(['job_role', 'attrition'])
                         .size().reset_index(name='count'))
    fig1 = px.bar(
        role_data,
        x='job_role', y='count', color='attrition',
        title='Attrition by Job Role',
        barmode='group',
        color_discrete_sequence=BIVA_COLORS
    )
    st.plotly_chart(fig1, use_container_width=True)

    if len(filtered['job_role'].unique()) > 1:
        top_role = (filtered.groupby('job_role')
                    .apply(lambda x: (x['attrition'] == 'Left').mean())
                    .idxmax())
        top_role_rate = round((filtered.groupby('job_role')
                               .apply(lambda x: (x['attrition'] == 'Left').mean())
                               .max() * 100), 1)
        st.error(f"🚨 **Insight:** The **{top_role}** sector has the highest attrition rate at {top_role_rate}% — it requires special attention from HR.")
    else:
        st.info(f"💡 **Insight:** Showing data for {filtered['job_role'].iloc[0]} sector only.")

    # Chart 2 — Work-Life Balance
    wlb_data = (filtered.groupby(['work_life_balance', 'attrition'])
                        .size().reset_index(name='count'))
    fig2 = px.bar(
        wlb_data,
        x='work_life_balance', y='count', color='attrition',
        title='Distribution Work-Life Balance and Attrition',
        barmode='group',
        color_discrete_sequence=BIVA_COLORS,
        category_orders={'work_life_balance': ['Poor', 'Fair', 'Good', 'Excellent']}
    )
    st.plotly_chart(fig2, use_container_width=True)

    poor_left  = len(filtered[(filtered['work_life_balance'] == 'Poor') & (filtered['attrition'] == 'Left')])
    poor_total = len(filtered[filtered['work_life_balance'] == 'Poor'])
    if poor_total > 0:
        poor_rate = round(poor_left / poor_total * 100, 1)
        st.error(f"🚨 **Insight:** {poor_rate}% of employees with Poor Work-Life Balance left the company — this is one of the strongest attrition drivers.")

    # Chart 3 — Monthly Income Box Plot
    income_attr = filtered[['monthly_income', 'attrition']].copy()
    fig3 = px.box(
        income_attr,
        x='attrition', y='monthly_income', color='attrition',
        title='Distribution Monthly Income and Attrition',
        color_discrete_sequence=BIVA_COLORS
    )
    st.plotly_chart(fig3, use_container_width=True)

    med_left   = round(filtered[filtered['attrition'] == 'Left']['monthly_income'].median(), 0)
    med_stayed = round(filtered[filtered['attrition'] == 'Stayed']['monthly_income'].median(), 0)
    diff_med   = round(abs(med_stayed - med_left), 0)
    if diff_med < 300:
        st.info(f"💡 **Insight:** The median salary is very similar — Left (${med_left:,.0f}) vs Stayed (${med_stayed:,.0f}). Salary is not the primary reason employees leave.")
    else:
        st.error(f"🚨 **Insight:** Clear salary gap — Left (${med_left:,.0f}) vs Stayed (${med_stayed:,.0f}). Compensation may be a contributing factor.")

    # Chart 4 — Job Satisfaction
    js_data = (filtered.groupby(['job_satisfaction', 'attrition'])
                       .size().reset_index(name='count'))
    fig4 = px.bar(
        js_data,
        x='job_satisfaction', y='count', color='attrition',
        title='Job Satisfaction vs Attrition',
        barmode='group',
        color_discrete_sequence=BIVA_COLORS,
        category_orders={'job_satisfaction': ['Low', 'Medium', 'High', 'Very High']}
    )
    st.plotly_chart(fig4, use_container_width=True)

    high_left  = len(filtered[(filtered['job_satisfaction'].isin(['High', 'Very High'])) & (filtered['attrition'] == 'Left')])
    high_total = len(filtered[filtered['job_satisfaction'].isin(['High', 'Very High'])])
    if high_total > 0:
        high_rate = round(high_left / high_total * 100, 1)
        st.warning(f"⚠️ **Insight:** {high_rate}% of employees with High/Very High satisfaction still left — likely because they are confident enough to find better opportunities elsewhere.")

# ══════════════════════════════════════════════
# Page: Multivariate
# ══════════════════════════════════════════════
elif page == "🔥 Multivariate":
    st.subheader("🔥 Multivariate Analysis")

    # Chart 1 — Correlation Heatmap
    numeric_cols = ['age', 'monthly_income', 'years_at_company',
                    'distance_from_home', 'number_of_promotions',
                    'company_tenure', 'number_of_dependents']
    corr = filtered[numeric_cols].corr().round(2)
    fig1 = px.imshow(
        corr,
        title='Correlation Heatmap',
        color_continuous_scale='RdBu_r',
        text_auto=True
    )
    st.plotly_chart(fig1, use_container_width=True)

    age_years_corr = round(corr.loc['age', 'years_at_company'], 2)
    st.info(f"💡 **Insight:** The strongest correlation is between Age and Years at Company = {age_years_corr} — logical. Monthly income shows near-zero correlation with all other variables.")

    # Chart 2 — Box Plot
    age_labels = ['18-25','26-30','31-35','36-40','41-45','46-50','51-55','56-60']

    filtered['age_group'] = pd.cut(
        filtered['age'],
        bins=[18, 25, 30, 35, 40, 45, 50, 55, 60],
        labels=age_labels,
        include_lowest=True
    )

    fig2 = px.box(
        filtered,
        x='age_group',
        y='monthly_income',
        color='attrition',
        title='Monthly Income by Age Group & Attrition',
        color_discrete_sequence=BIVA_COLORS,
        category_orders={'age_group': age_labels}
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.info("💡 **Insight:** The box plot shows the distribution of monthly income across different age groups. In general, monthly income increases with age. Analyzing the differences within each age group helps identify if lower income relative to peers is a driver for attrition.")

# ══════════════════════════════════════════════
# Page: Data
# ══════════════════════════════════════════════
elif page == "📄 Data":
    st.subheader("📄 Raw Data")
    st.dataframe(filtered, use_container_width=True)
    st.caption(f"Showing {len(filtered):,} rows")
