# Neo4j Geopath Analytics

## Übersicht
Das Projekt **Neo4j-Julian** dient der Modellierung, Abfrage und Visualisierung von Pfadverbindungen und Knotenstrukturen in Graphendatenbanken mittels Neo4j.

## Projektstruktur & Architektur
- `geopath/db.py`: Verbindungsschicht zur Neo4j-Datenbankinstanz.
- `geopath/importer.py`: Importskript zur Konvertierung von Geodaten in Graphknoten.
- `geopath/ui.py`: Grafische Benutzeroberfläche zur Pfadanalyse.
- `geopath/requirements.txt`: Python-Abhängigkeiten zur Neo4j-Anbindung.

## Hauptfunktionalitäten
- **Graph-Modellierung**: Erzeugung von Knoten und Kanten für geografische Daten.
- **Cypher-Abfragen**: Ausführung komplexer Pfadanalysen in Neo4j.
- **Benutzeroberfläche**: Visuelle Aufbereitung von Routen und Verbindungen.

## Ausführung & Nutzung
Die Anwendung erfordert eine laufende Neo4j-Datenbank. Nach Installation der Abhängigkeiten aus `requirements.txt` wird das Interface über `python geopath/ui.py` gestartet.

## Lizenz
Dieses Projekt steht unter der MIT-Lizenz.
