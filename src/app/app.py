import streamlit as st
from src.definitions.enums import Currencies, SalaryFrequency, TypeOfWork
from src.definitions.templates import JobSeeker, JobOpportunity
from src.scraper.olj_scraper import OLJScraper
from typing import List, Optional


class App:
    def __init__(self):
        self.keys = [
            "current_position", "industry", "years_of_experience", "salary", "type_of_work", "profile"
        ]
        self._initialize_app()
        self.reset_job_info()
        self.jobs: Optional[List[JobOpportunity]] = None
        self.loading = False

    @staticmethod
    def _initialize_app():
        st.set_page_config(page_title="hire-me-pls", layout='centered')

    def reset_job_info(self):
        for key in self.keys:
            if key not in st.session_state:
                st.session_state[key] = ""

    @staticmethod
    def _initialize_session_state():
        if "page" not in st.session_state:
            st.session_state.page = "main"

    def job_seeker_information_screen(self):
        st.header("Tell me about yourself")
        st.session_state.current_position = st.text_input("What's your current position?")

        industry_column, yoe_column = st.columns(2)
        st.session_state.industry = industry_column.text_input("What industry are you in?")
        st.session_state.years_of_experience = yoe_column.text_input("How many years of experience do you have?")

        currency, salary, frequency = st.columns([1, 3, 1])
        currency_value = currency.selectbox("Currency", Currencies.currencies())
        salary_value = salary.text_input("What's your expected salary?")
        frequency_value = frequency.selectbox("Frequency", SalaryFrequency.frequencies())
        st.session_state.salary = f'{currency_value} {salary_value} - {frequency_value}'

        st.session_state.type_of_work = st.selectbox("What type of work are you looking for?", TypeOfWork.types())

        st.session_state.profile = st.text_area("Tell me more about yourself!", height=300)
        st.button("Next", on_click=self.submit)

    def validate_inputs(self):
        for key in self.keys:
            if st.session_state[key] == "":
                st.error("Empty fields found.")
                return False
        return True

    def submit(self):
        # if not self.validate_inputs():
        #     return
        job_seeker = JobSeeker(
            current_position=st.session_state.current_position,
            industry=st.session_state.industry,
            years_of_experience=st.session_state.years_of_experience,
            skills=["Python"],
            profile=st.session_state.profile,
            salary_expectation=st.session_state.salary,
            type_of_work=TypeOfWork.work(st.session_state.type_of_work)
        )
        job_seeker = JobSeeker(
            current_position="AI Engineer",
            industry="Software Development",
            years_of_experience="1",
            skills=["Python"],
            profile="I am an experienced AI engineer with a focus on developing and deploying AI solutions to solve a client's business problems.",
            salary_expectation="Php 150,000 / month",
            type_of_work=TypeOfWork.FULL_TIME
        )
        scraper = OLJScraper(job_seeker=job_seeker)
        self.jobs = scraper.start()

    def jobs_screen(self):
        for job in self.jobs:
            with st.expander(job.job_title):
                self.show_project_details(job)

    def show_project_details(self, job: JobOpportunity):
        st.write(f'### {job.job_title}')
        st.write(job.job_description)
        st.write(job.salary)
        st.write(job.type_of_work.value)
        st.write(job.url)

    def loading_screen(self):
        st.write("Loading...")

    def main(self):
        if not self.jobs:
            if self.loading:
                self.loading_screen()
            else:
                self.job_seeker_information_screen()
        else:
            self.jobs_screen()
