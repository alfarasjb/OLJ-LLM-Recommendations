import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime as dt

import requests
from bs4 import BeautifulSoup, PageElement
from tqdm import tqdm

from src.services.chat_model import ChatModel
from src.definitions.templates import JobOpportunity, JobSeeker
from src.definitions.enums import TypeOfWork


class OLJScraper:
    def __init__(self, job_seeker: JobSeeker):
        self.chat_model = ChatModel()
        self.job_seeker = job_seeker
        self.base_url = 'https://www.onlinejobs.ph'
        self.max_pages = 5
        self.max_jobs_to_process = 10
        self.urls_today = self.get_jobs_today()

    @staticmethod
    def counter(page_number: int):
        # Based on OLJ
        return (page_number - 1) * 30

    def start(self):
        jobs = []
        def get_olj_job_recommendation(url: str):
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            overview = self.get_job_overview(soup)
            salary = overview['SALARY']
            type_of_work = TypeOfWork.work(overview['TYPE OF WORK'])

            # is_above_target_salary = self.is_above_target_salary(salary)
            # if not is_above_target_salary:
            #     return None
            job_description = self.get_job_details(soup)
            title = soup.find('h1').get_text(strip=True)
            job_opportunity = JobOpportunity(
                job_title=title,
                job_description=job_description,
                salary=salary,
                type_of_work=type_of_work,
                url=url
            )
            is_relevant = self.is_relevant(job_opportunity)
            if not is_relevant:
                return None
            return job_opportunity

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(get_olj_job_recommendation, url)
                for url in tqdm(self.urls_today[:self.max_jobs_to_process], desc="Getting Job Recommendations")
            ]
            for future in tqdm(futures):
                result = future.result()
                if result:
                    jobs.append(result)
        return jobs

    def is_relevant(self, job_opportunity: JobOpportunity) -> bool:
        # Send this to chat gpt
        return bool(self.chat_model.check_job_relevance(self.job_seeker, job_opportunity))

    def is_above_target_salary(self, salary: str) -> bool:
        # Send this to chatgpt
        # If no currency, assume in Php
        # TODO: Improve prompt
        return bool(self.chat_model.check_salary_relevance(salary))

    def get_jobs_today(self):
        urls = []

        def fetch_urls(page):
            url = self.base_url + f'/jobseekers/search/c/6/{self.counter(page + 1)}'
            return self.get_job_urls_in_page(url)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(fetch_urls, page) for page in tqdm(range(self.max_pages))]
            for future in futures:
                urls += future.result()
        return urls

    def get_job_urls_in_page(self, url: str):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        jobs = soup.find_all('div', class_='jobpost-cat-box latest-job-post card-hover-default')
        urls = []

        def get_url_from_job(job: PageElement):
            date = self.get_date_from_job_post(job)
            if date < dt.now().date():
                return None
            url = self.base_url + f"{job.find('a')['href']}"
            return url

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_url_from_job, job) for job in jobs]
            for future in futures:
                url = future.result()
                if url:
                    urls.append(url)

        return urls

    def get_date_from_job_post(self, job: PageElement):
        date = job.find('em').get_text(strip=True)
        date_match = re.search(r'Posted on (\w+ \d{1,2}, \d{4})', date)
        date = date_match.group(1)
        date = dt.strptime(date, '%b %d, %Y').date()
        return date

    def get_job_details(self, soup: BeautifulSoup):
        job_description = soup.find('p', id='job-description')
        text = job_description.get_text(separator='\n', strip=True)
        return text

    def get_job_overview(self, soup: BeautifulSoup):
        overview_card = soup.find('div', class_='card job-post shadow mb-4 mb-md-0')
        sections = overview_card.find_all('h3')
        mapping = {
            section.get_text(strip=True): section.find_next_sibling().get_text(strip=True)
            for section in sections
        }
        return mapping


if __name__ == "__main__":
    job_seeker = JobSeeker(
        current_position="AI Engineer",
        industry="Software Development",
        years_of_experience="1",
        skills=["Python"],
        profile="I am an experienced AI engineer with a focus on developing and deploying AI solutions to solve a client's business problems.",
        salary_expectation="Php 150,000 / month",
        type_of_work=TypeOfWork.FULL_TIME
    )
    olj = OLJScraper(job_seeker=job_seeker)
    jobs = olj.start()
    print(jobs)
