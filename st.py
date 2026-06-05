import streamlit as st
import pandas as pd
import plotly.express as px

# ── Page Config ──────────────────────────────
st.set_page_config(
    page_title="HR Attrition Dashboard",
    page_icon="logo.png",
    layout="wide"
)



# ── Colors — نفس الكود بتاعك بالظبط ──────────
UNI_COLORS  = ['pink', 'purple']   # Univariate
BIVA_COLORS = ['purple', 'blue']   # Bivariate & Multivariate

# ── Load Data ─────────────────────────────────
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

# ── Sidebar ───────────────────────────────────
with st.sidebar:
    col1, col2, col3 = st.columns([0.5, 9, 0.5])
    with col2:
        st.image('logo.png', use_container_width=True)
    
    st.markdown("<h3 style='text-align: center;'>HR Attrition Dashboard</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("**NAVIGATION**")
    page = st.radio(
        "Navigation",
        [
            "🏠 Overview",
            "📊 Univariate",
            "📈 Bivariate",
            "🔥 Multivariate",
            "📄 Data"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**FILTERS**")
    job_roles = ['All'] + sorted(df['job_role'].unique().tolist())
    selected_role = st.selectbox("🏢 Job Role", job_roles)

    attrition_options = ['All', 'Stayed', 'Left']
    selected_attrition = st.selectbox("👥 Attrition", attrition_options)






# ── Apply Filters ─────────────────────────────
filtered = df.copy()
if selected_role != 'All':
    filtered = filtered[filtered['job_role'] == selected_role]
if selected_attrition != 'All':
    filtered = filtered[filtered['attrition'] == selected_attrition]


# ── KPIs ──────────────────────────────────────
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
    st.info("💡 **Insight:** This chart shows the overall proportion of employees who stayed versus those who left. A high attrition rate may indicate underlying issues in workplace satisfaction.")

# ══════════════════════════════════════════════
# Page: Univariate
# ══════════════════════════════════════════════
elif page == "📊 Univariate":
    st.subheader("📊 Univariate Analysis")

    # Chart 1 — Attrition Distribution (pink, purple)
    att_data = filtered['attrition'].value_counts().reset_index()
    att_data.columns = ['attrition', 'count']
    fig1 = px.pie(
        att_data,
        names='attrition', values='count',
        title='Employee Attrition Distribution',
        color_discrete_sequence=UNI_COLORS
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.info("💡 **Insight:** This highlights the general turnover rate in the company.")

    # Chart 2 — Age Distribution (purple, pink)
    age_data = filtered[['age', 'attrition']].copy()
    fig2 = px.histogram(
        age_data,
        x='age', color='attrition',
        title='Age Distribution by Attrition',
        barmode='overlay', opacity=0.7,
        color_discrete_sequence=UNI_COLORS
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.error("🚨 **Insight:** Notice how attrition varies across different age groups. Typically, younger employees might have higher attrition rates as they explore career options.")

    # Chart 3 — Monthly Income Distribution (purple, blue)
    income_data = filtered[['monthly_income', 'attrition']].copy()
    fig3 = px.histogram(
        income_data,
        x='monthly_income', color='attrition',
        title='Monthly Income Distribution by Attrition',
        barmode='overlay', opacity=0.7,
        color_discrete_sequence=['purple', 'blue']
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.error("🚨 **Insight:** Employees with lower monthly incomes often show higher attrition rates. Compensation is a key driver for retention.")

# ══════════════════════════════════════════════
# Page: Bivariate
# ══════════════════════════════════════════════
elif page == "📈 Bivariate":
    st.subheader("📈 Bivariate Analysis")

    # Chart 1 — Attrition by Job Role (purple, blue)
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
    st.error("🚨 **Insight:** Certain job roles may experience higher turnover due to stress or market demand. Identifying these helps target retention strategies.")

    # Chart 2 — Work-Life Balance (purple, blue)
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
    st.error("🚨 **Insight:** Employees reporting 'Poor' work-life balance are generally more likely to leave the company.")

    # Chart 3 — Monthly Income Box Plot (purple, blue)
    income_attr = filtered[['monthly_income', 'attrition']].copy()
    fig3 = px.box(
        income_attr,
        x='attrition', y='monthly_income', color='attrition',
        title='Distribution Monthly Income and Attrition',
        color_discrete_sequence=BIVA_COLORS
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.error("🚨 **Insight:** The median income for employees who left is often lower than those who stayed, highlighting the impact of competitive pay.")

    # Chart 4 — Job Satisfaction (purple, blue)
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
    st.error("🚨 **Insight:** Lower job satisfaction directly correlates with higher attrition. Improving workplace morale is crucial for retaining talent.")

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
    st.info("💡 **Insight:** Darker squares indicate strong correlations between numerical variables, such as age and company tenure.")

    # Chart 2 — Age vs Income Scatter (purple, blue)
    fig2 = px.scatter(
        filtered.sample(min(3000, len(filtered))),
        x='age', y='monthly_income', color='attrition',
        title='Age vs Monthly Income by Attrition',
        opacity=0.6,
        color_discrete_sequence=BIVA_COLORS
    )
    st.plotly_chart(fig2, use_container_width=True)
    st.info("💡 **Insight:** Older employees tend to have higher incomes. This scatter plot helps identify if individuals leaving are underpaid relative to their age group.")

# ══════════════════════════════════════════════
# Page: Data
# ══════════════════════════════════════════════
elif page == "📄 Data":
    st.subheader("📄 Raw Data")
    st.dataframe(filtered, use_container_width=True)
    st.caption(f"Showing {len(filtered):,} rows")