"""
Resume_bombarder
"""

import os
import time
import json
from enum import Enum
from typing import Any, Callable, Tuple, Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
)

from config import settings
from config import dict_of_resumes as dict_resume


class Status(Enum):
    """
    Status of job application

    ==============  ======================
    SUCCESS         Job was applied
    FAILURE         Job was not applied
    ==============  ======================

    """

    SUCCESS = 0
    FAILURE = 1


os.system("cls")


def read_text_file(relative_path, file_name, encoding="utf-8"):
    """
    Reads the contents of a text file.

    Args:
        relative_path (str): The relative path of the file.
        file_name (str): The name of the file.
        encoding (str, optional): The encoding of the file. Defaults to "utf-8".

    Returns:
        str: The contents of the file.
    """
    file_path = os.path.join(relative_path, file_name)
    with open(file_path, "r", encoding=encoding) as f:
        return f.read()


MESSAGE = read_text_file("resources", "cover-letter-ru.txt", encoding="utf-8")
ANSWER = read_text_file("resources", "links-list.txt", encoding="utf-8")
USER_AGENT = settings.USER_AGENT
COOKIES_PATH = settings.COOKIES_PATH
LOCAL_STORAGE_PATH = settings.LOCAL_STORAGE_PATH
USER_AGENT = settings.USER_AGENT
USERNAME = settings.USERNAME
PASSWORD = settings.PASSWORD
LOGIN_PAGE = settings.LOGIN_PAGE
JOB_SEARCH_QUERY = settings.JOB_SEARCH_QUERY
EXCLUDE = settings.EXCLUDE
REGION = settings.REGION
SEARCH_LINK = settings.SEARCH_LINK
MIN_SALARY = settings.MIN_SALARY
ONLY_WITH_SALARY = settings.ONLY_WITH_SALARY
ADVANCED_SEARCH_URL_QUERY = getattr(settings, "ADVANCED_SEARCH_URL_QUERY", "")

# options = webdriver.EdgeOptions()

options = webdriver.ChromeOptions()
options.use_chromium = True
options.add_argument("start-maximized")
options.page_load_strategy = "eager"
options.add_argument(f"user-agent={USER_AGENT}")
options.add_experimental_option("detach", True)
# options = webdriver.EdgeOptions()
options = webdriver.ChromeOptions()
options.use_chromium = True
options.add_argument("start-maximized")
options.page_load_strategy = "eager"  # do not wait for images to load
options.add_argument(f"user-agent={USER_AGENT}")
options.add_experimental_option("detach", True)
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-certificate-errors-spki-list")
options.add_argument("--ignore-ssl-errors")
options.add_argument("log-level=3")
# s = 10
COUNTER = 0

# driver = webdriver.Edge(options=options)
DRIVER = webdriver.Chrome(options=options)
ACTION = ActionChains(DRIVER)
WAIT = WebDriverWait(DRIVER, 10)


def custom_wait(driver, timeout, condition_type, locator_tuple):
    """
    A function that performs a custom wait for a certain condition on a web element using Selenium WebDriver.

    :param driver: The WebDriver instance to use for waiting.
    :param timeout: The maximum time to wait for a condition to be true.
    :param condition_type: The type of condition to wait for (e.g., presence_of_element_located, visibility_of_element_located, etc.).
    :param locator_tuple: The tuple containing the locator strategy and locator value of the web element.

    :return: The web element once the condition is met.
    """
    wait = WebDriverWait(driver, timeout)
    return wait.until(condition_type(locator_tuple))


