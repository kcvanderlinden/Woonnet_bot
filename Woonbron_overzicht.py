from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, datetime, os, pickle
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

options = Options()
options.headless = True
options.add_argument("--window-size=1920,1080")
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')

def woonbron_aanbod():
    current_time = datetime.datetime.now()

    chromedriver_location = os.path.join(os.path.dirname(__file__), 'chromedriver')
    driver = webdriver.Chrome(options=options,
                              executable_path=chromedriver_location)
    driver.set_page_load_timeout(4)
    timeout = 4
    try:
        driver.get('https://woningzoeken.woonbron.nl/')
        element_present = EC.presence_of_element_located((By.ID, 'main'))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        driver.execute_script("window.stop();")
    submit_button = driver.find_element_by_xpath("//span[label/@for='radio0_status']")
    submit_button.click()
    driver.implicitly_wait(2)
    containers = driver.find_elements_by_xpath("//div[@class='box box--clickable box--gray-bg ng-isolate-scope']")

    # laden van de database
    if os.path.isfile('cache_folder/database_woonbron.txt'):
        with open('cache_folder/database_woonbron.txt', 'rb') as f:
            database = pickle.load(f)
    else:
        database = []

    entries = []
    for x in range(0,len(containers)):
        string = re.sub(r'\n|\t|', '', containers[x].get_attribute('innerHTML').strip())
        string = re.split('<|>', string)
        adres = string[string.index('h3 class="text--truncate ng-binding"') + 1]
        plaats = string[string.index('p class="text--truncate ng-binding"') + 1]
        plaats = re.split(',', plaats)[1].strip()
        prijs = string[string.index('span class="text--large text--energized ng-binding"') + 1]
        omschrijving = string[string.index('p class="text--truncate ng-binding"') + 3]
        omschrijving = '{}²'.format(re.split('\(', omschrijving)[1].strip())
        page_url = [('div class="box__media" afkl-lazy-image' in x) for x in string].index(True)
        url_index = re.split('\"|/', string[page_url])
        page_url = "https://woningzoeken.woonbron.nl/#!/huur/partikulier/detail/{}".format(url_index[8])
        type_verhuur = "Direct verhuur"
        entry = [adres, omschrijving, plaats, prijs, type_verhuur, page_url]

        # vergelijk deze entry met de database en als de entry nog niet voorkomt in de database, dan alleen toevoegen aan entries en uiteindelijk de database
        if entry not in database:
            entries.append(entry)
            database.append(entry)

    if len(entries) > 0:
        with open('cache_folder/database_woonbron.txt', 'wb') as f:
            pickle.dump(database, f)

        if os.path.isfile('cache_folder/{}{}_woonbron_overzicht.txt'.format(current_time.month, current_time.day)):
            with open('cache_folder/{}{}_woonbron_overzicht.txt'.format(current_time.month, current_time.day), 'rb') as f:
                cache = pickle.load(f)
            cache.extend(entries)
            with open('cache_folder/{}{}_woonbron_overzicht.txt'.format(current_time.month, current_time.day), 'wb') as f:
                pickle.dump(cache, f)
        else:
            with open('cache_folder/{}{}_woonbron_overzicht.txt'.format(current_time.month, current_time.day), 'wb') as f:
                pickle.dump(entries, f)

    driver.quit()
    return entries

def aanbod_message():
    current_time = datetime.datetime.now()
    if os.path.isfile('cache_folder/{}{}_woonbron_overzicht.txt'.format(current_time.month, current_time.day)):
        with open('cache_folder/{}{}_woonbron_overzicht.txt'.format(current_time.month, current_time.day), 'rb') as f:
            input = pickle.load(f)
    else:
        input = woonbron_aanbod()
    message = ''
    if len(input) > 0:
        for x in range(0, len(input)):
            message += "\n\n<a href='{}'>{} in {}</a>\n{} voor {}\n{}".format(input[x][5], input[x][0], input[x][2], input[x][1], input[x][3], input[x][4])
    else:
        message = "Er zijn geen nieuwe Woonbron woningen gevonden. Wil je het aanbod van gisteren bekijken? (/woonbron_oud) of wil je direct naar de <a href='https://woningzoeken.woonbron.nl/'>website</a>?"
    return message

def oud_aanbod_message():
    current_time = datetime.datetime.now()
    message = ''
    for x in range(1,7):
        a_day_back = datetime.date.today() - datetime.timedelta(days=x)
        if os.path.isfile('cache_folder/{}{}_woonbron_overzicht.txt'.format(current_time.month, a_day_back.day)):
            with open('cache_folder/{}{}_woonbron_overzicht.txt'.format(current_time.month, a_day_back.day), 'rb') as f:
                input = pickle.load(f)
                message = 'Dit zijn de woningen voor {}-{}:'.format(a_day_back.day, a_day_back.month)
                break
    else:
        input = []
    if len(input) > 0:
        for x in range(0, len(input)):
            message += "\n\n<a href='{}'>{} in {}</a>\n{} voor {}\n{}".format(input[x][5], input[x][0], input[x][2], input[x][1], input[x][3], input[x][4])
    else:
        message += 'Ik kon helaas ook geen oude advertenties van Woonbron vinden'
    return message