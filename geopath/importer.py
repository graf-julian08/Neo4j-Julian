"""
importer.py - REST Countries API → Neo4j Import
================================================
Dieses Modul lädt Länder-Daten von der REST Countries API
und importiert sie in die Neo4j Graph-Datenbank.
"""

import requests
from db import db


# REST Countries API Endpoint (mit fields Parameter, da /all ohne fields 400 zurückgibt)
API_URL = "https://restcountries.com/v3.1/all?fields=name,cca3,population,capital,continents,borders"


def fetch_countries_from_api():
    """
    Ruft alle Länder von der REST Countries API ab.
    
    Returns: Liste von Länder-Dictionaries oder None bei Fehler
    """
    print("📡 Lade Daten von REST Countries API...")
    
    try:
        response = requests.get(API_URL, timeout=30)
        response.raise_for_status()  # Wirft Exception bei HTTP Fehlern
        
        countries = response.json()
        print(f"✓ {len(countries)} Länder von API geladen!")
        return countries
        
    except requests.exceptions.Timeout:
        print("✗ Timeout: API antwortet nicht.")
        return None
    except requests.exceptions.RequestException as e:
        print(f"✗ API Fehler: {e}")
        return None


def extract_country_data(country_json):
    """
    Extrahiert die relevanten Daten aus dem API-Response.
    
    Args:
        country_json: Ein Länder-Objekt aus der API
        
    Returns: Dictionary mit den extrahierten Daten
    """
    # Name des Landes (common name)
    name = country_json.get("name", {}).get("common", "Unknown")
    
    # CCA3 Code für die Nachbar-Zuordnung (z.B. "DEU", "FRA")
    cca3 = country_json.get("cca3", "")
    
    # Bevölkerung
    population = country_json.get("population", 0)
    
    # Hauptstadt (kann eine Liste sein, wir nehmen die erste)
    capitals = country_json.get("capital", [])
    capital = capitals[0] if capitals else "Unknown"
    
    # Kontinent (kann mehrere sein, wir nehmen den ersten)
    continents = country_json.get("continents", [])
    continent = continents[0] if continents else "Unknown"
    
    # Nachbarländer (Liste von CCA3 Codes)
    borders = country_json.get("borders", [])
    
    return {
        "name": name,
        "cca3": cca3,
        "population": population,
        "capital": capital,
        "continent": continent,
        "borders": borders
    }


def import_to_neo4j(countries_data):
    """
    Importiert alle Länder-Daten in die Neo4j Datenbank.
    
    Ablauf:
    1. Datenbank leeren (optional, für sauberen Import)
    2. Continents als Nodes anlegen
    3. Countries als Nodes anlegen
    4. LOCATED_IN Relationships erstellen
    5. BORDERS Relationships erstellen (bidirektional)
    
    Args:
        countries_data: Liste der API-Daten
    """
    print("\n🔄 Starte Neo4j Import...")
    
    # Daten extrahieren
    countries = [extract_country_data(c) for c in countries_data]
    
    # Mapping: CCA3 Code → Ländername (für Nachbar-Zuordnung)
    cca3_to_name = {c["cca3"]: c["name"] for c in countries}
    
    with db.driver.session() as session:
        # 1. Datenbank leeren
        print("  → Lösche alte Daten...")
        session.run("MATCH (n) DETACH DELETE n")
        
        # 2. Kontinente anlegen (MERGE = erstellen falls nicht existiert)
        print("  → Erstelle Kontinente...")
        continents = set(c["continent"] for c in countries)
        for continent in continents:
            session.run(
                "MERGE (co:Continent {name: $name})",
                name=continent
            )
        
        # 3. Länder anlegen
        print("  → Erstelle Länder...")
        for country in countries:
            session.run("""
                MERGE (c:Country {name: $name})
                SET c.population = $population,
                    c.capital = $capital,
                    c.cca3 = $cca3
            """, 
                name=country["name"],
                population=country["population"],
                capital=country["capital"],
                cca3=country["cca3"]
            )
        
        # 4. LOCATED_IN Relationships
        print("  → Verknüpfe Länder mit Kontinenten...")
        for country in countries:
            session.run("""
                MATCH (c:Country {name: $country_name})
                MATCH (co:Continent {name: $continent_name})
                MERGE (c)-[:LOCATED_IN]->(co)
            """,
                country_name=country["name"],
                continent_name=country["continent"]
            )
        
        # 5. BORDERS Relationships (bidirektional!)
        print("  → Erstelle Nachbarschafts-Beziehungen...")
        border_count = 0
        for country in countries:
            for border_code in country["borders"]:
                # CCA3 Code in Ländername umwandeln
                neighbor_name = cca3_to_name.get(border_code)
                if neighbor_name:
                    # Bidirektional: A→B und B→A
                    session.run("""
                        MATCH (a:Country {name: $country_name})
                        MATCH (b:Country {name: $neighbor_name})
                        MERGE (a)-[:BORDERS]->(b)
                        MERGE (b)-[:BORDERS]->(a)
                    """,
                        country_name=country["name"],
                        neighbor_name=neighbor_name
                    )
                    border_count += 1
        
        print(f"  → {border_count} Nachbarschafts-Beziehungen erstellt.")
    
    # Statistik ausgeben
    total = db.get_total_countries()
    print(f"\n✅ Import abgeschlossen!")
    print(f"   → {total} Länder in der Datenbank")
    
    # Kontinent-Statistik
    stats = db.get_continent_statistics()
    print("\n   Länder pro Kontinent:")
    for stat in stats:
        print(f"   • {stat['continent']}: {stat['count']} Länder")


def run_import():
    """
    Hauptfunktion für den kompletten Import-Prozess.
    
    Returns: True bei Erfolg, False bei Fehler
    """
    # Verbindung prüfen
    if not db.driver:
        if not db.connect():
            return False
    
    # Daten von API laden
    countries_data = fetch_countries_from_api()
    if not countries_data:
        return False
    
    # In Neo4j importieren
    try:
        import_to_neo4j(countries_data)
        return True
    except Exception as e:
        print(f"✗ Import-Fehler: {e}")
        return False


# ============================================================
# Für direkten Aufruf: python importer.py
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("GeoPath Challenge - Datenimport")
    print("=" * 50)
    
    if db.connect():
        run_import()
        db.close()
