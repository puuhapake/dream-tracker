## Stora datamängder

Vi testar hur webbapplikationen reagerar till stora mängder av testdata. Se till att databasen har initialiserats, och kör

```$ python seed.py```

Det tar ca. 30 sekunder att skapa testdata med följande testdata:

```
USER_COUNT = 10_000
POST_COUNT = 1_000_000
COMMENT_COUNT = 3_000_000
LIKE_COUNT = 50_000_000
TAG_COUNT = 600_000
FRIEND_COUNT = 70_000
```

### Mätningar

Vi tillsätter mätningslogik till `app.py`:

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

Varje gång man utför en HTML-förfrågan skriver applikationen ut tidsmätningen till terminalen.

### Resultat

Resultat är medelvärden av tre (3) mätningar, avrundade till två decimal. Varje gång laddades sidan på ett sätt som förbigår information som lagrats i cacheminne (`CTRL+F5`).

#### Utan testdata

Vi börjar med att skapa bara en användare och ett inlägg.

| Sida | Tid |
| -----| --- |
| framsida | 0.05 s |
| inlägg | 0.03 s |
| användarsida | 0.04 s |
| andra sidor | 0.02 s |

#### Testdata

Med testdatan som skapas med `seed.py`, men utan sidor eller index

| Sida | Tid |
| -----| --- |
| framsida | 10.34 s |
| inlägg | 0.07 s |
| användarsida | 0.23 s |
| andra sidor | 0.03 s |

Applikationen är oanvändbart långsam.

#### Testdata med sidor

Med testdata, nu med sidor men inget index

| Sida | Tid |
| -----| --- |
| framsida | 0.74 s |
| inlägg | 0.04 s |
| användarsida | 0.05 s |
| andra sidor | 0.03 s |

#### Testdata med sidor samt index

Med testdata, sidor och index:

| Sida | Tid |
| -----| --- |
| framsida | 0.32 s |
| inlägg | 0.02 s |
| användarsida | 0.03 s |
| andra sidor | 0.02 s |

### Slutsatser

Applikationen fungerar relativt väl även med tiotals miljoner rader i databasen. Indexet och delade sidor gynnade applikationens effektivitet, och visar sig även att vara nödvändiga med stora datamängder.

Applikationen fungerar snabbare ifall man inte är inloggad, eftersom den inte blir tvungen att jämföra inläggets synlighetsvillkor med användarens rättigheter.

För att snabba upp framsidan kan även antalet användare som gillar varje inlägg lagras i databasen direkt, hellre än att räkna den om varje gång, exempelvis som ett heltal i `Posts`-tabellen som uppdateras med SQL `TRIGGER`-kommandot.