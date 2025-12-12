"""
Hybrid Question Generator - Combină template-based, rule-based și parametric
Core engine pentru generarea întrebărilor
"""

import random
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

from knowledge_base import KNOWLEDGE_BASE, QUESTION_TEMPLATES, REASONING_TEMPLATES
from rule_engine import RuleEngine
from parametric_generator import ParametricGenerator
from game_theory_utils import (
    generate_game_instance, format_matrix_ascii, find_pure_nash_equilibria,
    format_nash_equilibria, recommend_strategy, get_classic_game, CLASSIC_GAMES
)


class GenerationMode(Enum):
    """Moduri de generare disponibile"""
    TEMPLATE = "template"
    RULE_BASED = "rule_based"
    PARAMETRIC = "parametric"
    AUTO = "auto"


class Question:
    """Reprezentare a unei întrebări generate"""
    
    def __init__(self, 
                 text: str,
                 problem_type: str,
                 instance: Dict[str, Any],
                 correct_strategy: str,
                 reasoning: str,
                 difficulty: str,
                 generation_mode: str,
                 metadata: Optional[Dict[str, Any]] = None):
        self.text = text
        self.problem_type = problem_type
        self.instance = instance
        self.correct_strategy = correct_strategy
        self.reasoning = reasoning
        self.difficulty = difficulty
        self.generation_mode = generation_mode
        self.metadata = metadata or {}
        self.id = None  # Will be set when added to a test
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertește întrebarea la dicționar"""
        return {
            "id": self.id,
            "text": self.text,
            "problem_type": self.problem_type,
            "instance": self.instance,
            "correct_strategy": self.correct_strategy,
            "reasoning": self.reasoning,
            "difficulty": self.difficulty,
            "generation_mode": self.generation_mode,
            "metadata": self.metadata
        }
    
    def __str__(self) -> str:
        return f"Question(problem={self.problem_type}, difficulty={self.difficulty}, mode={self.generation_mode})"
    
    def __repr__(self) -> str:
        return self.__str__()


class HybridQuestionGenerator:
    """
    Generator hibrid care combină:
    1. Template-Based - pentru întrebări bogate și contextuale
    2. Rule-Based - pentru întrebări comparative și analitice
    3. Parametric - pentru volume mari și variații rapide
    """
    
    def __init__(self):
        self.knowledge_base = KNOWLEDGE_BASE
        self.question_templates = QUESTION_TEMPLATES
        self.reasoning_templates = REASONING_TEMPLATES
        self.rule_engine = RuleEngine()
        self.parametric_generator = ParametricGenerator()
        self.questions_generated = 0
        self.generation_history = []
    
    def generate_question(self, 
                         problem_type: Optional[str] = None,
                         difficulty: Optional[str] = None,
                         mode: GenerationMode = GenerationMode.AUTO) -> Question:
        """
        Generează o întrebare folosind modul specificat
        
        Args:
            problem_type: "n-queens", "hanoi", "graph_coloring", "knights_tour" sau None (random)
            difficulty: "easy", "medium", "hard" sau None (random)
            mode: GenerationMode enum
        
        Returns:
            Question object
        """
        # Select problem type if not specified
        if problem_type is None:
            problem_type = random.choice(list(self.knowledge_base.keys()))
        
        # Select difficulty if not specified
        if difficulty is None:
            difficulty = random.choice(["easy", "medium", "hard"])
        
        # Select generation mode
        if mode == GenerationMode.AUTO:
            mode = self._select_generation_mode()
        
        # Generate based on mode
        if mode == GenerationMode.TEMPLATE:
            question = self._template_generation(problem_type, difficulty)
        elif mode == GenerationMode.RULE_BASED:
            question = self._rule_based_generation(problem_type, difficulty)
        elif mode == GenerationMode.PARAMETRIC:
            question = self._parametric_generation(problem_type, difficulty)
        else:
            raise ValueError(f"Unknown generation mode: {mode}")
        
        self.questions_generated += 1
        self.generation_history.append({
            "problem_type": problem_type,
            "difficulty": difficulty,
            "mode": mode.value
        })
        
        return question
    
    def _select_generation_mode(self) -> GenerationMode:
        """
        Meta-logică pentru selectarea modului de generare
        
        Strategie:
        - Primele 3 întrebări: TEMPLATE (calitate înaltă, context bogat)
        - La fiecare 4 întrebări: RULE_BASED (comparativ, analitic)
        - Restul: PARAMETRIC (volum mare, diversitate)
        """
        if self.questions_generated < 3:
            return GenerationMode.TEMPLATE
        elif self.questions_generated % 4 == 0:
            return GenerationMode.RULE_BASED
        else:
            return GenerationMode.PARAMETRIC
    
    def _template_generation(self, problem_type: str, difficulty: str) -> Question:
        """
        Generare bazată pe template-uri din knowledge base
        Produce întrebări bogate cu mult context
        """
        problem_info = self.knowledge_base[problem_type]
        
        # Generate instance
        instance = self._generate_rich_instance(problem_type, difficulty)
        
        # Select best strategy using rule engine
        strategy, reasoning, confidence = self.rule_engine.infer_strategy(problem_type, instance)
        
        # Select template type based on difficulty
        if difficulty == "easy":
            template_type = "standard"
        elif difficulty == "medium":
            template_type = random.choice(["standard", "comparative"])
        else:  # hard
            template_type = random.choice(["comparative", "scenario", "theoretical"])
        
        templates = self.question_templates.get(template_type, self.question_templates["standard"])
        template = random.choice(templates)
        
        # Format instance description
        instance_desc = self._format_instance_rich(problem_type, instance)
        
        # Build question text
        question_text = template.format(
            problem_name=problem_info["name"],
            formatted_params=instance_desc,
            instance_description=instance_desc,
            strategy_list=self._get_strategy_list(problem_type),
            strategy_a=self._get_strategy_name(problem_type, 0),
            strategy_b=self._get_strategy_name(problem_type, 1),
            backtracking_complexity=self._get_complexity(problem_type, "backtracking"),
            local_search_complexity=self._get_complexity(problem_type, "local_search"),
            csp_complexity=self._get_complexity(problem_type, "csp"),
            time_limit=self._generate_constraint("time"),
            memory_limit=self._generate_constraint("memory"),
            strategy_name=strategy,
            correct_strategy=strategy
        )
        
        # Enhance reasoning with template
        enhanced_reasoning = self._enhance_reasoning(reasoning, problem_type, instance, strategy)
        
        return Question(
            text=question_text,
            problem_type=problem_type,
            instance=instance,
            correct_strategy=strategy,
            reasoning=enhanced_reasoning,
            difficulty=difficulty,
            generation_mode="template",
            metadata={"confidence": confidence, "template_type": template_type}
        )
    
    def _rule_based_generation(self, problem_type: str, difficulty: str) -> Question:
        """
        Generare bazată pe reguli - pentru întrebări comparative
        Creează situații unde mai multe strategii par valide
        """
        # Generate ambiguous instance (boundary case)
        instance = self._generate_boundary_instance(problem_type, difficulty)
        
        # Get all applicable strategies
        all_strategies = self.rule_engine.get_all_applicable_rules(problem_type, instance)
        
        if len(all_strategies) < 2:
            # Not ambiguous enough, get primary strategy
            strategy, reasoning, confidence = self.rule_engine.infer_strategy(problem_type, instance)
            alternatives = [strategy]
        else:
            # Multiple strategies applicable - create comparison
            strategy = all_strategies[0][0]
            reasoning = all_strategies[0][1]
            confidence = all_strategies[0][2]
            alternatives = [s[0] for s in all_strategies[:3]]
        
        # Create comparative question
        problem_info = self.knowledge_base[problem_type]
        instance_desc = self._format_instance_rich(problem_type, instance)
        
        question_text = f"""
