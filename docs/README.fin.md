# dream-tracker
Yksinkertainen some unen laadun kirjaamiseen sekä unten tarinoiden jakamiseen muiden käyttäjien kanssa.

Lue [seed-raportti](/docs/seed_report.fin.md)

## Toiminnot
Käyttäjät voivat
- luoda tunnuksen ja kirjautua sisään
- julkaista omia päivityksiä sekä muokata ja poistaa omia päivityksiään
- katsella sekä omia että muiden käyttäjien päivityksiä
- seurata toisia käyttäjiä ja nähdä näiden päivityksiä ohjelman etusivulla
- määritellä omille päivityksilleen yksilöllisen näkyvyysmääreen (esim. julkinen, yksityinen, vain seuraajille...)
- valita sopivia luokitteluja omille päivityksilleen
- hakea päivityksiä hakusanojen, luokittelujen ja/tai tilastojen perusteella
- tarkastella käyttäjien profiilisivuja, jotka sisältävät kyseenomaisen käyttäjän päivitykset sekä tilastot
- vastata päivityksiin sekä tykätä ja reagoida niihin
- lisätä päivityksiä omiin keräyslistoihin

# Asennus

1. Lataa repon sisältö ja avaa kansio valinnaisessa terminaalissa
2. Asenna `flask`:

```
$ pip install flask
```

tai virtuaaliympäristössä

```
$ python -m venv venv
$ venv/bin/activate
$ pip install flask
```

3. Käynnistä palvelin ja avaa osoite `localhost:5000` valinnaisella verkkoselaimella

```
$ flask run
```

Applikaatio alustaa tietokannan ja asetukset automaattisesti.