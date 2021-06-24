from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re, os, datetime, pickle, time
from selenium.common.exceptions import TimeoutException

options = Options()
options.headless = True
#options.add_argument("--window-size=1920,1080")
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
#options.add_argument('--headless')

def rijnmond_aanbod():
    current_time = datetime.datetime.now()

    chromedriver_location = os.path.join(os.path.dirname(__file__), 'chromedriver')
    driver = webdriver.Chrome(options=options,
                              executable_path=chromedriver_location)
    driver.set_page_load_timeout(5)
    try:
        driver.get('https://www.woonnetrijnmond.nl/nieuw-aanbod/')
    except TimeoutException:
        driver.execute_script("window.stop();")

    #scroll naar het einde van de pagina om alle container te laden.
    SCROLL_PAUSE_TIME = 1
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    containers = driver.find_elements_by_xpath("//a[@class='clean']")
    url = [x.get_attribute('href') for x in containers]
    if ('https://www.woonnetrijnmond.nl/complexen/' in url) == True:
        advert = url.index('https://www.woonnetrijnmond.nl/complexen/')
        containers.pop(advert)
        url.pop(advert)

    entries = []
    for x in range(0,len(url)):
        string = re.sub(r'\n|\t|', '', containers[x].get_attribute('innerHTML').strip())
        page_url = url[x]
        string = re.split('<|>', string)
        type_verhuur = string[string.index('Huur- ') + 4].strip()
        if type_verhuur == 'DirectKans' or type_verhuur == 'WoningLoting':
            adres = string[string.index('div class="box__title  ellipsis"') + 1].strip()
            omschrijving = string[string.index('div class="box__text  ellipsis"') + 1].strip().replace('&nbsp;', '')
            omschrijving = re.split('\(|\)', omschrijving.format())
            plaats = string[string.index('div class="box__title  ellipsis"') + 7].strip()
            prijs = string[string.index('div class="box--obj__price  text-blue  push-right"') + 1].replace('&nbsp;',
                                                                                                           '')
            entries.append([adres, omschrijving, plaats, prijs, type_verhuur, page_url])

    if len(entries) > 0:
        with open('cache_folder/{}{}_rijnmond_overzicht.txt'.format(current_time.month, current_time.day), 'wb') as f:
            pickle.dump(entries, f)
    driver.quit()
    return entries

def aanbod_message(mode = 0):
    current_time = datetime.datetime.now()
    message = ''
    if mode == 1:
        input = rijnmond_aanbod()
    else:
        for x in range(0,7):
            a_day_back = datetime.date.today() - datetime.timedelta(days=x)
            if os.path.isfile('cache_folder/{}{}_rijnmond_overzicht.txt'.format(current_time.month, a_day_back.day)):
                with open('cache_folder/{}{}_rijnmond_overzicht.txt'.format(current_time.month, a_day_back.day), 'rb') as f:
                    input = pickle.load(f)
                    message = 'Dit zijn de woningen van {}-{}:'.format(a_day_back.day, a_day_back.month)
                    break
        else:
            input = []
    if len(input) > 0:
        for x in range(0, len(input)):
            message += "\n\n<a href='{}'>{} in {}</a>\n{} voor {}\n{}".format(input[x][5], input[x][0], input[x][2], input[x][1][-2], input[x][3], input[x][4])
    else:
        message = 'Er zijn geen nieuwe DirectKans of WoningLoting woningen gevonden vandaag.'
    return message

