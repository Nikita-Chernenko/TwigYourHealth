import os
import sys
from collections import defaultdict
from time import sleep

from django.db import transaction
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
from deceases.models import BodyPart, Symptom

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
except NoSuchElementException:
    print("no banner")
try:
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

indexes = {}

body_parts_names = defaultdict(dict)


def save_symptoms(symptom_text, body_part, parent=None):
    # the same parent and child
    if symptom_text.strip() == "Навязчивые действия" and parent.strip() != "Разные навязчивые действия":
        symptom_text = "Разные навязчивые действия"
    elif symptom_text.strip() == "Навязчивые действия" and parent.strip() == "Навязчивые действия":
        parent_text = "Разные навязчивые действия"

    symptom, created = Symptom.objects.get_or_create(name=symptom_text)
    if not created and symptom.body_part:
        return False
    if parent:
        parent = Symptom.objects.get(name=parent)
    body_part = BodyPart.objects.get(name=body_part)
    symptom.parent = parent
    symptom.body_part = body_part
    symptom.save()
    return True


def recursive_symptoms(symp, body_part, parent_text=None):
    try:
        children = './parent::div/parent::div[contains(@class,"p_wrapp")]//div[contains(@class,"sub_children")]'
        symp.find_element_by_xpath(children)
        perform_click(symp)
        sleep(1.5)
        res = save_symptoms(symp.text, body_part, parent_text)
        if not res:
            return
        for s in symp.find_elements_by_xpath(f'{children}//div[contains(@class,"name_sympt")]'):
            recursive_symptoms(s, body_part, symp.text)
    except NoSuchElementException:
        if symp.text:
            save_symptoms(symp.text, body_part, parent_text)



@transaction.atomic
def call_rec():
    recursion_body_menu()


def recursion_body_menu(depth=0, body_part_parent=None):
    global indexes
    sleep(1)
    if (driver.find_element_by_id('screen_basket').is_displayed()):
        for symptom in driver.find_elements_by_xpath('//div[@class="btn_symptome pointer"]//div[@class="name_sympt"]'):
            recursive_symptoms(symptom, body_part_parent)
        return
    body_elements = driver.find_elements_by_xpath('//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')
    body_part_names = [el.text for el in body_elements]
    sleep(1)
    for ind in range(len(body_elements)):
        body_part, _ = BodyPart.objects.get_or_create(name=body_part_names[ind])
        if body_part_parent:
            body_part_parent = BodyPart.objects.get(name=body_part_parent)
        body_part.parent = body_part_parent
        body_part.save()
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
            body_element = \
                driver.find_elements_by_xpath(
                    '//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')[indexes[depth_ind]]
            perform_click(body_element)

        recursion_body_menu(depth + 1, body_part.name)


sleep(2)
body_area = driver.find_elements_by_xpath('//div[@id="nano-scroll"]//div[contains(@class,"btn_symptome")]')[1]
perform_click(body_area)
sleep(1)
body_rtn_btn = driver.find_element_by_id('bcd_loc')
perform_click(body_rtn_btn)
call_rec()
