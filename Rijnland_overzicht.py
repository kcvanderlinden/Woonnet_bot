from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, os
import datetime,time
import pickle
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

options = Options()
options.headless = True
#options.add_argument("--window-size=1920,1080")
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
#options.add_argument('--headless')


def rijnland_aanbod():
    current_time = datetime.datetime.now()

    chromedriver_location = os.path.join(os.path.dirname(__file__), 'chromedriver')
    driver = webdriver.Chrome(options=options, executable_path=chromedriver_location)
    #driver = webdriver.Chrome(options=options, executable_path='/Woonnet/chromedriver')
    driver.get('https://www.hureninhollandrijnland.nl/aanbod/te-huur#?gesorteerd-op=publicatiedatum-')
    timeout = 4
    try:
        element_present = EC.presence_of_element_located((By.ID, 'main'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out for Rijnland_overzicht")
    finally:
        print("Page loaded")

    # scroll naar het einde van de pagina om alle container te laden.
    SCROLL_PAUSE_TIME = 0.5
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    time.sleep(2)
    containers = driver.find_elements_by_xpath("//ng-include[@class='ng-scope']")

    # laden van de database
    if os.path.isfile('cache_folder/database_rijnland.txt'):
        with open('cache_folder/database_rijnland.txt', 'rb') as f:
            database = pickle.load(f)
    else:
        database = []

    entries = []
    for x in range(0, len(containers)):
        string = re.sub(r'\n|\t|', '', containers[x].get_attribute('innerHTML').strip())
        string = re.split('<|>', string)
        if True in [("ng-href" in x) for x in string]:
            index = [("ng-href" in x) for x in string].index(True)
            page_url = re.split('\"|\"', string[index])[1]
            page_url = "https://www.woonnet-haaglanden.nl{}".format(page_url)
            raw_adres = 'span ng-bind-html="::object.street" class="ng-binding"'
            adres = string[string.index(raw_adres) + 1] if raw_adres in string else ''
            adres += string[string.index(raw_adres) + 3] if raw_adres in string else ''
            raw_plaats = 'span class="address-part ng-binding ng-scope" ng-if="::!hideAdresCity"'
            plaats = string[string.index(raw_plaats) + 1] if raw_plaats in string else ''
            raw_prijs = 'span class="prijs ng-binding ng-scope" ng-if="::!toonAangepasteHuurprijs(object)"'
            prijs = string[string.index(raw_prijs) + 1].replace('&nbsp;', '') if raw_prijs in string else ''
            type_verhuur = string[
                [('span class="object-label-value ng-scope" translate="ModelCategorie' in x) for x in string].index(
                    True) + 1]
            raw_omschrijving = 'span class="icon-icon_woonoppervlakte object-label-icon"'
            omschrijving = string[string.index(raw_omschrijving) + 5] if raw_omschrijving in string else ''
            entry = [adres, omschrijving, plaats, prijs, type_verhuur, page_url]

            entry = [adres, omschrijving, plaats, prijs, type_verhuur, page_url]

            # vergelijk deze entry met de database en als de entry nog niet voorkomt in de database, dan alleen toevoegen aan entries en uiteindelijk de database
            if entry not in database:
                entries.append(entry)
                database.append(entry)

    if len(entries) > 0:
        with open('cache_folder/database_rijnland.txt', 'wb') as f:
            pickle.dump(database, f)

        if os.path.isfile('cache_folder/{}{}_rijnland_overzicht.txt'.format(current_time.month, current_time.day)):
            with open('cache_folder/{}{}_rijnland_overzicht.txt'.format(current_time.month, current_time.day), 'rb') as f:
                cache = pickle.load(f)
            cache.extend(entries)
            with open('cache_folder/{}{}_rijnland_overzicht.txt'.format(current_time.month, current_time.day), 'wb') as f:
                pickle.dump(cache, f)
        else:
            with open('cache_folder/{}{}_rijnland_overzicht.txt'.format(current_time.month, current_time.day), 'wb') as f:
                pickle.dump(entries, f)
    driver.quit()
    return entries


def aanbod_message():
    current_time = datetime.datetime.now()
    if os.path.isfile('cache_folder/{}{}_rijnland_overzicht.txt'.format(current_time.month, current_time.day)):
        with open('cache_folder/{}{}_rijnland_overzicht.txt'.format(current_time.month, current_time.day), 'rb') as f:
            input = pickle.load(f)
    else:
        input = rijnland_aanbod()
    message = ''
    if len(input) > 0:
        for x in range(0, len(input)):
            message += "\n\n<a href='{}'>{} in {}</a>\n{} voor {}\n{}".format(input[x][5], input[x][0], input[x][2],
                                                                              input[x][1], input[x][3], input[x][4])
    else:
        message = 'Er zijn geen (nieuwe) woningen gevonden vandaag.'
    return message