def eternal_wait(
    driver,
    timeout: int,
    condition_type: Callable[[Any], bool],
    locator_tuple: Tuple[str, str],
) -> Any:
    """
    Waits for an element to satisfy a condition until timeout is reached.
    :param driver: The WebDriver instance to use for waiting.
    :param timeout: The maximum time to wait for a condition to be true.
    :param condition_type: The type of condition to wait for (e.g., presence_of_element_located, visibility_of_element_located, etc.).
    :param locator_tuple: The tuple containing the locator strategy and locator value of the web element.
    :return: The web element once the condition is met.
    """
    while True:
        try:
            element = WebDriverWait(driver, timeout).until(
                condition_type(locator_tuple)
            )
            return element
        except TimeoutException:
            print(
                f"\n\nWaiting for the element(s) {locator_tuple} to become {condition_type}…"
            )
            time.sleep(0.5)
            continue


def load_data_from_json(path):
    """
    Load data from a JSON file.

    Args:
        path (str): The path to the JSON file.

    Returns:
        dict: The data loaded from the JSON file.
    """
    return json.load(open(path, "r", encoding="utf-8"))


def save_data_to_json(data, path):
    """
    Save data to a JSON file.

    Args:
        data: The data to be saved to the JSON file.
        path: The path to the JSON file.

    Returns:
        None
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data, open(path, "w", encoding="utf-8"))


def add_cookies(cookies: List[Dict], driver: webdriver):
    """
    Add cookies to the webdriver.

    :param cookies: A list of dictionaries representing the cookies to be added.
    :param driver: The webdriver to which the cookies will be added.
    :return: None
    """
    for cookie in cookies:
        driver.add_cookie(cookie)


def add_local_storage(local_storage: Dict[str, str], driver: webdriver):
    """
    Add items from the provided local_storage dictionary to the window.localStorage of the webdriver.

    :param local_storage: A dictionary containing keys and values to be added to the window.localStorage
    :param driver: The webdriver instance to execute the script on
    :return: None
    """
    keys = list(local_storage.keys())
    values = list(local_storage.values())
    for key, value in zip(keys, values):
        driver.execute_script(
            f"window.localStorage.setItem({json.dumps(key)}, {json.dumps(value)});"
        )


def get_first_folder(
    path: str,
) -> str:
    """
    Return the first folder in the given path.

    Args:
        path: The path to be parsed.

    Returns:
        str: The first folder in the given path.
    """
    return os.path.normpath(path).split(os.sep)[0]


def delete_folder(folder_path: str) -> None:
    """
    Deletes a folder and all its contents recursively.

    Parameters:
    - folder_path: str, the path to the folder to be deleted.

    Returns:
    - None
    """
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path: str = os.path.join(folder_path, filename)
            if os.path.isdir(file_path):
                delete_folder(file_path)
            else:
                os.remove(file_path)
        os.rmdir(folder_path)


def success(driver: webdriver) -> bool:
    """
    Checks if the user is logged in successfully.

    Parameters:
    - driver: WebDriver, the driver.

    Returns:
    - bool: True if the user is logged in successfully, False otherwise.
    """
    try:
        custom_wait(
            driver,
            10,
            EC.presence_of_element_located,
            (By.XPATH, '//a[@data-qa="mainmenu_myResumes"]'),
        )
        return True
    except NoSuchElementException:
        return False


def navigate_and_check(probe_page: str, driver: webdriver) -> bool:
    """
    Navigates to a given web page using the provided webdriver and checks for success.
    :param probe_page: the URL of the page to navigate to
    :param driver: the webdriver to use for navigation
    :return: True if the navigation and check is successful, False otherwise
    """
    driver.get(probe_page)
    time.sleep(5)
    if success(driver):
        save_data_to_json(driver.get_cookies(), COOKIES_PATH)
        save_data_to_json(
            {
                key: driver.execute_script(
                    f"return window.localStorage.getItem('{key}');"
                )
                for key in driver.execute_script(
                    "return Object.keys(window.localStorage);"
                )
            },
            LOCAL_STORAGE_PATH,
        )
        return True
    else:
        return False


def login(login_page: str, driver: webdriver, username: str, password: str) -> None:
    """
    Logs into the given login page using the provided driver, username, and password.

    Args:
        login_page (str): The URL of the login page.
        driver (webdriver): The Selenium webdriver object.
        username (str): The username for logging in.
        password (str): The password for logging in.

    Returns:
        None
    """
    driver.get(login_page)

    show_more_button: WebElement = eternal_wait(
        driver,
        10,
        EC.element_to_be_clickable,
        (By.XPATH, '//button[@data-qa="expand-login-by-password"]'),
    )
    ACTION.click(show_more_button).perform()

    login_field: WebElement = eternal_wait(
        driver,
        10,
        EC.element_to_be_clickable,
        (By.XPATH, '//input[@data-qa="login-input-username"]'),
    )
    password_field: WebElement = eternal_wait(
        driver, 10, EC.element_to_be_clickable, (By.XPATH, '//input[@type="password"]')
    )

    login_field.send_keys(username)
    password_field.send_keys(password)

    login_button: WebElement = eternal_wait(
        driver,
        10,
        EC.element_to_be_clickable,
        (By.XPATH, "//button[@data-qa='account-login-submit']"),
    )
    click_and_wait(login_button, 5)


def check_cookies_and_login(
    driver: webdriver,
    login_page: str,
    cookies_path: str,
    local_storage_path: str,
    search_link: str,
    username: str,
    password: str,
) -> None:
    """
    Check cookies and login using the provided WebDriver, login page URL, cookies path, local storage path, search link, username, and password.
    """
    driver.get(login_page)

    if os.path.exists(cookies_path) and os.path.exists(local_storage_path):
        add_cookies(load_data_from_json(cookies_path), driver)
        add_local_storage(load_data_from_json(local_storage_path), driver)

        if navigate_and_check(search_link, driver):
            return
        else:
            delete_folder(get_first_folder(cookies_path))

    login(login_page, driver, username, password)
    navigate_and_check(search_link, driver)


def scroll_to_bottom(driver: webdriver, delay: float = 2.0) -> None:
    """Scrolls the page down until it reaches the bottom."""
    last_height: int = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        time.sleep(delay)
        new_height: int = driver.execute_script("return document.body.scrollHeight")
        if last_height == new_height:
            break
        last_height = new_height


def click_and_wait(element: WebElement, delay: float = 1.0) -> None:
    """
    Clicks the given WebElement and waits for the given delay.

    Args:
        element: The WebElement to be clicked.
        delay: The delay in seconds.

    Returns:
        None
    """
    ACTION.move_to_element(element).click().perform()
    time.sleep(delay)


def js_click(driver: webdriver, element: WebElement) -> None:
    """
    Clicks the given WebElement using JavaScript.

    Args:
        driver: The Selenium WebDriver object.
        element: The WebElement to be clicked.

    Returns:
        None
    """
    try:
        if element.is_displayed() and element.is_enabled():
            driver.execute_script(
                """
                arguments[0].scrollIntoView();
                var event = new MouseEvent('click', {
                    view: window,
                    bubbles: true,
                    cancelable: true
                });
                arguments[0].dispatchEvent(event);
                """,
                element,
            )
        else:
            print("Element is not visible or not enabled for clicking.")
    except ElementNotInteractableException as e:
        print(f"An error occurred: {e}")


def select_all_countries(
    driver: webdriver,
) -> None:
    """
    Selects all countries using the provided webdriver.

    Args:
        driver (webdriver): The webdriver to use for selecting the countries.

    Returns:
        None
    """
    region_select_button: WebElement = WAIT.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//button[@data-qa="advanced-search-region-selectFromList"]')
        )
    )
    region_select_button.click()
    countries: List[WebElement] = driver.find_elements(
        By.XPATH, '//input[@name="bloko-tree-selector-default-name-0"]'
    )
    for country in countries:
        country.click()
    region_submit_button: WebElement = WAIT.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//button[@data-qa="bloko-tree-selector-popup-submit"]')
        )
    )
    region_submit_button.click()


def international_ok(
    driver: webdriver,
) -> None:
    """
    Clicks the international relocation confirmation button if it's present.

    Returns:
        None
    """
    try:
        international: WebElement = WAIT.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[@data-qa="relocation-warning-confirm"]')
            )
        )
        international.click()
    except TimeoutException:
        pass
    driver.refresh()


def check_cover_letter_popup(
    message: str,
    driver: webdriver,
) -> str:
    """Check the cover letter popup and submit a message.

    Args:
        message (str): The cover letter message to be submitted.
        WAIT (WebDriverWait): The WebDriverWait instance for waiting for elements.

    Returns:
        str: The status of the cover letter submission, either 'SUCCESS' or 'FAILURE'.
    """
    global COUNTER
    try:
        cover_letter_popup = WAIT.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//textarea[@data-qa="vacancy-response-popup-form-letter-input"]',
                )
            )
        )
        set_value_with_event(cover_letter_popup, message, driver)

        ACTION.click(
            WAIT.until(
                EC.element_to_be_clickable(
                    (By.XPATH, '//button[@data-qa="vacancy-response-submit-popup"]')
                )
            )
        ).perform()

        popup_cover_letter_submit_button = WAIT.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[@data-qa="vacancy-response-submit-popup"]')
            )
        )
        driver.execute_script("arguments[0].click()", popup_cover_letter_submit_button)
        time.sleep(3)
        try:
            error = WAIT.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="bloko-translate-guard"]')
                )
            )
            if error:
                return Status.SUCCESS
        except Exception:
            pass
        WAIT.until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="vacancy-actions_responded"]')
            )
        )
        COUNTER += 1
        return Status.SUCCESS
    except Exception:
        return Status.FAILURE


def set_value_with_event(element: WebElement, value: str, driver: webdriver):
    """
    Sets the value of a web element and triggers an input event.

    Args:
        element (WebElement): The web element to set the value for.
        value (str): The value to set.
        driver (webdriver): The webdriver instance to execute the script.

    Returns:
        None
    """
    ACTION.move_to_element(element).click().perform()
    driver.execute_script("arguments[0].value = '';", element)
    driver.execute_script(
        """
    var setValue = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set;
    var element = arguments[0];
    var value = arguments[1];
    
    setValue.call(element, value);
    
    var event = new Event('input', { bubbles: true });
    element.dispatchEvent(event);
    """,
        element,
        value,
    )


def answer_questions(
    driver: webdriver,
    wait: WebDriverWait,
) -> str:
    """
    Scrolls through the questions, answers them, and submits the response.

    Args:
    - driver: The WebDriver instance for interacting with the browser.
    - WAIT: The WebDriverWait instance for waiting for elements to be located.
    - ACTION: The ActionChains instance for performing browser actions.
    - ANSWER: The string representing the answer to the questions.
    - COUNTER: The integer representing the count of questions answered.

    Returns:
    - str: The status of the response, either 'SUCCESS' or 'FAILURE'.
    """
    global COUNTER
    try:
        ul_containers = driver.find_elements(By.XPATH, '//div[@data-qa="task-body"]/ul')
        for ul in ul_containers:
            input_elements = ul.find_elements(
                By.XPATH, './/input[@type="radio" or @type="checkbox"]'
            )
            if input_elements:
                driver.execute_script(
                    "arguments[0].scrollIntoView(); arguments[0].click();",
                    input_elements[-1],
                )
    except Exception:
        pass
    try:
        test_questions_presence = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@data-qa="task-body"]//textarea')
            )
        )
        if test_questions_presence:
            try:
                questions = driver.find_elements(
                    By.XPATH, '//div[@data-qa="task-body"]//textarea'
                )
                for question in questions:
                    set_value_with_event(question, ANSWER, driver)

                submit_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, '//button[@data-qa="vacancy-response-submit-popup"]')
                    )
                )
                driver.execute_script(
                    "arguments[0].removeAttribute('disabled')", submit_button
                )
                ACTION.click(submit_button).perform()
                time.sleep(3)
                try:
                    error = wait.until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//div[@class="bloko-translate-guard"]')
                        )
                    )
                    if error:
                        return Status.SUCCESS
                except Exception:
                    pass
                wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//div[@class="vacancy-actions_responded"]')
                    )
                )
                COUNTER += 1
                return Status.SUCCESS
            except Exception:
                return Status.FAILURE
    except Exception:
        return Status.FAILURE


def fill_in_cover_letter(
    message: str,
    driver: webdriver,
    wait: WebDriverWait,
) -> str:
    """
    Fill in a cover letter in a web form using the provided message and web driver.

    Args:
        message (str): The cover letter message to be filled in.
        driver (webdriver): The web driver used to interact with the web form.
        wait (WebDriverWait): The wait object for waiting for elements to be interactable.

    Returns:
        str: The status of the cover letter filling process, either 'SUCCESS' or 'FAILURE'.
    """
    global COUNTER
    scroll_to_bottom(driver)
    try:
        cover_letter_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[@data-qa="vacancy-response-letter-toggle"]')
            )
        )
        driver.execute_script("arguments[0].click()", cover_letter_button)

        cover_letter_text = wait.until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//form[@action="/applicant/vacancy_response/edit_ajax"]/textarea',
                )
            )
        )
        set_value_with_event(cover_letter_text, message, driver)

        submit_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, '//button[@data-qa="vacancy-response-letter-submit"]')
            )
        )
        driver.execute_script(
            "arguments[0].scrollIntoView(); arguments[0].click()", submit_button
        )
        time.sleep(1)
        try:
            error = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//div[@class="bloko-translate-guard"]')
                )
            )
            if error:
                return Status.SUCCESS
        except Exception:
            pass
        wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@data-qa="vacancy-response-letter-informer"]')
            )
        )
        COUNTER += 1
        return Status.SUCCESS
    except Exception:
        return Status.FAILURE


def choose_resume(
    job_title: str,
    driver: webdriver,
) -> None:
    """
    A function to choose a resume based on the job title using a webdriver.

    Args:
        job_title (str): The job title to match with the resume.
        driver (webdriver): The webdriver to interact with the web page.

    Returns:
        None
    """
    try:
        default_button = driver.find_element(
            By.XPATH,
            f"//input[@id='{dict_resume.RESUME_CODES[f'{dict_resume.DEFAULT_RESUME}']}']",
        )
        driver.execute_script(
            "arguments[0].scrollIntoView();  arguments[0].click();", default_button
        )

        for resume, code in dict_resume.RESUME_CODES.items():
            resume_button = driver.find_element(By.XPATH, f"//input[@id='{code}']")
            driver.execute_script(
                "arguments[0].scrollIntoView(); arguments[0].click();", resume_button
            )
            if resume.lower() in job_title.lower():
                break
    except NoSuchElementException as e:
        print(f"Failed to choose resume: Element not found {e}")
        print("\n")


def click_all_jobs_on_the_page(
    driver: webdriver,
    wait: WebDriverWait,
) -> None:
    global COUNTER
    scroll_to_bottom(driver)
    vacancy_info: Dict[str, Optional[str]] = {}
    vacancy_elements = driver.find_elements(
        By.XPATH,
        '//div[@class="vacancy-serp-item__layout"]',
    )
    for element in vacancy_elements:
        try:
            element.find_element(
                By.XPATH,
                './/a[@class="bloko-button bloko-button_kind-success bloko-button_scale-small"]',
            )
        except NoSuchElementException:
            continue

        title = element.find_element(
            By.XPATH, './/span[@data-qa="serp-item__title"]'
        ).text
        apply_link = None
        try:
            link_element = element.find_element(By.XPATH, './/a[@class="bloko-link"]')

            apply_link = link_element.get_attribute("href")
            vacancy_info[title] = apply_link
        except Exception:
            print("Apply link not found for:", title)
            vacancy_info[title] = None

        vacancy_info[title] = apply_link

    eternal_wait(
        driver,
        10,
        EC.presence_of_element_located,
        (By.XPATH, '//div[@data-qa="vacancies-search-header"]'),
    )

    for title, apply_link in vacancy_info.items():
        print(f"********************{title}********************")
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(3)
        driver.get(apply_link)
        time.sleep(3)

        try:
            company_name = custom_wait(
                driver,
                10,
                EC.presence_of_element_located,
                (By.XPATH, '//a[@data-qa="vacancy-company-name"]'),
            ).text
        except Exception:
            pass
        try:
            vacancy_title = custom_wait(
                driver,
                10,
                EC.presence_of_element_located,
                (By.XPATH, '//h1[@data-qa="vacancy-title"]'),
            ).text
        except Exception:
            pass
        if company_name and vacancy_title:
            customized_message = f"Здравствуйте, уважаемый рекрутер {company_name}!\nПрошу рассмотреть мою кандидатуру на вакансию «{vacancy_title}».\n\n{MESSAGE}"
        elif company_name:
            customized_message = (
                f"Здравствуйте, уважаемый рекрутер {company_name}!\n\n{MESSAGE}"
            )
        elif vacancy_title:
            customized_message = f"Здравствуйте, уважаемый рекрутер!\nПрошу рассмотреть мою кандидатуру на вакансию «{vacancy_title}».\n\n{MESSAGE}"
        else:
            customized_message = MESSAGE

        try:
            job_l = driver.find_element(
                By.XPATH,
                './/a[@class="bloko-button bloko-button_kind-success bloko-button_scale-large bloko-button_stretched"]',
            )
            driver.get(job_l.get_attribute("href"))
        except Exception:
            return Status.FAILURE

        time.sleep(1)
        international_ok(driver)
        choose_resume(title, driver)
        if fill_in_cover_letter(customized_message, driver, wait) == Status.SUCCESS:
            driver.close()
            time.sleep(1)
            driver.switch_to.window(driver.window_handles[0])
            print("Успешно!\n")
        elif check_cover_letter_popup(customized_message, driver) == Status.SUCCESS:
            driver.close()
            time.sleep(1)
            driver.switch_to.window(driver.window_handles[0])
            print("Успешно!\n")
        else:
            try:
                answer_questions(driver, wait)
                driver.close()
                time.sleep(1)
                driver.switch_to.window(driver.window_handles[0])
            except Exception:
                driver.close()
                time.sleep(1)
                driver.switch_to.window(driver.window_handles[0])
                print("Не удалось отправить резюме!\n")
                continue


def clear_region(
    driver: webdriver,
) -> None:
    """
    Clears the region by clicking on all the 'bloko-tag__cross' buttons within a custom wait of 10 seconds.

    Args:
        driver (webdriver): The WebDriver instance to use

    Returns:
        None
    """
    try:
        clear_region_buttons = custom_wait(
            driver,
            10,
            EC.presence_of_all_elements_located,
            (By.XPATH, '//button[@data-qa="bloko-tag__cross"]'),
        )
        for button in clear_region_buttons:
            js_click(driver, button)
    except Exception:
        return


def advanced_search(
    driver: webdriver,
) -> None:
    """
    Perform an advanced search using the given webdriver.

    Args:
        driver (webdriver): The webdriver to use for the advanced search.

    Returns:
        None
    """
    advanced_search_button = eternal_wait(
        driver,
        10,
        EC.element_to_be_clickable,
        (By.XPATH, '//a[@data-qa="advanced-search"]'),
    )

    js_click(driver, advanced_search_button)
    advanced_search_textarea = eternal_wait(
        driver,
        10,
        EC.element_to_be_clickable,
        (By.XPATH, '//input[@data-qa="vacancysearch__keywords-input"]'),
    )
    advanced_search_textarea.send_keys(JOB_SEARCH_QUERY)
    advanced_search_textarea.send_keys(Keys.TAB)

    if REGION == "global":
        clear_region(driver)

    try:
        exclude_these_results = custom_wait(
            driver,
            10,
            EC.element_to_be_clickable,
            (By.XPATH, '//input[@name="excluded_text"]'),
        )
        exclude_these_results.send_keys(EXCLUDE)
    except Exception:
        pass

    try:
        no_agency = custom_wait(
            driver,
            5,
            EC.element_to_be_clickable,
            (
                By.XPATH,
                '//input[@data-qa="advanced-search__label-item-label_not_from_agency"]',
            ),
        )
        js_click(driver, no_agency)
    except Exception:
        pass

    salary = custom_wait(
        driver,
        10,
        EC.element_to_be_clickable,
        (By.XPATH, '//input[@data-qa="advanced-search-salary"]'),
    )
    salary.send_keys(MIN_SALARY)

    if ONLY_WITH_SALARY:
        salary_only_checkbox = custom_wait(
            driver,
            10,
            EC.element_to_be_clickable,
            (By.XPATH, '//input[@name="only_with_salary"]'),
        )
        js_click(driver, salary_only_checkbox)

    quantity = driver.find_element(
        By.XPATH, '//input[@data-qa="advanced-search__items_on_page-item_100"]'
    )
    js_click(driver, quantity)

    advanced_search_submit_button = WAIT.until(
        EC.element_to_be_clickable(
            (By.XPATH, '//button[@data-qa="advanced-search-submit-button"]')
        )
    )
    js_click(driver, advanced_search_submit_button)


def main():
    global COUNTER

    check_cookies_and_login(
        DRIVER,
        LOGIN_PAGE,
        COOKIES_PATH,
        LOCAL_STORAGE_PATH,
        SEARCH_LINK,
        USERNAME,
        PASSWORD,
    )

    if ADVANCED_SEARCH_URL_QUERY:
        DRIVER.get(ADVANCED_SEARCH_URL_QUERY)
    else:
        advanced_search(DRIVER)

    while COUNTER < 200:
        if click_all_jobs_on_the_page(DRIVER, WAIT) == Status.FAILURE:
            os.system("cls")
            print(
                "It's either the hh.ru server has become undresponsive or all the links within the current search query have been clicked. \n 1) check if hh.ru is alive and responsive \n 2) check if you have clicked all the links available for the job search query. In that case, change the 'JOB_SEARCH_QUERY = ' value. \n \n Sincerely Yours, \n NAKIGOE.ORG\n"
            )
            DRIVER.close()
            DRIVER.quit()

        DRIVER.switch_to.window(DRIVER.window_handles[0])

        try:
            next_page_button = WAIT.until(
                EC.element_to_be_clickable((By.XPATH, '//a[@data-qa="pager-next"]'))
            )
            DRIVER.execute_script("arguments[0].click()", next_page_button)
        except Exception:
            os.system("cls")
            print(
                "It's either the hh.ru server has become undresponsive or all the links within the current search query have been clicked. \n 1) check if hh.ru is alive and responsive \n 2) check if you have clicked all the links available for the job search query. In that case change the 'JOB_SEARCH_QUERY = ' value. \n \n Sincerely Yours, \n NAKIGOE.ORG\n"
            )
            DRIVER.close()
            DRIVER.quit()

    os.system("cls")
    print(
        "Congratulations!\n The script has completed successfully in one go!!! You've sent 200 resumes today, that is currently a limit on HH.RU\n Come again tomorrow! \n \n Sincerely Yours, \n NAKIGOE.ORG\n"
    )


if __name__ == "__main__":
    main()
