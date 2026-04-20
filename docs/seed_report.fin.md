## Suuret tietomäärät

Kokeillaan, miten applikaatio reagoi suureen testidataan. Varmista, että tietokanta on alustettu, ja suorita komento

```$ python seed.py```

Testidatan luominen kestää noin 30 sekuntia. Data luodaan näillä arvoilla:

```
USER_COUNT = 10_000
POST_COUNT = 1_000_000
COMMENT_COUNT = 3_000_000
LIKE_COUNT = 50_000_000
TAG_COUNT = 600_000
FRIEND_COUNT = 70_000
```

### Mittaukset

Lisätään mittauslogiikkaa pääsovellukseen (`app.py`):

```
from flask import g
from time import time

@app.before_request
def before_request():
    g.start_time = time()

@app.after_request
def after_request(response):
    t = round(time() - g.start_time, 2)
    print(f">> Request time: {t} seconds")
    return response
```

Joka kerta, kun käyttäjä tekee HTML-pyynnon, ohjelma tulostaa ajanmittauksen terminaaliin.

### Tulokset

Tulokset on ilmoitettu kolmen mittauksen keskiarvona, pyöristettynä kahteen desimaalilukuun. Sivu pyydettiin joka kerta ilman välimuistissa olevia tietoja (`CTRL+F5`).

#### Ilman testidataa

Luodaan aluksi vain yksi käyttäjä ja yksi tietokohde.

| Sivu | Aika |
| -----| --- |
| etusivu | 0.05 s |
| tietokohde | 0.03 s |
| käyttäjäsivu | 0.04 s |
| muut | 0.02 s |

#### Testidata

Luodaan testidata `seed.py`-tiedoston avulla, mutta ilman indeksejä tai sivutusta.

| Sivu | Aika |
| -----| --- |
| etusivu | 10.34 s |
| tietokohde | 0.07 s |
| käyttäjäsivu | 0.23 s |
| muut | 0.03 s |

Sivu on käyttökelvottoman hidas.

#### Testidata sivutuksella

Saman testidatan kanssa, nyt siten, että sivut, joissa on paljon tietoa, on jaettu kahdenkymmenen julkaisun alasivuihin.

| Sivu | Aika |
| -----| --- |
| etusivu | 0.74 s |
| tietokohde | 0.04 s |
| käyttäjäsivu | 0.05 s |
| muut | 0.03 s |

#### Testidata sivutuksella ja indekseillä

Lopulta kokeillaan saman testidatan kanssa lisätä sivutuksen lisäksi tietokantaa nopeuttavia indeksejä.

| Sivu | Aika |
| -----| --- |
| etusivu | 0.32 s |
| tietokohde | 0.02 s |
| käyttäjäsivu | 0.03 s |
| muut | 0.02 s |

### Johtopäätökset

Applikaatio toimii suhteellisen hyvin jopa kymmenien miljoonien tietokantarivien kanssa. Indeksit ja sivutus auttoivat paljon, ja olivat käytännössä pakollisia suuren datan kanssa.

Sivu latautuu nopeammin jos ei ole kirjautuneena sisään, koska applikaation ei silloin tarvitse verrata julkaisujen näkyvyysmääreiden ja käyttäjän näköluvan relaatiota.

Etusivun lataamisen nopeutta voi vielä tehostaa sillä, että tykkäysten määrä säilytettäisi suoraan tietokannassa, esimerkiksi `Posts`-taulukon rivissä `like_count` joka päivitetään SQL `TRIGGER`-komennon avulla.