Problema: {problem_info['name']}
Instanță: {instance_desc}

Analizați și comparați următoarele strategii pentru această instanță:

{self._format_strategy_comparison(problem_type, alternatives, instance)}

Care este alegerea optimă și de ce? Argumentați considerând:
- Complexitatea temporală și spațială
- Caracteristicile specifice ale instanței
- Trade-off-uri între optimalitate și eficiență
"""
        
        # Build comprehensive reasoning
        comprehensive_reasoning = self._build_comparative_reasoning(
            problem_type, instance, strategy, alternatives
        )
        
        return Question(
            text=question_text.strip(),
            problem_type=problem_type,
            instance=instance,
            correct_strategy=strategy,
            reasoning=comprehensive_reasoning,
            difficulty=difficulty,
            generation_mode="rule_based",
            metadata={"alternatives": alternatives, "confidence": confidence}
        )
    
    def _parametric_generation(self, problem_type: str, difficulty: str) -> Question:
        """
        Generare parametrică - pentru volum mare și variații rapide
        """
        # Special handling for game theory
        if problem_type == "game_theory":
            return self._game_theory_generation(difficulty)
        
        # Use parametric generator
        instance = self.parametric_generator.generate_instance(problem_type, difficulty)
        strategy = self.parametric_generator.lookup_strategy(problem_type, instance)
        reasoning = self.parametric_generator.get_reasoning(problem_type, instance, strategy)
        
        # Simple question format
        problem_info = self.knowledge_base[problem_type]
        instance_desc = self.parametric_generator.format_instance(problem_type, instance)
        
        question_text = f"""
