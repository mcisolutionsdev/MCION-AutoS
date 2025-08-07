from selenium.webdriver.common.by import By

import time

from automation import find_to_driver

chrome_path = "/usr/bin/google-chrome"
profile_path = "/home/nguyen-duc-kien/.config/google-chrome/"
profile_name = "Default"
driver = find_to_driver( chrome_path, profile_path, profile_name )

web_url = 'https://www.linkedin.com/'
driver.get( web_url )
time.sleep( 4 )

create_post_btn_x_path = '/html/body/div[5]/div[3]/div/div/div[2]/div/div/main/div[1]/div[2]/div[2]/button/span/span'
create_post_btn = driver.find_element( By.XPATH, create_post_btn_x_path )
create_post_btn.click()
time.sleep( 2 )

editor_xpath = '//div[contains(@class, "ql-editor") and @contenteditable="true" and contains(@data-placeholder, "What do you want to talk about?")]'
editor_div = driver.find_element( By.XPATH, editor_xpath )

editor_div.click()

p_tag = editor_div.find_element( By.TAG_NAME, "p" )
p_tag.send_keys( "This content is posted by Selenium" )
time.sleep( 2 )

media_btn_path = "/html/body/div[4]/div/div/div/div[2]/div/div[2]/div[2]/div[1]/div/section/div[2]/ul/li[2]/div/div/span/button"
media_btn = driver.find_element( By.XPATH, media_btn_path )
media_btn.click()
time.sleep( 2 )

input_file_id = "/html/body/div[4]/div/div/div/div[2]/div/div/div[1]/div/div[2]/input"
abs_image_path = r"C:\Users\MSI\OneDrive\Hình ảnh\blog.png"
input_file = driver.find_element( By.XPATH, input_file_id )
input_file.send_keys( abs_image_path )

next_btn_path = '/html/body/div[4]/div/div/div/div[2]/div/div/div[2]/div/button[2]'
next_btn = driver.find_element( By.XPATH, next_btn_path )
next_btn.click()
time.sleep( 2 )

post_btn_xpath = "/html/body/div[4]/div/div/div/div[2]/div/div/div[2]/div[4]/div/div[2]/button"
post_btn = driver.find_element( By.XPATH, post_btn_xpath )
post_btn.click()
time.sleep( 2 )

try:
    driver.close()
except Exception:
    print( Exception )
