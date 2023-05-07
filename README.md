# Lenkkeilysovellus

Sovellus ei ole vielä fly.io-palvelussa. Ohjeet sovelluksen käynnistämiseen paikallisesti README:n [lopussa](https://github.com/samulioll/lenkkeilysovellus/blob/main/README.md#sovelluksen-k%C3%A4ynnist%C3%A4minen-paikallisesti).

## Perusidea

Sovellus mihin käyttäjät voivat lisätä kävellen, juosten tai pyöräillen tekemiään lenkkejä. Sovelluksessa on ominaisuuksia, joilla käyttäjät voivat nähdä yhteenvetoja sekä omista tilastoista että myös muiden (joilla tiedot ovat julkisia). Käyttäjät voivat liittyä ryhmiin ja myös ryhmien yhteenvetoja voi tarkastella. Käyttäjät voivat myös jättää kommentteja muiden aktiviteetteihin.

## Tarkempi kuvaus

- Käyttäjäprofiili
	- Käyttäjät voivat luoda itselleen käyttäjäprofiilin.
	- Käyttäjät voivat asettaa profiilinsa näkyvyyden yksityiseksi.

- Profiilisivu
	- Jokainen käyttäjä näkee tiivistetyt tilastot omista lenkeistään.
	- Jokainen käyttäjä voi nähdä tietyn toisen käyttäjän tilastot jos tämän profiili on julkinen.

- Ryhmät
	- Käyttäjät voivat liittyä ryhmiin.
	- Käyttäjät voivat poistua ryhmistä.
	- Käyttäjät voivat luoda ryhmiä.
	- Ryhmän ylläpitäjät voivat poistaa jäseniä.
	- Ryhmän ylläpitäjät voivat tehdä jäsenistä ylläpitäjiä.
	- Ryhmän omistaja voi poistaa ylläpito-oikeudet.
	- Jos omistaja lähtee ryhmästä niin ensimmäisestä ylläpitäjästä tai sen jälkeen jäsenestä tulee omistaja. Jos ei ole muita jäseniä niin ryhmä poistuu.
	- Ryhmän perustaja voi poistaa ryhmän.

- Ryhmäsivu
	- Ryhmän tilastot.
	- Ryhmän jäsenet.
	- Ryhmän ylläpitosivu ylläpitäjille.

- Lenkkien lisäys tietokantaan
	- Käyttäjät voivat lisätä tekemiään lenkkejä ja niiden tiedot tallennetaan tietokantaan.
	- Kommentin lisäys lenkin lisäyksen yhteydessä.

- Kommentointi
	- Käyttäjät voivat kommentoida lenkkejä.
	- Käyttäjät voivat poistaa omia kommenttejaan.
	- Uusista lukemattomista kommenteista tulee ilmoitus aktiviteetin omistajalle, joka poistuu kun tämä on nähnyt kommentin.

- Leaderboardit
	- Leaderboard käyttäjille.
	- Leaderboard ryhmille.
	- Leaderboardin voi järjestää minkä tahansa tilaston mukaan.

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
	- Jos haluat testitietokannan, jossa on lisättynä muutama ryhmä valmiiksi:
		```
		psql < test_schema.sql
		```

5. Voit nyt käynnistää sovelluksen komennolla:
```
flask run
```
