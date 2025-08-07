from selenium.webdriver.common.by import By

import time

from automation import find_to_driver

chrome_path = "/usr/bin/google-chrome"
profile_path = "/home/nguyen-duc-kien/.config/google-chrome/"
profile_name = "Default"
driver = find_to_driver( chrome_path, profile_path, profile_name )

yt_url = 'https://www.youtube.com/channel/UCIIDLAe0oCVpVJoCFc7oKJw/community?show_create_dialog=1'
driver.get( yt_url )
time.sleep( 2 )

text_poll_x_path = '//*[@id="poll-button"]//button'
text_poll = driver.find_element( By.XPATH, text_poll_x_path )
text_poll.click()

options = [ "Lựa chọn 1" ]
# options = [ "Lựa chọn 1", "Lựa chọn 2" ]
# options = [ "Lựa chọn 1", "Lựa chọn 2", "Lựa chọn 3" ]
# options = [ "Lựa chọn 1", "Lựa chọn 2", "Lựa chọn 3", "Lựa chọn 4" ]

num_options = len( options )
click_needed = max( 0, num_options - 2 )

for index, option in enumerate( options ):
    if index == 0:
        # Trường đầu tiên đã có sẵn input
        input_field = driver.find_element( By.XPATH, '//input[@placeholder="Add option"]' )
    else:
        if index <= click_needed:
            add_btn_xpath = '//*[@id="add-option"]//button'
            add_btn = driver.find_element( By.XPATH, add_btn_xpath )
            add_btn.click()
            time.sleep( 0.5 )

        input_field = driver.find_elements( By.XPATH, '//input[@placeholder="Add option"]' )[ index ]
    
    input_field.send_keys( option )
    time.sleep( 0.3 )

print( "Đã thêm tất cả các lựa chọn vào khảo sát." )
