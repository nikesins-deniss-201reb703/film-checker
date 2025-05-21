# film-checker

## Vispārīgs apraksts

Ši programma ļauj apkopot dažādu informāciju par jums interesējošu filmu vai seriālu, izmantojot IMDB tīmekļa API un GRAPHQL. Ar šīs programmas palīdzību jūs varat iegūt tādus datus kā filmas reitingu, nelielu aprakstu par sižetu, izdošanas gadu, žanrus, oriģinālvalodas, kurās ir izdota filma, vecuma ierobežojumu filmai. Kā arī ir iespēja iegūt informāciju par interesējošo aktieri, viņa biogrāfiju un kādās filmās tas piedalījās. Programma var izmantot meklēšanai arī filmas,seriāla vai aktiera ID no IMBD tīmekļa vietnes.

## Programmas izmantošana

Lai izmantot programmu, jums vajag ievadīt sekojošus datus:

* IMDB vietnes meklēšanas loga izmantošanai:  python film-ch.py -s
* Meklēšana pēc aktiera vārda un uzvārda: python film-ch.py -p
* Meklēšana pēc filmas vai seriāla nosaukuma: python film-ch.py -t
* Palīdzībai ar programmas komandām: python film-ch.py --help

## Izmantotās bibliotēkas

Mēs izmantojām šīs bibliotēkas, lai nodrošinātu programmas funkcionalitāti:

* `re` – regulāro izteiksmju izmantošanai, lai atškirtu id no nosaukuma.
* `requests` – vienkāršotai un ērtai HTTP pieprasījumu veikšanai.
* `urllib` – lai apstrādātu URL un veiktu HTTP pieprasījumus.
* `typer` – komandrindas interfeisa izveidei un argumentu apstrādei.
* `Annotated` no `typing_extensions` – izmantojam, lai citēt argumentu metadatus.
* `PrettyTable` – datu attēlošanai tabulas formātā konsolē.
* `gql` – GraphQL pieprasījumu veikšanai un datu iegūšanai no API.
* `List` no `typing` – lai izmantotu standarta List datu tipa implementēšanai Python.
