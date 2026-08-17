import pandas as pd
import numpy as np

COLUMN_ALIASES = {

    "sales": [
        "sales",
        "sale",
        "amount",
        "total amount",
        "sales amount",
        "revenue",
        "total sales",
        "total revenue",
        "revenue amount",
        "net sales",
        "selling price",
        "sales value"
    ],

    "profit": [
        "profit",
        "profits",
        "net profit",
        "profit amount",
        "profit value",
        "gross profit"
    ],

    "quantity": [
        "quantity",
        "qty",
        "units",
        "units sold",
        "quantity sold",
        "number of units"
    ],

    "discount": [
        "discount",
        "discount rate",
        "discount percentage",
        "discount percent"
    ],

    "order_id": [
        "order id",
        "orderid",
        "order number",
        "order no",
        "order"
    ],

    "date": [
        "order date",
        "orderdate",
        "date",
        "purchase date",
        "transaction date",
        "sales date",
        "invoice date"
    ],

    "customer": [
        "customer name",
        "customername",
        "customer",
        "client name",
        "client",
        "buyer name",
        "buyer"
    ],

    "customer_id": [
        "customer id",
        "customerid",
        "client id",
        "clientid",
        "buyer id"
    ],

    "product": [
        "product name",
        "productname",
        "product",
        "item name",
        "item",
        "product description"
    ],

    "subcategory": [
        "sub category",
        "sub-category",
        "subcategory",
        "product sub category",
        "product sub-category",
        "product subcategory"
    ],

    "category": [
        "category",
        "product category",
        "item category",
        "main category"
    ],

    "region": [
        "region",
        "sales region",
        "geographical region",
        "geographic region"
    ],

    "state": [
        "state",
        "province",
        "state name",
        "province name"
    ],

    "city": [
        "city",
        "city name",
        "town"
    ],

    "payment": [
        "payment mode",
        "paymentmode",
        "payment-mode",
        "payment method",
        "payment type",
        "payment"
    ],

    "year": [
        "year",
        "sales year",
        "order year"
    ]
}


def normalize_name(name):
    """
    Convert a column name into a normalized form.

    Examples:
        CustomerName -> customername
        Customer_Name -> customer name
        Payment-Mode -> payment mode
    """

    return (
        str(name)
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
        .replace("/", " ")
        .replace(".", " ")
    )


def compact_name(name):
    """
    Remove spaces so names such as:

        Customer Name
        CustomerName
        customer_name

    can be compared.
    """

    return normalize_name(name).replace(" ", "")


def find_exact_alias(df, aliases):
    """
    Find a column using normalized aliases.
    """

    normalized_columns = {
        normalize_name(column): column
        for column in df.columns
    }

    compact_columns = {
        compact_name(column): column
        for column in df.columns
    }

    for alias in aliases:

        normalized_alias = normalize_name(alias)

        if normalized_alias in normalized_columns:
            return normalized_columns[
                normalized_alias
            ]

        compact_alias = compact_name(alias)

        if compact_alias in compact_columns:
            return compact_columns[
                compact_alias
            ]

    return None



def numeric_score(series):
    """
    Determine how strongly a column behaves like numeric data.
    """

    if series.empty:
        return 0

    converted = pd.to_numeric(
        series,
        errors="coerce"
    )

    return converted.notna().mean()


def date_score(series):
    """
    Determine how strongly a column behaves like a date.
    """

    if series.empty:
        return 0

    converted = pd.to_datetime(
        series,
        errors="coerce"
    )

    return converted.notna().mean()


def text_score(series):
    """
    Determine how strongly a column behaves like text.
    """

    if series.empty:
        return 0

    return (
        series.astype(str)
        .notna()
        .mean()
    )




