"""
Answer Evaluator - Evaluează răspunsurile utilizatorului
Suportă evaluare text și extragere din PDF
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from difflib import SequenceMatcher

from knowledge_base import KNOWLEDGE_BASE


class Answer:
    """Reprezentare a unui răspuns de la utilizator"""
    
    def __init__(self, 
                 strategy: str,
                 reasoning: str = "",
                 raw_text: str = ""):
        self.strategy = strategy
        self.reasoning = reasoning
        self.raw_text = raw_text
        self.parsed_concepts = []
    
    def __str__(self) -> str:
        return f"Answer(strategy={self.strategy}, reasoning_length={len(self.reasoning)})"


class AnswerEvaluator:
    """Evaluează răspunsurile utilizatorilor și calculează score"""
    
    def __init__(self):
        self.knowledge_base = KNOWLEDGE_BASE
        self.strategy_synonyms = self._build_strategy_synonyms()
        self.key_concepts = self._extract_key_concepts()
        self.game_theory_rubric = self._build_game_theory_rubric()
    
    def _build_strategy_synonyms(self) -> Dict[str, List[str]]:
        """Construiește un dicționar extins de sinonime pentru strategii - tolerant la variații"""
        return {
            "backtracking": ["backtracking", "back tracking", "back-tracking", "cautare cu revenire", 
                           "explorare exhaustiva", "brute force"],
            "backtracking_with_heuristics": ["backtracking cu heuristici", "backtracking heuristic", 
                                            "forward checking", "mrv", "backtracking optimizat"],
            "csp_forward_checking": ["csp", "constraint satisfaction", "forward checking", 
                                    "arc consistency", "satisfacerea constrangerilor"],
            "local_search": ["local search", "cautare locala", "hill climbing", "min conflicts",
                           "local", "cautare"],
            "simulated_annealing": ["simulated annealing", "recoacere simulata", "annealing", 
                                   "recoacere", "sa"],
            "recursive_divide_conquer": ["recursiv", "recursive", "divide and conquer", "divide et impera"],
            "iterative": ["iterativ", "iterative", "bucla"],
            "frame_stewart_algorithm": ["frame stewart", "frame-stewart"],
            "dynamic_programming": ["programare dinamica", "dynamic programming", "dp", "memoization",
                                   "memorizare"],
            "greedy_basic": ["greedy", "lacom", "algoritm lacom", "greedy basic"],
            "greedy_dsatur": ["dsatur", "degree of saturation", "greedy dsatur"],
            "backtracking_with_bounds": ["branch and bound", "backtracking with bounds", "b&b"],
            "welsh_powell": ["welsh powell", "welsh-powell"],
            "planar_4color": ["4 color", "four color", "4-color", "planar"],
            "local_search_tabu": ["tabu search", "cautare tabu", "tabu"],
            "warnsdorff_heuristic": ["warnsdorff", "warnsdorf"],
            "backtracking_warnsdorff": ["backtracking warnsdorff", "warnsdorff backtracking"],
            "divide_conquer": ["divide conquer", "divide and conquer", "divide et impera"],
            # Game Theory strategies 
            "pure_strategy_enumeration": [
                "enumerare", "enumeration", "enumerarea strategiilor",
                "strategii pure", "pure strategy", "pure strategies", 
                "verificare directa", "verificare", "direct verification",
                "enumerare pura", "enumerare strategii pure",
                "pura", "pure", "strategii", "enumeration pure",
                "analiza directa", "metoda directa", "direct"
            ],
            "best_response_analysis": [
                "best response", "raspuns optim", "raspunsuri optime",
                "analiza best response", "best-response",
                "analiza raspunsurilor optime", "br analysis",
                "raspuns cel mai bun", "cel mai bun raspuns",
                "raspunsuri", "best responses"
            ],
            "dominance_elimination": [
                "eliminare", "eliminare iterativa", "iesds", "iterated elimination",
                "strategie dominata", "strategii dominate", "dominated strategy",
                "dominanta", "dominant", "eliminarea strategiilor",
                "eliminare dominanta", "dominance", "iterative elimination",
                "eliminating dominated", "dominate"
            ],
            "mixed_strategy_calculation": [
                "strategii mixte", "mixed strategy", "mixed strategies",
                "echilibru mixt", "mixed equilibrium", "mixte",
                "probabilitati", "randomizare", "mixed",
                "calcul mixt", "strategie mixta", "probabilistic",
                "randomization", "echilibru in strategii mixte"
            ]
        }
    
    def _build_game_theory_rubric(self) -> Dict[str, Dict[str, int]]:
        """Construiește rubrica de evaluare pentru teoria jocurilor"""
        return {
            "complexity_analysis": {
                "max_points": 25,
                "keywords": ["complexitate", "complexity", "o(", "O(", "exponential", "polinomial",
                           "liniar", "linear", "patratic", "n²", "mn", "m×n"],
                "description": "Analiza complexității metodei alese"
            },
            "game_characteristics": {
                "max_points": 25,
                "keywords": ["2x2", "3x3", "dimensiune", "echilibru", "nash", "pur", "pure",
                           "mixt", "mixed", "dominant", "dominat", "zero-sum", "coordonare"],
                "description": "Identificarea caracteristicilor jocului"
            },
            "method_justification": {
                "max_points": 30,
                "keywords": ["deoarece", "pentru ca", "because", "fiindca", "intrucat",
                           "avantaj", "eficient", "optim", "rapid", "simplu", "direct"],
                "description": "Justificarea alegerii metodei"
            },
            "tradeoff_analysis": {
                "max_points": 20,
                "keywords": ["trade-off", "compromis", "alternativ", "versus", "vs", "in schimb",
                           "dezavantaj", "avantaj", "comparat", "fata de"],
                "description": "Analiza trade-off-urilor între metode"
            }
        }
    
    def _extract_key_concepts(self) -> Dict[str, List[str]]:
        """Extrage concepte cheie din knowledge base"""
        concepts = {}
        
        for problem_type, info in self.knowledge_base.items():
            concepts[problem_type] = []
            
            for strategy_name, strategy_info in info["strategies"].items():
                # Extract keywords from advantages and reasoning
                concepts[problem_type].extend([
                    "complexitate", "complexity",
                    "optim", "optimal",
                    "eficient", "efficient",
                    "exponential", "exponențial",
                    "polinomial", "polynomial",
                    "heuristic", "euristică"
                ])
                
                # Add specific terms from strategy
                if "time_complexity" in strategy_info:
                    complexity = strategy_info["time_complexity"]
                    concepts[problem_type].append(complexity)
        
        return concepts
    
    def parse_answer(self, answer_text: str) -> Answer:
        """
        Parsează răspunsul utilizatorului din text
        
        Args:
            answer_text: Text răspuns utilizator
        
        Returns:
            Answer object
        """
        answer_text_lower = answer_text.lower()
        
        # Extract strategy name
        detected_strategy = None
        max_matches = 0
        
        for strategy, synonyms in self.strategy_synonyms.items():
            matches = sum(1 for syn in synonyms if syn in answer_text_lower)
            if matches > max_matches:
                max_matches = matches
                detected_strategy = strategy
        
        # If no strategy detected, try to extract from structured answer
        if not detected_strategy:
            # Look for patterns like "Răspuns: X" or "Strategie: X"
            patterns = [
                r"răspuns[:\s]+([a-z_]+)",
                r"strategie[:\s]+([a-z_]+)",
                r"alegere[:\s]+([a-z_]+)",
                r"optim[:\s]+([a-z_]+)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, answer_text_lower)
                if match:
                    potential_strategy = match.group(1)
                    # Try to match with known strategies
                    for strategy in self.strategy_synonyms.keys():
                        if potential_strategy in strategy or strategy in potential_strategy:
                            detected_strategy = strategy
                            break
                if detected_strategy:
                    break
        
        # Extract reasoning (everything after first newline or after "justificare")
        reasoning = ""
        reasoning_markers = ["justificare", "motivatie", "explicatie", "deoarece", "pentru ca"]
        
        for marker in reasoning_markers:
            if marker in answer_text_lower:
                idx = answer_text_lower.index(marker)
                reasoning = answer_text[idx:].strip()
                break
        
        if not reasoning:
            # Take full text as reasoning
            reasoning = answer_text
        
        answer = Answer(
            strategy=detected_strategy or "unknown",
            reasoning=reasoning,
            raw_text=answer_text
        )
        
        # Extract concepts
        answer.parsed_concepts = self._extract_concepts_from_text(reasoning)
        
        return answer
    
    def _extract_concepts_from_text(self, text: str) -> List[str]:
        """Extrage concepte cheie din text"""
        text_lower = text.lower()
        found_concepts = []
        
        concept_keywords = [
            "complexitate", "complexity", "O(", "o(",
            "optim", "optimal",
            "eficient", "efficient",
            "exponential", "exponențial",
            "polinomial", "polynomial",
            "heuristic", "euristică", "heuristici",
            "backtrack", "forward checking",
            "local search", "simulated annealing",
            "divide", "conquer",
            "greedy", "lacom",
            "recursiv", "iterativ",
            "memorie", "memory", "space",
            "timp", "time",
            "garantează", "garanteaza", "guarantees"
        ]
        
        for keyword in concept_keywords:
            if keyword in text_lower:
                found_concepts.append(keyword)
        
        return found_concepts
    
    def evaluate_answer(self, 
                       user_answer: Answer,
                       correct_strategy: str,
                       correct_reasoning: str,
                       problem_type: str,
                       instance: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluează răspunsul utilizatorului
        
        Returns:
            Dict cu:
            - score: 0-100
            - strategy_correct: bool
            - reasoning_score: 0-100
            - feedback: str
            - breakdown: dict cu detalii scoring
        """
        # 1. Strategy matching (40% din scor)
        strategy_score, strategy_correct = self._evaluate_strategy(
            user_answer.strategy, correct_strategy, problem_type, instance
        )
        
        # 2. Reasoning quality (60% din scor)
        reasoning_score, reasoning_details = self._evaluate_reasoning(
            user_answer.reasoning,
            correct_reasoning,
            user_answer.parsed_concepts,
            problem_type
        )
        
        # Calculate total score
        total_score = int(strategy_score * 0.4 + reasoning_score * 0.6)
        
        # Generate feedback - cu detalii pentru toate tipurile de probleme
        feedback = self._generate_feedback(
            strategy_correct,
            strategy_score,
            reasoning_score,
            correct_strategy,
            correct_reasoning,
            problem_type=problem_type,
            reasoning_details=reasoning_details
        )
        
        return {
            "score": total_score,
            "strategy_correct": strategy_correct,
            "strategy_score": strategy_score,
            "reasoning_score": reasoning_score,
            "feedback": feedback,
            "reasoning_details": reasoning_details,
            "breakdown": {
                "strategy_points": strategy_score * 0.4,
                "reasoning_points": reasoning_score * 0.6
            },
            "correct_strategy": correct_strategy,
            "correct_reasoning": correct_reasoning
        }
    
    def _evaluate_strategy(self, 
                          user_strategy: str,
                          correct_strategy: str,
                          problem_type: str,
                          instance: Dict[str, Any]) -> Tuple[int, bool]:
        """
        Evaluează strategia aleasă
        
        Returns:
            (score 0-100, is_correct bool)
        """
        # Exact match
        if user_strategy == correct_strategy:
            return 100, True
        
        # Check if unknown
        if user_strategy == "unknown":
            return 0, False
        
        # Check if it's an acceptable alternative
        acceptable_alternatives = self._get_acceptable_alternatives(
            correct_strategy, problem_type, instance
        )
        
        if user_strategy in acceptable_alternatives:
            # Alternative validă dar nu optimă
            return 70, False
        
        # Check if it's in the same family
        if self._strategies_related(user_strategy, correct_strategy):
            return 50, False
        
        # Completely wrong
        return 0, False
    
    def _get_acceptable_alternatives(self,
                                    correct_strategy: str,
                                    problem_type: str,
                                    instance: Dict[str, Any]) -> List[str]:
        """Returnează strategii alternative acceptabile"""
        alternatives = []
        
        # Based on problem type and instance characteristics
        if problem_type == "n-queens":
            size = instance.get("size", 0)
            if 8 <= size <= 15:
                # In this range, multiple strategies work
                alternatives = ["backtracking", "backtracking_with_heuristics", "csp_forward_checking"]
        
        elif problem_type == "hanoi":
            towers = instance.get("towers", 3)
            disks = instance.get("disks", 0)
            if towers == 3 and 15 <= disks <= 25:
                alternatives = ["recursive_divide_conquer", "iterative"]
        
        elif problem_type == "graph_coloring":
            vertices = instance.get("vertices", 0)
            if 100 <= vertices <= 500:
                alternatives = ["greedy_dsatur", "welsh_powell"]
        
        elif problem_type == "knights_tour":
            size = instance.get("board_size", 0)
            if size >= 8:
                alternatives = ["warnsdorff_heuristic", "backtracking_warnsdorff"]
        
        return alternatives
    
    def _strategies_related(self, strategy1: str, strategy2: str) -> bool:
        """Verifică dacă două strategii sunt înrudite"""
        families = [
            ["backtracking", "backtracking_with_heuristics", "backtracking_with_bounds", "backtracking_warnsdorff"],
            ["local_search", "simulated_annealing", "local_search_tabu"],
            ["greedy_basic", "greedy_dsatur", "welsh_powell"],
            ["recursive_divide_conquer", "divide_conquer"],
            # Game theory strategy families
            ["pure_strategy_enumeration", "best_response_analysis"],  # Both find pure NE
            ["dominance_elimination", "pure_strategy_enumeration"]     # Related analysis methods
        ]
        
        for family in families:
            if strategy1 in family and strategy2 in family:
                return True
        
        return False
    
    def _evaluate_reasoning(self,
                           user_reasoning: str,
                           correct_reasoning: str,
                           user_concepts: List[str],
                           problem_type: str) -> Tuple[int, str]:
        """
        Evaluează calitatea justificării folosind rubrica unificată.
        
        Rubrica (aceeași pentru toate problemele):
        - Analiza complexității (25p)
        - Caracteristici problemă (25p)
        - Justificare metodă (30p)
        - Trade-offs (20p)
        
        Returns:
            (score 0-100, feedback detaliat)
        """
        # Verificare răspuns gol sau doar spații - direct 0 puncte
        if not user_reasoning or not user_reasoning.strip():
            return 0, "❌ Justificare lipsă: Nu ai oferit nicio justificare.\n\n💡 RECOMANDĂRI:\n   1. Explică DE CE ai ales această metodă\n   2. Menționează complexitatea\n   3. Identifică caracteristicile problemei"
        
        # EXACT MATCH: Dacă răspunsul este identic cu baremul, acordă 100 puncte
        if user_reasoning.strip() == correct_reasoning.strip():
            return 100, "✅ Complexitate: Perfect (+25p)\n✅ Caracteristici problemă: Perfect (+25p)\n✅ Justificare: Excelentă (+30p)\n✅ Trade-offs: Discuție completă (+20p)\n🎯 Răspuns identic cu baremul!"
        
        reasoning_lower = user_reasoning.lower()
        correct_lower = correct_reasoning.lower() if correct_reasoning else ""
        score = 0
        feedback_details = []
        missing_elements = []
        
        # BONUS: Verifică similaritatea cu răspunsul corect (până la +15p bonus)
        similarity_bonus = 0
        if correct_reasoning:
            similarity = self._calculate_similarity(user_reasoning, correct_reasoning)
            if similarity > 0.8:
                similarity_bonus = 15
            elif similarity > 0.6:
                similarity_bonus = 10
            elif similarity > 0.4:
                similarity_bonus = 5
        
        # 1. ANALIZA COMPLEXITĂȚII (25 puncte)
        complexity_score = 0
        complexity_keywords = ["complexitate", "complexity", "o(", "O(", "liniar", "linear",
                              "exponential", "polinomial", "m×n", "mn", "n²", "n!", "patratic",
                              "timp", "time", "spatiu", "space", "memorie", "rapid", "lent",
                              "temporal", "spațial"]
        found_complexity = [kw for kw in complexity_keywords if kw.lower() in reasoning_lower]
        
        if len(found_complexity) >= 2:
            complexity_score = 25
            feedback_details.append("✅ Complexitate: Analiză completă (+25p)")
        elif len(found_complexity) == 1:
            complexity_score = 15
            feedback_details.append("⚠️ Complexitate: Parțial (+15p) - detaliază mai mult")
            missing_elements.append("Adaugă notația Big-O exactă (ex: O(n!), O(n²))")
        else:
            missing_elements.append("Menționează complexitatea metodei (timp/spațiu)")
        score += complexity_score
        
        # 2. CARACTERISTICI PROBLEMĂ (25 puncte) - specifice fiecărui tip
        char_score = 0
        problem_keywords = self._get_problem_keywords(problem_type)
        found_chars = [kw for kw in problem_keywords if kw.lower() in reasoning_lower]
        
        if len(found_chars) >= 3:
            char_score = 25
            feedback_details.append("✅ Caracteristici problemă: Bine identificate (+25p)")
        elif len(found_chars) >= 1:
            char_score = 15
            feedback_details.append("⚠️ Caracteristici problemă: Parțial (+15p)")
            missing_elements.append("Menționează mai multe caracteristici specifice problemei")
        else:
            missing_elements.append("Identifică caracteristicile problemei (dimensiune, constrângeri)")
        score += char_score
        
        # 3. JUSTIFICARE METODĂ (30 puncte)
        just_score = 0
        justification_patterns = [
            # Conectori explicativi
            (r"deoarece|pentru c[aă]|because|fiindc[aă]|întruc[aâ]t|datorit[aă]|este cea mai", 10),
            # Calificative de eficiență
            (r"optim[aă]?|eficient[aă]?|rapid[aă]?|simpl[aău]|garanteaz[aă]|reduce|minimiz|direct[aă]?|clar[aă]?", 10),
            # Referințe la metodă/strategie
            (r"aceast[aă] metod[aă]|aceast[aă] strategie|am ales|recomand|aleg|trebuie|necesit[aă]|folosit[aă]", 10),
            # Termeni tehnici din justificări (bonus)
            (r"forward checking|backtrack|heuristic|complet[aă]|exhaustiv|căutare|search|echilibr|profil", 5)
        ]
        
        for pattern, points in justification_patterns:
            if re.search(pattern, reasoning_lower):
                just_score += points
        
        # Cap la 30 puncte
        just_score = min(30, just_score)
        
        if just_score >= 25:
            feedback_details.append("✅ Justificare: Excelentă (+30p)")
            just_score = 30
        elif just_score >= 15:
            feedback_details.append(f"⚠️ Justificare: Bună (+{just_score}p) - explică mai clar DE CE")
            missing_elements.append("Folosește conectori explicativi (deoarece, pentru că)")
        elif just_score > 0:
            feedback_details.append(f"⚠️ Justificare: Minimală (+{just_score}p)")
            missing_elements.append("Explică DE CE această metodă e potrivită pentru această problemă")
        else:
            missing_elements.append("Justifică alegerea: DE CE această metodă e optimă?")
        score += just_score
        
        # 4. TRADE-OFFS (20 puncte)
        tradeoff_score = 0
        tradeoff_keywords = ["trade-off", "compromis", "alternativ", "versus", "vs",
                           "în schimb", "dezavantaj", "avantaj", "comparat", "față de",
                           "dar", "însă", "totuși", "pe de altă parte", "reduce", "crește",
                           "simplu", "direct", "complex", "eficient", "rapid", "lent",
                           "optim", "cea mai", "mai bun", "garantat"]
        found_tradeoffs = [kw for kw in tradeoff_keywords if kw.lower() in reasoning_lower]
        
        if len(found_tradeoffs) >= 2:
            tradeoff_score = 20
            feedback_details.append("✅ Trade-offs: Discuție completă (+20p)")
        elif len(found_tradeoffs) == 1:
            tradeoff_score = 10
            feedback_details.append("⚠️ Trade-offs: Parțial (+10p)")
            missing_elements.append("Compară cu metode alternative")
        else:
            missing_elements.append("Discută trade-off-urile: ce pierzi/câștigi vs alte metode?")
        score += tradeoff_score
        
        # Adaugă bonus pentru similaritate
        if similarity_bonus > 0:
            score += similarity_bonus
            feedback_details.append(f"🎯 Bonus similaritate cu răspunsul model (+{similarity_bonus}p)")
        
        # Construiește feedback-ul final
        feedback = "\n".join(feedback_details)
        
        if missing_elements:
            feedback += "\n\n💡 RECOMANDĂRI PENTRU ÎMBUNĂTĂȚIRE:\n"
            for i, elem in enumerate(missing_elements, 1):
                feedback += f"   {i}. {elem}\n"
        
        return min(100, score), feedback
    
    def _get_problem_keywords(self, problem_type: str) -> List[str]:
        """Returnează cuvinte cheie specifice pentru fiecare tip de problemă"""
        keywords = {
            "n-queens": ["regina", "regine", "queens", "atac", "attack", "tabla", "board",
                        "diagonala", "coloana", "rand", "n=", "dimensiune", "solutie", "solutii",
                        "toate", "find_all", "find_one", "complet", "heuristic", "forward", "checking",
                        "backtrack", "cautare", "spatiu"],
            "hanoi": ["turn", "turle", "towers", "disc", "discuri", "disks", "mutari", "moves",
                     "tija", "peg", "recursiv", "iterativ", "minim", "optim", "2^n", "divide"],
            "graph_coloring": ["culoare", "culori", "colors", "nod", "noduri", "vertices",
                              "muchie", "muchii", "edges", "adiacent", "graf", "graph", "cromatic",
                              "dsatur", "welsh", "powell", "greedy", "backtrack"],
            "knights_tour": ["cal", "knight", "tabla", "board", "mutare", "mutari", "moves",
                           "patrat", "casuta", "tur", "tour", "hamiltonian", "warnsdorff",
                           "heuristic", "backtrack"],
            "game_theory": ["nash", "echilibru", "equilibrium", "strategie", "strategy",
                          "dominant", "dominat", "payoff", "plata", "best response",
                          "jucator", "player", "matrice", "matrix", "mixt", "mixed", "pur", "pure",
                          "2x2", "3x3", "coordonare", "zero-sum", "eliminare", "enumerare"]
        }
        return keywords.get(problem_type, ["dimensiune", "complexitate", "solutie", "optim"])
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculează similaritatea între două texte"""
        # Normalize
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        # Use SequenceMatcher for similarity
        similarity = SequenceMatcher(None, text1_lower, text2_lower).ratio()
        
        # Also check for common words
        words1 = set(re.findall(r'\w+', text1_lower))
        words2 = set(re.findall(r'\w+', text2_lower))
        
        if words1 and words2:
            word_similarity = len(words1 & words2) / len(words1 | words2)
            # Average both methods
            similarity = (similarity + word_similarity) / 2
        
        return similarity
    
    def _check_problem_specific_reasoning(self, reasoning: str, problem_type: str) -> int:
        """Verifică dacă justificarea conține elemente specifice problemei"""
        reasoning_lower = reasoning.lower()
        score = 0
        
        if problem_type == "n-queens":
            terms = ["regine", "queens", "atac", "attack", "tabla", "board"]
            score = min(15, sum(5 for term in terms if term in reasoning_lower))
        
        elif problem_type == "hanoi":
            terms = ["turle", "towers", "discuri", "disks", "mutari", "moves"]
            score = min(15, sum(5 for term in terms if term in reasoning_lower))
        
        elif problem_type == "graph_coloring":
            terms = ["culori", "colors", "noduri", "vertices", "muchii", "edges", "adiacent"]
            score = min(15, sum(5 for term in terms if term in reasoning_lower))
        
        elif problem_type == "knights_tour":
            terms = ["cal", "knight", "tabla", "board", "mutari", "moves", "patrat"]
            score = min(15, sum(5 for term in terms if term in reasoning_lower))
        
        elif problem_type == "game_theory":
            terms = ["nash", "echilibru", "equilibrium", "strategie", "strategy", 
                    "dominant", "dominata", "payoff", "plata", "best response",
                    "raspuns optim", "jucator", "player", "matrice", "matrix",
                    "mixt", "mixed", "pur", "pure"]
            score = min(15, sum(3 for term in terms if term in reasoning_lower))
        
        return score
    
    def _generate_feedback(self,
                          strategy_correct: bool,
                          strategy_score: int,
                          reasoning_score: int,
                          correct_strategy: str,
                          correct_reasoning: str,
                          problem_type: str = None,
                          reasoning_details: str = None) -> str:
        """Generează feedback educativ pentru utilizator"""
        
        feedback = "╔══════════════════════════════════════════════════════════════╗\n"
        feedback += "║                    📊 EVALUARE RĂSPUNS                       ║\n"
        feedback += "╚══════════════════════════════════════════════════════════════╝\n\n"
        
        # Strategy feedback
        feedback += "┌─── 🎯 STRATEGIE ─────────────────────────────────────────────┐\n"
        if strategy_correct:
            feedback += "│ ✅ CORECT! Ai identificat strategia optimă.                  │\n"
        elif strategy_score >= 70:
            feedback += "│ ⚠️  ACCEPTABIL - Strategia funcționează, dar nu e optimă.    │\n"
            feedback += f"│ 💡 Strategia optimă: {correct_strategy:<40} │\n"
        elif strategy_score >= 50:
            feedback += "│ ⚠️  ÎNRUDITĂ - Ai ales o metodă din aceeași familie.         │\n"
            feedback += f"│ 💡 Strategia optimă: {correct_strategy:<40} │\n"
        else:
            feedback += "│ ❌ INCORECT - Această metodă nu e potrivită aici.            │\n"
            feedback += f"│ 💡 Strategia corectă: {correct_strategy:<39} │\n"
        
        feedback += f"│ Punctaj: {strategy_score}/100 (contribuție 40% la total)              │\n"
        feedback += "└──────────────────────────────────────────────────────────────┘\n\n"
        
        # Reasoning feedback - cu detalii pentru game theory
        feedback += "┌─── 📝 JUSTIFICARE ───────────────────────────────────────────┐\n"
        
        if reasoning_score >= 80:
            feedback += "│ ✅ EXCELENT! Justificare completă și bine argumentată.       │\n"
        elif reasoning_score >= 60:
            feedback += "│ ✓  BINE - Argumente solide, dar poți îmbunătăți.             │\n"
        elif reasoning_score >= 40:
            feedback += "│ ⚠️  PARȚIAL - Lipsesc elemente importante.                   │\n"
        else:
            feedback += "│ ❌ INSUFICIENT - Justificarea necesită mult mai mult detaliu.│\n"
        
        feedback += f"│ Punctaj: {reasoning_score}/100 (contribuție 60% la total)              │\n"
        feedback += "└──────────────────────────────────────────────────────────────┘\n"
        
        # Add detailed reasoning feedback if available (pentru game theory)
        if reasoning_details:
            feedback += "\n📋 DETALII EVALUARE JUSTIFICARE:\n"
            feedback += "─" * 60 + "\n"
            feedback += reasoning_details + "\n"
        
        # Overall score
        total = int(strategy_score * 0.4 + reasoning_score * 0.6)
        
        feedback += "\n╔══════════════════════════════════════════════════════════════╗\n"
        if total >= 80:
            feedback += f"║  🌟 PUNCTAJ TOTAL: {total}/100 - EXCELENT!                       ║\n"
        elif total >= 60:
            feedback += f"║  ✓  PUNCTAJ TOTAL: {total}/100 - BINE                            ║\n"
        elif total >= 40:
            feedback += f"║  ⚠️  PUNCTAJ TOTAL: {total}/100 - NECESITĂ ÎMBUNĂTĂȚIRI          ║\n"
        else:
            feedback += f"║  ❌ PUNCTAJ TOTAL: {total}/100 - REVIZUIEȘTE MATERIALUL          ║\n"
        feedback += "╚══════════════════════════════════════════════════════════════╝\n\n"
        
        # Add correct reasoning with educational context
        feedback += "═══════════════════════════════════════════════════════════════\n"
        feedback += "                    📚 RĂSPUNS MODEL\n"
        feedback += "═══════════════════════════════════════════════════════════════\n\n"
        feedback += f"🎯 Strategie: {correct_strategy}\n\n"
        feedback += "📝 Justificare:\n"
        feedback += "─" * 60 + "\n"
        feedback += f"{correct_reasoning}\n"
        feedback += "─" * 60 + "\n"
        
        # Educational tips based on problem type
        feedback += "\n💡 SFATURI PENTRU ÎMBUNĂTĂȚIRE:\n"
        feedback += "─" * 60 + "\n"
        
        if problem_type == "game_theory":
            feedback += "• Verifică ÎNTÂI dacă există echilibru Nash pur\n"
            feedback += "• Dacă NU există echilibru pur → trebuie strategii mixte\n"
            feedback += "• Pentru jocuri 2x2 cu echilibru pur → enumerare directă\n"
            feedback += "• Dacă există strategie dominantă → eliminare iterativă (IESDS)\n"
            feedback += "• Menționează ÎNTOTDEAUNA complexitatea metodei alese\n"
        elif problem_type == "n-queens":
            feedback += "• Pentru N mic (≤15): backtracking simplu e suficient\n"
            feedback += "• Pentru N mediu (15-50): folosește heuristici (MRV, forward checking)\n"
            feedback += "• Pentru N mare (>50): local search sau simulated annealing\n"
            feedback += "• Menționează complexitatea: O(n!) pentru backtracking\n"
        elif problem_type == "hanoi":
            feedback += "• Pentru 3 turnuri: soluția recursivă clasică e optimă\n"
            feedback += "• Pentru 4+ turnuri: algoritmul Frame-Stewart\n"
            feedback += "• Număr minim mutări pentru 3 turnuri: 2^n - 1\n"
            feedback += "• Menționează dacă preferi recursiv vs iterativ\n"
        elif problem_type == "graph_coloring":
            feedback += "• Pentru grafuri mici: backtracking garantează optim\n"
            feedback += "• Pentru grafuri mari: greedy DSatur sau Welsh-Powell\n"
            feedback += "• Grafuri planare: teorema celor 4 culori\n"
            feedback += "• Menționează numărul cromatic și densitatea grafului\n"
        elif problem_type == "knights_tour":
            feedback += "• Heuristica Warnsdorff: alegem căsuța cu cele mai puține opțiuni\n"
            feedback += "• Pentru table mari: Warnsdorff e aproape întotdeauna optim\n"
            feedback += "• Tur închis vs deschis: turul închis revine la start\n"
            feedback += "• Backtracking simplu devine ineficient pentru N > 6\n"
        else:
            feedback += "• Analizează dimensiunea și caracteristicile instanței\n"
            feedback += "• Menționează complexitatea temporală și spațială\n"
            feedback += "• Compară cu metode alternative când e relevant\n"
            feedback += "• Justifică DE CE metoda aleasă e potrivită\n"
        
        return feedback


def evaluate_from_text(question_data: Dict[str, Any], answer_text: str) -> Dict[str, Any]:
    """
    Helper function pentru evaluare rapidă din text
    
    Args:
        question_data: Dict cu informații despre întrebare (din Question.to_dict())
        answer_text: Text răspuns utilizator
    
    Returns:
        Dict cu rezultatul evaluării
    """
    evaluator = AnswerEvaluator()
    
    # Parse answer
    user_answer = evaluator.parse_answer(answer_text)
    
    # Evaluate
    result = evaluator.evaluate_answer(
        user_answer=user_answer,
        correct_strategy=question_data["correct_strategy"],
        correct_reasoning=question_data["reasoning"],
        problem_type=question_data["problem_type"],
        instance=question_data["instance"]
    )
    
    # Adaugă răspunsul utilizatorului în rezultat pentru PDF
    result['user_answer'] = f"Strategie: {user_answer.strategy}\nJustificare: {user_answer.reasoning}"
    
    return result


if __name__ == "__main__":
    # Test the evaluator
    evaluator = AnswerEvaluator()
    
    print("=== ANSWER EVALUATOR TEST ===\n")
    
    # Test case 1: Correct answer
    test_question = {
        "problem_type": "n-queens",
        "instance": {"size": 8},
        "correct_strategy": "backtracking",
        "reasoning": "Pentru n=8, backtracking poate explora complet spațiul de căutare în timp rezonabil. Complexitatea O(n!) este acceptabilă pentru dimensiuni mici."
    }
    
    user_answer_text = """
    Răspuns: backtracking
    
    Justificare: Pentru n=8, spațiul de căutare este suficient de mic pentru explorare completă.
    Backtracking garantează găsirea tuturor soluțiilor cu complexitate O(8!), ceea ce este
    acceptabil în practică. Strategia este optimă pentru această dimensiune deoarece
    putem găsi soluția exactă rapid.
    """
    
    result = evaluate_from_text(test_question, user_answer_text)
    
    print(result["feedback"])
    print(f"\n📊 Score: {result['score']}/100")
    
    print("\n" + "="*70)
    print("\n=== TEST 2: Partial answer ===\n")
    
    user_answer_text2 = "Backtracking pentru că merge bine"
    
    result2 = evaluate_from_text(test_question, user_answer_text2)
    print(result2["feedback"])
    print(f"\n📊 Score: {result2['score']}/100")
