import streamlit as st
import pandas as pd
import plotly.express as px

st.title("LogLens 🔍")

uploaded_file = st.file_uploader("Upload your log", type=["csv", "txt", "log"])

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8").splitlines()
    rows = [line.strip().split(",") for line in content]
    df = pd.DataFrame(rows)

    keyword = st.text_input("📌 Please input keyword")

    if keyword:
        filtered_rows = df[
            df.apply(
                lambda row: row.astype(str)
                .str.contains(keyword, case=False, na=False)
                .any(),
                axis=1,
            )
        ]

        if filtered_rows.empty:
            st.warning("❌ Nothing found ..")
        else:
            key_value_list = []
            for row in filtered_rows.itertuples(index=False):
                if len(row) < 2:
                    continue
                x_val = row[0]
                for item in row[1:]:
                    if isinstance(item, str) and ":" in item:
                        parts = item.split(":")
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            key_value_list.append((x_val, key, value))

            if not key_value_list:
                st.warning("❌ Nothing found..")
            else:
                kv_df = pd.DataFrame(key_value_list, columns=["x", "key", "value"])
                kv_df["value"] = pd.to_numeric(kv_df["value"], errors="coerce")

                unique_keys = kv_df["key"].unique()
                selected_key = st.selectbox("📈 What do you want to see?", unique_keys)

                filtered = kv_df[kv_df["key"] == selected_key].reset_index(drop=True)

                # hovertemplate 작성
                hover_text = (
                    "x: %{customdata[0]}<br>"
                    "key: %{customdata[1]}<br>"
                    "value: %{customdata[2]}"
                )

                fig = px.line(
                    filtered,
                    x="x",
                    y="value",
                    title=f"{value} from {uploaded_file.name}",
                    markers=True,
                )

                fig.update_traces(
                    hovertemplate=hover_text,
                    customdata=filtered[["x", "key", "value"]].values,
                )

                fig.update_xaxes(title_text="")
                fig.update_layout(
                    yaxis_title=f"{selected_key}",
                    title_font_family="Arial",
                    font=dict(family="Arial", size=14),
                )
                st.plotly_chart(fig, use_container_width=True)
