import logging

import streamlit as st

from src.app.job_seeker_form import JobSeekerForm

logger = logging.getLogger(__name__)


class App:
    def __init__(self):
        self.job_seeker_form = JobSeekerForm()
        self.keys = [
            "current_position", "industry", "years_of_experience", "salary", "type_of_work", "profile"
        ]
        self._initialize_session_state()
        self._initialize_app()

    @staticmethod
    def _initialize_app():
        st.set_page_config(page_title="hire-me-pls", layout='centered')

    @staticmethod
    def _initialize_session_state():
        if "page" not in st.session_state:
            st.session_state.page = "main"
        if "loading" not in st.session_state:
            st.session_state.loading = False
        if "jobs" not in st.session_state:
            st.session_state.jobs = []
        if "salary_value" not in st.session_state:
            st.session_state.salary_value = ""

    def validate_inputs(self):
        for key in self.keys:
            if st.session_state[key] == "":
                st.error("Empty fields found.")
                return False
        return True

    def main(self):
        self.job_seeker_form.main()