def detect_schema(df):
    """
    Identify the business role of each column.

    The function combines:
        1. Column-name matching
        2. Normalized-name matching
        3. Data-type detection
        4. Dataset structure

    It does NOT rename columns.
    It simply creates a mapping between business roles
    and the original dataset columns.
    """

    schema = {
        "sales": None,
        "profit": None,
        "quantity": None,
        "discount": None,
        "order_id": None,
        "date": None,
        "customer": None,
        "customer_id": None,
        "product": None,
        "subcategory": None,
        "category": None,
        "region": None,
        "state": None,
        "city": None,
        "payment": None,
        "year": None
    }



    for role, aliases in COLUMN_ALIASES.items():

        schema[role] = find_exact_alias(
            df,
            aliases
        )

   

    if schema["date"] is None:

        for column in df.columns:

            if date_score(
                df[column]
            ) >= 0.75:

                schema["date"] = column
                break

  

    if schema["sales"] is None:

        candidates = []

        for column in df.columns:

            if column in [
                schema["profit"],
                schema["quantity"],
                schema["discount"],
                schema["year"]
            ]:
                continue

            score = numeric_score(
                df[column]
            )

            if score >= 0.90:

                candidates.append(
                    (
                        column,
                        score,
                        df[column]
                        .nunique()
                    )
                )

        if candidates:

            candidates.sort(
                key=lambda x: x[2],
                reverse=True
            )

            schema["sales"] = candidates[0][0]

    

    if schema["quantity"] is None:

        for column in df.columns:

            if column == schema["sales"]:
                continue

            if numeric_score(
                df[column]
            ) < 0.90:
                continue

            values = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            if (
                values.min() >= 0
                and values.max() <= 100
                and values.nunique() <= 100
            ):

                schema["quantity"] = column
                break

  
    if schema["profit"] is None:

        for column in df.columns:

            if column in [
                schema["sales"],
                schema["quantity"],
                schema["discount"]
            ]:
                continue

            if numeric_score(
                df[column]
            ) < 0.90:
                continue

            values = pd.to_numeric(
                df[column],
                errors="coerce"
            )

            if (
                values.min() < 0
                or values.nunique() > 20
            ):

                schema["profit"] = column
                break

    

    geography = (
        schema["region"]
        or schema["state"]
        or schema["city"]
    )

    schema["geography"] = geography

    if schema["region"]:

        schema["geography_label"] = "Region"

    elif schema["state"]:

        schema["geography_label"] = "State"

    elif schema["city"]:

        schema["geography_label"] = "City"

    else:

        schema["geography_label"] = "Geography"

    
    if schema["product"]:

        schema["product_label"] = "Product"

    elif schema["subcategory"]:

        schema["product"] = (
            schema["subcategory"]
        )

        schema["product_label"] = (
            "Sub-Category"
        )

    else:

        schema["product_label"] = "Product"

  

    if schema["customer"]:

        schema["customer_label"] = (
            "Customer"
        )

    elif schema["customer_id"]:

        schema["customer"] = (
            schema["customer_id"]
        )

        schema["customer_label"] = (
            "Customer ID"
        )

    else:

        schema["customer_label"] = (
            "Customer"
        )

   

    if schema["year"] is None:

        if schema["date"]:

            schema["year"] = "__generated_year__"

  

    schema["sales_label"] = (
        schema["sales"]
        or "Sales"
    )

    schema["profit_label"] = (
        schema["profit"]
        or "Profit"
    )

    schema["quantity_label"] = (
        schema["quantity"]
        or "Quantity"
    )

    schema["date_label"] = (
        schema["date"]
        or "Date"
    )

    return schema


def clean_data(df):

    data = df.copy()

    
    data = data.dropna(
        how="all"
    )

    data = data.dropna(
        axis=1,
        how="all"
    )

    
    data.columns = (
        data.columns
        .astype(str)
        .str.strip()
    )

    
    schema = detect_schema(
        data
    )

    
    for role in [
        "sales",
        "profit",
        "quantity",
        "discount"
    ]:

        column = schema.get(
            role
        )

        if column:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            )

    
    date_column = schema.get(
        "date"
    )

    if date_column:

        data[date_column] = pd.to_datetime(
            data[date_column],
            errors="coerce"
        )

   
    if (
        schema.get("year")
        == "__generated_year__"
        and date_column
    ):

        data["__InsightFlow_Year__"] = (
            data[date_column].dt.year
        )

    
    data = data.drop_duplicates()

    return data.reset_index(
        drop=True
    )




def get_column(schema, role):

    return schema.get(
        role
    )


