#!/bin/bash

# The previous errors indicate a mismatch in the Python environment being used.
# We are now attempting to call the Streamlit executable directly. 
# This relies on the installed package's 'bin' directory being added to the system PATH.
streamlit run streamlit_app.py --server.port 8501 --server.enableCORS false
# streamlit run streamlit_app.py --server.port 8501 --server.enableCORS false --browser.serverAddress localhostb