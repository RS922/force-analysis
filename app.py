import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Force Plate Analysis")

st.markdown("""
<style>
section.main > div { max-width: 1000px; margin: auto; }
</style>
""", unsafe_allow_html=True)

# Controls
st.sidebar.header("Display Settings")
chart_height = st.sidebar.slider("Chart Height (px)", min_value=200, max_value=600, value=300, step=50)
sort_order = st.sidebar.selectbox("Sort Angles", options=["Ascending", "Descending"])

left_file = st.file_uploader("Upload Left Leg CSV", type="csv")
right_file = st.file_uploader("Upload Right Leg CSV", type="csv")

if left_file and right_file:
    try:
        df_left = pd.read_csv(left_file)
        df_right = pd.read_csv(right_file)
    except Exception as e:
        st.error(f"Error reading files: {e}")
        st.stop()

    grouped_left = df_left.groupby('angle')
    grouped_right = df_right.groupby('angle')

    summary = []

    angles = sorted(set(grouped_left.groups.keys()).union(grouped_right.groups.keys()), reverse=(sort_order == "Descending"))

    for angle in angles:
        left = grouped_left.get_group(angle) if angle in grouped_left.groups else pd.DataFrame(columns=['left'])
        right = grouped_right.get_group(angle) if angle in grouped_right.groups else pd.DataFrame(columns=['right'])

        std_left = left['left'].std() if not left.empty else 0
        std_right = right['right'].std() if not right.empty else 0
        summary.append((angle, std_left, std_right))

        st.subheader(f"Force Over Time at Angle {angle}")

        max_len = max(len(left), len(right))
        time_axis = [round(i * 0.1, 1) for i in range(max_len)]

        chart_data = pd.DataFrame({
            'Time (s)': time_axis,
            'Left': left['left'].reset_index(drop=True).reindex(range(max_len)),
            'Right': right['right'].reset_index(drop=True).reindex(range(max_len))
        }).set_index('Time (s)')

        st.line_chart(chart_data, height=chart_height)

        if not left.empty:
            bp_left = round(left['left'].idxmin() * 0.1, 1)
            st.caption(f"Left leg breakpoint at {bp_left}s")
        if not right.empty:
            bp_right = round(right['right'].idxmin() * 0.1, 1)
            st.caption(f"Right leg breakpoint at {bp_right}s")

    summary_df = pd.DataFrame(summary, columns=['Angle', 'STD Left', 'STD Right'])
    st.subheader("STD DEV by Angle")
    st.bar_chart(summary_df.set_index('Angle'), height=chart_height)

    csv = summary_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Summary CSV", csv, "summary.csv", "text/csv")

    st.markdown("""
    ---
    **To print this page:**  
    Use your browser’s print feature (Ctrl+P or Cmd+P) to save or print the full analysis.
    """)