def get_year_column(df, schema):

    if (
        schema.get("year")
        == "__generated_year__"
    ):

        if "__InsightFlow_Year__" in df.columns:
            return "__InsightFlow_Year__"

    return schema.get(
        "year"
    )


def get_product_column(schema):

    return schema.get(
        "product"
    )


def get_customer_column(schema):

    return schema.get(
        "customer"
    )


def get_geography_column(schema):

    return schema.get(
        "geography"
    )




def get_data_quality(df):

    rows, columns = df.shape

    missing = int(
        df.isna()
        .sum()
        .sum()
    )

    cells = rows * columns

    missing_percentage = (
        missing / cells * 100
        if cells
        else 0
    )

    duplicates = int(
        df.duplicated()
        .sum()
    )

    if missing == 0 and duplicates == 0:

        status = "Good"

    elif missing_percentage < 5:

        status = "Acceptable"

    else:

        status = "Needs Attention"

    return {
        "rows": rows,
        "columns": columns,
        "missing_values": missing,
        "missing_percentage": missing_percentage,
        "duplicates": duplicates,
        "status": status
    }




def get_column_profile(df, schema=None):

    profile = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str),
        "Non-Null Count": df.notna().sum().values,
        "Missing Values": df.isna().sum().values,
        "Unique Values": df.nunique().values
    })

    if schema:

        role_map = {}

        for role, column in schema.items():

            if (
                column
                and column in df.columns
            ):

                role_map.setdefault(
                    column,
                    []
                ).append(
                    role.replace(
                        "_",
                        " "
                    ).title()
                )

        profile["Detected Role"] = (
            profile["Column"]
            .map(
                lambda x:
                ", ".join(
                    role_map.get(
                        x,
                        []
                    )
                )
            )
        )

    return profile




def get_missing_values(df):

    missing = df.isna().sum()

    missing = missing[
        missing > 0
    ]

    if missing.empty:

        return pd.DataFrame(
            columns=[
                "Column",
                "Missing Values",
                "Missing %"
            ]
        )

    result = (
        missing
        .rename(
            "Missing Values"
        )
        .reset_index()
    )

    result.columns = [
        "Column",
        "Missing Values"
    ]

    result["Missing %"] = (
        result["Missing Values"]
        / len(df)
        * 100
    ).round(2)

    return result.sort_values(
        "Missing Values",
        ascending=False
    )




def get_numeric_summary(
    df,
    schema=None
):

    if schema:

        columns = [
            schema.get(role)
            for role in [
                "sales",
                "quantity",
                "discount",
                "profit"
            ]
            if schema.get(role)
            and schema.get(role) in df.columns
        ]

    else:

        columns = [
            column
            for column in [
                "Sales",
                "Quantity",
                "Discount",
                "Profit"
            ]
            if column in df.columns
        ]

    if not columns:

        return pd.DataFrame()

    data = df[
        columns
    ].copy()

    for column in columns:

        data[column] = pd.to_numeric(
            data[column],
            errors="coerce"
        )

    summary = (
        data
        .describe()
        .T
        .reset_index()
        .rename(
            columns={
                "index": "Column"
            }
        )
    )

    summary = summary.rename(
        columns={
            column: column
            for column in summary.columns
        }
    )

    summary.iloc[
        :,
        1:
    ] = summary.iloc[
        :,
        1:
    ].round(4)

    return summary




def get_duplicate_records(df):

    return df[
        df.duplicated(
            keep=False
        )
    ].copy()




def calculate_kpis(
    df,
    schema=None
):

    if schema is None:
        schema = detect_schema(df)

    def total(role):

        column = schema.get(
            role
        )

        if not column or column not in df.columns:
            return 0

        return pd.to_numeric(
            df[column],
            errors="coerce"
        ).sum()

    sales = total("sales")
    profit = total("profit")
    quantity = total("quantity")

    order_column = schema.get(
        "order_id"
    )

    if order_column:

        orders = df[
            order_column
        ].nunique()

    else:

        orders = len(df)

    customer_column = (
        get_customer_column(
            schema
        )
    )

    customers = (
        df[customer_column].nunique()
        if customer_column
        else 0
    )

    margin = (
        profit / sales * 100
        if sales
        else 0
    )

    return {
        "sales": sales,
        "profit": profit,
        "margin": margin,
        "quantity": quantity,
        "orders": orders,
        "customers": customers
    }




