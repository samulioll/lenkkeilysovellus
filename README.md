# Lenkkeilysovellus

Sovellus ei ole vielä fly.io-palvelussa. Ohjeet sovelluksen käynnistämiseen paikallisesti README:n lopussa.

## Perusidea

Sovellus mihin käyttäjät voivat lisätä kävellen, juosten tai pyöräillen tekemiään lenkkejä. Sovelluksessa on ominaisuuksia, joilla käyttäjät voivat nähdä yhteenvetoja sekä omista tilastoista että myös muiden (joilla tiedot ovat julkisia). Käyttäjät voivat liittyä ryhmiin ja myös ryhmien yhteenvetoja voi tarkastella. Käyttäjät voivat myös jättää kommentteja muiden aktiviteetteihin.

## Tarkempi kuvaus

- Käyttäjäprofiili
	- Käyttäjät voivat luoda itselleen käyttäjäprofiilin.

- Ryhmät
	- Käyttäjät voivat liittyä ryhmiin.

- Lenkkien lisäys tietokantaan
	- Käyttäjät voivat lisätä tekemiään lenkkejä ja niiden tiedot tallennetaan tietokantaan.

- Henkilökohtaiset tilastot
	- Jokainen käyttäjä näkee monipuoliset tilastot omista lenkeistään.

- Tietyn käyttäjän tilastot
	- Jokainen käyttäjä voi nähdä tietyn toisen käyttäjän tilastot jos tämä käyttäjä on asettanut se julkiseksi

- Kaikkien käyttäjien tilastot
	- Jokainen käyttäjä voi nähdä tilastot kaikkien käyttäjien tekemistä lenkeistä, riippumatta yksityisyysasetuksista. Kokonaistilastoista ei kuitenkaan voi yksilöidä käyttäjiä.

## Tilanne 2.4.

Sovelluksen perusrakenne on kasassa. Käyttäjäprofiilin luominen onnistuu ja sisään- ja uloskirjautuminen on mahdollista. Myös aktiviteettien lisäämisen peruslogiikka on kasassa, joskin alkeellisessa muodossa. Käyttäjät näkevät kaikki aktiviteettinsa omalla "dashboard"-sivulla. 

- Käyttäjäprofiilit
	- Sovellus tunnistaa jos käyttäjä yrittää rekisteröityä käyttäjänimellä joka on jo käytössä.
	- Salasana pyydetään kahdesti jolla varmistetaan että käyttäjä kirjoittaa sen oikein.
	- Sisään- ja uloskirjautuminen toimii oikein.

- Aktiviteetit
	- Aktiviteettien lisääminen onnistuu dashboard-sivun kautta. 
	- Toistaiseksi uusien reittien lisääminen ei ole mahdollista, mutta se ominaisuus on tulossa.
	- Aktiviteettien kommentointi ei ole vielä mahdollista.
	- Käyttäjät näkevät listan kaikista aktiviteeteistaan dashboard-sivulla.
	- Tulevaisuudessa dashboard-sivulta näkee myös tiivistetysti tilastoja omista aktiviteeteista.

- Ryhmät
	- Ei vielä toiminnallisuutta ryhmien luomiseen tai niihin liittymiseen.
	- Ryhmien aktiviteettien yhteenvedon näkeminen tulee myös myöhemmin.

## Sovelluksen käynnistäminen paikallisesti

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

4. Määritä sovelluksen tietokannan skeema komennolla:
~~~
psql < schema.sql
~~~

5. Voit nyt käynnistää sovelluksen komennolla:
	flask run
