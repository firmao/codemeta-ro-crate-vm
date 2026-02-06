import json
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD

# Manually define the Schema.org namespace
SCHEMA = Namespace("http://schema.org/")

# Now you can use it just like before:
# g.add((event_uri, SCHEMA.location, Literal("Central Park")))

def create_knowledge_graph(data_source):
    # 1. Initialize the Graph and Namespaces
    g = Graph()
    EX = Namespace("http://example.org/user/")
    
    # 2. Load your Google Data (Simulated JSON structure)
    # In a real scenario, use: with open('location_history.json') as f: data = json.load(f)
    data = [
        {"timestamp": "2026-02-06T10:00:00Z", "place": "Central Park", "activity": "Walking"},
        {"timestamp": "2026-02-06T12:00:00Z", "place": "Joe's Coffee", "activity": "Stationary"}
    ]

    for i, entry in enumerate(data):
        # Create a unique URI for each event
        event_uri = EX[f"event_{i}"]
        
        # 3. Add Triples (Subject -> Predicate -> Object)
        g.add((event_uri, RDF.type, SCHEMA.Event))
        g.add((event_uri, SCHEMA.startDate, Literal(entry['timestamp'], datatype=XSD.dateTime)))
        g.add((event_uri, SCHEMA.location, Literal(entry['place'])))
        g.add((event_uri, SCHEMA.description, Literal(entry['activity'])))

    # 4. Serialize the graph to a file (Turtle format is very readable)
    g.serialize(destination='google_donation_kg.ttl', format='turtle')
    print("Knowledge Graph created: google_donation_kg.ttl")

if __name__ == "__main__":
    create_knowledge_graph("google_data.json")