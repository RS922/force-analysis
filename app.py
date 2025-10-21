import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Force Plate Analysis")

left_file = st.file_uploader("Upload Left Leg CSV", type="csv")
right_file = st.file_uploader("Upload Right Leg CSV", type="csv")

if left_file and right_file:
    df_left = pd.read_csv(left_file)
    df_right = pd.read_csv(right_file)

    grouped_left = df_left.groupby('angle')
    grouped_right = df_right.groupby('angle')

    summary = []

    for angle in sorted(set(grouped_left.groups.keys()).union(grouped_right.groups.keys())):
        left = grouped_left.get_group(angle) if angle in grouped_left.groups else pd.DataFrame(columns=['left'])
        right = grouped_right.get_group(angle) if angle in grouped_right.groups else pd.DataFrame(columns=['right'])

        std_left = left['left'].std() if not left.empty else 0
        std_right = right['right'].std() if not right.empty else 0
        summary.append((angle, std_left, std_right))

        st.subheader(f"Force Over Time at Angle {angle}")
        # Create time axis in seconds (0.1s per row)
        max_len = max(len(left), len(right))
        time_axis = [round(i * 0.1, 1) for i in range(max_len)]

        chart_data = pd.DataFrame({
            'Time (s)': time_axis,
            'Left': left['left'].reset_index(drop=True).reindex(range(max_len)),
            'Right': right['right'].reset_index(drop=True).reindex(range(max_len))
        })

chart_data = chart_data.set_index('Time (s)')
st.line_chart(chart_data)

    summary_df = pd.DataFrame(summary, columns=['Angle', 'STD Left', 'STD Right'])
    st.subheader("STD DEV by Angle")
    st.bar_chart(summary_df.set_index('Angle'))

    csv = summary_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Summary CSV", csv, "summary.csv", "text/csv")