def category_analysis(
    df,
    schema=None
):

    if schema is None:
        schema = detect_schema(df)

    category = schema.get(
        "category"
    )

    sales = schema.get(
        "sales"
    )

    profit = schema.get(
        "profit"
    )

    if not category or not sales:
        return pd.DataFrame()

    columns = [sales]

    if profit:
        columns.append(profit)

    data = (
        df.groupby(
            category
        )[columns]
        .sum()
        .reset_index()
    )

    data = data.rename(
        columns={
            category: "Category",
            sales: "Sales",
            profit: "Profit"
            if profit
            else profit
        }
    )

    return data




def geographic_analysis(
    df,
    schema=None
):

    if schema is None:
        schema = detect_schema(df)

    geography = get_geography_column(
        schema
    )

    sales = schema.get(
        "sales"
    )

    if not geography or not sales:
        return pd.DataFrame()

    data = (
        df.groupby(
            geography
        )[sales]
        .sum()
        .reset_index()
    )

    return data.rename(
        columns={
            geography: schema.get(
                "geography_label",
                "Geography"
            ),
            sales: "Sales"
        }
    )



def product_analysis(
    df,
    schema=None
):

    if schema is None:
        schema = detect_schema(df)

    product = get_product_column(
        schema
    )

    sales = schema.get(
        "sales"
    )

    if not product or not sales:
        return pd.DataFrame()

    return (
        df.groupby(
            product
        )[sales]
        .sum()
        .reset_index()
        .rename(
            columns={
                product: schema.get(
                    "product_label",
                    "Product"
                ),
                sales: "Sales"
            }
        )
    )




def advanced_product_analysis(
    df,
    schema=None
):

    if schema is None:
        schema = detect_schema(df)

    product = get_product_column(
        schema
    )

    sales = schema.get(
        "sales"
    )

    profit = schema.get(
        "profit"
    )

    if not product or not sales:
        return pd.DataFrame()

    columns = [sales]

    if profit:
        columns.append(profit)

    data = (
        df.groupby(
            product
        )[columns]
        .sum()
        .reset_index()
    )

    data = data.rename(
        columns={
            product: schema.get(
                "product_label",
                "Product"
            ),
            sales: "Sales",
            profit: "Profit"
            if profit
            else profit
        }
    )

    if "Profit" in data.columns:

        data["Profit Margin %"] = np.where(
            data["Sales"] != 0,
            data["Profit"]
            / data["Sales"]
            * 100,
            0
        ).round(2)

    return data



