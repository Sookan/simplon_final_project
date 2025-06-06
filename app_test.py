if __name__ == "__main__":
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.wait import WebDriverWait

    import time

    def test_app_run(driver : webdriver):
        try:
            driver.get(root_url)
            valid = True

        except:
            valid = False
        return valid

    def test_go_to_root(driver: webdriver):
        wait = WebDriverWait(driver, 2)

        try:
            element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "objectBox.objectBox-string"))).text
            valid = element == "\"World\""

        except:
            valid = False

        return valid

    def test_not_login_redirection(driver: webdriver):
        try:
            driver.get(root_url + "dashboard")
            valid = driver.current_url == "http://127.0.0.1:8000/login"

        except:
            valid = False

        return valid

    def test_login(driver: webdriver):

        try:
            driver.get(root_url + "login")
            email = driver.find_element(By.ID, "email")
            email.send_keys("test@test.com")
            password = driver.find_element(By.ID, "pwd")
            password.send_keys("test@test.com")
            driver.find_element(By.ID, "submit").click()
            valid = driver.current_url == "http://127.0.0.1:8000/dashboard"

        except:
            valid = False

        return valid

    def test_cookie(driver: webdriver):

        try:
            driver.get(root_url + "cookie")
            wait = WebDriverWait(driver, 2)
            wait.until(EC.presence_of_element_located((By.ID, "/user_id")))
            driver.find_element(By.ID, "/user_id").text.split()[-1]
            valid = driver.find_element(By.ID, "/access_token").text.split()[-1]

        except:
            valid = False

        return valid

    def test_favorite_is_good(driver: webdriver):

        try:
            driver.get(root_url + "dashboard")
            wait = WebDriverWait(driver, 2)
            wait.until(EC.presence_of_element_located((By.ID, "index-select")))
            element = driver.find_element(By.ID, "index-select")
            valid = element.get_attribute("value") == "^DJI"

        except:
            valid = False

        return valid


    def test_deconection(driver: webdriver):

        try:
            driver.get(root_url + "dashboard")
            wait = WebDriverWait(driver, 2)
            wait.until(EC.presence_of_element_located((By.ID, "index-select")))
            driver.find_element(By.ID, "deconection-button").click()
            driver.get(root_url + "cookie")
            try :
                wait = WebDriverWait(driver, 2)
                wait.until(EC.presence_of_element_located((By.ID, "/user_id")))
                valid = False
            except :
                valid = test_not_login_redirection(driver)

        except:
            valid = False

        return valid

    root_url = "http://127.0.0.1:8000/"

    with webdriver.Firefox() as driver:

        assert test_app_run(driver), ("l'app nbe tourne pas ou est inaccessible")

        assert test_go_to_root(driver), ("le chemain root n'affiche pas la bonne valeur")

        assert test_not_login_redirection(driver), ("l'app ne redirige pas vers le login")

        assert test_login(driver), ("impossible de se connecter")

        cookie = test_cookie(driver)
        assert cookie, ("il n'y a pas de cookie enregister après le login")


        assert test_favorite_is_good(driver), ("le favorie n'est pas le bon")

        assert test_deconection(driver), ("la deconection ne c'est pas dérouler comme prévue")

        test_login(driver)
        new_cookie = test_cookie(driver)
        assert new_cookie != cookie, ("le cookie n'as pas changer après le deusième login")

