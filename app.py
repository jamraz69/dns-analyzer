
import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

st.set_page_config(page_title="DNS Stability Analyzer", layout="wide")

st.title("DNS Stability Analyzer")

uploaded_file = st.file_uploader(
    "Upload DNS Assay Image",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:

    img = Image.open(uploaded_file).convert("L")
    img_rgb = Image.open(uploaded_file).convert("RGB")

    width, height = img.size

    st.image(img_rgb, caption="Uploaded Image", use_container_width=True)

    st.subheader("Tube Coordinates")

    col1, col2 = st.columns(2)

    with col1:
        blank_x = st.number_input(
            "Blank X",
            min_value=0,
            max_value=width,
            value=min(150, width)
        )

        blank_y = st.number_input(
            "Blank Y",
            min_value=0,
            max_value=height,
            value=min(300, height)
        )

        c4_x = st.number_input(
            "4°C Sample X",
            min_value=0,
            max_value=width,
            value=min(300, width)
        )

        c4_y = st.number_input(
            "4°C Sample Y",
            min_value=0,
            max_value=height,
            value=min(300, height)
        )

    with col2:
        c25_x = st.number_input(
            "25°C Sample X",
            min_value=0,
            max_value=width,
            value=min(450, width)
        )

        c25_y = st.number_input(
            "25°C Sample Y",
            min_value=0,
            max_value=height,
            value=min(300, height)
        )

        c37_x = st.number_input(
            "37°C Sample X",
            min_value=0,
            max_value=width,
            value=min(600, width)
        )

        c37_y = st.number_input(
            "37°C Sample Y",
            min_value=0,
            max_value=height,
            value=min(300, height)
        )

    radius = st.slider(
        "Circle Radius",
        min_value=5,
        max_value=100,
        value=40
    )

    if st.button("Analyze"):

        gray = np.array(img)

        tube_coordinates = {
            "Blank": {
                "x": blank_x,
                "y": blank_y
            },
            "4C_Sample": {
                "x": c4_x,
                "y": c4_y
            },
            "25C_Sample": {
                "x": c25_x,
                "y": c25_y
            },
            "37C_Sample": {
                "x": c37_x,
                "y": c37_y
            }
        }

        raw_means = {}

        y_grid, x_grid = np.ogrid[:height, :width]

        for tube_name, placement in tube_coordinates.items():

            x = placement["x"]
            y = placement["y"]

            mask = (
                (x_grid - x) ** 2 +
                (y_grid - y) ** 2
            ) <= radius ** 2

            mean_val = gray[mask].mean()

            raw_means[tube_name] = round(
                float(mean_val),
                3
            )

        active_reference = raw_means["37C_Sample"]

        blank_background = 220.0

        net_color_0 = (
            blank_background -
            active_reference
        )

        results = []

        for sample_name in [
            "4C_Sample",
            "25C_Sample",
            "37C_Sample"
        ]:

            net_color_t = (
                blank_background -
                raw_means[sample_name]
            )

            remaining_activity = (
                net_color_t /
                net_color_0
            ) * 100

            degradation = (
                100 -
                remaining_activity
            )

            results.append({
                "Sample ID":
                    sample_name,

                "Raw Mean Gray Value":
                    raw_means[sample_name],

                "Net Color Index":
                    round(net_color_t, 3),

                "Remaining Activity (%)":
                    round(
                        remaining_activity,
                        2
                    ),

                "Total Degradation (%)":
                    round(
                        max(0, degradation),
                        2
                    )
            })

        df = pd.DataFrame(results)

        st.subheader("Results")

        st.dataframe(
            df,
            use_container_width=True
        )

        preview = img_rgb.copy()

        draw = ImageDraw.Draw(preview)

        for tube in tube_coordinates.values():

            x = tube["x"]
            y = tube["y"]

            draw.ellipse(
                (
                    x - radius,
                    y - radius,
                    x + radius,
                    y + radius
                ),
                outline="red",
                width=3
            )

        st.subheader("Selected Regions")

        st.image(
            preview,
            use_container_width=True
        )

        csv = df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="stability_report.csv",
            mime="text/csv"
        )
