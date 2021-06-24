# Woonnet_bot

Dit is een volledige werkend concept en zou aangepast kunnen worden om andere sociale huurwebsites uit andere regio's te ondersteunen.

## Wat is het?
Dit is een Telegram Bot die nieuwe sociale huurwoning advertenties uit de regio van Delft verzameld. Websites die gebruikt worden zijn https://www.woonnetrijnmond.nl/ (alleen de nieuwe woningen die elke dag tussen 18.00 en 20.00 uur online komen), https://www.hureninhollandrijnland.nl/aanbod/ (alles), https://www.woonnet-haaglanden.nl/aanbod/ (alles) en https://www.woonbron.nl/ (alleen de Direct Huren huurwoningen). Dit is handig als je bij één of meerdere organisaties staat ingeschreven en up-to-date gehouden wilt worden van het aanbod. In het geval van Woonnet Rijnmond wordt je dus ook elke avond op de hoogte gesteld van nieuwe DirectKans woningen die om 20.00 uur open komen voor reacties en op basis van reactie snelheid op de advertentie verhuurd worden.

De bot is zo geschreven dat op de bot in ieder geval op drie momenten van de dag automatisch het aanbod van de woonnet organisaties ophaalt en van Rijnmond om 18.30 uur een update stuurt. Met de volgende commando's kunnen acties gevraagd worden van de bot.
1. ```/rijnland```    - Overzicht van nieuwste aanbod in Rijnland.
2. ```/rijnmond```    - Overzicht van 'nieuwste' aanbod in Rijnmond.
3. ```/woonbron```    - Overzicht van directe huurwoningen.
4. ```/haaglanden```  - Overzicht nieuwste aanbod.

Hierbij een voorbeeld van hoe zo'n bericht er uit kan zien.

![screenshot](https://i.imgur.com/78j4Fzp.png)

## Hoe werkt het?
Deze bot maakt gebruik van Selenium om de websites te laden en vereist daarom ChromeDriver en een Google Chrome Browser (of Chromium) om te werken. De ChromeDriver kan [hier](https://chromedriver.chromium.org/downloads) gedownload worden (let op dat de chromedriver dezelfde versie moet zijn als het Chromebrowser van je systeem) en moet in de project map geplaatst worden.

Daarnaast vereist de werking van de bot zelf een ```TELEGRAM_TOKEN``` en een ```TELEGRAM_DEV_ID```. De eerste is een token die je kan verkrijgen door een bot te registreren bij de BotFather en de tweede moet het telegram id zijn van het Telegram account waar de foutmeldingen naar gestuurd mogen worden (bijvoorbeeld je eigen Telegram account).

De bot kan ook makkelijk gestart worden door het bijgeleverde ```Dockerfile``` met Docker te gebruiken. Hierdoor worden de vereiste python packages uit ```requirements.txt``` en een Chromium Browser automatisch geïnstalleerd.
```bash
$ cd /navigeer/naar/de/project/map

$ docker build -t woonnet_bot .

$ docker run woonnet_bot
```
