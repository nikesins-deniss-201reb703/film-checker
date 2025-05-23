from typing import List
import re
import urllib.parse as urlparse
import requests
import typer
from typing_extensions import Annotated
from prettytable import PrettyTable 
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

app = typer.Typer(
    name="Film Checker", 
    help="A simple way to check films and their details.", 
    add_completion=False, 
    pretty_exceptions_enable=False
)

gqlApiUrl = "https://graph.imdbapi.dev/v1"
def searchApiUrl(query):
    query = urlparse.quote_plus(query)
    return f"https://v3.sg.media-imdb.com/suggestion/x/{query}.json"

# Select your transport with a defined url endpoint
transport = AIOHTTPTransport(url=gqlApiUrl, ssl=True)
# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)

# GraphQL queries
titleById = """
    query titleById($id: ID!) {
        title(id: $id) {
            id
            type
            is_adult
            primary_title
            original_title
            start_year
            end_year
            runtime_minutes
            plot
            rating {
                aggregate_rating
                votes_count
            }
            genres
            certificates {
                country {
                    code
                    name
                }
                rating
            }
            spoken_languages {
                code
                name
            }
            origin_countries {
                code
                name
            }
            critic_review {
                score
                review_count
            }
            directors: credits(first: 5, categories: ["director"]) {
                name {
                    id
                    display_name
                }
            }
            writers: credits(first: 5, categories: ["writer"]) {
                name {
                    id
                    display_name
                }
            }
            casts: credits(first: 5, categories: ["actor", "actress"]) {
                name {
                    id
                    display_name
                }
                characters
            }
        }
    }
"""

personById = """
    query nameById($id: ID!) {
        name(id: $id) {
            id
            display_name
            alternate_names
            birth_year
            birth_location
            death_year
            death_location
            dead_reason
            known_for {
                id
                primary_title
            }
        }
    }
"""

def searchByName(name, search, personOrTitle=''):
    response = requests.get(searchApiUrl(name))
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}")
    data_json = response.json()
    if "d" not in data_json:
        raise Exception("Error: No data found")
    data = data_json["d"]
    if len(data) == 0:
        raise Exception("Error: No data found")
    
    table = PrettyTable(["id", "name", "summary"])
    table.add_autoindex()
    foundExactMatch = 0
    data_excactMatch = []
    
    for index, item in enumerate(data):
        item_id = item.setdefault("id", "")
        item_name = item.setdefault("l", "")
        item_summary = item.setdefault("s", "")
        
        table.add_row([index, item_id, name, item_summary])
        if not search:
            if item_id.startswith(personOrTitle) and item_name.lower() == name.lower():
                foundExactMatch += 1
                data_excactMatch.append(item)
                # return item_id
                
    if foundExactMatch > 0:
        print("if you want to search and get all search candidates, please use -s option")
        if len(data_excactMatch) == 1:
            # Get the id of the selected item
            selectedItem = data_excactMatch[0]
            selectedId = selectedItem["id"]
            print("Found excact match: ", item_name)
            return selectedId
        else:
            # Print the table
            print("Found multiple exact matches:")
            table = PrettyTable(["id", "name", "summary"])
            table.add_autoindex()
            for index, item in enumerate(data_excactMatch):
                item_id = item.setdefault("id", "")
                item_name = item.setdefault("l", "")
                item_summary = item.setdefault("s", "")
                
                table.add_row([index, item_id, name, item_summary])
        
    print(table)
    
    searchIndex = typer.prompt("Enter index of what you searching? (nothing to cancel)", default=-1, type=int)
    if searchIndex == -1:
        print("Cancelled")
        return
    
    if foundExactMatch > 0 and (searchIndex < 0 or searchIndex >= len(data_excactMatch)):
        print("Invalid index")
        return
    elif searchIndex < 0 or searchIndex >= len(data):
        print("Invalid index")
        return
    
    # Get the id of the selected item
    selectedItem = []
    if foundExactMatch > 0:
        # Get the id of the selected item
        selectedItem = data_excactMatch[searchIndex]
    else:
        # Get the id of the selected item
        selectedItem = data[searchIndex]
    selectedId = selectedItem["id"]
    return selectedId

def getTitleOrPerson(id):
    # if id has "tt" prefix, it is a title
    if id.startswith("tt"):
        # Get the title details
        getTitle(id)
    # if id has "nm" prefix, it is a person
    elif id.startswith("nm"):
        # Get the person details
        getPerson(id)
    
def getTitle(id):
    # Provide a GraphQL query
    query = gql(titleById)

    # Execute the query on the transport
    result = client.execute(query, variable_values={"id": id})
    # Print the result
    printTitleResult(result)
    
