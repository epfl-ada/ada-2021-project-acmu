import os

import pandas as pd
import streamlit as st

from config import CUSTOM_DATA_DIR


def initialise_app():
    st.title('Political Party Interests with Quotebank')
    st.subheader('Applied Data Analysis Project - Team ACMU')
    st.dataframe(data=pd.read_pickle(os.path.join(CUSTOM_DATA_DIR, 'stats.pkl')))


if __name__ == '__main__':
    print(os.getcwd())
    initialise_app()
