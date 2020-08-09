#!/bin/bash

from selenium import webdriver
from selenium.webdriver.support import wait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common import desired_capabilities
import time

def fill_form(func):
    def form_data(firstname, lastname, email, telephone, address, zip_code):
        driver = func()
        firstname = driver.find_element_by_xpath('/html/body/main/div/div/div[1]/div/form/div[1]/div[1]/div/input')
        lastname = driver.find_element_by_xpath('/html/body/main/div/div/div[1]/div/form/div[1]/div[2]/div/input')
        email = driver.find_element_by_xpath('/html/body/main/div/div/div[1]/div/form/div[2]/div[1]/div/input')
        telephone = driver.find_element_by_xpath('/html/body/main/div/div/div[1]/div/form/div[2]/div[2]/div/input')
        address = driver.find_element_by_xpath('/html/body/main/div/div/div[1]/div/form/div[3]/input')
        zip_code = driver.find_element_by_xpath('/html/body/main/div/div/div[1]/div/form/div[4]/div[3]/input')

        time.sleep(2)

        firstname.send_keys(firstname)
        lastname.send_keys(lastname)
        email.send_keys(email)
        telephone.send_keys(telephone)
        address.send_keys(address)
        zip_code.send_keys(zip_code)
        
        submit = driver.find_element_by_xpath('/html/body/main/div/div/div[1]/div/form/button')
        submit.click()

        return driver
    return form_data

@fill_form
def payment_process():
    driver = webdriver.Edge(executable_path='C:\\Users\\Pende\\Documents\\edge_driver\\msedgedriver.exe')
    driver.get('https://nawoka.fr/')
    
    # capabilities = desired_capabilities.DesiredCapabilities.CHROME.copy()
    # capabilities['platform'] = 'WINDOWS'
    # capabilities['version'] = '10'

    wait.WebDriverWait(driver, 3000).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/div[2]/div[1]/a')))
    link_to_tops = driver.find_element_by_xpath('/html/body/main/div[2]/div[1]/a')
    link_to_tops.click()

    wait.WebDriverWait(driver, 5000).until(ec.element_to_be_clickable((By.XPATH, '/html/body/main/div/section/div[2]/div[3]/a')))
    link_to_products = driver.find_element_by_xpath('/html/body/main/div/section/div[2]/div[3]/a')
    link_to_products.click()

    product_link = driver.find_element_by_xpath('/html/body/main/div/div/section/div/div[2]/div/div[2]/a')
    product_link.click()

    add_to_cart = driver.find_element_by_xpath('//*[@id="btn_add_to_cart"]')
    add_to_cart.click()

    time.sleep(3)

    driver.execute_script('window.location.href="https://nawoka.fr/shop/cart";')

    continue_to_shipment = driver.find_element_by_xpath('/html/body/main/div/div[2]/div/div/div/a')
    continue_to_shipment.click()

    return driver


if __name__ == "__main__":
    driver = payment_process('John', 'Pendenque', 'pendenquejohn@gmail.com', '0668552975', '36 rue de Suède', 59000)
    driver.close()
