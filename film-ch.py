import typer
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

app = typer.Typer(name="Film Checker", help="A simple way to check films and their details.", add_completion=False, pretty_exceptions_enable=False)

@app.command()
def hello(name: str):
    print(f"Hello {name}")
    
@app.command()
def goodbye(name: str, formal: bool = False):
    if formal:
        print(f"Goodbye Ms. {name}. Have a good day.")
    else:
        print(f"Bye {name}!")

@app.command()
def gqldemo():
    """
    A simple GraphQL demo using the gql library.
    """

    # Select your transport with a defined url endpoint
    transport = AIOHTTPTransport(url="https://graph.imdbapi.dev/v1", ssl=True)

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Provide a GraphQL query
    query = gql(
        """
        query titleById {
        title(id: "tt0944947") {
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
    )

    # Execute the query on the transport
    result = client.execute(query)
    print(result)

if __name__ == "__main__":
    app()
    
    
# Programm block sheme
# query (person name or title name) -> find person or title id -> show details
# default options:
# - search title by closest name
# possible options:
# - search person by closest name -p name
# - show person list -P name
# - search title by closest name -t name
# - show title list -T name