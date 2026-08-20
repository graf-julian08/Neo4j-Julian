"""
ui.py - Premium Tkinter GUI für GeoPath Challenge
==================================================
Professionelles Trivia-Game Design mit:
- Dark Mode Premium Farbschema
- Animierte Effekte
- Streak-System Anzeige
- Mehrere Fragetypen
- Fullscreen Mode (macOS 14")
"""

import tkinter as tk
from tkinter import messagebox, font
import threading

from db import db
from importer import run_import
from game_logic import game, QuestionType


# ============================================================
# PREMIUM DESIGN KONSTANTEN
# ============================================================
COLORS = {
    # Hintergründe
    "bg_dark": "#0a0a1a",        # Tiefes Schwarz-Blau
    "bg_card": "#12122a",        # Karten-Hintergrund
    "bg_input": "#1a1a35",       # Input-Felder
    
    # Akzentfarben
    "accent_gold": "#ffd700",    # Gold für Score/Highlights
    "accent_cyan": "#00d4ff",    # Cyan für Buttons
    "accent_purple": "#9b59b6",  # Lila für Hover
    
    # Feedback
    "success": "#00ff88",        # Richtig (Neon-Grün)
    "error": "#ff4466",          # Falsch (Neon-Rot)
    "warning": "#ff9500",        # Streak-Bonus
    
    # Text
    "text_primary": "#ffffff",   # Haupttext
    "text_secondary": "#8888aa", # Sekundärtext
    "text_muted": "#555577",     # Gedämpfter Text
    
    # Buttons
    "btn_primary": "#3498db",    # Hellblau für besseren Kontrast
    "btn_hover": "#5dade2",      # Hover-Zustand
    "btn_active": "#85c1e9",     # Aktiv/Gedrückt
    "btn_text": "#000000",       # Schwarzer Text auf Buttons
}

FONTS = {
    "title": ("Helvetica Neue", 56, "bold"),
    "subtitle": ("Helvetica Neue", 24),
    "heading": ("Helvetica Neue", 32, "bold"),
    "question": ("Helvetica Neue", 28, "bold"),
    "body": ("Helvetica Neue", 18),
    "button": ("Helvetica Neue", 20, "bold"),
    "button_large": ("Helvetica Neue", 22, "bold"),
    "score": ("Helvetica Neue", 42, "bold"),
    "streak": ("Helvetica Neue", 20, "bold"),
    "small": ("Helvetica Neue", 16),
}


