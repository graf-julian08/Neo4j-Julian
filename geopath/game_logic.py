"""
game_logic.py - Spiellogik für GeoPath Challenge
=================================================
Dieses Modul enthält die Kernlogik des Spiels:
- Verschiedene Fragetypen generieren
- Antworten auswerten mit Streak-System
- Punktestand mit Multiplikator verwalten
"""

import random
from db import db
from enum import Enum


class QuestionType(Enum):
    """Verschiedene Fragetypen für Abwechslung."""
    NEIGHBOR = "neighbor"        # Welches Land grenzt an X?
    YES_NO = "yes_no"           # Grenzen A und B aneinander?
    CAPITAL = "capital"         # Wie heißt die Hauptstadt von X?
    CONTINENT = "continent"     # Auf welchem Kontinent liegt X?


class GameState:
    """
    Verwaltet den aktuellen Spielzustand.
    Erweitert mit Streak-System und Multi-Fragetypen.
    """
    
    def __init__(self):
        """Initialisiert einen neuen Spielzustand."""
        self.score = 0                    # Aktuelle Punktzahl
        self.rounds_played = 0            # Anzahl gespielter Runden
        self.max_rounds = 10              # Maximale Runden pro Spiel
        self.streak = 0                   # Aktuelle Richtig-Serie
        self.best_streak = 0              # Beste Serie im Spiel
        self.current_question_type = None # Aktueller Fragetyp
        self.current_country = None       # Aktuelles Land (Dictionary)
        self.current_correct_answer = None  # Richtige Antwort
        self.current_options = []         # Alle Antwortoptionen
        self.highscore = 0                # Session Highscore
    
    def reset(self):
        """Setzt das Spiel zurück (behält Highscore)."""
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        self.rounds_played = 0
        self.streak = 0
        self.best_streak = 0
        self.current_question_type = None
        self.current_country = None
        self.current_correct_answer = None
        self.current_options = []
    
    def get_multiplier(self):
        """Berechnet den Streak-Multiplikator."""
        if self.streak >= 5:
            return 3  # 3x ab 5 richtigen
        elif self.streak >= 3:
            return 2  # 2x ab 3 richtigen
        return 1      # 1x normal


