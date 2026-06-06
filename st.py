import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

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
        [
            "🏠 Overview",
            "📊 Univariate",
            "📈 Bivariate",
            "🔥 Multivariate",
            "━━━━━━━━━━━━━━",
            "Q1 · The Headline",
            "Q2 · Overtime",
            "Q3 · Remote Work",
            "Q4 · Pay Fairness",
            "Q5 · Retention Timeline",
            "Q6 · Engagement Warning",
            "Q7 · Life Stage",
            "Q8 · Career Stagnation",
            "Q9 · Highest-Risk Profile",
            "Q10 · What Moves the Needle",
            "━━━━━━━━━━━━━━",
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
    fig = px.pie(att_data, names='attrition', values='count',
                 title='Employee Attrition Distribution',
                 color_discrete_sequence=UNI_COLORS)
    st.plotly_chart(fig, use_container_width=True)
    if left_rate > 50:
        st.error(f"🚨 **Insight:** {left_rate}% of employees left — requires immediate HR intervention!")
    elif left_rate > 40:
        st.warning(f"⚠️ **Insight:** {left_rate}% of employees left — a concerning rate. HR should investigate root causes.")
    else:
        st.info(f"💡 **Insight:** {left_rate}% of employees left — reasonable but needs monitoring.")

# ══════════════════════════════════════════════
# Page: Univariate
# ══════════════════════════════════════════════
elif page == "📊 Univariate":
    st.subheader("📊 Univariate Analysis")

    att_data = filtered['attrition'].value_counts().reset_index()
    att_data.columns = ['attrition', 'count']
    fig1 = px.pie(att_data, names='attrition', values='count',
                  title='Employee Attrition Distribution',
                  color_discrete_sequence=UNI_COLORS)
    st.plotly_chart(fig1, use_container_width=True)
    st.info(f"💡 **Insight:** {left_rate}% of {total:,} employees left, while {100 - left_rate}% stayed.")

    fig2 = px.histogram(filtered, x='age', color='attrition',
                        title='Age Distribution by Attrition',
                        barmode='overlay', opacity=0.7,
                        color_discrete_sequence=UNI_COLORS)
    st.plotly_chart(fig2, use_container_width=True)

    avg_age_left   = round(filtered[filtered['attrition'] == 'Left']['age'].mean(), 1)
    avg_age_stayed = round(filtered[filtered['attrition'] == 'Stayed']['age'].mean(), 1)
    if abs(avg_age_left - avg_age_stayed) < 2:
        st.info(f"💡 **Insight:** Average age who left ({avg_age_left}) is close to stayed ({avg_age_stayed}) — age is not a significant driver.")
    else:
        st.error(f"🚨 **Insight:** Age difference detected — Left avg: {avg_age_left} vs Stayed avg: {avg_age_stayed}.")

    fig3 = px.histogram(filtered, x='monthly_income', color='attrition',
                        title='Monthly Income Distribution by Attrition',
                        barmode='overlay', opacity=0.7,
                        color_discrete_sequence=['purple', 'blue'])
    st.plotly_chart(fig3, use_container_width=True)

    avg_inc_left   = round(filtered[filtered['attrition'] == 'Left']['monthly_income'].mean(), 0)
    avg_inc_stayed = round(filtered[filtered['attrition'] == 'Stayed']['monthly_income'].mean(), 0)
    diff = round(avg_inc_stayed - avg_inc_left, 0)
    if abs(diff) < 200:
        st.info(f"💡 **Insight:** Income difference is minimal — Left (${avg_inc_left:,.0f}) vs Stayed (${avg_inc_stayed:,.0f}). Salary alone is not the main driver.")
    else:
        st.error(f"🚨 **Insight:** Income gap of ${diff:,.0f} — Left (${avg_inc_left:,.0f}) vs Stayed (${avg_inc_stayed:,.0f}).")

# ══════════════════════════════════════════════
# Page: Bivariate
# ══════════════════════════════════════════════
elif page == "📈 Bivariate":
    st.subheader("📈 Bivariate Analysis")

    role_data = filtered.groupby(['job_role', 'attrition']).size().reset_index(name='count')
    fig1 = px.bar(role_data, x='job_role', y='count', color='attrition',
                  title='Attrition by Job Role', barmode='group',
                  color_discrete_sequence=BIVA_COLORS)
    st.plotly_chart(fig1, use_container_width=True)

    if len(filtered['job_role'].unique()) > 1:
        top_role = (filtered.groupby('job_role')
                    .apply(lambda x: (x['attrition'] == 'Left').mean()).idxmax())
        top_rate = round(filtered.groupby('job_role')
                         .apply(lambda x: (x['attrition'] == 'Left').mean()).max() * 100, 1)
        st.error(f"🚨 **Insight:** **{top_role}** has the highest attrition at {top_rate}%.")

    wlb_data = filtered.groupby(['work_life_balance', 'attrition']).size().reset_index(name='count')
    fig2 = px.bar(wlb_data, x='work_life_balance', y='count', color='attrition',
                  title='Work-Life Balance vs Attrition', barmode='group',
                  color_discrete_sequence=BIVA_COLORS,
                  category_orders={'work_life_balance': ['Poor', 'Fair', 'Good', 'Excellent']})
    st.plotly_chart(fig2, use_container_width=True)

    poor_left  = len(filtered[(filtered['work_life_balance'] == 'Poor') & (filtered['attrition'] == 'Left')])
    poor_total = len(filtered[filtered['work_life_balance'] == 'Poor'])
    if poor_total > 0:
        st.error(f"🚨 **Insight:** {round(poor_left/poor_total*100,1)}% of Poor Work-Life Balance employees left.")

    fig3 = px.box(filtered, x='attrition', y='monthly_income', color='attrition',
                  title='Monthly Income vs Attrition', color_discrete_sequence=BIVA_COLORS)
    st.plotly_chart(fig3, use_container_width=True)

    js_data = filtered.groupby(['job_satisfaction', 'attrition']).size().reset_index(name='count')
    fig4 = px.bar(js_data, x='job_satisfaction', y='count', color='attrition',
                  title='Job Satisfaction vs Attrition', barmode='group',
                  color_discrete_sequence=BIVA_COLORS,
                  category_orders={'job_satisfaction': ['Low', 'Medium', 'High', 'Very High']})
    st.plotly_chart(fig4, use_container_width=True)

# ══════════════════════════════════════════════
# Page: Multivariate
# ══════════════════════════════════════════════
elif page == "🔥 Multivariate":
    st.subheader("🔥 Multivariate Analysis")

    numeric_cols = ['age', 'monthly_income', 'years_at_company',
                    'distance_from_home', 'number_of_promotions',
                    'company_tenure', 'number_of_dependents']
    corr = filtered[numeric_cols].corr().round(2)
    fig1 = px.imshow(corr, title='Correlation Heatmap',
                     color_continuous_scale='RdBu_r', text_auto=True)
    st.plotly_chart(fig1, use_container_width=True)
    st.info(f"💡 **Insight:** Strongest correlation: Age vs Years at Company = {round(corr.loc['age','years_at_company'],2)}")

    fig2 = px.scatter(filtered.sample(min(3000, len(filtered))),
                      x='age', y='monthly_income', color='attrition',
                      title='Age vs Monthly Income by Attrition', opacity=0.6,
                      color_discrete_sequence=BIVA_COLORS)
    st.plotly_chart(fig2, use_container_width=True)

# ══════════════════════════════════════════════
# Q1 · The Headline
# ══════════════════════════════════════════════
elif page == "Q1 · The Headline":
    st.subheader("Q1 · The Headline")
    st.markdown("*What share of employees left overall, and which job role is losing the most people?*")

    # Overall attrition rate
    overall_left = round((df['attrition'] == 'Left').mean() * 100, 1)
    st.metric("Overall Attrition Rate", f"{overall_left}%")

    # Attrition by job role
    role_rate = (df.groupby('job_role')
                 .apply(lambda x: (x['attrition'] == 'Left').mean() * 100)
                 .round(1).reset_index())
    role_rate.columns = ['job_role', 'attrition_rate']
    role_rate = role_rate.sort_values('attrition_rate', ascending=False)

    fig = px.bar(role_rate, x='job_role', y='attrition_rate',
                 title='Attrition Rate % by Job Role',
                 color='attrition_rate', color_continuous_scale='Reds',
                 text='attrition_rate')
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    top = role_rate.iloc[0]
    st.error(f"🚨 **{top['job_role']}** has the highest attrition rate at **{top['attrition_rate']}%** — HR should prioritize retention efforts in this sector first.")

# ══════════════════════════════════════════════
# Q2 · Overtime
# ══════════════════════════════════════════════
elif page == "Q2 · Overtime":
    st.subheader("Q2 · Overtime")
    st.markdown("*Are employees who work overtime more likely to leave, and by how much?*")

    ot = df.groupby('overtime').apply(lambda x: (x['attrition'] == 'Left').mean() * 100).round(1).reset_index()
    ot.columns = ['overtime', 'attrition_rate']

    fig = px.bar(ot, x='overtime', y='attrition_rate',
                 title='Attrition Rate by Overtime',
                 color='overtime', color_discrete_sequence=BIVA_COLORS,
                 text='attrition_rate')
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    yes_rate = ot[ot['overtime'] == 'Yes']['attrition_rate'].values[0]
    no_rate  = ot[ot['overtime'] == 'No']['attrition_rate'].values[0]
    diff_ot  = round(yes_rate - no_rate, 1)
    st.error(f"🚨 **Insight:** Employees working overtime leave at **{yes_rate}%** vs **{no_rate}%** for those who don't — a difference of **{diff_ot}%**. HR should review workload policies and consider overtime limits.")

# ══════════════════════════════════════════════
# Q3 · Remote Work
# ══════════════════════════════════════════════
elif page == "Q3 · Remote Work":
    st.subheader("Q3 · Remote Work")
    st.markdown("*Does offering remote work appear to keep people?*")

    remote = df.groupby('remote_work').apply(lambda x: (x['attrition'] == 'Left').mean() * 100).round(1).reset_index()
    remote.columns = ['remote_work', 'attrition_rate']

    fig = px.bar(remote, x='remote_work', y='attrition_rate',
                 title='Attrition Rate by Remote Work',
                 color='remote_work', color_discrete_sequence=BIVA_COLORS,
                 text='attrition_rate')
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    remote_pct = round((df['remote_work'] == 'Yes').mean() * 100, 1)
    yes_r = remote[remote['remote_work'] == 'Yes']['attrition_rate'].values[0]
    no_r  = remote[remote['remote_work'] == 'No']['attrition_rate'].values[0]

    if yes_r < no_r:
        st.info(f"💡 **Insight:** Remote workers leave at **{yes_r}%** vs **{no_r}%** for non-remote — remote work appears to help retention. However, only **{remote_pct}%** of staff work remotely, so this finding applies to a small group and should be interpreted cautiously.")
    else:
        st.warning(f"⚠️ **Insight:** Remote workers leave at **{yes_r}%** vs **{no_r}%** — remote work alone doesn't seem to reduce attrition. Only **{remote_pct}%** work remotely, limiting what we can conclude.")

# ══════════════════════════════════════════════
# Q4 · Pay Fairness
# ══════════════════════════════════════════════
elif page == "Q4 · Pay Fairness":
    st.subheader("Q4 · Pay Fairness")
    st.markdown("*Within the same job level, do lower-paid employees leave more often?*")

    df['income_quartile'] = df.groupby('job_level')['monthly_income'].transform(
        lambda x: pd.qcut(x, q=4, labels=['Q1 Low', 'Q2', 'Q3', 'Q4 High'], duplicates='drop')
    )

    pay_data = df.groupby(['job_level', 'income_quartile']).apply(
        lambda x: (x['attrition'] == 'Left').mean() * 100
    ).round(1).reset_index()
    pay_data.columns = ['job_level', 'income_quartile', 'attrition_rate']

    fig = px.bar(pay_data, x='income_quartile', y='attrition_rate',
                 color='job_level', barmode='group',
                 title='Attrition Rate by Income Quartile within Job Level',
                 color_discrete_sequence=['purple', 'blue', 'pink'])
    st.plotly_chart(fig, use_container_width=True)

    st.warning("⚠️ **Insight:** Lower-paid employees (Q1) consistently show higher attrition rates within each job level. **Recommendation:** Establish clear pay bands ensuring the bottom quartile is brought closer to market median — this is where pay increases would have the highest retention impact.")

# ══════════════════════════════════════════════
# Q5 · Retention Timeline
# ══════════════════════════════════════════════
elif page == "Q5 · Retention Timeline":
    st.subheader("Q5 · Retention Timeline")
    st.markdown("*At what stage of an employee's time at the company is attrition highest?*")

    df['tenure_band'] = pd.cut(df['years_at_company'],
                                bins=[0, 2, 5, 10, 20, 60],
                                labels=['0-2 yrs', '3-5 yrs', '6-10 yrs', '11-20 yrs', '20+ yrs'])

    timeline = df.groupby('tenure_band').apply(
        lambda x: (x['attrition'] == 'Left').mean() * 100
    ).round(1).reset_index()
    timeline.columns = ['tenure_band', 'attrition_rate']

    fig = px.line(timeline, x='tenure_band', y='attrition_rate',
                  title='Attrition Rate by Years at Company',
                  markers=True, color_discrete_sequence=['purple'])
    fig.update_traces(line_width=3, marker_size=10)
    st.plotly_chart(fig, use_container_width=True)

    peak = timeline.loc[timeline['attrition_rate'].idxmax(), 'tenure_band']
    peak_rate = timeline['attrition_rate'].max()
    st.error(f"🚨 **Insight:** Attrition peaks at **{peak}** with a rate of **{peak_rate}%**. Retention efforts should be focused on **onboarding and early career support** — this is where the company loses the most people.")

# ══════════════════════════════════════════════
# Q6 · Engagement Warning Signs
# ══════════════════════════════════════════════
elif page == "Q6 · Engagement Warning":
    st.subheader("Q6 · Engagement Warning Signs")
    st.markdown("*Which combination of Job Satisfaction + Work-Life Balance is the strongest early-warning sign?*")

    combo = df.groupby(['job_satisfaction', 'work_life_balance']).apply(
        lambda x: (x['attrition'] == 'Left').mean() * 100
    ).round(1).reset_index()
    combo.columns = ['job_satisfaction', 'work_life_balance', 'attrition_rate']

    pivot = combo.pivot(index='job_satisfaction', columns='work_life_balance', values='attrition_rate')

    fig = px.imshow(pivot, title='Attrition Rate % by Job Satisfaction & Work-Life Balance',
                    color_continuous_scale='Reds', text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    worst = combo.loc[combo['attrition_rate'].idxmax()]
    st.error(f"🚨 **Insight:** The highest-risk combination is **Job Satisfaction = {worst['job_satisfaction']}** + **Work-Life Balance = {worst['work_life_balance']}** with **{worst['attrition_rate']}%** attrition rate. Managers should watch for employees showing both signals simultaneously.")

# ══════════════════════════════════════════════
# Q7 · Life Stage
# ══════════════════════════════════════════════
elif page == "Q7 · Life Stage":
    st.subheader("Q7 · Life Stage")
    st.markdown("*Do age, marital status, and number of dependents change who leaves?*")

    df['age_group'] = pd.cut(df['age'], bins=[18, 30, 40, 50, 60],
                              labels=['18-30', '31-40', '41-50', '51-60'])

    life = df.groupby(['age_group', 'marital_status']).apply(
        lambda x: (x['attrition'] == 'Left').mean() * 100
    ).round(1).reset_index()
    life.columns = ['age_group', 'marital_status', 'attrition_rate']

    fig1 = px.bar(life, x='age_group', y='attrition_rate', color='marital_status',
                  title='Attrition Rate by Age Group & Marital Status',
                  barmode='group', color_discrete_sequence=['purple', 'blue', 'pink'])
    st.plotly_chart(fig1, use_container_width=True)

    dep = df.groupby('number_of_dependents').apply(
        lambda x: (x['attrition'] == 'Left').mean() * 100
    ).round(1).reset_index()
    dep.columns = ['number_of_dependents', 'attrition_rate']

    fig2 = px.bar(dep, x='number_of_dependents', y='attrition_rate',
                  title='Attrition Rate by Number of Dependents',
                  color_discrete_sequence=['purple'], text='attrition_rate')
    fig2.update_traces(texttemplate='%{text}%', textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)

    worst_life = life.loc[life['attrition_rate'].idxmax()]
    st.error(f"🚨 **Insight:** Highest risk group: Age **{worst_life['age_group']}** + **{worst_life['marital_status']}** at **{worst_life['attrition_rate']}%**. Targeted retention benefits (flexible hours, childcare support) could help retain this segment.")

# ══════════════════════════════════════════════
# Q8 · Career Stagnation
# ══════════════════════════════════════════════
elif page == "Q8 · Career Stagnation":
    st.subheader("Q8 · Career Stagnation")
    st.markdown("*Does lack of growth drive attrition? Promotions, job level, leadership & innovation opportunities.*")

    # Promotions vs Attrition
    promo = df.groupby('number_of_promotions').apply(
        lambda x: (x['attrition'] == 'Left').mean() * 100
    ).round(1).reset_index()
    promo.columns = ['number_of_promotions', 'attrition_rate']

    fig1 = px.bar(promo, x='number_of_promotions', y='attrition_rate',
                  title='Attrition Rate by Number of Promotions',
                  color_discrete_sequence=['purple'], text='attrition_rate')
    fig1.update_traces(texttemplate='%{text}%', textposition='outside')
    st.plotly_chart(fig1, use_container_width=True)

    # Leadership & Innovation
    opp = df.groupby(['leadership_opportunities', 'innovation_opportunities']).apply(
        lambda x: (x['attrition'] == 'Left').mean() * 100
    ).round(1).reset_index()
    opp.columns = ['leadership', 'innovation', 'attrition_rate']

    fig2 = px.bar(opp, x='leadership', y='attrition_rate', color='innovation',
                  title='Attrition by Leadership & Innovation Opportunities',
                  barmode='group', color_discrete_sequence=BIVA_COLORS)
    st.plotly_chart(fig2, use_container_width=True)

    no_promo_rate = round((df[df['number_of_promotions'] == 0]['attrition'] == 'Left').mean() * 100, 1)
    st.error(f"🚨 **Insight:** Employees with **0 promotions** have a **{no_promo_rate}%** attrition rate. Employees without leadership or innovation opportunities also leave at higher rates. **Recommendation:** Implement clear career progression paths and promote from within.")

# ══════════════════════════════════════════════
# Q9 · Highest-Risk Profile
# ══════════════════════════════════════════════
elif page == "Q9 · Highest-Risk Profile":
    st.subheader("Q9 · Highest-Risk Profile")
    st.markdown("*Combine 3-4 factors to construct the single highest-risk employee profile.*")

    # Build risk profile
    mask = (
        (df['work_life_balance'].isin(['Poor', 'Fair'])) &
        (df['overtime'] == 'Yes') &
        (df['number_of_promotions'] == 0) &
        (df['job_satisfaction'].isin(['Low', 'Medium']))
    )

    risk_group = df[mask]
    baseline   = round((df['attrition'] == 'Left').mean() * 100, 1)
    risk_rate  = round((risk_group['attrition'] == 'Left').mean() * 100, 1) if len(risk_group) > 0 else 0
    count      = len(risk_group)
    diff_risk  = round(risk_rate - baseline, 1)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Company Baseline Attrition", f"{baseline}%")
    with col2:
        st.metric("High-Risk Profile Attrition", f"{risk_rate}%", f"+{diff_risk}%")
    with col3:
        st.metric("Employees Matching Profile", f"{count:,}")

    st.markdown("### 🎯 Highest-Risk Profile Definition")
    st.markdown("""
    An employee is considered **highest-risk** if they match ALL of:
    - ❌ **Work-Life Balance:** Poor or Fair
    - ❌ **Overtime:** Yes
    - ❌ **Promotions:** 0 (never promoted)
    - ❌ **Job Satisfaction:** Low or Medium
    """)

    # Visualize
    labels = ['Company Average', 'High-Risk Profile']
    values = [baseline, risk_rate]
    fig = px.bar(x=labels, y=values, title='Attrition Rate: Company Average vs High-Risk Profile',
                 color=labels, color_discrete_sequence=['blue', 'red'], text=values)
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

    st.error(f"🚨 **Insight:** The high-risk profile has **{risk_rate}%** attrition vs company average of **{baseline}%** — that's **{diff_risk}% higher**. There are **{count:,} employees** matching this profile. Leadership should prioritize interventions for this group immediately.")

# ══════════════════════════════════════════════
# Q10 · What Moves the Needle
# ══════════════════════════════════════════════
elif page == "Q10 · What Moves the Needle":
    st.subheader("Q10 · What Moves the Needle")
    st.markdown("*If HR could fix only one thing next quarter, what does the data say it should be?*")

    baseline = round((df['attrition'] == 'Left').mean() * 100, 1)

    drivers = {
        'Poor Work-Life Balance': round((df[df['work_life_balance'].isin(['Poor','Fair'])]['attrition'] == 'Left').mean() * 100, 1),
        'Overtime = Yes':         round((df[df['overtime'] == 'Yes']['attrition'] == 'Left').mean() * 100, 1),
        '0 Promotions':           round((df[df['number_of_promotions'] == 0]['attrition'] == 'Left').mean() * 100, 1),
        'Low Job Satisfaction':   round((df[df['job_satisfaction'].isin(['Low','Medium'])]['attrition'] == 'Left').mean() * 100, 1),
        'No Remote Work':         round((df[df['remote_work'] == 'No']['attrition'] == 'Left').mean() * 100, 1),
    }

    driver_df = pd.DataFrame(list(drivers.items()), columns=['Driver', 'Attrition Rate'])
    driver_df['Above Baseline'] = (driver_df['Attrition Rate'] - baseline).round(1)
    driver_df = driver_df.sort_values('Above Baseline', ascending=False)

    fig = px.bar(driver_df, x='Driver', y='Above Baseline',
                 title='How Much Each Driver Shifts Attrition Above Baseline',
                 color='Above Baseline', color_continuous_scale='Reds',
                 text='Above Baseline')
    fig.update_traces(texttemplate='+%{text}%', textposition='outside')
    fig.add_hline(y=0, line_dash='dash', line_color='gray')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🏆 Top 3 Drivers Ranked")
    for i, row in driver_df.head(3).iterrows():
        st.markdown(f"**#{driver_df.index.get_loc(i)+1} {row['Driver']}** → Attrition rate: {row['Attrition Rate']}% (+{row['Above Baseline']}% above baseline)")

    top_driver = driver_df.iloc[0]
    st.error(f"""
    🎯 **#1 Recommendation: Fix {top_driver['Driver']}**

    This single factor drives attrition **{top_driver['Above Baseline']}% above** the company baseline.

    **Concrete action:** Address work-life balance issues through overtime policies, flexible scheduling, and workload reviews.

    **Estimated impact:** If attrition in this group drops by even 20%, the company could retain an estimated **{round(len(df[df['work_life_balance'].isin(['Poor','Fair'])]) * 0.2):,} employees** next quarter.
    """)

# ══════════════════════════════════════════════
# Dividers — skip
# ══════════════════════════════════════════════
elif page == "━━━━━━━━━━━━━━":
    st.info("👆 Please select a page from the navigation menu.")

# ══════════════════════════════════════════════
# Page: Data
# ══════════════════════════════════════════════
elif page == "📄 Data":
    st.subheader("📄 Raw Data")
    st.dataframe(filtered, use_container_width=True)
    st.caption(f"Showing {len(filtered):,} rows")
