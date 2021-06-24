from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, datetime, os, pickle, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

options = Options()
options.headless = True
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')


def haaglanden_aanbod():
    current_time = datetime.datetime.now()

    chromedriver_location = os.path.join(os.path.dirname(__file__), 'chromedriver')
    #laden van de website met Selenium en een timeout
    driver = webdriver.Chrome(options=options,
                              executable_path=chromedriver_location)
    driver.get('https://www.woonnet-haaglanden.nl/aanbod/te-huur#?ik-zoek-een=1&gesorteerd-op=publicatiedatum-')
    timeout = 4
    try:
        element_present = EC.presence_of_element_located((By.ID, 'main'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out for Haaglanden_overzicht")
    finally:
        print("Page loaded")

    #laden van de database
    if os.path.isfile('cache_folder/database_haaglanden.txt'):
        with open('cache_folder/database_haaglanden.txt', 'rb') as f:
            database = pickle.load(f)
    else:
        database = []

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
    #scraping van de containers op de website
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
            prijs = string[string.index(raw_prijs) + 1].replace('&nbsp;','') if raw_prijs in string else ''
            raw_type_verhuur = 'span class="object-label-value ng-scope" translate="ModelCategorie'
            index_type_verhuur = [(raw_type_verhuur in x) for x in string]
            type_verhuur = string[index_type_verhuur.index(True) + 1] if True in index_type_verhuur else ''
            raw_omschrijving = 'span class="icon-icon_woonoppervlakte object-label-icon"'
            omschrijving = string[string.index(raw_omschrijving) + 5] if raw_omschrijving in string else ''
            entry = [adres, omschrijving, plaats, prijs, type_verhuur, page_url]

            #vergelijk deze entry met de database en als de entry nog niet voorkomt in de database, dan alleen toevoegen aan entries en uiteindelijk de database
            if entry not in database and entry.count('') < 2:
                entries.append(entry)
                database.append(entry)

    if len(entries) > 0:
        with open('cache_folder/database_haaglanden.txt', 'wb') as f:
            pickle.dump(database, f)

        if os.path.isfile('cache_folder/{}{}_haaglanden_overzicht.txt'.format(current_time.month, current_time.day)):
            with open('cache_folder/{}{}_haaglanden_overzicht.txt'.format(current_time.month, current_time.day), 'rb') as f:
                cache = pickle.load(f)
            cache.extend(entries)
            with open('cache_folder/{}{}_haaglanden_overzicht.txt'.format(current_time.month, current_time.day), 'wb') as f:
                pickle.dump(cache, f)
        else:
            with open('cache_folder/{}{}_haaglanden_overzicht.txt'.format(current_time.month, current_time.day), 'wb') as f:
                pickle.dump(entries, f)
    driver.quit()
    return entries

def aanbod_message():
    current_time = datetime.datetime.now()
    if os.path.isfile('cache_folder/{}{}_haaglanden_overzicht.txt'.format(current_time.month, current_time.day)):
        with open('cache_folder/{}{}_haaglanden_overzicht.txt'.format(current_time.month, current_time.day), 'rb') as f:
            input = pickle.load(f)
    else:
        input = haaglanden_aanbod()
    message = ''
    if len(input) > 0:
        #limit message length
        max_entries = len(input) if len(input) < 15 else 14
        for x in range(0, max_entries):
            message += "\n\n<a href='{}'>{} in {}</a>\n{} voor {}\n{}".format(input[x][5], input[x][0], input[x][2], input[x][1], input[x][3], input[x][4])
    else:
        message = 'Er zijn geen (nieuwe) woningen gevonden vandaag.'
    return message
