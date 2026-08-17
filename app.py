import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from analyzer import (
    clean_data,
    detect_schema,
    get_data_quality,
    get_column_profile,
    get_missing_values,
    get_numeric_summary,
    get_duplicate_records,
    calculate_kpis,
    category_analysis,
    geographic_analysis,
    product_analysis,
    sales_growth_analysis,
    profitability_analysis,
    performance_ranking,
    sales_profit_analysis,
    generate_business_recommendations,
    generate_insights,
    customer_analysis,
    advanced_product_analysis,
    detect_anomalies,
    monthly_sales_anomalies,
    pareto_analysis
)




st.set_page_config(
    page_title="InsightFlow",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)




st.markdown("""
<style>

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
}

.subtitle {
    color: #a0a8b5;
    font-size: 17px;
    margin-bottom: 25px;
}

.section-title {
    font-size: 30px;
    font-weight: 650;
    margin-top: 25px;
    margin-bottom: 20px;
}

.dashboard-card {
    background: #151922;
    border: 1px solid #2b303b;
    border-radius: 14px;
    padding: 20px;
    min-height: 125px;
    margin-bottom: 15px;
}

.card-title {
    font-size: 15px;
    color: #aeb6c3;
    margin-bottom: 10px;
}

.card-value {
    font-size: 28px;
    font-weight: 650;
    color: #ffffff;
}

.card-description {
    font-size: 13px;
    color: #8993a2;
    margin-top: 7px;
}

.insight-card {
    background: #182f25;
    border-left: 4px solid #27d17f;
    padding: 17px 20px;
    border-radius: 10px;
    margin-bottom: 12px;
}

.recommendation-card {
    background: #182c43;
    border-left: 4px solid #4da3ff;
    padding: 16px 20px;
    border-radius: 9px;
    margin-bottom: 12px;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 550;
    min-height: 48px;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)



states = [
    "visual_analysis",
    "business_analysis",
    "profile_analysis",
    "advanced_analysis"
]

for state in states:
    if state not in st.session_state:
        st.session_state[state] = None




def money(value):
    return f"₹{float(value):,.2f}"


def percent(value):
    return f"{float(value):.2f}%"


def card(title, value, description=""):
    st.markdown(
        f"""
        <div class="dashboard-card">
            <div class="card-title">{title}</div>
            <div class="card-value">{value}</div>
            <div class="card-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section(title):
    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True
    )


def analysis_buttons(items, state_key, columns=3):

    for start in range(0, len(items), columns):

        row = items[start:start + columns]
        cols = st.columns(columns)

        for col, (label, value) in zip(cols, row):

            with col:

                if st.button(
                    label,
                    use_container_width=True,
                    key=f"{state_key}_{value}"
                ):
                    st.session_state[state_key] = value


