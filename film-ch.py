from typing import List
import urllib.parse as urlparse
import typer
from typing_extensions import Annotated
import requests
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

def searchByName(name):
    response = requests.get(searchApiUrl(name))
    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}")
    data = response.json()
    
    for item in data["d"]:
        print("id: ", item["id"])
        print("name: ", item["l"])
        print("summary: ", item["s"])
        print("---------------------")

# @app.command()
def getTitle(id):
    # Provide a GraphQL query
    query = gql(titleById)

    # Execute the query on the transport
    result = client.execute(query, variable_values={"id": "tt0944947"})
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
    result = client.execute(query, variable_values={"id": "nm0908094"})
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
    
def main(name: List[str], person: Annotated[bool, typer.Option("--person", "-p")] = False, title: Annotated[bool, typer.Option("--title", "-t")] = True):
    name = " ".join(name)
    print(f"Searching: {name}")
    
    # if (person):
    #     # Search for a person
    #     print("Searching for a person...")
    #     # searchPerson(name)
    # elif (title):
    #     # Search for a title
    #     print("Searching for a title...")
    #     getTitle(name)
        
    searchByName(name)

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