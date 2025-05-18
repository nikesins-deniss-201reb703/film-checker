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
List from typing
re
urllib
requests
typer
Annotated from typing_extensions
PrettyTable 
gql
