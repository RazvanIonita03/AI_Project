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
    
    def _build_strategy_synonyms(self) -> Dict[str, List[str]]:
        """Construiește un dicționar de sinonime pentru strategii"""
        return {
            "backtracking": ["backtracking", "back tracking", "cautare cu revenire", "explorare exhaustiva"],
            "backtracking_with_heuristics": ["backtracking cu heuristici", "backtracking heuristic", "forward checking", "mrv"],
            "csp_forward_checking": ["csp", "constraint satisfaction", "forward checking", "arc consistency"],
            "local_search": ["local search", "cautare locala", "hill climbing", "min conflicts"],
            "simulated_annealing": ["simulated annealing", "recoacere simulata", "annealing"],
            "recursive_divide_conquer": ["recursiv", "recursive", "divide and conquer", "divide et impera"],
            "iterative": ["iterativ", "iterative"],
            "frame_stewart_algorithm": ["frame stewart", "frame-stewart"],
            "dynamic_programming": ["programare dinamica", "dynamic programming", "dp", "memoization"],
            "greedy_basic": ["greedy", "lacom", "algoritm lacom"],
            "greedy_dsatur": ["dsatur", "degree of saturation", "greedy dsatur"],
            "backtracking_with_bounds": ["branch and bound", "backtracking with bounds"],
            "welsh_powell": ["welsh powell", "welsh-powell"],
            "planar_4color": ["4 color", "four color", "4-color", "planar"],
            "local_search_tabu": ["tabu search", "cautare tabu"],
            "warnsdorff_heuristic": ["warnsdorff", "warnsdorf"],
            "backtracking_warnsdorff": ["backtracking warnsdorff", "warnsdorff backtracking"],
            "divide_conquer": ["divide conquer", "divide and conquer", "divide et impera"]
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
        reasoning_score, reasoning_feedback = self._evaluate_reasoning(
            user_answer.reasoning,
            correct_reasoning,
            user_answer.parsed_concepts,
            problem_type
        )
        
        # Calculate total score
        total_score = int(strategy_score * 0.4 + reasoning_score * 0.6)
        
        # Generate feedback
        feedback = self._generate_feedback(
            strategy_correct,
            strategy_score,
            reasoning_score,
            correct_strategy,
            correct_reasoning
        )
        
        return {
            "score": total_score,
            "strategy_correct": strategy_correct,
            "strategy_score": strategy_score,
            "reasoning_score": reasoning_score,
            "feedback": feedback,
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
            ["recursive_divide_conquer", "divide_conquer"]
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
        Evaluează calitatea justificării
        
        Returns:
            (score 0-100, feedback string)
        """
        score = 0
        feedback_parts = []
        
        # 1. Length check (minimum effort)
        if len(user_reasoning) < 20:
            feedback_parts.append("❌ Justificare prea scurtă")
            return 10, "; ".join(feedback_parts)
        
        score += 10
        feedback_parts.append("✓ Lungime adecvată")
        
        # 2. Concept coverage (30 points)
        required_concepts = ["complexitate", "eficient", "optim", "timp", "spatiu"]
        found_required = sum(1 for concept in required_concepts 
                           if any(concept in c.lower() for c in user_concepts))
        
        concept_score = min(30, int(found_required / len(required_concepts) * 30))
        score += concept_score
        
        if concept_score >= 20:
            feedback_parts.append("✓ Concepte cheie prezente")
        else:
            feedback_parts.append("⚠ Lipsesc unele concepte cheie")
        
        # 3. Complexity analysis (25 points)
        has_big_o = bool(re.search(r'O\s*\(', user_reasoning, re.IGNORECASE))
        mentions_complexity = any(word in user_reasoning.lower() 
                                 for word in ["complexitate", "complexity"])
        
        if has_big_o and mentions_complexity:
            score += 25
            feedback_parts.append("✓ Analiză de complexitate prezentă")
        elif has_big_o or mentions_complexity:
            score += 15
            feedback_parts.append("⚠ Analiză de complexitate parțială")
        else:
            feedback_parts.append("❌ Lipsește analiza de complexitate")
        
        # 4. Similarity with correct reasoning (20 points)
        similarity = self._calculate_similarity(user_reasoning, correct_reasoning)
        similarity_score = int(similarity * 20)
        score += similarity_score
        
        if similarity > 0.5:
            feedback_parts.append("✓ Raționament similar cu cel corect")
        elif similarity > 0.3:
            feedback_parts.append("⚠ Raționament parțial similar")
        else:
            feedback_parts.append("❌ Raționament diferit de cel așteptat")
        
        # 5. Problem-specific analysis (15 points)
        problem_specific_score = self._check_problem_specific_reasoning(
            user_reasoning, problem_type
        )
        score += problem_specific_score
        
        if problem_specific_score >= 10:
            feedback_parts.append("✓ Analiză specifică problemei")
        
        return min(100, score), "; ".join(feedback_parts)
    
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
        
        return score
    
    def _generate_feedback(self,
                          strategy_correct: bool,
                          strategy_score: int,
                          reasoning_score: int,
                          correct_strategy: str,
                          correct_reasoning: str) -> str:
        """Generează feedback pentru utilizator"""
        
        feedback = "=== EVALUARE RĂSPUNS ===\n\n"
        
        # Strategy feedback
        if strategy_correct:
            feedback += "✅ STRATEGIE CORECTĂ!\n"
        elif strategy_score >= 70:
            feedback += "⚠️ STRATEGIE ACCEPTABILĂ (nu optimă)\n"
            feedback += f"💡 Strategia optimă era: {correct_strategy}\n"
        elif strategy_score >= 50:
            feedback += "⚠️ STRATEGIE ÎNRUDITĂ (dar nu cea mai bună)\n"
            feedback += f"💡 Strategia optimă era: {correct_strategy}\n"
        else:
            feedback += "❌ STRATEGIE INCORECTĂ\n"
            feedback += f"💡 Strategia corectă era: {correct_strategy}\n"
        
        feedback += f"Punctaj strategie: {strategy_score}/100\n\n"
        
        # Reasoning feedback
        feedback += "--- JUSTIFICARE ---\n"
        if reasoning_score >= 80:
            feedback += "✅ Justificare excelentă!\n"
        elif reasoning_score >= 60:
            feedback += "✓ Justificare bună, dar poate fi îmbunătățită\n"
        elif reasoning_score >= 40:
            feedback += "⚠️ Justificare parțială - lipsesc elemente importante\n"
        else:
            feedback += "❌ Justificare insuficientă\n"
        
        feedback += f"Punctaj justificare: {reasoning_score}/100\n\n"
        
        # Overall
        total = int(strategy_score * 0.4 + reasoning_score * 0.6)
        feedback += f"--- PUNCTAJ TOTAL: {total}/100 ---\n\n"
        
        # Add correct reasoning
        feedback += "=== RĂSPUNS CORECT COMPLET ===\n"
        feedback += f"Strategie: {correct_strategy}\n\n"
        feedback += f"Justificare:\n{correct_reasoning}\n"
        
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
