import os
import sys
from collections import defaultdict
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome import service

sys.path.append(os.path.dirname(os.path.abspath('.')))
# Do not forget the change iCrawler part based on your project name
os.environ['DJANGO_SETTINGS_MODULE'] = 'TwigYourHealth.settings'

# This is required only if Django Version > 1.8
import django

django.setup()
# Scrapy settings
from deceases.models import BodyArea, BodyPart, Symptom

webdriver_service = service.Service('/home/nikita/web_drivers/operadriver')
webdriver_service.start()

capabilities = {'operaOptions': {'debuggerAddress': "localhost:1212"}}

driver = webdriver.Remote(webdriver_service.service_url, capabilities)

# driver = webdriver.Chrome(executable_path='/home/nikita/chromedriver')

driver.get('https://online-diagnos.ru/diagnostics')
sleep(2)
# # Wait 20 seconds for page to load
timeout = 5
print('connected')


def perform_click(el):
    webdriver.ActionChains(driver).move_to_element(el).click(el).perform()


try:
    warning = driver.find_element_by_xpath("//div[@id='warning-msg']/div/button")
    warning.click()
except NoSuchElementException:
    print('no warning')
    pass
try:
    js = "var aa=document.getElementById('static_footer_sponsor');aa.parentNode.removeChild(aa)"
    driver.execute_script(js)
    js = "var aa=document.getElementById('header_wrap');aa.parentNode.removeChild(aa)"
    driver.execute_script(js)
    sleep(1)
    weight_element = driver.find_element_by_id('weight_patient')

    weight_element.send_keys('90')
    # weight_element = driver.find_element_by_id('weight_patient')
    height_element = driver.find_element_by_id('growth_patient')

    height_element.send_keys('185')

    sex_element = driver.find_element_by_css_selector('.sex-ico.sex_man')

    perform_click(sex_element)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    next = driver.find_element_by_id('valid-form-and-next')

    perform_click(next)
except NoSuchElementException:
    print('no weight form')
    pass

# for ind_a, b_a in enumerate(body_areas):
#     sleep(1)
#     body_area = driver.find_elements_by_xpath('//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')[ind_a]
#
#     webdriver.ActionChains(driver).move_to_element(body_area).click(body_area).perform()
#     sleep(1)
#     body_parts = driver.find_elements_by_xpath('//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')
#     return_btn = driver.find_element_by_xpath('//div[@id="nano-scroll"]//div[@class="zoomout"]')
#     webdriver.ActionChains(driver).move_to_element(return_btn).click(return_btn).perform()
#     for ind_p, b_p in enumerate(body_parts):
#         sleep(1)
#
#         body_area = driver.find_elements_by_xpath('//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')[
#             ind_a]
#         body_area_name = body_area.text
#         if ind_p == 0:
#             print(body_area_name)
#         webdriver.ActionChains(driver).move_to_element(body_area).click(body_area).perform()
#         sleep(1)
#         body_part = driver.find_elements_by_xpath('//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')[
#             ind_p]
#         body_part_name = body_part.find_element_by_class_name('name_sympt').text
#         print(body_part_name)
#         webdriver.ActionChains(driver).move_to_element(body_part).click(body_part).perform()
#         sleep(1)
#         symptoms = driver.find_elements_by_xpath('//div[@class="btn_symptome pointer"]//div[@class="name_sympt"]')
#         for symptom in symptoms:
#             print(symptom.text)
#         btn = driver.find_element_by_id('bcd_loc')
#         btn.click()
#     print('part')


indexes = {}

body_parts_names = defaultdict(lambda: {})


def save_symptoms(symptom_text):
    global indexes
    global body_parts_names
    body_area = body_parts_names[0][indexes[0]]
    try:
        body_part = body_parts_names[1][indexes[1]]
    except (KeyError, IndexError):
        body_part = body_area
    body_area, _ = BodyArea.objects.get_or_create(name=body_area)
    body_part, _ = BodyPart.objects.get_or_create(name=body_part, body_area=body_area)
    symptom, _ = Symptom.objects.get_or_create(name=symptom_text)
    symptom.body_part = body_part
    symptom.save()


def recursive_symptoms(symp):
    try:
        children = './parent::div/parent::div[contains(@class,"p_wrapp")]//div[contains(@class,"sub_children")]'
        print(symp.text)
        symp.find_element_by_xpath(children)
        perform_click(symp)
        sleep(1)
        for s in symp.find_elements_by_xpath(f'{children}//div[contains(@class,"name_sympt")]'):
            recursive_symptoms(s)
    except NoSuchElementException:
        if symp.text:
            save_symptoms(symp.text)


def recursion_body_menu(depth=0):
    global indexes
    global body_parts_names
    sleep(1)
    if (driver.find_element_by_id('screen_basket').is_displayed()):
        for symptom in driver.find_elements_by_xpath('//div[@class="btn_symptome pointer"]//div[@class="name_sympt"]'):
            recursive_symptoms(symptom)
        return
    body_elements = driver.find_elements_by_xpath('//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')
    if depth < 2:
        for ind, el in enumerate(body_elements):
            body_parts_names[depth][ind] = el.text
    sleep(1)
    for ind in range(len(body_elements)):
        if depth == 0:
            indexes = {}
        indexes[depth] = ind
        symptoms_rtn_btn = driver.find_element_by_id('bcd_dia')
        perform_click(symptoms_rtn_btn)
        sleep(1)
        body_rtn_btn = driver.find_element_by_id('bcd_loc')
        perform_click(body_rtn_btn)

        for depth_ind in range(depth + 1):
            sleep(1.5)
            print([indexes[depth_ind]])
            body_element = \
                driver.find_elements_by_xpath(
                    '//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')[indexes[depth_ind]]
            perform_click(body_element)

        recursion_body_menu(depth + 1)


sleep(2)
body_area = driver.find_elements_by_xpath('//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')[1]
perform_click(body_area)
sleep(1)
body_rtn_btn = driver.find_element_by_id('bcd_loc')
perform_click(body_rtn_btn)
recursion_body_menu()
