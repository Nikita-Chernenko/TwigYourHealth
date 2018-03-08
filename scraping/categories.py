from time import sleep

from selenium import webdriver
from selenium.webdriver.chrome import service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Specifying incognito mode as you launch your browser[OPTIONAL]


webdriver_service = service.Service('/home/nikita/opera/operadriver')
webdriver_service.start()

capabilities = {'operaOptions': {'debuggerAddress': "localhost:1212"}}

driver = webdriver.Remote(webdriver_service.service_url, capabilities)
# driver = webdriver.Chrome(executable_path='/home/nikita/chromedriver')

driver.get('https://online-diagnos.ru/diagnostics')
# # Wait 20 seconds for page to load
timeout = 5
print('f')

sleep(1)
print('dd')
# # Get all of the titles for the pinned repositories
# # We are not just getting pure titles but we are getting a selenium object
# # with selenium elements of the titles.
#
# # find_elements_by_xpath - Returns an array of selenium objects.
print('f')
try:
    warning = driver.find_element_by_xpath("//div[@id='warning-msg']/div/button")
    warning.click()
except NoSuchElementException:
    print('no warning')
    pass
try:

    weight_element = driver.find_element_by_id('weight_patient')

    weight_element.send_keys('90')
    # weight_element = driver.find_element_by_id('weight_patient')
    height_element = driver.find_element_by_id('growth_patient')

    height_element.send_keys('185')

    sex_element = driver.find_element_by_css_selector('.sex-ico.sex_man')

    webdriver.ActionChains(driver).move_to_element(sex_element).click(sex_element).perform()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(0.1)
    next = driver.find_element_by_id('valid-form-and-next')

    next.click()
except NoSuchElementException:
    print('no weight form')
    pass

sleep(1)
body_areas = driver.find_elements_by_xpath('//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')
for ind_a, b_a in enumerate(body_areas):
    sleep(1)
    body_area = driver.find_elements_by_xpath('//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')[ind_a]

    webdriver.ActionChains(driver).move_to_element(body_area).click(body_area).perform()
    sleep(1)
    body_parts = driver.find_elements_by_xpath('//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')
    return_btn = driver.find_element_by_xpath('//div[@id="nano-scroll"]//div[@class="zoomout"]')
    webdriver.ActionChains(driver).move_to_element(return_btn).click(return_btn).perform()
    for ind_p, b_p in enumerate(body_parts):
        sleep(1)

        body_area = driver.find_elements_by_xpath('//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')[ind_a]
        body_area_name = body_area.text
        if ind_p == 0:
            print(body_area_name)
        webdriver.ActionChains(driver).move_to_element(body_area).click(body_area).perform()
        sleep(1)
        body_part = driver.find_elements_by_xpath('//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')[ind_p]
        body_part_name = body_part.find_element_by_class_name('name_sympt').text
        print(body_part_name)
        webdriver.ActionChains(driver).move_to_element(body_part).click(body_part).perform()
        sleep(1)
        symptoms = driver.find_elements_by_xpath('//div[@class="btn_symptome pointer"]//div[@class="name_sympt"]')
        for symptom in symptoms:
            print(symptom.text)
        btn = driver.find_element_by_id('bcd_loc')
        btn.click()
    print('part')
