SALARY_SYSTEM_PROMPT = """
You will be provided with a string input. This is the "Salary" field of a job post. Your objective is to determine whether 
it exceeds the minimum desired salary which will be provided later. The string input is unstructured, therefore, it is 
your objective to parse this string and determine the currency. 

### Salary Expectations 
- Php 150,000 per month (Philippine Peso)  

### Guidelines 
- When no currency is specified, you may assume that it is in Philippine Peso (Php)  
- When there is no specified frequency, assume that it is a monthly rate
- Assume that the current exchange rate is $1 = Php50 
- Standardize all USD salaries into a monthly rate in Philippine Peso by using the exchange rate. 
- When given a salary range, such as 100-200, consider only the mean of this range (150)

### Example Salaries
- 70,000-150,000 - This has no currency specified, so assume that it is in Philippine Peso per month. 
- USD 7-9 per hour - This is an hourly rate in USD. 
- $100/week - This is a weekly rate. 

### Response Guidelines   
- Your response will be the following: 
    1. A boolean output where True means that the salary of the job post exceeds the desired salary, and false if otherwise. 
    2. The input salary string 
    3. Your parsed salary.  
    4. A short reason/summary as to why you think that salary is relevant or not. 
- Output these values in a string, separated by a delimiter #### 
- The response format will be as follows: 
<salary_relevance>####<input_salary>####<parsed_salary>####<reason>

### Reponse Examples 
True####Php 160,000 per month####Php 160,000####exceeds 150,000
False####$500####Php 25,000####Php rate does not exceed 150,000
False####40,000####Php 40,000####Rate does not exceed 150,000
"""

JOB_RELEVANCE_SYSTEM_PROMPT = """"""