def dark_chart(fig):

    fig.update_layout(
        template="plotly_dark"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


def show_insights(df):

    insights = generate_insights(df)

    if not insights:

        st.info(
            "No automated insights could be generated."
        )

        return

    for insight in insights:

        st.markdown(
            f"""
            <div class="insight-card">
                📊 {insight}
            </div>
            """,
            unsafe_allow_html=True
        )


def show_recommendations(df):

    recommendations = (
        generate_business_recommendations(df)
    )

    for recommendation in recommendations:

        st.markdown(
            f"""
            <div class="recommendation-card">
                💡 {recommendation}
            </div>
            """,
            unsafe_allow_html=True
        )




st.markdown(
    '<div class="main-title">📊 InsightFlow</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Intelligent Business Analytics Platform'
    '</div>',
    unsafe_allow_html=True
)



uploaded_file = st.file_uploader(
    "Choose your business dataset",
    type=["csv", "xlsx", "xls"]
)

if uploaded_file is None:

    st.info(
        "📁 Upload a CSV or Excel dataset to begin."
    )

    st.stop()


try:

    if uploaded_file.name.lower().endswith(".csv"):

        raw_df = pd.read_csv(
            uploaded_file
        )

    else:

        raw_df = pd.read_excel(
            uploaded_file
        )

except Exception as error:

    st.error(
        f"Unable to read the dataset: {error}"
    )

    st.stop()




try:

    schema = detect_schema(
        raw_df
    )

    df = clean_data(
        raw_df
    )

except Exception as error:

    st.error(
        f"Unable to analyze the dataset: {error}"
    )

    st.stop()



st.success(
    f"Dataset loaded successfully — "
    f"{len(df):,} records and {len(df.columns):,} columns."
)



with st.expander("🔎 Filters"):

    filtered_df = df.copy()

    filter_roles = [
        ("Year", "Year"),
        ("Geography", "geography"),
        ("Category", "Category"),
        ("Customer", "customer")
    ]

    available_filters = []

    for label, role in filter_roles:

        if role in schema and schema[role]:

            available_filters.append(
                (label, schema[role])
            )

    if available_filters:

        cols = st.columns(
            len(available_filters)
        )

        for col, (label, column) in zip(
            cols,
            available_filters
        ):

            with col:

                values = sorted(
                    df[column]
                    .dropna()
                    .unique()
                    .tolist(),
                    key=str
                )

                selected = st.multiselect(
                    label,
                    values,
                    key=f"filter_{column}"
                )

                if selected:

                    filtered_df = filtered_df[
                        filtered_df[column].isin(
                            selected
                        )
                    ]


st.info(
    f"Showing {len(filtered_df):,} records "
    f"out of {len(df):,} total records."
)



section("📊 Business Performance")

kpis = calculate_kpis(
    filtered_df,
    schema
)

kpi_cards = [
    (
        "Total Sales",
        money(kpis["sales"]),
        "Total revenue / sales value"
    ),
    (
        "Total Profit",
        money(kpis["profit"]),
        "Total profit generated"
    ),
    (
        "Profit Margin",
        percent(kpis["margin"]),
        "Profit as a percentage of sales"
    ),
    (
        "Units Sold",
        f"{int(kpis['quantity']):,}",
        "Total quantity sold"
    ),
    (
        "Orders",
        f"{int(kpis['orders']):,}",
        "Unique orders"
    ),
    (
        "Customers",
        f"{int(kpis['customers']):,}",
        "Unique customers"
    )
]

for start in range(0, 6, 3):

    cols = st.columns(3)

    for col, data in zip(
        cols,
        kpi_cards[start:start + 3]
    ):

        with col:
            card(*data)




st.markdown(
    "### 🤖 Automated Business Insights"
)

show_insights(
    filtered_df
)



visual_tab, business_tab, profile_tab, advanced_tab = st.tabs(
    [
        "📊 Visual Analytics",
        "💼 Business Analysis",
        "🔍 Data Profiling",
        "🔬 Advanced Analytics"
    ]
)




with visual_tab:

    section("📈 Visual Analytics")

    analysis_buttons(
        [
            ("📈 Sales Trend", "sales"),
            ("🏷️ Category Analysis", "category"),
            ("🌍 Geographic Analysis", "geography"),
            ("🏆 Top Products", "products"),
            ("💰 Profit Analysis", "profit"),
            ("💳 Payment Analysis", "payment")
        ],
        "visual_analysis"
    )

    visual = (
        st.session_state.visual_analysis
    )




    if visual == "sales":

        st.subheader(
            "📈 Sales Trend"
        )

        data = sales_growth_analysis(
            filtered_df,
            schema
        )

        if data.empty:

            st.warning(
                "A valid date and sales column could not be identified."
            )

        else:

            fig = px.line(
                data,
                x="Month",
                y="Sales",
                markers=True,
                title="Sales Trend"
            )

            dark_chart(fig)



    elif visual == "category":

        st.subheader(
            "🏷️ Category Analysis"
        )

        data = category_analysis(
            filtered_df,
            schema
        )

        if data.empty:

            st.warning(
                "A category column could not be identified."
            )

        else:

            fig = px.bar(
                data.sort_values(
                    "Sales",
                    ascending=False
                ),
                x="Category",
                y="Sales",
                text_auto=".2s"
            )

            dark_chart(fig)




    elif visual == "geography":

        geo_name = (
            schema.get(
                "geography_label",
                "Geography"
            )
        )

        st.subheader(
            f"🌍 Sales by {geo_name}"
        )

        data = geographic_analysis(
            filtered_df,
            schema
        )

        if data.empty:

            st.warning(
                "No suitable geographic column was identified."
            )

        else:

            geo_column = data.columns[0]

            fig = px.bar(
                data.sort_values(
                    "Sales",
                    ascending=False
                ),
                x=geo_column,
                y="Sales",
                text_auto=".2s"
            )

            dark_chart(fig)




    elif visual == "products":

        product_label = schema.get(
            "product_label",
            "Product"
        )

        st.subheader(
            f"🏆 Top {product_label}"
        )

        data = product_analysis(
            filtered_df,
            schema
        )

        if data.empty:

            st.warning(
                "No suitable product-level column was identified."
            )

        else:

            product_column = data.columns[0]

            data = (
                data
                .sort_values(
                    "Sales",
                    ascending=False
                )
                .head(10)
                .sort_values("Sales")
            )

            fig = px.bar(
                data,
                x="Sales",
                y=product_column,
                orientation="h",
                text_auto=".2s"
            )

            dark_chart(fig)




    elif visual == "profit":

        st.subheader(
            "💰 Profit Analysis"
        )

        data = category_analysis(
            filtered_df,
            schema
        )

        if (
            data.empty
            or "Profit" not in data.columns
        ):

            st.warning(
                "Profit and category data could not be identified."
            )

        else:

            fig = px.bar(
                data.sort_values(
                    "Profit",
                    ascending=False
                ),
                x="Category",
                y="Profit",
                text_auto=".2s"
            )

            dark_chart(fig)




    elif visual == "payment":

        st.subheader(
            "💳 Payment Analysis"
        )

        payment_column = schema.get(
            "payment"
        )

        sales_column = schema.get(
            "sales"
        )

        if not payment_column or not sales_column:

            st.warning(
                "A payment column and sales column "
                "could not be identified."
            )

        else:

            data = (
                filtered_df
                .groupby(payment_column)[sales_column]
                .sum()
                .reset_index()
            )

            fig = px.bar(
                data.sort_values(
                    sales_column,
                    ascending=False
                ),
                x=payment_column,
                y=sales_column,
                text_auto=".2s"
            )

            dark_chart(fig)


    else:

        st.info(
            "👆 Select a visualization above."
        )




with business_tab:

    section("💼 Business Analysis")

    analysis_buttons(
        [
            ("📈 Sales Growth", "growth"),
            ("💰 Profitability", "profitability"),
            ("🏆 Performance Ranking", "ranking"),
            ("⚖️ Sales vs Profit", "sales_profit"),
            ("💡 Recommendations", "recommendations")
        ],
        "business_analysis",
        columns=2
    )

    analysis = (
        st.session_state.business_analysis
    )


    if analysis == "growth":

        st.subheader(
            "📈 Sales Growth Analysis"
        )

        data = sales_growth_analysis(
            filtered_df,
            schema
        )

        if data.empty:

            st.warning(
                "A valid date and sales column could not be identified."
            )

        else:

            st.dataframe(
                data,
                use_container_width=True,
                hide_index=True
            )

            fig = px.bar(
                data,
                x="Year",
                y="Growth %",
                text="Growth %",
                title="Year-over-Year Sales Growth"
            )

            fig.update_traces(
                texttemplate="%{text:.2f}%",
                textposition="outside"
            )

            dark_chart(fig)


    elif analysis == "profitability":

        st.subheader(
            "💰 Profitability Analysis"
        )

        data = profitability_analysis(
            filtered_df,
            schema
        )

        if data.empty:

            st.warning(
                "Category, sales and profit data could not be identified."
            )

        else:

            st.dataframe(
                data,
                use_container_width=True,
                hide_index=True
            )

            if "Profit Margin %" in data.columns:

                fig = px.bar(
                    data.sort_values(
                        "Profit Margin %",
                        ascending=False
                    ),
                    x="Category",
                    y="Profit Margin %",
                    text_auto=".2f"
                )

                dark_chart(fig)


    elif analysis == "ranking":

        st.subheader(
            "🏆 Performance Ranking"
        )

        rankings = performance_ranking(
            filtered_df,
            schema
        )

        for title, key in [
            ("Top Category", "top_category"),
            ("Top Geographic Area", "top_geography"),
            ("Top Product", "top_product")
        ]:

            row = rankings.get(key)

            if row is not None:

                column = row.index[0]
                value = row.iloc[0]

                sales_value = (
                    row["Sales"]
                    if "Sales" in row.index
                    else 0
                )

                card(
                    title,
                    str(value),
                    f"Sales: {money(sales_value)}"
                )


    elif analysis == "sales_profit":

        st.subheader(
            "⚖️ Sales vs Profit"
        )

        data = sales_profit_analysis(
            filtered_df,
            schema
        )

        if data.empty:

            st.warning(
                "Sales and profit data could not be identified."
            )

        else:

            dimension = data.columns[0]

            fig = px.scatter(
                data,
                x="Sales",
                y="Profit",
                size="Sales",
                color=dimension,
                hover_name=dimension
            )

            dark_chart(fig)


    elif analysis == "recommendations":

        st.subheader(
            "💡 Business Recommendations"
        )

        show_recommendations(
            filtered_df
        )


    else:

        st.info(
            "👆 Select a business analysis above."
        )




with profile_tab:

    section("🔍 Data Profiling")

    analysis_buttons(
        [
            ("📊 Data Quality", "quality"),
            ("📋 Column Information", "columns"),
            ("🔢 Numeric Summary", "numeric"),
            ("⚠️ Missing Values", "missing"),
            ("🔁 Duplicate Records", "duplicates"),
            ("📄 Dataset Preview", "preview")
        ],
        "profile_analysis",
        columns=2
    )

    profile = (
        st.session_state.profile_analysis
    )


    if profile == "quality":

        quality = get_data_quality(
            filtered_df
        )

        cards = [
            (
                "Rows",
                f"{quality['rows']:,}",
                "Number of records"
            ),
            (
                "Columns",
                f"{quality['columns']:,}",
                "Number of fields"
            ),
            (
                "Missing Values",
                f"{quality['missing_values']:,}",
                f"{quality['missing_percentage']:.2f}% of cells"
            ),
            (
                "Duplicate Rows",
                f"{quality['duplicates']:,}",
                quality["status"]
            )
        ]

        cols = st.columns(4)

        for col, data in zip(
            cols,
            cards
        ):

            with col:
                card(*data)


    elif profile == "columns":

        st.subheader(
            "📋 Column Information"
        )

        st.dataframe(
            get_column_profile(
                filtered_df,
                schema
            ),
            use_container_width=True,
            hide_index=True
        )


    elif profile == "numeric":

        st.subheader(
            "🔢 Numeric Summary"
        )

        data = get_numeric_summary(
            filtered_df,
            schema
        )

        if data.empty:

            st.info(
                "No meaningful numeric business metrics were identified."
            )

        else:

            st.dataframe(
                data,
                use_container_width=True,
                hide_index=True
            )


    elif profile == "missing":

        st.subheader(
            "⚠️ Missing Values"
        )

        data = get_missing_values(
            filtered_df
        )

        if data.empty:

            st.success(
                "No missing values were found."
            )

        else:

            st.dataframe(
                data,
                use_container_width=True,
                hide_index=True
            )


    elif profile == "duplicates":

        st.subheader(
            "🔁 Duplicate Records"
        )

        data = get_duplicate_records(
            filtered_df
        )

        if data.empty:

            st.success(
                "No duplicate records were found."
            )

        else:

            st.warning(
                f"{len(data):,} duplicate records found."
            )

            st.dataframe(
                data,
                use_container_width=True,
                hide_index=True
            )


    elif profile == "preview":

        st.subheader(
            "📄 Dataset Preview"
        )

        st.dataframe(
            filtered_df.head(100),
            use_container_width=True,
            height=500
        )


    else:

        st.info(
            "👆 Select a profiling option above."
        )




with advanced_tab:

    section("🔬 Advanced Analytics")

    analysis_buttons(
        [
            ("👥 Customer Analysis", "customer"),
            ("📦 Product Analysis", "product"),
            ("🚨 Anomaly Detection", "anomaly"),
            ("📊 Pareto Analysis", "pareto")
        ],
        "advanced_analysis",
        columns=2
    )

    advanced = (
        st.session_state.advanced_analysis
    )


 

    if advanced == "customer":

        customer_label = schema.get(
            "customer_label",
            "Customer"
        )

        st.subheader(
            f"👥 {customer_label} Analysis"
        )

        data = customer_analysis(
            filtered_df,
            schema
        )

        if data.empty:

            st.warning(
                "No suitable customer column was identified."
            )

        else:

            customer_column = data.columns[0]

            top = (
                data
                .sort_values(
                    "Sales",
                    ascending=False
                )
                .head(10)
                .sort_values("Sales")
            )

            fig = px.bar(
                top,
                x="Sales",
                y=customer_column,
                orientation="h",
                text_auto=".2s",
                title=f"Top {customer_label}s by Sales"
            )

            dark_chart(fig)

            st.dataframe(
                data,
                use_container_width=True,
                hide_index=True
            )



    elif advanced == "product":

        product_label = schema.get(
            "product_label",
            "Product"
        )

        st.subheader(
            f"📦 {product_label} Analysis"
        )

        data = advanced_product_analysis(
            filtered_df,
            schema
        )

        if data.empty:

            st.warning(
                "No suitable product-level column was identified."
            )

        else:

            product_column = data.columns[0]

            top_sales = (
                data
                .sort_values(
                    "Sales",
                    ascending=False
                )
                .head(10)
                .sort_values("Sales")
            )

            fig = px.bar(
                top_sales,
                x="Sales",
                y=product_column,
                orientation="h",
                text_auto=".2s",
                title=f"Top {product_label}s by Sales"
            )

            dark_chart(fig)

            if "Profit" in data.columns:

                top_profit = (
                    data
                    .sort_values(
                        "Profit",
                        ascending=False
                    )
                    .head(10)
                    .sort_values("Profit")
                )

                fig = px.bar(
                    top_profit,
                    x="Profit",
                    y=product_column,
                    orientation="h",
                    text_auto=".2s",
                    title=f"Top {product_label}s by Profit"
                )

                dark_chart(fig)




    elif advanced == "anomaly":

        st.subheader(
            "🚨 Anomaly Detection"
        )

        st.write(
            "InsightFlow identifies unusually high or low "
            "sales and profit values using statistical analysis."
        )

        sales_anomalies = detect_anomalies(
            filtered_df,
            schema
        )

        if sales_anomalies.empty:

            st.success(
                "✅ No significant sales anomalies detected."
            )

        else:

            st.dataframe(
                sales_anomalies,
                use_container_width=True,
                hide_index=True
            )


        monthly = monthly_sales_anomalies(
            filtered_df,
            schema
        )

        if not monthly.empty:

            st.markdown(
                "### 📅 Monthly Sales Anomalies"
            )

            anomalies = monthly[
                monthly["Anomaly"]
            ]

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=monthly["Month"],
                    y=monthly["Sales"],
                    mode="lines+markers",
                    name="Normal Sales",
                    line=dict(
                        color="#66b3ff"
                    ),
                    marker=dict(
                        size=7,
                        color="#66b3ff"
                    )
                )
            )

            if not anomalies.empty:

                fig.add_trace(
                    go.Scatter(
                        x=anomalies["Month"],
                        y=anomalies["Sales"],
                        mode="markers",
                        name="Anomaly",
                        marker=dict(
                            size=15,
                            color="#ff4b4b"
                        )
                    )
                )

            fig.update_layout(
                title="Monthly Sales with Anomaly Detection",
                xaxis_title="Month",
                yaxis_title="Sales",
                template="plotly_dark"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            c1, c2 = st.columns(2)

            with c1:

                st.info(
                    "🔵 **Blue dots** — normal sales values."
                )

            with c2:

                st.error(
                    "🔴 **Red dots** — statistically unusual values."
                )


   

    elif advanced == "pareto":

        st.subheader(
            "📊 Pareto / 80-20 Analysis"
        )

        dimensions = {}

        if schema.get("product"):
            dimensions[
                schema.get(
                    "product_label",
                    "Product"
                )
            ] = "product"

        if schema.get("customer"):
            dimensions[
                schema.get(
                    "customer_label",
                    "Customer"
                )
            ] = "customer"

        if schema.get("geography"):
            dimensions[
                schema.get(
                    "geography_label",
                    "Geography"
                )
            ] = "geography"

        if schema.get("category"):
            dimensions["Category"] = "category"

        if not dimensions:

            st.warning(
                "No suitable dimension was identified."
            )

        else:

            selected_label = st.selectbox(
                "Analyze sales contribution by:",
                list(dimensions.keys())
            )

            selected_role = dimensions[
                selected_label
            ]

            data = pareto_analysis(
                filtered_df,
                schema,
                selected_role
            )

            if data.empty:

                st.warning(
                    "Unable to generate Pareto analysis."
                )

            else:

                dimension = data.columns[0]

                within_80 = data[
                    data["Cumulative %"] <= 80
                ]

                c1, c2 = st.columns(2)

                with c1:

                    card(
                        "Total Entities",
                        f"{len(data):,}",
                        selected_label
                    )

                with c2:

                    card(
                        "Entities within 80%",
                        f"{max(len(within_80), 1):,}",
                        "Highest sales contribution"
                    )

                fig = px.bar(
                    data.head(20),
                    x=dimension,
                    y="Sales",
                    title=f"Sales Contribution by {selected_label}"
                )

                fig.update_layout(
                    template="plotly_dark",
                    xaxis_tickangle=-45
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.dataframe(
                    data,
                    use_container_width=True,
                    hide_index=True
                )


    else:

        st.info(
            "👆 Select an advanced analysis above."
        )




st.markdown("---")

st.caption(
    "InsightFlow • Intelligent Business Analytics Platform"
)