def sales_growth_analysis(
    df,
    schema=None
):

    if schema is None:
        schema = detect_schema(df)

    date = schema.get(
        "date"
    )

    sales = schema.get(
        "sales"
    )

    if not date or not sales:
        return pd.DataFrame()

    data = df.copy()

    data[date] = pd.to_datetime(
        data[date],
        errors="coerce"
    )

    data[sales] = pd.to_numeric(
        data[sales],
        errors="coerce"
    )

    data = data.dropna(
        subset=[
            date,
            sales
        ]
    )

    if data.empty:
        return pd.DataFrame()

    data["Year"] = (
        data[date]
        .dt.year
    )

    data["Month"] = (
        data[date]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly = (
        data.groupby(
            "Month"
        )[sales]
        .sum()
        .reset_index()
        .rename(
            columns={
                sales: "Sales"
            }
        )
        .sort_values("Month")
    )

    monthly["Year"] = (
        monthly["Month"]
        .dt.year
    )

    monthly["Growth %"] = (
        monthly["Sales"]
        .pct_change()
        .fillna(0)
        * 100
    ).round(2)

    return monthly




def profitability_analysis(
    df,
    schema=None
):

    data = category_analysis(
        df,
        schema
    )

    if (
        data.empty
        or "Profit" not in data.columns
    ):

        return pd.DataFrame()

    data["Profit Margin %"] = np.where(
        data["Sales"] != 0,
        data["Profit"]
        / data["Sales"]
        * 100,
        0
    ).round(2)

    return data



def performance_ranking(
    df,
    schema=None
):

    if schema is None:
        schema = detect_schema(df)

    result = {
        "top_category": None,
        "top_geography": None,
        "top_product": None
    }

    mappings = [
        (
            "category",
            "top_category"
        ),
        (
            "geography",
            "top_geography"
        ),
        (
            "product",
            "top_product"
        )
    ]

    sales = schema.get(
        "sales"
    )

    if not sales:
        return result

    for role, key in mappings:

        column = schema.get(
            role
        )

        if not column:
            continue

        data = (
            df.groupby(
                column
            )[sales]
            .sum()
            .reset_index()
            .sort_values(
                sales,
                ascending=False
            )
        )

        if not data.empty:

            result[key] = (
                data.iloc[0]
            )

    return result




def sales_profit_analysis(
    df,
    schema=None
):

    data = category_analysis(
        df,
        schema
    )

    return data



def customer_analysis(
    df,
    schema=None
):

    if schema is None:
        schema = detect_schema(df)

    customer = get_customer_column(
        schema
    )

    sales = schema.get(
        "sales"
    )

    if not customer or not sales:
        return pd.DataFrame()

    return (
        df.groupby(
            customer
        )[sales]
        .sum()
        .reset_index()
        .sort_values(
            sales,
            ascending=False
        )
        .rename(
            columns={
                customer: schema.get(
                    "customer_label",
                    "Customer"
                ),
                sales: "Sales"
            }
        )
    )




def generate_business_recommendations(
    df,
    schema=None
):

    if schema is None:
        schema = detect_schema(df)

    recommendations = []

    kpis = calculate_kpis(
        df,
        schema
    )

    margin = kpis["margin"]

    if margin < 10:

        recommendations.append(
            "Profit margin is relatively low. "
            "Review pricing, discounts and operating costs."
        )

    elif margin >= 20:

        recommendations.append(
            "The business has a strong overall profit margin."
        )

    else:

        recommendations.append(
            "Profitability is at a moderate level. "
            "Review high-cost products and discount patterns."
        )


    category = schema.get(
        "category"
    )

    sales = schema.get(
        "sales"
    )

    if category and sales:

        data = (
            df.groupby(
                category
            )[sales]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        if not data.empty:

            recommendations.append(
                f"{data.index[0]} is the strongest "
                "category by sales."
            )

    geography = get_geography_column(
        schema
    )

    if geography and sales:

        data = (
            df.groupby(
                geography
            )[sales]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        if not data.empty:

            recommendations.append(
                f"{data.index[0]} is the strongest "
                "geographic area by sales."
            )

  
    discount = schema.get(
        "discount"
    )

    if discount:

        avg_discount = pd.to_numeric(
            df[discount],
            errors="coerce"
        ).mean()

        if avg_discount > 0.2:

            recommendations.append(
                "Average discount levels are relatively high. "
                "Review discounting strategies."
            )

    return recommendations




def generate_insights(
    df,
    schema=None
):

    if schema is None:
        schema = detect_schema(df)

    insights = []

    kpis = calculate_kpis(
        df,
        schema
    )

    insights.extend([
        (
            f"Total sales are "
            f"{kpis['sales']:,.2f} "
            f"with total profit of "
            f"{kpis['profit']:,.2f}."
        ),
        (
            f"Overall profit margin is "
            f"{kpis['margin']:.2f}%."
        )
    ])

    for role, message in [
        (
            "category",
            "category"
        ),
        (
            "geography",
            "geographic area"
        ),
        (
            "product",
            "product"
        )
    ]:

        column = schema.get(
            role
        )

        sales = schema.get(
            "sales"
        )

        if not column or not sales:
            continue

        data = (
            df.groupby(
                column
            )[sales]
            .sum()
            .sort_values(
                ascending=False
            )
        )

        if not data.empty:

            insights.append(
                f"{data.index[0]} has the "
                f"highest sales among "
                f"{message}s."
            )

    return insights




def detect_anomalies(
    df,
    schema=None
):

    if schema is None:
        schema = detect_schema(df)

    sales = schema.get(
        "sales"
    )

    if not sales:
        return pd.DataFrame()

    data = df.copy()

    data[sales] = pd.to_numeric(
        data[sales],
        errors="coerce"
    )

    data = data.dropna(
        subset=[
            sales
        ]
    )

    if len(data) < 5:
        return pd.DataFrame()

    q1, q3 = data[
        sales
    ].quantile(
        [0.25, 0.75]
    )

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    anomalies = data[
        (data[sales] < lower)
        |
        (data[sales] > upper)
    ].copy()

    if anomalies.empty:
        return anomalies

    anomalies["Anomaly Type"] = np.where(
        anomalies[sales] < lower,
        "Low",
        "High"
    )

    std = data[sales].std()

    if std:

        anomalies[
            "Detection Score"
        ] = (
            (
                anomalies[sales]
                - data[sales].mean()
            )
            / std
        ).abs().round(2)

    else:

        anomalies[
            "Detection Score"
        ] = 0

    return anomalies.sort_values(
        sales,
        ascending=False
    )



def monthly_sales_anomalies(
    df,
    schema=None
):

    if schema is None:
        schema = detect_schema(df)

    date = schema.get(
        "date"
    )

    sales = schema.get(
        "sales"
    )

    if not date or not sales:
        return pd.DataFrame()

    data = df.copy()

    data[date] = pd.to_datetime(
        data[date],
        errors="coerce"
    )

    data[sales] = pd.to_numeric(
        data[sales],
        errors="coerce"
    )

    data = data.dropna(
        subset=[
            date,
            sales
        ]
    )

    if data.empty:
        return pd.DataFrame()

    monthly = (
        data.groupby(
            data[date]
            .dt.to_period("M")
        )[sales]
        .sum()
        .reset_index()
    )

    monthly["Month"] = (
        monthly[date]
        .dt.to_timestamp()
    )

    monthly = monthly[
        ["Month", sales]
    ].rename(
        columns={
            sales: "Sales"
        }
    )

    if len(monthly) < 5:
        return pd.DataFrame()

    q1, q3 = monthly[
        "Sales"
    ].quantile(
        [0.25, 0.75]
    )

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    monthly["Anomaly"] = (
        (monthly["Sales"] < lower)
        |
        (monthly["Sales"] > upper)
    )

    monthly["Anomaly Type"] = np.select(
        [
            monthly["Sales"] < lower,
            monthly["Sales"] > upper
        ],
        [
            "Low",
            "High"
        ],
        default="Normal"
    )

    std = monthly["Sales"].std()

    if std:

        monthly[
            "Detection Score"
        ] = (
            (
                monthly["Sales"]
                - monthly["Sales"].mean()
            )
            / std
        ).abs().round(2)

    else:

        monthly[
            "Detection Score"
        ] = 0

    return monthly




def pareto_analysis(
    df,
    schema=None,
    dimension_role=None
):

    if schema is None:
        schema = detect_schema(df)

    sales = schema.get(
        "sales"
    )

    if not sales:
        return pd.DataFrame()

 
    if dimension_role:

        if dimension_role == "product":
            dimension = get_product_column(schema)

        elif dimension_role == "customer":
            dimension = get_customer_column(schema)

        elif dimension_role == "geography":
            dimension = get_geography_column(schema)

        elif dimension_role == "category":
            dimension = schema.get("category")

        else:
            dimension = None

    else:

        dimension = (
            get_product_column(schema)
            or schema.get("category")
        )

    if not dimension:
        return pd.DataFrame()

    data = (
        df.groupby(
            dimension
        )[sales]
        .sum()
        .reset_index()
        .sort_values(
            sales,
            ascending=False
        )
    )

    data = data.rename(
        columns={
            dimension: (
                schema.get(
                    "product_label",
                    "Product"
                )
                if dimension
                == get_product_column(schema)
                else dimension
            ),
            sales: "Sales"
        }
    )

    total = data[
        "Sales"
    ].sum()

    data["Sales %"] = (
        data["Sales"]
        / total
        * 100
        if total
        else 0
    )

    data["Cumulative %"] = (
        data["Sales %"]
        .cumsum()
    )

    data[
        [
            "Sales %",
            "Cumulative %"
        ]
    ] = data[
        [
            "Sales %",
            "Cumulative %"
        ]
    ].round(2)

    return data.reset_index(
        drop=True
    )