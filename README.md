# Lenkkeilysovellus

Sovellus ei ole vielä fly.io-palvelussa. Ohjeet sovelluksen käynnistämiseen paikallisesti README:n [lopussa](https://github.com/samulioll/lenkkeilysovellus/blob/main/README.md#sovelluksen-k%C3%A4ynnist%C3%A4minen-paikallisesti).

## Perusidea

Sovellus mihin käyttäjät voivat lisätä kävellen, juosten tai pyöräillen tekemiään lenkkejä. Sovelluksessa on ominaisuuksia, joilla käyttäjät voivat nähdä yhteenvetoja sekä omista tilastoista että myös muiden (joilla tiedot ovat julkisia). Käyttäjät voivat liittyä ryhmiin ja myös ryhmien yhteenvetoja voi tarkastella. Käyttäjät voivat myös jättää kommentteja muiden aktiviteetteihin.

## Tarkempi kuvaus

- Käyttäjäprofiili
	- (✓) Käyttäjät voivat luoda itselleen käyttäjäprofiilin.

- Ryhmät
	- (_) Käyttäjät voivat luoda ryhmiä.
	- (✓) Käyttäjät voivat liittyä ryhmiin.
	- (✓) Käyttäjät voivat poistua ryhmistä.
	- (✓) Jokainen käyttäjä voi nähdä omien ryhmien tilastot.

- Lenkkien lisäys tietokantaan
	- (✓) Käyttäjät voivat lisätä tekemiään lenkkejä ja niiden tiedot tallennetaan tietokantaan.

- Kommentointi
	- (✓) Käyttäjät voivat kommentoida lenkkejä.
	- (✓) Käyttäjät voivat poistaa omia kommenttejaan.
	- (✓) Uusista lukemattomista kommenteista tulee ilmoitus

- Henkilökohtaiset tilastot
	- (_) Jokainen käyttäjä näkee monipuoliset tilastot omista lenkeistään.

- Tietyn käyttäjän tilastot
	- (_) Jokainen käyttäjä voi nähdä tietyn toisen käyttäjän tilastot jos tämä käyttäjä on asettanut se julkiseksi

- Kaikkien käyttäjien tilastot
	- (_) Jokainen käyttäjä voi nähdä tilastot kaikkien käyttäjien tekemistä lenkeistä, riippumatta yksityisyysasetuksista. Kokonaistilastoista ei kuitenkaan voi yksilöidä käyttäjiä.

- Kaikien ryhmien tilastot
	- (_) Jokainen käyttäjä voi nähdä tilastot kaikkien ryhmien tekemistä lenkeistä, riippumatta yksityisyysasetuksista. Kokonaistilastoista ei kuitenkaan voi yksilöidä käyttäjiä.

## Tilanne 23.4.

Sovelluksen perusrakenne ja suurin osa suunnitellusta toiminnallisuudesta on kasassa.  

- Käyttäjäprofiilit
	- Sovellus tunnistaa jos käyttäjä yrittää rekisteröityä käyttäjänimellä joka on jo käytössä.
	- Salasana pyydetään kahdesti jolla varmistetaan että käyttäjä kirjoittaa sen oikein.
	- Sisään- ja uloskirjautuminen toimii oikein.

- Aktiviteetit
	- Aktiviteettien lisääminen onnistuu. 
	- Toistaiseksi uusien reittien lisääminen ei ole mahdollista, mutta se ominaisuus on tulossa.
	- Aktiviteettien kommentointi ei ole vielä mahdollista, pl. aktiviteetin lisäyksen yhteydessä tehtävä mahdollinen oma kommentti.
	- Käyttäjät näkevät listan viimeaikaisista aktiviteeteistaan dashboard-sivulla. (Aktiviteettien formatointi on vielä tekemättä)
	- Kaikki omat aktiviteetit löytyvät linkin takaa.
	- Tulevaisuudessa dashboard-sivulta näkee myös tilastoja omista aktiviteeteista.

- Ryhmät
	- Ryhmiin voi liittyä ja niistä voi poistua.
	- Ryhmistä näkee myös niiden jäsenet.
	- Käyttäjät näkevät listan omien ryhmien jäsenten viimeaikaisista aktiviteeteista dashboard-sivulla.
	- Kaikki omien ryhmien jäsenten aktiviteetit löytyvät linkin takaa.
	- Uusien ryhmien luominen tulee myöhemmin.

- Kommentointi
	- Kommenttien rakenne on jo olemassa, mutta käyttöliittymä kommentointiin on vielä kesken.
	- Aktiviteetin lisäyksen yhteydessä voi jo jättäää oman kommentin aktiviteettiin.
	- Tulossa myös ilmoitusjärjestelmä uusista lukemattomista kommenteista omiin aktiviteetteihin.

## Sovelluksen käynnistäminen paikallisesti

Sovellus tarvitsee toimiakseen käynnissä olevan postgresql-yhteyden. Voit asentaa ja aktivoida postgresql:n [tämän](https://github.com/hy-tsoha/local-pg) ohjeen mukaisesti. Älä unohda lopettaa skriptiä sovelluksen testaamisen jälkeen!

1. Kloonaa repositorio koneellesi ja luo sen juurikansioon tiedosto .env, ja lisää sen sisälle seuraavat rivit:
```
DATABASE_URL=<tietokannan-paikallinen-osoite>
SECRET_KEY=<salainen-avain>
```

2. Aktivoi sen jälkeen virtuaaliympäristö komennolla: 

```
python3 -m venv venv
source venv/bin/activate
```

3. Asenna sitten sovelluksen riippuvuudet komennolla:
```
pip install -r ./requirements.txt
```

4. Määritä sovelluksen tietokannan skeema:
	- Jos haluat tyhjän tietokannan ilman testitietoja:
		```
		psql < schema.sql
		```
	- Jos haluat testitietokannan, jossa on lisättynä muutama ryhmä valmiiksi.
	  Tämän version skeema myös tyhjentää taulut jos haluat nollata tietokannan helposti:
		```
		psql < test_schema.sql
		```

5. Voit nyt käynnistää sovelluksen komennolla:
```
flask run
```
