import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport


logging.basicConfig()

# British Gas account login page
LOGIN_PAGE_URL = "https://www.britishgas.co.uk/identity/"

# My Energy overview page
# MYENERGY_PAGE_URL = 'https://www.britishgas.co.uk/apps/britishgas/components/PEEAEnergyUsage/GET.servlet'
MYENERGY_PAGE_URL = "https://www.britishgas.co.uk/smartreport?accounts={account_id}"

# URL to GraphQL server for energy data
MYENERGY_GRAPHQL_URL = "https://www.britishgas.co.uk/myenergy_prod/me-api/graphql"

# GraphQL request time out (seconds)
TIMEOUT_S = 20


def daily_history_query(first_datetime, last_datetime):
    """Build the GraqhQL query to retrieve  daily data between two dates.
    Args:
        first_datetime (datetime.datetime): beginning of data series
        last_datetime (datetime.datetime): end of date series
    Returns: (dict)
    """
    day_range = 'from:"{0:s}.000Z", to:"{1:s}.999Z"'.format(
        first_datetime.isoformat(), last_datetime.isoformat()
    )

    # The "half_hourly" granularity is not visible yet.
    return gql(
        """query DetailedHistory {
        consumptionRange(granularity:daily, %s) {
            from
            partial
            estimated {
                cost
                energy
            }
            empty
            zoomable
            tou
            cost(costUnit:pounds)
            energy(energyUnit:kwh)
            fuel
            daysWithData
        }
    }"""
        % day_range
    )


def login(username, password):
    
    driver = webdriver.Firefox()
    driver.get(LOGIN_PAGE_URL)
    try:
        WebDriverWait(driver, TIMEOUT_S).until(EC.presence_of_element_located((By.ID, "loginForm-email")))
    except TimeoutException:
        logging.warning("Timeout for page to load")

    driver.find_element(By.ID, "loginForm-email").click()
    driver.find_element(By.ID, "loginForm-email").send_keys(username)
    driver.find_element(By.ID, "loginForm-next").click()
    try:
        WebDriverWait(driver, TIMEOUT_S).until(EC.presence_of_element_located((By.ID, "loginForm-password")))
    except TimeoutException:
        logging.warning("Timeout for page to load")
    driver.find_element(By.ID, "loginForm-password").click()
    driver.find_element(By.ID, "loginForm-password").send_keys(password)
    driver.find_element(By.ID, "loginForm-submit").click()
    
    try:
        WebDriverWait(driver, TIMEOUT_S).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".account-number")))
    except TimeoutException:
        logging.warning("Timeout for page to load")

    account_id = driver.find_element(By.CSS_SELECTOR, ".account-number").text
    
    driver.get(MYENERGY_PAGE_URL.format(account_id=account_id))
    sleep(10)
    graphql_token = driver.execute_script(
        "return window.localStorage.getItem('myenergy.token');"
    ).strip('"')

    sleep(5)
    driver.close()
    return graphql_token


def get_graphql_client(graphql_token):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
        "Authorization": graphql_token,
    }
    return Client(
        transport=RequestsHTTPTransport(
            url=MYENERGY_GRAPHQL_URL, headers=headers, timeout=TIMEOUT_S
        ),
        # fetch_schema_from_transport=True,
    )
