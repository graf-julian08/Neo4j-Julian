"""
db.py - Neo4j Datenbankverbindung und Cypher-Queries
=====================================================
Dieses Modul stellt die Verbindung zur Neo4j Datenbank her
und enthält alle Cypher-Queries für das Spiel.
"""

from neo4j import GraphDatabase


# ============================================================
# KONFIGURATION - HIER DEINE NEO4J CREDENTIALS EINTRAGEN!
# ============================================================
# URI: Normalerweise "bolt://localhost:7687" für lokale Neo4j Desktop Installation
# USER: Standardmäßig "neo4j"
# PASSWORD: Das Passwort, das du beim Erstellen der Datenbank gesetzt hast

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Nailuj18@NESA08"  # <-- HIER DEIN PASSWORT EINTRAGEN!


class Database:
    """
    Klasse für die Neo4j Datenbankverbindung.
    Verwendet den offiziellen Neo4j Python Driver.
    """
    
    def __init__(self):
        """Initialisiert die Datenbankverbindung."""
        self.driver = None
        
    def connect(self):
        """
        Stellt die Verbindung zur Neo4j Datenbank her.
        Returns: True bei Erfolg, False bei Fehler
        """
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD)
            )
            # Verbindung testen
            self.driver.verify_connectivity()
            print("✓ Verbindung zur Neo4j Datenbank hergestellt!")
            return True
        except Exception as e:
            print(f"✗ Fehler bei der Verbindung: {e}")
            return False
    
    def close(self):
        """Schließt die Datenbankverbindung."""
        if self.driver:
            self.driver.close()
            print("Datenbankverbindung geschlossen.")
    
    # ============================================================
    # CYPHER QUERIES - Die wichtigsten Abfragen für das Spiel
    # ============================================================
    
    def get_random_country(self):
        """
        Holt ein zufälliges Land aus der Datenbank.
        
        Cypher Query:
        MATCH (c:Country)
        RETURN c ORDER BY rand() LIMIT 1
        
        Returns: Dictionary mit Länder-Daten oder None
        """
        query = """
        MATCH (c:Country)
        RETURN c.name AS name, c.population AS population, c.capital AS capital
        ORDER BY rand() LIMIT 1
        """
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            if record:
                return {
                    "name": record["name"],
                    "population": record["population"],
                    "capital": record["capital"]
                }
            return None
    
    def get_neighbors(self, country_name):
        """
        Holt alle Nachbarländer eines bestimmten Landes.
        
        Cypher Query:
        MATCH (c:Country {name:$name})-[:BORDERS]->(n:Country)
        RETURN n.name
        
        Args:
            country_name: Name des Landes
            
        Returns: Liste von Nachbarländer-Namen
        """
        query = """
        MATCH (c:Country {name: $name})-[:BORDERS]->(n:Country)
        RETURN n.name AS neighbor
        """
        with self.driver.session() as session:
            result = session.run(query, name=country_name)
            return [record["neighbor"] for record in result]
    
    def get_random_country_with_neighbors(self):
        """
        Holt ein zufälliges Land, das mindestens einen Nachbarn hat.
        Wichtig für das Quiz - Inselstaaten werden ausgeschlossen.
        
        Returns: Dictionary mit Länder-Daten oder None
        """
        query = """
        MATCH (c:Country)-[:BORDERS]->(n:Country)
        WITH c, count(n) AS neighbor_count
        WHERE neighbor_count > 0
        RETURN c.name AS name, c.population AS population, c.capital AS capital
        ORDER BY rand() LIMIT 1
        """
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            if record:
                return {
                    "name": record["name"],
                    "population": record["population"],
                    "capital": record["capital"]
                }
            return None
    
    def get_random_countries(self, count=4, exclude=None):
        """
        Holt mehrere zufällige Länder (für falsche Antworten).
        
        Args:
            count: Anzahl der Länder
            exclude: Liste von Ländern, die ausgeschlossen werden sollen
            
        Returns: Liste von Länder-Namen
        """
        if exclude is None:
            exclude = []
        
        query = """
        MATCH (c:Country)
        WHERE NOT c.name IN $exclude
        RETURN c.name AS name
        ORDER BY rand() LIMIT $count
        """
        with self.driver.session() as session:
            result = session.run(query, exclude=exclude, count=count)
            return [record["name"] for record in result]
    
    def get_country_details(self, country_name):
        """
        Holt detaillierte Informationen zu einem Land.
        
        Args:
            country_name: Name des Landes
            
        Returns: Dictionary mit allen Details
        """
        query = """
        MATCH (c:Country {name: $name})
        OPTIONAL MATCH (c)-[:LOCATED_IN]->(co:Continent)
        OPTIONAL MATCH (c)-[:BORDERS]->(n:Country)
        RETURN c.name AS name, 
               c.population AS population, 
               c.capital AS capital,
               co.name AS continent,
               collect(n.name) AS neighbors
        """
        with self.driver.session() as session:
            result = session.run(query, name=country_name)
            record = result.single()
            if record:
                return {
                    "name": record["name"],
                    "population": record["population"],
                    "capital": record["capital"],
                    "continent": record["continent"],
                    "neighbors": record["neighbors"]
                }
            return None
    
    def get_continent_statistics(self):
        """
        Holt Statistiken: Anzahl Länder pro Kontinent.
        
        Cypher Query:
        MATCH (co:Continent)<-[:LOCATED_IN]-(c:Country)
        RETURN co.name, count(c)
        
        Returns: Liste von Dictionaries mit Kontinent und Anzahl
        """
        query = """
        MATCH (co:Continent)<-[:LOCATED_IN]-(c:Country)
        RETURN co.name AS continent, count(c) AS country_count
        ORDER BY country_count DESC
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [{"continent": r["continent"], "count": r["country_count"]} 
                    for r in result]
    
    def get_total_countries(self):
        """Zählt die Gesamtanzahl der Länder in der Datenbank."""
        query = "MATCH (c:Country) RETURN count(c) AS total"
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            return record["total"] if record else 0
    
    def clear_database(self):
        """
        Löscht alle Nodes und Relationships aus der Datenbank.
        Wird vor dem Import aufgerufen.
        """
        query = "MATCH (n) DETACH DELETE n"
        with self.driver.session() as session:
            session.run(query)
            print("✓ Datenbank geleert.")
    
    # ============================================================
    # NEUE QUERIES FÜR ERWEITERTE FRAGETYPEN
    # ============================================================
    
    def get_random_country_with_capital(self):
        """
        Holt ein zufälliges Land mit bekannter Hauptstadt.
        Für Hauptstadt-Fragen.
        """
        query = """
        MATCH (c:Country)
        WHERE c.capital IS NOT NULL AND c.capital <> "Unknown"
        RETURN c.name AS name, c.capital AS capital
        ORDER BY rand() LIMIT 1
        """
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            if record:
                return {"name": record["name"], "capital": record["capital"]}
            return None
    
    def get_random_capitals(self, count=3, exclude=None):
        """
        Holt zufällige Hauptstädte für falsche Antworten.
        """
        if exclude is None:
            exclude = []
        
        query = """
        MATCH (c:Country)
        WHERE c.capital IS NOT NULL 
          AND c.capital <> "Unknown"
          AND NOT c.capital IN $exclude
        RETURN DISTINCT c.capital AS capital
        ORDER BY rand() LIMIT $count
        """
        with self.driver.session() as session:
            result = session.run(query, exclude=exclude, count=count)
            return [record["capital"] for record in result]
    
    def get_random_country_with_continent(self):
        """
        Holt ein zufälliges Land mit Kontinent.
        Für Kontinent-Fragen.
        """
        query = """
        MATCH (c:Country)-[:LOCATED_IN]->(co:Continent)
        RETURN c.name AS name, co.name AS continent
        ORDER BY rand() LIMIT 1
        """
        with self.driver.session() as session:
            result = session.run(query)
            record = result.single()
            if record:
                return {"name": record["name"], "continent": record["continent"]}
            return None
    
    def get_all_continents(self):
        """Holt alle Kontinente für Multiple-Choice."""
        query = """
        MATCH (co:Continent)
        RETURN co.name AS name
        ORDER BY co.name
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [record["name"] for record in result]
    
    def check_if_neighbors(self, country1, country2):
        """
        Prüft ob zwei Länder Nachbarn sind.
        Für Ja/Nein Fragen.
        """
        query = """
        MATCH (a:Country {name: $country1})-[:BORDERS]->(b:Country {name: $country2})
        RETURN count(*) > 0 AS are_neighbors
        """
        with self.driver.session() as session:
            result = session.run(query, country1=country1, country2=country2)
            record = result.single()
            return record["are_neighbors"] if record else False
    
    def get_two_random_countries(self):
        """Holt zwei zufällige Länder für Ja/Nein Fragen."""
        query = """
        MATCH (c:Country)
        RETURN c.name AS name
        ORDER BY rand() LIMIT 2
        """
        with self.driver.session() as session:
            result = session.run(query)
            countries = [record["name"] for record in result]
            if len(countries) == 2:
                return countries
            return None


# ============================================================
# Globale Datenbankinstanz
# ============================================================
db = Database()
