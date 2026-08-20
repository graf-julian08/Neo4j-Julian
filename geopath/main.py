#!/usr/bin/env python3
"""
main.py - Einstiegspunkt für GeoPath Challenge
===============================================

GeoPath Challenge ist ein Lern-Spiel, bei dem Spieler
Nachbarländer erraten müssen. Das Spiel nutzt:
- Neo4j als Graph-Datenbank
- REST Countries API für echte Länderdaten
- tkinter für die grafische Oberfläche

Autor: GeoPath Team
Lizenz: MIT
"""

from ui import GeoPathApp


def main():
    """Hauptfunktion - startet die Anwendung."""
    print("=" * 50)
    print("🌍 GeoPath Challenge")
    print("=" * 50)
    print()
    print("Starte Anwendung...")
    print("Tipp: Überprüfe die Neo4j Credentials in db.py")
    print()
    
    # Anwendung erstellen und starten
    app = GeoPathApp()
    
    # Cleanup beim Schließen
    app.root.protocol("WM_DELETE_WINDOW", app.on_close)
    
    # Hauptschleife starten
    app.run()


if __name__ == "__main__":
    main()
