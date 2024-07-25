import logging

import requests.exceptions
import streamlit as st
from streamlit_tags import st_tags

from src.definitions.enums import Currencies, SalaryFrequency, TypeOfWork
from src.definitions.templates import JobSeeker, JobOpportunity
from src.scraper.olj_scraper import OLJScraper
from src.utils.decorators import job_seeker_info

logger = logging.getLogger(__name__)


class JobSeekerForm:
    def __init__(self):

        self.keys = [
            "current_position", "industry", "years_of_experience", "salary_expectation", "type_of_work", "profile", "salary_value"
        ]
        self.reset_job_info()

    def main(self):
        if st.session_state.current_position == "":
            self.current_position_screen()
            return
        elif st.session_state.industry == "":
            self.industry_screen()
            return
        elif st.session_state.years_of_experience == "":
            self.yoe_screen()
            return
        elif st.session_state.salary_value == "" or not st.session_state.salary_complete:
            self.salary_screen()
            return
        elif st.session_state.type_of_work == "" or not st.session_state.type_of_work_complete:
            self.type_of_work_screen()
            return
        elif st.session_state.profile == "":
            self.profile_screen()
            return
        elif len(st.session_state.skills) == 0 or not st.session_state.skills_complete:
            self.skills_screen()
            return
        elif not st.session_state.keywords_complete:
            self.keywords_screen()
            return
        else:
            job_seeker_attributes = {
                key: st.session_state[key]
                for key, _ in JobSeeker.__annotations__.items()
            }
            job_seeker = JobSeeker(**job_seeker_attributes)
            scraper = OLJScraper(job_seeker=job_seeker, search_keywords=st.session_state.keywords)
            with st.spinner("Please wait"):
                try:
                    st.session_state.jobs = scraper.start()
                    self.jobs_screen()
                except requests.exceptions.ConnectionError:
                    st.error("Connection Error. Please try again later.")
                except Exception as e:
                    st.error(f"Something went wrong..")

    """ 
    Screens 
    """
    @job_seeker_info(title="What's your current position?")
    def current_position_screen(self):
        st.session_state.current_position = st.text_input("Current Position")

    @job_seeker_info(title="What industry are you in?")
    def industry_screen(self):
        st.session_state.industry = st.text_input("Industry")

    @job_seeker_info(title="How many years of experience do you have?")
    def yoe_screen(self):
        st.session_state.years_of_experience = st.text_input("Years of Experience")

    @job_seeker_info(title="What's your expected salary?", callback=lambda: setattr(st.session_state, 'salary_complete', True))
    def salary_screen(self):
        currency, salary, frequency = st.columns([1, 3, 1])
        currency_value = currency.selectbox("Currency", Currencies.currencies())
        salary_value = salary.text_input("What's your expected salary?")
        frequency_value = frequency.selectbox("Frequency", SalaryFrequency.frequencies())
        st.session_state.salary_value = salary_value
        st.session_state.salary_expectation = f'{currency_value} {salary_value} - {frequency_value}'

    @job_seeker_info(title="What type of work are you looking for?", callback=lambda: setattr(st.session_state, 'type_of_work_complete', True))
    def type_of_work_screen(self):
        st.session_state.type_of_work = st.selectbox("Type of Work", TypeOfWork.types())

    @job_seeker_info(title="Tell me more about yourself")
    def profile_screen(self):
        st.session_state.profile = st.text_area("Profile", height=300)

    @job_seeker_info(title="What are you good at?", callback=lambda: setattr(st.session_state, 'skills_complete', True))
    def skills_screen(self):
        st.session_state.skills = st_tags(label="Skills", text="")

    @job_seeker_info(title="Anything specific you're looking for?", callback=lambda: setattr(st.session_state, 'keywords_complete', True))
    def keywords_screen(self):
        st.session_state.keywords = st_tags(label="Search Keywords", text="")

    def jobs_screen(self):
        st.title("Jobs")
        st.button("Go Back", on_click=self.clear_jobs)
        for job in st.session_state.jobs:
            with st.expander(job.job_title):
                self.show_project_details(job)

    """
    Helpers
    """
    def reset_job_info(self):
        if "start_search" not in st.session_state:
            st.session_state.start_search = False
        if "skills_complete" not in st.session_state:
            st.session_state.skills_complete = False
        if "keywords_complete" not in st.session_state:
            st.session_state.keywords_complete = False
        if "salary_complete" not in st.session_state:
            st.session_state.salary_complete = False
        if "type_of_work_complete" not in st.session_state:
            st.session_state.type_of_work_complete = False
        if "skills" not in st.session_state:
            st.session_state.skills = []
        if "keywords" not in st.session_state:
            st.session_state.keywords = []

        for key in self.keys:
            if key not in st.session_state:
                st.session_state[key] = ""

    def clear_jobs(self):
        st.session_state.jobs = []
        st.session_state.skills = []
        st.session_state.jobs = []
        for key in self.keys:
            st.session_state[key] = ""

    def show_project_details(self, job: JobOpportunity):
        st.write(f'### {job.job_title}')
        st.write(f"Read more: {job.url}")
        st.write(f"Salary: {job.salary}")
        st.write(f"Type of Work: {job.type_of_work.value}")