def printTitleResult(result):
    # Print the result
    # print(result)

    data = result["title"]
    id = data["id"]
    title = data["primary_title"]
    original_title = data["original_title"]
    start_year = data["start_year"]
    end_year = data["end_year"]
    runtime_minutes = data["runtime_minutes"]
    is_adult = data["is_adult"]
    type = data["type"]
    plot = data["plot"]
    rating = data["rating"]
    aggregate_rating = rating["aggregate_rating"]
    votes_count = rating["votes_count"]
    genres = data["genres"]
    certificates = data["certificates"]
    spoken_languages = data["spoken_languages"]
    origin_countries = data["origin_countries"]
    critic_review = data["critic_review"]
    directors = data["directors"]
    writers = data["writers"]
    casts = data["casts"]
    
    str_to_print = f"{title} ({id})"
    if original_title:
        str_to_print += f", {original_title}"
    str_to_print += "\n"
    if type:
        str_to_print += f"Type: {type}"
        str_to_print += "\n"
    if start_year:
        str_to_print += f"Released in {start_year}"
    if end_year:
        str_to_print += f" - {end_year}"
    if start_year or end_year:
        str_to_print += "\n"
    if runtime_minutes:
        str_to_print += f"Runtime: {runtime_minutes} minutes"
        str_to_print += "\n"
    if is_adult != None:
        str_to_print += f"Adult: {is_adult}"
        str_to_print += "\n"
    if plot:
        str_to_print += f"Plot: {plot}"
        str_to_print += "\n"
    if rating:
        str_to_print += f"Rating: {aggregate_rating} ({votes_count} votes)"
        str_to_print += "\n"
    if genres:
        str_to_print += f"Genres: {', '.join(genres)}"
        str_to_print += "\n"
    if certificates:
        str_to_print += f"Certificates: ({len(certificates)}) \n"
        for certificate in certificates:
            country = certificate["country"]
            country_name = country["name"]
            rating = certificate["rating"]
            str_to_print += " "*4 + f"{country_name}: {rating}\n"
    if spoken_languages:
        str_to_print += f"Spoken languages: ({len(spoken_languages)}) \n"
        for language in spoken_languages:
            language_name = language["name"]
            str_to_print += " "*4 + f"{language_name}"
        str_to_print += "\n"
    if origin_countries:
        str_to_print += f"Origin countries: ({len(origin_countries)}) \n"
        for country in origin_countries:
            country_name = country["name"]
            str_to_print += " "*4 + f"{country_name}\n"
    if critic_review:
        str_to_print += f"Critic review: {critic_review['score']} ({critic_review['review_count']} reviews)"
        str_to_print += "\n"
    if directors:
        str_to_print += f"Directors: ({len(directors)}) \n"
        for director in directors:
            director_name = director["name"]["display_name"]
            director_id = director["name"]["id"]
            str_to_print += " "*4 + f"{director_name} ({director_id})\n"
    if writers:
        str_to_print += f"Writers: ({len(writers)}) \n"
        for writer in writers:
            writer_name = writer["name"]["display_name"]
            writer_id = writer["name"]["id"]
            str_to_print += " "*4 + f"{writer_name} ({writer_id})\n"
    if casts:
        str_to_print += f"Casts: ({len(casts)}) \n"
        for cast in casts:
            cast_name = cast["name"]["display_name"]
            cast_id = cast["name"]["id"]
            characters = cast["characters"]
            str_to_print += " "*4 + f"{cast_name} ({cast_id})"
            if isinstance(characters, list):
                str_to_print += f", {', '.join(characters)}"
            str_to_print += "\n"

    print("-" * 20)
    print(str_to_print)

def getPerson(id):
    # Provide a GraphQL query
    query = gql(personById)

    # Execute the query on the transport
    result = client.execute(query, variable_values={"id": id})
    # Print the result
    printPersonResult(result)
    
def printPersonResult(result):
    # Print the result
    # print(result)

    data = result["name"]
    id = data["id"]
    name = data["display_name"]
    alt_name = data["alternate_names"]
    birth_year = data["birth_year"]
    birth_location = data["birth_location"]
    death_year = data["death_year"]
    death_location = data["death_location"]
    dead_reason = data["dead_reason"]
    known_for = data["known_for"]

    str_to_print = f"{name} ({id})"
    if alt_name:
        str_to_print += f", also known as ({', '.join(alt_name)})"
    str_to_print += "\n"

    if birth_year:
        str_to_print += f"Born in {birth_year}"
    if birth_location:
        str_to_print += f", {birth_location}"
    if birth_year or birth_location:
        str_to_print += "\n"

    if death_year:
        str_to_print += f"Dead in {death_year}"
    if death_location:
        str_to_print += f", {death_location}"
    if dead_reason:
        str_to_print += f", {dead_reason}"
    if death_year or death_location or dead_reason:
        str_to_print += "\n"
    
    if known_for:
        str_to_print += f"Known for ({len(known_for)}): \n"
        for known in known_for:
            str_to_print += " "*4 + f"{known['primary_title']} ({known['id']}), \n"
        str_to_print = str_to_print[:-3]

    print("-" * 20)
    print(str_to_print)
    
def main(name: List[str], search: Annotated[bool, typer.Option("--search", "-s")] = False, person: Annotated[bool, typer.Option("--person", "-p")] = False, title: Annotated[bool, typer.Option("--title", "-t")] = False):
    name = " ".join(name)
    # Check if the name is empty
    if not name:
        print("Name is empty")
        return
    print("Searching for:", name)
    
    # print("search: ", search)
    # print("person: ", person)
    # print("title: ", title)
    
    # Check if the search is id
    if re.match(r"^(tt|nm)\d+$", name):
        print("Searching by id:", name)
        getTitleOrPerson(name)
        return
        
    personOrTitle = ''
    if title:
        personOrTitle = 'tt'
    elif person:
        personOrTitle = 'nm'
    # print("personOrTitle: ", personOrTitle)
    try:
        # Search for the title or person
        id = searchByName(name, search, personOrTitle)
    except Exception as e:
        print(e)
        return
    
    if id is None:
        return
    
    print("Selected id: ", id)
    
    # Get the title or person details
    getTitleOrPerson(id)
    
if __name__ == "__main__":
    typer.run(main)
    
# Programm block sheme
# query (person name or title name) -> find person or title id -> show details
# default options:
# - search title by closest name
# possible options:
# - search person by closest name -p name
# - show person list -P name
# - search title by closest name -t name
# - show title list -T name