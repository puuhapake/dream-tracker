# dream-tracker
En enkel social plattform för att mäta och dokumentera sömnkvalitet samt de dynamiska scenerna som eventuellt uppstår under drömsömn.

[Dokumentaatio on myös saatavilla suomeksi](README.fin.md).
[Documentation also available in English](README.eng.md).

## Funktioner
Användare kan
- skapa ett konto och logga in
- skapa nya inlägg samt redigera och radera sina egna inlägg
- se sina egna likväl andra användares inlägg
- följa andra användare och få deras inlägg i sitt flöde
- ange synlighetsvillkor för sina inlägg (ex. offentlig, enbart följare, privat...)
- välja kategorier till sina egna inlägg,
- söka efter inlägg enligt sökord, filterkategorier eller statistik,
- se användares profilsidor, som visar deras inlägg samt aktuell statistik om dem,
- svara på, gilla och reagera på inlägg,
- lägga till inlägg i samlingslistor

# Installation

1. Ladda ner repon och navigera till dess mapp med en valfri terminal
2. Installera `flask`:

```
$ pip install flask
```

eller i en `venv`-virtualomgivning:

```
$ python -m venv venv
$ venv/bin/activate
```

3. Starta servern och navigera till `localhost:5000` med en valfri webbläsare

```
$ flask run
```

Programmet skapar databasen och konfigureringar automatiskt.