Problema: {problem_info['name']}
Parametri: {instance_desc}

Care este strategia de rezolvare cea mai potrivită pentru această instanță?

Justificați alegerea considerând complexitatea computațională și caracteristicile instanței.
"""
        
        return Question(
            text=question_text.strip(),
            problem_type=problem_type,
            instance=instance,
            correct_strategy=strategy,
            reasoning=reasoning,
            difficulty=difficulty,
            generation_mode="parametric",
            metadata={}
        )
    
    def _generate_rich_instance(self, problem_type: str, difficulty: str) -> Dict[str, Any]:
        """Generează o instanță bogată cu context suplimentar"""
        
        # Special handling for game theory
        if problem_type == "game_theory":
            return self._generate_game_theory_instance(difficulty)
        
        # Start with parametric instance
        instance = self.parametric_generator.generate_instance(problem_type, difficulty)
        
        # Add contextual information based on difficulty
        if difficulty == "hard":
            # Add constraints or special conditions
            if problem_type == "n-queens" and random.random() > 0.5:
                instance["has_constraints"] = True
                instance["constraint_type"] = "forbidden_positions"
            elif problem_type == "hanoi" and random.random() > 0.5:
                instance["has_costs"] = True
            elif problem_type == "graph_coloring":
                instance["need_optimal"] = True
        
        return instance
    
    def _generate_game_theory_instance(self, difficulty: str) -> Dict[str, Any]:
        """Generează o instanță de teoria jocurilor cu matrice"""
        game = generate_game_instance(difficulty)
        
        # Build instance dict with all needed info
        instance = {
            "game_name": game.get("name", "Joc"),
            "game_type": game.get("name_en", "game").lower().replace(" ", "_").replace("'", ""),
            "matrix": game["matrix"],
            "row_strategies": game.get("row_strategies", ["R1", "R2"]),
            "col_strategies": game.get("col_strategies", ["C1", "C2"]),
            "strategies_per_player": len(game["matrix"]),
            "has_pure_nash": game.get("has_pure_nash", True),
            "pure_nash": game.get("pure_nash", []),
            "has_dominant_strategy": game.get("has_dominant_strategy", False),
            "description": game.get("description", "")
        }
        
        return instance
    
    def _game_theory_generation(self, difficulty: str) -> Question:
        """
        Generare specială pentru teoria jocurilor cu matrice afișată
        """
        instance = self._generate_game_theory_instance(difficulty)
        
        # Get recommended strategy
        game_data = {
            "matrix": instance["matrix"],
            "has_pure_nash": instance["has_pure_nash"],
            "pure_nash": instance["pure_nash"],
            "has_dominant_strategy": instance["has_dominant_strategy"]
        }
        strategy, reasoning, confidence = recommend_strategy(game_data)
        
        # Format matrix for display
        matrix_display = format_matrix_ascii(
            instance["matrix"],
            instance["row_strategies"],
            instance["col_strategies"]
        )
        
        # Format Nash equilibria answer
        if instance["has_pure_nash"] and instance["pure_nash"]:
            nash_answer = format_nash_equilibria(
                instance["pure_nash"],
                instance["row_strategies"],
                instance["col_strategies"]
            )
        else:
            nash_answer = "Nu există echilibru Nash în strategii pure. Trebuie calculat echilibrul în strategii mixte."
        
        # Build question text
        question_text = f"""
