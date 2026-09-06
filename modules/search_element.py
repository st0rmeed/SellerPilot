from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def search_element(driver, locator, wait, clickable=True):
    if clickable:
        element = WebDriverWait(driver, wait).until(
            EC.element_to_be_clickable(locator))
    else:
        element = WebDriverWait(driver, wait).until(
            EC.visibility_of_element_located(locator)
        )

    return element
