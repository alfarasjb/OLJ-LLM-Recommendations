from functools import wraps
from typing import Callable, Optional

import streamlit as st
from tenacity import RetryCallState


def decreasing_wait(retry_state: RetryCallState) -> float:
    initial_wait = 2
    decrease_factor = 0.75

    # Calculate the wait time based on the number of previous attempts
    wait_time = initial_wait * (decrease_factor ** retry_state.attempt_number)
    return wait_time


def job_seeker_info(title: str, callback: Optional[Callable] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            st.title(title)
            func(*args, **kwargs)
            st.button("Next", on_click=callback)
        return wrapper
    return decorator