Problema: Teoria Jocurilor (Formă Normală)
Joc: {instance['game_name']}

Considerați următorul joc în formă normală (matriceală):

{matrix_display}

Întrebări:
1. Există echilibru Nash în strategii pure? Dacă da, care este/sunt?
2. Care este metoda optimă de analiză pentru a găsi echilibrul?

Opțiuni de analiză:
a) Enumerare directă a strategiilor pure
b) Analiza Best Response
c) Eliminare Iterativă a Strategiilor Dominate (IESDS)
d) Calculul echilibrului în strategii mixte

Justificați alegerea metodei considerând caracteristicile jocului.
"""
        
        # Build complete reasoning
        full_reasoning = f"{nash_answer}\n\nMetoda optimă: {strategy}\n{reasoning}"
        
        return Question(
            text=question_text.strip(),
            problem_type="game_theory",
            instance=instance,
            correct_strategy=strategy,
            reasoning=full_reasoning,
            difficulty=difficulty,
            generation_mode="parametric",
            metadata={"confidence": confidence, "nash_answer": nash_answer}
        )
    
    def _generate_boundary_instance(self, problem_type: str, difficulty: str) -> Dict[str, Any]:
        """Generează instanțe la granița dintre strategii (cazuri ambigue)"""
        
        # Valori de graniță actualizate pentru domeniile:
        # N-Queens [4,25], Hanoi [1,22], Graph [5,50], Knight [5,12]
        boundary_values = {
            "n-queens": [10, 18, 25],  # Boundaries: backtracking/heuristics/csp
            "hanoi": {"towers": [3], "disks": [10, 15, 20]},  # Doar 3 tije, graniță la 15
            "graph_coloring": {"vertices": [20, 35, 50]},  # Boundaries în domeniul [5,50]
            "knights_tour": {"board_size": [7, 10, 12]}  # Boundaries în domeniul [5,12]
        }
        
        if problem_type == "n-queens":
            size = random.choice(boundary_values["n-queens"])
            return {"size": size, "objective": random.choice(["find_one", "find_all"])}
        
        elif problem_type == "hanoi":
            return {
                "towers": random.choice(boundary_values["hanoi"]["towers"]),
                "disks": random.choice(boundary_values["hanoi"]["disks"])
            }
        
        elif problem_type == "graph_coloring":
            vertices = random.choice(boundary_values["graph_coloring"]["vertices"])
            return {
                "vertices": vertices,
                "graph_type": random.choice(["random", "sparse"]),
                "density": round(random.uniform(0.25, 0.35), 2)
            }
        
        elif problem_type == "knights_tour":
            return {
                "board_size": random.choice(boundary_values["knights_tour"]["board_size"]),
                "tour_type": random.choice(["open", "closed"])
            }
        
        elif problem_type == "game_theory":
            # Boundary case: Matching Pennies (no pure NE) vs games with pure NE
            boundary_games = ["matching_pennies", "battle_of_sexes", "chicken"]
            game_type = random.choice(boundary_games)
            game = get_classic_game(game_type)
            return {
                "game_name": game.get("name", "Joc"),
                "game_type": game_type,
                "matrix": game["matrix"],
                "row_strategies": game.get("row_strategies", ["R1", "R2"]),
                "col_strategies": game.get("col_strategies", ["C1", "C2"]),
                "strategies_per_player": len(game["matrix"]),
                "has_pure_nash": game.get("has_pure_nash", True),
                "pure_nash": game.get("pure_nash", []),
                "has_dominant_strategy": game.get("has_dominant_strategy", False),
                "description": game.get("description", "")
            }
        
        return self.parametric_generator.generate_instance(problem_type, difficulty)
    
    def _format_instance_rich(self, problem_type: str, instance: Dict[str, Any]) -> str:
        """Formatare bogată a instanței cu detalii suplimentare"""
        
        # Special handling for game theory - include matrix
        if problem_type == "game_theory":
            matrix = instance.get("matrix", [])
            row_strats = instance.get("row_strategies", ["R1", "R2"])
            col_strats = instance.get("col_strategies", ["C1", "C2"])
            game_name = instance.get("game_name", "Joc")
            
            result = f"{game_name} ({len(matrix)}x{len(matrix[0]) if matrix else 0})\n\n"
            result += "Matricea de plăți:\n"
            result += format_matrix_ascii(matrix, row_strats, col_strats)
            # Strip trailing spaces but keep structure, add double newline for proper separation
            result = result.rstrip() + "\n\n"
            return result
        
        base_format = self.parametric_generator.format_instance(problem_type, instance)
        
        # Add complexity hints
        if problem_type == "n-queens":
            size = instance.get("size", 0)
            base_format += f" (spațiu de căutare: ~O({size}!))"
        elif problem_type == "hanoi":
            disks = instance.get("disks", 0)
            base_format += f" (număr minim mutări: 2^{disks}-1 = {2**disks - 1})"
        
        return base_format
    
    def _get_strategy_list(self, problem_type: str) -> str:
        """Returnează lista de strategii pentru problemă"""
        strategies = list(self.knowledge_base[problem_type]["strategies"].keys())
        return ", ".join([s.replace("_", " ").title() for s in strategies[:4]])
    
    def _get_strategy_name(self, problem_type: str, index: int) -> str:
        """Returnează numele unei strategii"""
        strategies = list(self.knowledge_base[problem_type]["strategies"].keys())
        if index < len(strategies):
            return strategies[index].replace("_", " ").title()
        return "Backtracking"
    
    def _get_complexity(self, problem_type: str, strategy_key: str) -> str:
        """Returnează complexitatea unei strategii"""
        strategies = self.knowledge_base[problem_type]["strategies"]
        for key, info in strategies.items():
            if strategy_key in key:
                return info.get("time_complexity", "O(n)")
        return "O(n²)"
    
    def _generate_constraint(self, constraint_type: str) -> str:
        """Generează constrângeri pentru scenarii"""
        if constraint_type == "time":
            return random.choice(["1 secundă", "5 secunde", "10 secunde", "1 minut"])
        elif constraint_type == "memory":
            return random.choice(["100 MB", "500 MB", "1 GB", "2 GB"])
        return "standard"
    
    def _enhance_reasoning(self, base_reasoning: str, problem_type: str, 
                          instance: Dict[str, Any], strategy: str) -> str:
        """Îmbogățește justificarea cu detalii din knowledge base"""
        strategy_info = None
        for key, info in self.knowledge_base[problem_type]["strategies"].items():
            if key == strategy:
                strategy_info = info
                break
        
        if not strategy_info:
            return base_reasoning
        
        enhanced = f"{base_reasoning}\n\n"
        enhanced += f"Detalii despre {strategy_info['name']}:\n"
        enhanced += f"- Complexitate temporală: {strategy_info['time_complexity']}\n"
        enhanced += f"- Complexitate spațială: {strategy_info['space_complexity']}\n"
        enhanced += f"- Avantaje: {', '.join(strategy_info['advantages'][:2])}\n"
        
        return enhanced
    
    def _format_strategy_comparison(self, problem_type: str, strategies: List[str], 
                                   instance: Dict[str, Any]) -> str:
        """Formatează comparația între strategii"""
        comparison = ""
        
        for i, strategy in enumerate(strategies, 1):
            strategy_info = self.knowledge_base[problem_type]["strategies"].get(strategy, {})
            if strategy_info:
                comparison += f"{i}. {strategy_info.get('name', strategy)}:\n"
                comparison += f"   - Complexitate: {strategy_info.get('time_complexity', 'N/A')}\n"
                comparison += f"   - Cel mai bun pentru: {strategy_info.get('best_for', 'N/A')}\n"
                comparison += f"   - Avantaj principal: {strategy_info.get('advantages', [''])[0]}\n\n"
        
        return comparison
    
    def _build_comparative_reasoning(self, problem_type: str, instance: Dict[str, Any],
                                    best_strategy: str, alternatives: List[str]) -> str:
        """Construiește o justificare comparativă detaliată"""
        reasoning = f"Strategia optimă este: {best_strategy}\n\n"
        reasoning += "Analiza comparativă:\n\n"
        
        # Main strategy
        main_info = self.knowledge_base[problem_type]["strategies"].get(best_strategy, {})
        reasoning += f"✓ {best_strategy}:\n"
        reasoning += f"  - Complexitate: {main_info.get('time_complexity', 'N/A')}\n"
        reasoning += f"  - Motivație: {main_info.get('when_to_use', 'N/A')}\n\n"
        
        # Alternatives
        for alt in alternatives:
            if alt != best_strategy:
                alt_info = self.knowledge_base[problem_type]["strategies"].get(alt, {})
                reasoning += f"✗ {alt}:\n"
                reasoning += f"  - Dezavantaj pentru acest caz: {alt_info.get('disadvantages', ['N/A'])[0]}\n\n"
        
        return reasoning
    
    def generate_test(self, num_questions: int = 10, 
                     problem_distribution: Optional[Dict[str, int]] = None,
                     difficulty_distribution: Optional[Dict[str, float]] = None) -> List[Question]:
        """
        Generează un test complet cu mai multe întrebări
        
        Args:
            num_questions: Numărul total de întrebări
            problem_distribution: Dict cu număr de întrebări per problemă
            difficulty_distribution: Dict cu proporții pentru dificultăți
        
        Returns:
            Listă de Question objects
        """
        questions = []
        
        # Default distributions
        if problem_distribution is None:
            problems = list(self.knowledge_base.keys())
            problem_distribution = {p: num_questions // len(problems) for p in problems}
            # Add remainder to first problem
            problem_distribution[problems[0]] += num_questions % len(problems)
        
        if difficulty_distribution is None:
            difficulty_distribution = {"easy": 0.3, "medium": 0.4, "hard": 0.3}
        
        # Generate questions for each problem
        for problem_type, count in problem_distribution.items():
            for _ in range(count):
                # Select difficulty based on distribution
                difficulty = random.choices(
                    list(difficulty_distribution.keys()),
                    weights=list(difficulty_distribution.values())
                )[0]
                
                question = self.generate_question(problem_type, difficulty)
                questions.append(question)
        
        # Assign IDs
        for i, q in enumerate(questions, 1):
            q.id = i
        
        # Shuffle for variety
        random.shuffle(questions)
        
        return questions
    
    def get_statistics(self) -> Dict[str, Any]:
        """Returnează statistici despre întrebările generate"""
        if not self.generation_history:
            return {"total": 0}
        
        problem_counts = {}
        difficulty_counts = {}
        mode_counts = {}
        
        for entry in self.generation_history:
            problem_counts[entry["problem_type"]] = problem_counts.get(entry["problem_type"], 0) + 1
            difficulty_counts[entry["difficulty"]] = difficulty_counts.get(entry["difficulty"], 0) + 1
            mode_counts[entry["mode"]] = mode_counts.get(entry["mode"], 0) + 1
        
        return {
            "total": self.questions_generated,
            "by_problem": problem_counts,
            "by_difficulty": difficulty_counts,
            "by_mode": mode_counts
        }


if __name__ == "__main__":
    # Test the hybrid generator
    generator = HybridQuestionGenerator()
    
    print("=== HYBRID QUESTION GENERATOR TEST ===\n")
    
    # Generate test with mixed questions
    test_questions = generator.generate_test(num_questions=6)
    
    for q in test_questions:
        print(f"\n{'='*80}")
        print(f"ÎNTREBAREA #{q.id} [{q.generation_mode.upper()}]")
        print(f"Problemă: {q.problem_type} | Dificultate: {q.difficulty}")
        print('='*80)
        print(q.text)
        print(f"\n--- RĂSPUNS CORECT ---")
        print(f"Strategie: {q.correct_strategy}")
        print(f"\n--- JUSTIFICARE ---")
        print(q.reasoning)
    
    print(f"\n\n{'='*80}")
    print("STATISTICI GENERARE")
    print('='*80)
    stats = generator.get_statistics()
    print(f"Total întrebări: {stats['total']}")
    print(f"\nDistribuție probleme: {stats['by_problem']}")
    print(f"Distribuție dificultate: {stats['by_difficulty']}")
    print(f"Distribuție mod generare: {stats['by_mode']}")
