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
            posters {
            url
            width
            height
            }
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
                avatars {
                url
                width
                height
                }
            }
            }
            writers: credits(first: 5, categories: ["writer"]) {
            name {
                id
                display_name
                avatars {
                url
                width
                height
                }
            }
            }
            casts: credits(first: 5, categories: ["actor", "actress"]) {
            name {
                id
                display_name
                avatars {
                url
                width
                height
                }
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
            avatars {
                url
                width
                height
            }
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
    

# @app.command()
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
    
    # Print the title
    print("Title: ", result["title"]["primary_title"])
    # Print the plot
    print("Plot: ", result["title"]["plot"])
    # Print the rating
    votes = result["title"]["rating"]["votes_count"]
    print("Rating: ", result["title"]["rating"]["aggregate_rating"], f"({votes} votes)")
    # Print the genres
    print("Genres: ", ", ".join(result["title"]["genres"]))
    # Print the certificates
    for certificate in result["title"]["certificates"]:
        print("Certificate: ", certificate["country"]["name"], certificate["rating"])
    # Print the spoken languages
    for language in result["title"]["spoken_languages"]:
        print("Language: ", language["name"])
    # Print the origin countries
    for country in result["title"]["origin_countries"]:
        print("Country: ", country["name"])
    # Print the critic review
    if result["title"]["critic_review"] is not None:
        # Print the critic review
        print("Critic Review: ", result["title"]["critic_review"]["score"], result["title"]["critic_review"]["review_count"])
    
# @app.command()
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
    
    # Print the name
    print("Name: ", result["name"]["display_name"])
    # Print the birth year
    print("Birth Year: ", result["name"]["birth_year"])
    # Print the birth location
    print("Birth Location: ", result["name"]["birth_location"])
    # Print the death year
    print("Death Year: ", result["name"]["death_year"])
    # Print the death location
    print("Death Location: ", result["name"]["death_location"])
    # Print the dead reason
    print("Dead Reason: ", result["name"]["dead_reason"])
    # Print the known for
    for known in result["name"]["known_for"]:
        print("Known For: ", known["primary_title"])
    
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