class GameLogic:
    """
    Hauptklasse für die Spiellogik.
    Generiert verschiedene Fragetypen und wertet Antworten aus.
    """
    
    # Basis-Punkte pro richtiger Antwort
    BASE_POINTS = 10
    
    def __init__(self):
        """Initialisiert die Spiellogik."""
        self.state = GameState()
    
    def start_new_game(self):
        """Startet ein neues Spiel."""
        self.state.reset()
        return self.generate_question()
    
    def get_random_question_type(self):
        """Wählt einen zufälligen Fragetyp."""
        # Gewichtung: Nachbarn am häufigsten
        weights = [
            (QuestionType.NEIGHBOR, 40),
            (QuestionType.YES_NO, 25),
            (QuestionType.CAPITAL, 20),
            (QuestionType.CONTINENT, 15),
        ]
        total = sum(w for _, w in weights)
        r = random.randint(1, total)
        cumulative = 0
        for qtype, weight in weights:
            cumulative += weight
            if r <= cumulative:
                return qtype
        return QuestionType.NEIGHBOR
    
    def generate_question(self):
        """
        Generiert eine neue Frage basierend auf zufälligem Typ.
        
        Returns: Dictionary mit question, options, type, oder None
        """
        # Zufälligen Fragetyp wählen
        question_type = self.get_random_question_type()
        
        # Entsprechende Frage generieren
        if question_type == QuestionType.NEIGHBOR:
            return self._generate_neighbor_question()
        elif question_type == QuestionType.YES_NO:
            return self._generate_yes_no_question()
        elif question_type == QuestionType.CAPITAL:
            return self._generate_capital_question()
        elif question_type == QuestionType.CONTINENT:
            return self._generate_continent_question()
        
        return None
    
    def _generate_neighbor_question(self):
        """
        Generiert eine Nachbar-Frage.
        "Welches Land grenzt an [LAND]?"
        """
        # Land mit Nachbarn finden
        country = db.get_random_country_with_neighbors()
        if not country:
            return self._generate_capital_question()  # Fallback
        
        # Nachbarn abrufen
        neighbors = db.get_neighbors(country["name"])
        if not neighbors:
            return self._generate_capital_question()  # Fallback
        
        # Richtige Antwort
        correct_answer = random.choice(neighbors)
        
        # Falsche Antworten
        wrong_answers = db.get_random_countries(
            count=5,
            exclude=[country["name"]] + neighbors
        )[:3]
        
        # Optionen mischen
        all_options = [correct_answer] + wrong_answers
        random.shuffle(all_options)
        
        # State aktualisieren
        self.state.current_question_type = QuestionType.NEIGHBOR
        self.state.current_country = country
        self.state.current_correct_answer = correct_answer
        self.state.current_options = all_options
        
        return {
            "type": QuestionType.NEIGHBOR,
            "question": f"Welches Land grenzt an {country['name']}?",
            "country": country,
            "options": all_options,
            "correct": correct_answer
        }
    
    def _generate_yes_no_question(self):
        """
        Generiert eine Ja/Nein-Frage.
        "Grenzen [LAND A] und [LAND B] aneinander?"
        """
        countries = db.get_two_random_countries()
        if not countries or len(countries) < 2:
            return self._generate_neighbor_question()  # Fallback
        
        country1, country2 = countries
        are_neighbors = db.check_if_neighbors(country1, country2)
        
        correct_answer = "Ja" if are_neighbors else "Nein"
        
        # State aktualisieren
        self.state.current_question_type = QuestionType.YES_NO
        self.state.current_country = {"name": f"{country1} & {country2}"}
        self.state.current_correct_answer = correct_answer
        self.state.current_options = ["Ja", "Nein"]
        
        return {
            "type": QuestionType.YES_NO,
            "question": f"Grenzen {country1} und {country2} aneinander?",
            "country": {"name": f"{country1} & {country2}"},
            "options": ["Ja", "Nein"],
            "correct": correct_answer
        }
    
    def _generate_capital_question(self):
        """
        Generiert eine Hauptstadt-Frage.
        "Wie heißt die Hauptstadt von [LAND]?"
        """
        country = db.get_random_country_with_capital()
        if not country:
            return self._generate_neighbor_question()  # Fallback
        
        correct_answer = country["capital"]
        
        # Falsche Hauptstädte
        wrong_capitals = db.get_random_capitals(
            count=5,
            exclude=[correct_answer]
        )[:3]
        
        if len(wrong_capitals) < 3:
            return self._generate_neighbor_question()  # Fallback
        
        # Optionen mischen
        all_options = [correct_answer] + wrong_capitals
        random.shuffle(all_options)
        
        # State aktualisieren
        self.state.current_question_type = QuestionType.CAPITAL
        self.state.current_country = country
        self.state.current_correct_answer = correct_answer
        self.state.current_options = all_options
        
        return {
            "type": QuestionType.CAPITAL,
            "question": f"Wie heißt die Hauptstadt von {country['name']}?",
            "country": country,
            "options": all_options,
            "correct": correct_answer
        }
    
    def _generate_continent_question(self):
        """
        Generiert eine Kontinent-Frage.
        "Auf welchem Kontinent liegt [LAND]?"
        """
        country = db.get_random_country_with_continent()
        if not country:
            return self._generate_neighbor_question()  # Fallback
        
        correct_answer = country["continent"]
        
        # Alle Kontinente als Optionen
        all_continents = db.get_all_continents()
        if not all_continents or len(all_continents) < 3:
            return self._generate_neighbor_question()  # Fallback
        
        # 3 falsche Kontinente
        wrong_continents = [c for c in all_continents if c != correct_answer]
        random.shuffle(wrong_continents)
        wrong_continents = wrong_continents[:3]
        
        # Optionen mischen
        all_options = [correct_answer] + wrong_continents
        random.shuffle(all_options)
        
        # State aktualisieren
        self.state.current_question_type = QuestionType.CONTINENT
        self.state.current_country = country
        self.state.current_correct_answer = correct_answer
        self.state.current_options = all_options
        
        return {
            "type": QuestionType.CONTINENT,
            "question": f"Auf welchem Kontinent liegt {country['name']}?",
            "country": country,
            "options": all_options,
            "correct": correct_answer
        }
    
    def check_answer(self, selected_answer):
        """
        Überprüft die ausgewählte Antwort mit Streak-System.
        
        Args:
            selected_answer: Der Name des gewählten Landes
            
        Returns: Dictionary mit Ergebnis-Infos
        """
        is_correct = selected_answer == self.state.current_correct_answer
        
        # Streak und Punkte berechnen
        if is_correct:
            self.state.streak += 1
            if self.state.streak > self.state.best_streak:
                self.state.best_streak = self.state.streak
            
            multiplier = self.state.get_multiplier()
            score_change = self.BASE_POINTS * multiplier
            self.state.score += score_change
        else:
            self.state.streak = 0
            score_change = 0
        
        self.state.rounds_played += 1
        
        return {
            "correct": is_correct,
            "correct_answer": self.state.current_correct_answer,
            "score_change": score_change,
            "total_score": self.state.score,
            "rounds_played": self.state.rounds_played,
            "streak": self.state.streak,
            "multiplier": self.state.get_multiplier(),
            "is_game_over": self.state.rounds_played >= self.state.max_rounds
        }
    
    def get_score(self):
        """Gibt den aktuellen Punktestand zurück."""
        return self.state.score
    
    def get_rounds_played(self):
        """Gibt die Anzahl gespielter Runden zurück."""
        return self.state.rounds_played
    
    def get_max_rounds(self):
        """Gibt die maximale Rundenanzahl zurück."""
        return self.state.max_rounds
    
    def get_streak(self):
        """Gibt die aktuelle Streak zurück."""
        return self.state.streak
    
    def get_multiplier(self):
        """Gibt den aktuellen Multiplikator zurück."""
        return self.state.get_multiplier()
    
    def get_highscore(self):
        """Gibt den Session-Highscore zurück."""
        return self.state.highscore
    
    def get_current_country_info(self):
        """Gibt Infos zum aktuellen Land zurück."""
        if self.state.current_country:
            name = self.state.current_country.get("name", "")
            if " & " not in name:  # Nicht für Ja/Nein Fragen
                return db.get_country_details(name)
        return None
    
    def is_game_over(self):
        """Prüft ob das Spiel zu Ende ist."""
        return self.state.rounds_played >= self.state.max_rounds


# ============================================================
# Globale Spiellogik-Instanz
# ============================================================
game = GameLogic()
