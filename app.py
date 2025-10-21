import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

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
        fig, ax = plt.subplots()
        if angle in grouped_left.groups:
            left = grouped_left.get_group(angle)
            ax.plot(range(len(left)), left['left'], label='Left', color='blue')
            std_left = left['left'].std()
        else:
            std_left = 0

        if angle in grouped_right.groups:
            right = grouped_right.get_group(angle)
            ax.plot(range(len(right)), right['right'], label='Right', color='red')
            std_right = right['right'].std()
        else:
            std_right = 0

        ax.set_title(f'Force Over Time at Angle {angle}')
        ax.set_xlabel('Time (row index)')
        ax.set_ylabel('Force')
        ax.legend()
        st.pyplot(fig)

        summary.append((angle, std_left, std_right))

    summary_df = pd.DataFrame(summary, columns=['Angle', 'STD Left', 'STD Right'])
    st.subheader("STD DEV by Angle")
    st.bar_chart(summary_df.set_index('Angle'))

    csv = summary_df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Summary CSV", csv, "summary.csv", "text/csv")