class GeoPathApp:
    """
    Premium GeoPath Challenge Anwendung.
    Trivia-Game Style mit Animationen und Effekten.
    Fullscreen für macOS 14".
    """
    
    def __init__(self):
        """Initialisiert die Anwendung."""
        # Hauptfenster
        self.root = tk.Tk()
        self.root.title("🌍 GeoPath Challenge")
        self.root.configure(bg=COLORS["bg_dark"])
        
        # Fullscreen aktivieren (macOS)
        self.root.attributes("-fullscreen", True)
        
        # ESC zum Beenden
        self.root.bind("<Escape>", lambda e: self.on_close())
        
        # Bildschirmgröße ermitteln
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # Container
        self.container = tk.Frame(self.root, bg=COLORS["bg_dark"])
        self.container.pack(fill="both", expand=True)
        
        # Screens
        self.screens = {}
        self.current_screen = None
        
        # Status
        self.db_connected = False
        self.option_buttons = []
        self.score_animation_id = None
        
        # Screens erstellen
        self._create_screens()
        self.show_screen("start")
    
    def _create_screens(self):
        """Erstellt alle Screens."""
        self.screens["start"] = self._create_start_screen()
        self.screens["game"] = self._create_game_screen()
        self.screens["info"] = self._create_info_screen()
        self.screens["gameover"] = self._create_gameover_screen()
    
    def show_screen(self, screen_name):
        """Zeigt einen Screen an."""
        for screen in self.screens.values():
            screen.pack_forget()
        
        if screen_name in self.screens:
            self.screens[screen_name].pack(fill="both", expand=True)
            self.current_screen = screen_name
    
    # ============================================================
    # START SCREEN - Premium Design (ohne Import Button)
    # ============================================================
    
    def _create_start_screen(self):
        """Erstellt den Start-Screen mit Premium-Design."""
        frame = tk.Frame(self.container, bg=COLORS["bg_dark"])
        
        # Zentrierter Content Container
        content = tk.Frame(frame, bg=COLORS["bg_dark"])
        content.place(relx=0.5, rely=0.5, anchor="center")
        
        # Emoji (größer für Fullscreen)
        emoji_label = tk.Label(
            content,
            text="🌍",
            font=("Helvetica", 100),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_dark"]
        )
        emoji_label.pack()
        
        # Haupttitel
        title = tk.Label(
            content,
            text="GEOPATH CHALLENGE",
            font=FONTS["title"],
            fg=COLORS["accent_gold"],
            bg=COLORS["bg_dark"]
        )
        title.pack(pady=15)
        
        # Untertitel
        subtitle = tk.Label(
            content,
            text="Das ultimative Geographie-Quiz",
            font=FONTS["subtitle"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_dark"]
        )
        subtitle.pack(pady=5)
        
        # Feature-Liste
        features_frame = tk.Frame(content, bg=COLORS["bg_dark"])
        features_frame.pack(pady=40)
        
        features = [
            "🗺️ 250+ Länder aus der echten Welt",
            "🔥 Streak-System mit Bonus-Multiplikator",
            "❓ 4 verschiedene Fragetypen",
            "🏆 Punkte sammeln und Highscore knacken",
        ]
        
        for feature in features:
            lbl = tk.Label(
                features_frame,
                text=feature,
                font=FONTS["body"],
                fg=COLORS["text_secondary"],
                bg=COLORS["bg_dark"]
            )
            lbl.pack(pady=6)
        
        # Start Button (groß und prominent)
        self.start_btn = self._create_premium_button(
            content,
            "🎮  SPIEL STARTEN",
            self._on_start_click,
            width=35,
            style="primary"
        )
        self.start_btn.pack(pady=50)
        
        # Footer
        footer_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        footer_frame.pack(side="bottom", pady=40)
        
        tk.Label(
            footer_frame,
            text="Powered by Neo4j Graph Database  •  Drücke ESC zum Beenden",
            font=FONTS["small"],
            fg=COLORS["text_muted"],
            bg=COLORS["bg_dark"]
        ).pack()
        
        return frame
    
    # ============================================================
    # GAME SCREEN - Premium Quiz Interface (Fullscreen)
    # ============================================================
    
    def _create_game_screen(self):
        """Erstellt den Game-Screen mit Premium-Design."""
        frame = tk.Frame(self.container, bg=COLORS["bg_dark"])
        
        # === HEADER ===
        header = tk.Frame(frame, bg=COLORS["bg_card"], height=100)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        # Zurück Button
        back_btn = tk.Button(
            header,
            text="← MENÜ",
            font=FONTS["body"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"],
            activebackground=COLORS["bg_dark"],
            activeforeground=COLORS["text_primary"],
            border=0,
            cursor="hand2",
            command=lambda: self.show_screen("start")
        )
        back_btn.pack(side="left", padx=50, pady=30)
        
        # Runden-Anzeige (Mitte)
        self.rounds_label = tk.Label(
            header,
            text="RUNDE 1/10",
            font=FONTS["body"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"]
        )
        self.rounds_label.pack(side="left", expand=True)
        
        # Score (rechts, groß und golden)
        score_container = tk.Frame(header, bg=COLORS["bg_card"])
        score_container.pack(side="right", padx=50)
        
        tk.Label(
            score_container,
            text="SCORE",
            font=FONTS["small"],
            fg=COLORS["text_muted"],
            bg=COLORS["bg_card"]
        ).pack()
        
        self.score_label = tk.Label(
            score_container,
            text="0",
            font=FONTS["score"],
            fg=COLORS["accent_gold"],
            bg=COLORS["bg_card"]
        )
        self.score_label.pack()
        
        # === STREAK BANNER ===
        self.streak_frame = tk.Frame(frame, bg=COLORS["bg_dark"], height=60)
        self.streak_frame.pack(fill="x", pady=15)
        
        self.streak_label = tk.Label(
            self.streak_frame,
            text="",
            font=FONTS["streak"],
            fg=COLORS["warning"],
            bg=COLORS["bg_dark"]
        )
        self.streak_label.pack()
        
        # === FRAGE-CARD ===
        question_card = tk.Frame(
            frame,
            bg=COLORS["bg_card"],
            padx=80,
            pady=50
        )
        question_card.pack(fill="x", padx=150, pady=30)
        
        # Fragetyp-Badge
        self.question_type_label = tk.Label(
            question_card,
            text="",
            font=FONTS["body"],
            fg=COLORS["accent_cyan"],
            bg=COLORS["bg_card"]
        )
        self.question_type_label.pack(pady=(0, 20))
        
        # Frage-Text
        self.question_label = tk.Label(
            question_card,
            text="",
            font=FONTS["question"],
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
            wraplength=1200
        )
        self.question_label.pack(pady=15)
        
        # Info Button
        self.info_btn = tk.Button(
            question_card,
            text="ℹ️ Land-Info anzeigen",
            font=FONTS["small"],
            fg=COLORS["text_muted"],
            bg=COLORS["bg_input"],
            activebackground=COLORS["btn_hover"],
            activeforeground=COLORS["text_primary"],
            border=0,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self._show_country_info
        )
        self.info_btn.pack(pady=20)
        
        # === ANTWORT-BUTTONS (2x2 Grid) ===
        self.options_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        self.options_frame.pack(pady=40)
        
        # === FEEDBACK ===
        self.feedback_frame = tk.Frame(frame, bg=COLORS["bg_dark"])
        self.feedback_frame.pack(pady=15)
        
        self.feedback_label = tk.Label(
            self.feedback_frame,
            text="",
            font=FONTS["heading"],
            fg=COLORS["text_primary"],
            bg=COLORS["bg_dark"]
        )
        self.feedback_label.pack()
        
        self.feedback_detail = tk.Label(
            self.feedback_frame,
            text="",
            font=FONTS["body"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_dark"]
        )
        self.feedback_detail.pack(pady=5)
        
        # === NÄCHSTE RUNDE BUTTON ===
        self.next_btn = self._create_premium_button(
            frame,
            "NÄCHSTE RUNDE →",
            self._next_round,
            width=30,
            style="primary"
        )
        # Wird erst nach Antwort angezeigt
        
        # === PROGRESS BAR ===
        progress_container = tk.Frame(frame, bg=COLORS["bg_dark"])
        progress_container.pack(side="bottom", fill="x", padx=150, pady=40)
        
        # Dynamische Breite für Fullscreen
        self.progress_canvas = tk.Canvas(
            progress_container,
            height=10,
            bg=COLORS["bg_card"],
            highlightthickness=0
        )
        self.progress_canvas.pack(fill="x")
        
        return frame
    
    def _update_progress_bar(self):
        """Aktualisiert die Progress-Bar."""
        self.progress_canvas.delete("all")
        
        # Canvas-Breite ermitteln
        self.progress_canvas.update_idletasks()
        canvas_width = self.progress_canvas.winfo_width()
        
        progress = game.get_rounds_played() / game.get_max_rounds()
        bar_width = int(canvas_width * progress)
        
        if bar_width > 0:
            self.progress_canvas.create_rectangle(
                0, 0, bar_width, 10,
                fill=COLORS["accent_cyan"],
                outline=""
            )
    
    def _update_streak_display(self):
        """Aktualisiert die Streak-Anzeige."""
        streak = game.get_streak()
        multiplier = game.get_multiplier()
        
        if streak >= 3:
            self.streak_label.configure(
                text=f"🔥 STREAK: {streak} • {multiplier}x BONUS 🔥",
                fg=COLORS["warning"]
            )
        elif streak > 0:
            self.streak_label.configure(
                text=f"✓ {streak} richtig in Folge",
                fg=COLORS["success"]
            )
        else:
            self.streak_label.configure(text="")
    
    def _get_question_type_text(self, qtype):
        """Gibt den deutschen Text für den Fragetyp zurück."""
        types = {
            QuestionType.NEIGHBOR: "🗺️ NACHBARLÄNDER",
            QuestionType.YES_NO: "❓ JA ODER NEIN",
            QuestionType.CAPITAL: "🏛️ HAUPTSTADT",
            QuestionType.CONTINENT: "🌍 KONTINENT",
        }
        return types.get(qtype, "")
    
    # ============================================================
    # GAME OVER SCREEN (Fullscreen)
    # ============================================================
    
    def _create_gameover_screen(self):
        """Erstellt den Game-Over Screen."""
        frame = tk.Frame(self.container, bg=COLORS["bg_dark"])
        
        # Zentrierter Content
        content = tk.Frame(frame, bg=COLORS["bg_dark"])
        content.place(relx=0.5, rely=0.5, anchor="center")
        
        # Trophy
        tk.Label(
            content,
            text="🏆",
            font=("Helvetica", 100),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_dark"]
        ).pack()
        
        tk.Label(
            content,
            text="SPIEL BEENDET!",
            font=FONTS["title"],
            fg=COLORS["accent_gold"],
            bg=COLORS["bg_dark"]
        ).pack(pady=25)
        
        # Score Container
        score_box = tk.Frame(content, bg=COLORS["bg_card"], padx=80, pady=40)
        score_box.pack(pady=40)
        
        tk.Label(
            score_box,
            text="DEIN SCORE",
            font=FONTS["body"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"]
        ).pack()
        
        self.final_score_label = tk.Label(
            score_box,
            text="0",
            font=("Helvetica Neue", 72, "bold"),
            fg=COLORS["accent_gold"],
            bg=COLORS["bg_card"]
        )
        self.final_score_label.pack()
        
        self.final_streak_label = tk.Label(
            score_box,
            text="",
            font=FONTS["body"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"]
        )
        self.final_streak_label.pack(pady=15)
        
        # Buttons
        btn_frame = tk.Frame(content, bg=COLORS["bg_dark"])
        btn_frame.pack(pady=40)
        
        self._create_premium_button(
            btn_frame,
            "🔄  NOCHMAL SPIELEN",
            self._restart_game,
            width=30,
            style="primary"
        ).pack(pady=12)
        
        self._create_premium_button(
            btn_frame,
            "🏠  ZURÜCK ZUM MENÜ",
            lambda: self.show_screen("start"),
            width=30,
            style="secondary"
        ).pack(pady=12)
        
        return frame
    
    # ============================================================
    # INFO SCREEN (Fullscreen)
    # ============================================================
    
    def _create_info_screen(self):
        """Erstellt den Info-Screen."""
        frame = tk.Frame(self.container, bg=COLORS["bg_dark"])
        
        # Header
        header = tk.Frame(frame, bg=COLORS["bg_card"], height=90)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Button(
            header,
            text="← Zurück zum Spiel",
            font=FONTS["body"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"],
            border=0,
            cursor="hand2",
            command=lambda: self.show_screen("game")
        ).pack(side="left", padx=50, pady=25)
        
        self.info_title = tk.Label(
            header,
            text="",
            font=FONTS["heading"],
            fg=COLORS["accent_gold"],
            bg=COLORS["bg_card"]
        )
        self.info_title.pack(side="right", padx=50)
        
        # Info Container
        info_box = tk.Frame(frame, bg=COLORS["bg_card"], padx=80, pady=60)
        info_box.pack(padx=200, pady=80, fill="both", expand=True)
        
        self.info_labels = {}
        
        info_items = [
            ("continent", "🌍 Kontinent"),
            ("capital", "🏛️ Hauptstadt"),
            ("population", "👥 Bevölkerung"),
            ("neighbors", "🤝 Nachbarländer"),
        ]
        
        for key, label_text in info_items:
            row = tk.Frame(info_box, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=20)
            
            tk.Label(
                row,
                text=label_text,
                font=FONTS["body"],
                fg=COLORS["text_secondary"],
                bg=COLORS["bg_card"],
                width=20,
                anchor="w"
            ).pack(side="left")
            
            value = tk.Label(
                row,
                text="",
                font=FONTS["body"],
                fg=COLORS["text_primary"],
                bg=COLORS["bg_card"],
                wraplength=800,
                anchor="w",
                justify="left"
            )
            value.pack(side="left", fill="x", expand=True)
            
            self.info_labels[key] = value
        
        return frame
    
    # ============================================================
    # BUTTON FACTORY
    # ============================================================
    
    def _create_premium_button(self, parent, text, command, width=20, style="primary"):
        """Erstellt einen Premium-styled Button mit Hover-Effekt."""
        
        if style == "primary":
            bg = COLORS["accent_cyan"]
            fg = COLORS["bg_dark"]
            hover_bg = "#33e0ff"
        else:
            bg = COLORS["btn_primary"]
            fg = COLORS["text_primary"]
            hover_bg = COLORS["btn_hover"]
        
        btn = tk.Button(
            parent,
            text=text,
            font=FONTS["button"],
            fg=fg,
            bg=bg,
            activebackground=hover_bg,
            activeforeground=fg,
            width=width,
            height=2,
            border=0,
            cursor="hand2",
            command=command
        )
        
        # Hover-Effekte
        def on_enter(e):
            btn.configure(bg=hover_bg)
        
        def on_leave(e):
            btn.configure(bg=bg)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def _create_option_button(self, parent, text, row, col):
        """Erstellt einen Antwort-Button für das Quiz."""
        btn = tk.Button(
            parent,
            text=text,
            font=FONTS["button_large"],
            fg="#000000",  # Schwarzer Text für besseren Kontrast
            bg=COLORS["btn_primary"],
            activebackground=COLORS["btn_active"],
            activeforeground="#000000",
            width=28,
            height=3,
            border=0,
            cursor="hand2",
            command=lambda t=text: self._on_answer_click(t)
        )
        
        # Hover-Effekte
        def on_enter(e):
            if btn["state"] != "disabled":
                btn.configure(bg=COLORS["btn_hover"])
        
        def on_leave(e):
            if btn["state"] != "disabled":
                btn.configure(bg=COLORS["btn_primary"])
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        btn.grid(row=row, column=col, padx=20, pady=20)
        return btn
    
    # ============================================================
    # EVENT HANDLERS
    # ============================================================
    
    def _on_start_click(self):
        """Handler für Start-Button."""
        # Verbindung herstellen
        if not self.db_connected:
            if not db.connect():
                messagebox.showerror(
                    "Verbindungsfehler",
                    "Keine Verbindung zur Neo4j Datenbank!\n\n"
                    "Stelle sicher, dass:\n"
                    "1. Neo4j Desktop läuft\n"
                    "2. Die Datenbank gestartet ist\n"
                    "3. Die Credentials in db.py korrekt sind"
                )
                return
            self.db_connected = True
        
        # Prüfen ob Daten vorhanden
        total = db.get_total_countries()
        if total == 0:
            messagebox.showerror(
                "Keine Daten",
                "Die Datenbank ist leer!\n\n"
                "Bitte führe zuerst den Datenimport aus:\n"
                "python importer.py"
            )
            return
        
        self._start_new_game()
    
    def _start_new_game(self):
        """Startet ein neues Spiel."""
        question_data = game.start_new_game()
        if question_data:
            self._display_question(question_data)
            self.show_screen("game")
        else:
            messagebox.showerror(
                "Fehler",
                "Konnte keine Frage generieren!"
            )
    
    def _restart_game(self):
        """Startet das Spiel neu."""
        self._start_new_game()
    
    def _display_question(self, question_data):
        """Zeigt eine Frage an."""
        # Header aktualisieren
        self.score_label.configure(text=str(game.get_score()))
        self.rounds_label.configure(
            text=f"RUNDE {game.get_rounds_played() + 1}/{game.get_max_rounds()}"
        )
        
        # Streak
        self._update_streak_display()
        
        # Progress
        self._update_progress_bar()
        
        # Fragetyp-Badge
        self.question_type_label.configure(
            text=self._get_question_type_text(question_data["type"])
        )
        
        # Frage
        self.question_label.configure(text=question_data["question"])
        
        # Feedback zurücksetzen
        self.feedback_label.configure(text="")
        self.feedback_detail.configure(text="")
        self.next_btn.pack_forget()
        
        # Info-Button nur bei nicht-JaNein Fragen
        if question_data["type"] == QuestionType.YES_NO:
            self.info_btn.pack_forget()
        else:
            self.info_btn.pack(pady=20)
        
        # Alte Buttons entfernen
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        
        # Neue Buttons im Grid
        self.option_buttons = []
        options = question_data["options"]
        
        # Bei 2 Optionen (Ja/Nein): nebeneinander
        # Bei 4 Optionen: 2x2 Grid
        if len(options) == 2:
            for i, option in enumerate(options):
                btn = self._create_option_button(self.options_frame, option, 0, i)
                self.option_buttons.append(btn)
        else:
            for i, option in enumerate(options):
                row = i // 2
                col = i % 2
                btn = self._create_option_button(self.options_frame, option, row, col)
                self.option_buttons.append(btn)
    
    def _on_answer_click(self, selected_answer):
        """Handler für Antwort-Klick."""
        print(f"DEBUG: Antwort geklickt: {selected_answer}")  # Debug
        
        result = game.check_answer(selected_answer)
        print(f"DEBUG: Ergebnis: {result}")  # Debug
        
        # Score mit Animation
        self._animate_score(result["total_score"])
        
        # Streak aktualisieren
        self._update_streak_display()
        
        # Buttons färben
        for btn in self.option_buttons:
            btn.configure(state="disabled", cursor="arrow")
            btn.unbind("<Enter>")
            btn.unbind("<Leave>")
            
            btn_text = btn.cget("text")
            if btn_text == result["correct_answer"]:
                btn.configure(bg=COLORS["success"], fg="#000000")
                print(f"DEBUG: Button '{btn_text}' grün gefärbt")  # Debug
            elif btn_text == selected_answer and not result["correct"]:
                btn.configure(bg=COLORS["error"], fg="#000000")
                print(f"DEBUG: Button '{btn_text}' rot gefärbt")  # Debug
        
        # Force update
        self.root.update_idletasks()
        
        # Feedback
        if result["correct"]:
            if result["multiplier"] > 1:
                self.feedback_label.configure(
                    text=f"✅ RICHTIG! +{result['score_change']} Punkte",
                    fg=COLORS["success"]
                )
                self.feedback_detail.configure(
                    text=f"🔥 {result['multiplier']}x Streak-Bonus!",
                    fg=COLORS["warning"]
                )
            else:
                self.feedback_label.configure(
                    text=f"✅ RICHTIG! +{result['score_change']} Punkte",
                    fg=COLORS["success"]
                )
                self.feedback_detail.configure(text="")
        else:
            self.feedback_label.configure(
                text="❌ FALSCH!",
                fg=COLORS["error"]
            )
            self.feedback_detail.configure(
                text=f"Richtig war: {result['correct_answer']}",
                fg=COLORS["text_secondary"]
            )
        
        # Progress
        self._update_progress_bar()
        
        # Automatisch nach 2 Sekunden zur nächsten Frage
        if result["is_game_over"]:
            # Nach 2 Sekunden Game Over anzeigen
            self.root.after(2000, self._show_game_over)
        else:
            # Nach 2 Sekunden nächste Runde
            self.root.after(2000, self._next_round)
    
    def _animate_score(self, target_score):
        """Animiert den Score-Counter."""
        current = int(self.score_label.cget("text"))
        
        if current < target_score:
            step = max(1, (target_score - current) // 5)
            new_score = min(current + step, target_score)
            self.score_label.configure(text=str(new_score))
            self.score_animation_id = self.root.after(
                50, lambda: self._animate_score(target_score)
            )
        else:
            self.score_label.configure(text=str(target_score))
    
    def _next_round(self):
        """Startet die nächste Runde."""
        question_data = game.generate_question()
        if question_data:
            self._display_question(question_data)
        else:
            messagebox.showerror("Fehler", "Konnte keine Frage generieren!")
    
    def _show_game_over(self):
        """Zeigt den Game-Over Screen."""
        self.final_score_label.configure(text=str(game.get_score()))
        self.final_streak_label.configure(
            text=f"Beste Serie: {game.state.best_streak} richtige Antworten"
        )
        self.show_screen("gameover")
    
    def _show_country_info(self):
        """Zeigt Länder-Infos."""
        info = game.get_current_country_info()
        if info:
            self._display_country_info(info)
            self.show_screen("info")
    
    def _display_country_info(self, info):
        """Zeigt Länder-Details an."""
        self.info_title.configure(text=f"📍 {info['name']}")
        
        self.info_labels["continent"].configure(
            text=info.get("continent", "Unbekannt") or "Unbekannt"
        )
        self.info_labels["capital"].configure(
            text=info.get("capital", "Unbekannt") or "Unbekannt"
        )
        
        population = info.get("population", 0)
        if population:
            pop_formatted = f"{population:,}".replace(",", ".")
            self.info_labels["population"].configure(text=pop_formatted)
        else:
            self.info_labels["population"].configure(text="Unbekannt")
        
        neighbors = info.get("neighbors", [])
        if neighbors:
            self.info_labels["neighbors"].configure(text=", ".join(neighbors))
        else:
            self.info_labels["neighbors"].configure(text="Keine (Inselstaat)")
    
    # ============================================================
    # APP LIFECYCLE
    # ============================================================
    
    def run(self):
        """Startet die Anwendung."""
        self.root.mainloop()
    
    def on_close(self):
        """Cleanup beim Schließen."""
        if self.score_animation_id:
            self.root.after_cancel(self.score_animation_id)
        if self.db_connected:
            db.close()
        self.root.destroy()
