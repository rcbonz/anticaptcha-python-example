#!/usr/bin/env python
# pylint: disable=unused-argument

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import options
from selenium.webdriver.chrome.options import Options

import json
import time
import random
from pathlib import Path

from anticaptchaofficial.recaptchav2proxyless import recaptchaV2Proxyless

"Create you account and API_KEY using my link so you can help me: http://getcaptchasolution.com/oyd6boc637"
SOLVERKEY = "<Your API KEY here>"

options = Options()
options.headless = False

driver = webdriver.Chrome(options=options)

BASE_URL = "https://www.google.com/recaptcha/api2/demo"


# It's usefull to save cookies so chances of having to spend anticaptcha API are lower
def save_cookies(driver, path="cookies.json"):
    with open(path, 'w') as filehandler:
        json.dump(driver.get_cookies(), filehandler)
    print("[ ] Session cookies successfully saved.")
    return

# Load cookies, usefull in my experience
def load_cookies(driver, path="cookies.json"):
    driver.get(BASE_URL)
    my_file = Path(path)
    if my_file.is_file():
        with open(path, 'r') as cookiesfile:
            cookies = json.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)
        print("[ ] Session cookies successfully Loaded.")
        return
    else:
        print("[ ] Session cookies file does not exists.")
        return


"The main repository function"
def solve_recaptcha():
    while True:
        try:
            if driver.find_element_by_class_name("g-recaptcha"): # Try to find if theres recaptcha on the page
                print("[ ] reCAPTCHA detected")
            else:
                print("[ ] reCAPTCHA not detected")
                return # If it doesn't, just returns
            print("[ ] Starting anticaptcha")
            WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[name^='a-'][src^='https://www.google.com/recaptcha/api2/anchor?']"))) # Wait for recaptcha iframe to be available and.. Time out 10 secs
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[@id='recaptcha-anchor']")) )# Wait for recaptcha anchor to be clickable. Time out 10 secs
            driver.switch_to.default_content()
            data_sitekey = driver.find_element_by_class_name('g-recaptcha').get_attribute('data-sitekey') # The sitekey will be needed for anticaptcha to do the job
            solver = recaptchaV2Proxyless() # Here the magic starts
            solver.set_verbose(0)
            solver.set_key(SOLVERKEY)
            solver.set_website_url(BASE_URL)
            solver.set_website_key(data_sitekey)
            g_response = solver.solve_and_return_solution()
            if g_response != 0: # If answer not 0, success!
                print("[ ] g-response SUCCESS")
                driver.execute_script('document.getElementById("g-recaptcha-response").innerHTML = "{}";'.format(g_response)) # Sends captcha solution
                return
            else:
                print("[ ] Task finished with error "+solver.error_code)
                print("[ ] Reporting anticaptcha error via API.")
                solver.report_incorrect_image_captcha() # Report anticaptcha error to the API
                print("[ ] Refreshing page...")
                driver.refresh() # Refresh page and try again if anticaptcha didn't work
                print("[ ] Trying again.")
        except Exception as err:
            print(err)
            driver.close()
            exit()


def load_page():
    while True:
        try:
            load_cookies(driver) # Fistly try to load cookies previously saved
            driver.get(BASE_URL) # Calls for target url
            solve_recaptcha() # Call function to handle captcha
            print("[ ] Sleeping, pretending to be a human")
            time.sleep(random.uniform(4.0, 7.0)) # Usefull line to pretend being a human
            print("[ ] Submiting form")
            driver.find_element_by_xpath('//*[@id="recaptcha-demo-submit"]').click()
            if "Verification Success" in driver.find_element_by_xpath('/html/body/div').text: # Check if next page is what we expect
                print("[ ] Verification Success... Hooray!")
            save_cookies(driver) # Save cookies for eventual later use
            driver.close()
            return
        except Exception as err:
            print(err)
            driver.close()
            exit()


if __name__ == '__main__':
    load_page()

