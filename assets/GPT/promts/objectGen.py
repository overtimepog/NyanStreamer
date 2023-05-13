import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time

# Define the order of the files
file_names = ["rules.txt", "refrence.txt", "questTemp.txt", "armorTemp.txt", "weaponTemp.txt", "enemyTemp.txt", "petTemp.txt", "structureTemp.txt", "chestTemp.txt", "end.txt"]
email = "truen2005@gmail.com"
password = "Dawgdawg2005"

#start up the driver
if __name__ == "__main__":
    driver = uc.Chrome()
    def check_exists_by_xpath(xpath):
        try:
            driver.find_element(By.XPATH, xpath)
        except:
            return False
        return True

    def check_exists_by_css(css):
        try:
            driver.find_element(By.CSS_SELECTOR, css)
        except:
            return False
        return True

    driver.get("https://chat.openai.com/auth/login")

    driver.find_element(By.XPATH, '//*[@id="__next"]/div[1]/div[1]/div[4]/button[1]').click()
    time.sleep(5)

    driver.find_element(By.XPATH, '/html/body/div[1]/main/section/div/div/div/div[4]/form[2]/button').click()
    time.sleep(5)

    while True:
        if check_exists_by_xpath('//*[@id="identifierId"]'):
            usernamebox = driver.find_element(By.XPATH, '//*[@id="identifierId"]')
            for s in email:
                usernamebox.send_keys(s)
                print("sent", s)
            print("username: " + email + " entered")
            break
        else:
            print("waiting for username box")
            continue

    time.sleep(2)
    while True:
        if check_exists_by_xpath('//*[@id="identifierNext"]/div/button/span'):
            driver.find_element(By.XPATH, '//*[@id="identifierNext"]/div/button/span').click()
            print("next button clicked")
            break
        else:
            print("next button not found")
            continue

    time.sleep(2)
    while True:
        if check_exists_by_xpath('//*[@id="password"]/div[1]/div/div[1]/input'):
            passwordbox = driver.find_element(By.XPATH, '//*[@id="password"]/div[1]/div/div[1]/input')
            for s in password:
                if s == '?':
                    passwordbox.send_keys('?')
                    print('sent', '?')
                else:    
                    passwordbox.send_keys(s)
                    print("sent", s)
            print("password: " + password + " entered")
            break
        else:
            print("waiting for password box")
            continue

    time.sleep(2)
    while True:
        if check_exists_by_css('#view_container > div > div > div.pwWryf.bxPAYd > div > div.WEQkZc > div > form > span > section > div > div > div.SdBahf.Fjk18.Jj6Lae > div.OyEIQ.uSvLId > div:nth-child(2) > span'):
            print("Wrong Password")
            driver.close()
            break
        else:
            print("clicking next")
            break

    time.sleep(3)
    while True:
        if check_exists_by_xpath('//*[@id="passwordNext"]/div/button/span'):
            driver.find_element(By.XPATH, '//*[@id="passwordNext"]/div/button/span').click()
            print("next button clicked")
            break
        else:
            print("next button not found")
            continue

    while True:
        if check_exists_by_css('#view_container > div > div > div.pwWryf.bxPAYd > div > div.WEQkZc > div > form > span > section > div > div > span > figure > samp'):
            number = driver.find_element(By.CSS_SELECTOR, '#view_container > div > div > div.pwWryf.bxPAYd > div > div.WEQkZc > div > form > span > section > div > div > span > figure > samp').text
            print("verification required")
            print(number)
            continue
        else:
            print("no verification required")
            break


    # Read each file and generate a response
    for file_name in file_names:
        with open(file_name, 'r') as f:
            prompt = f.read()
        
