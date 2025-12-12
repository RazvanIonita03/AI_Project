"""
Parametric Question Generator
Generare rapidă de întrebări din spațiul parametric
"""

import random
import itertools
from typing import Dict, List, Any, Tuple


class ParametricGenerator:
    """Generator parametric pentru volume mari de întrebări"""
    
    def __init__(self):
        self.parameter_space = self._define_parameter_space()
        self.strategy_mappings = self._define_strategy_mappings()
    
    def _define_parameter_space(self) -> Dict[str, Dict[str, List[Any]]]:
        """Definește spațiul parametric pentru fiecare problemă"""
        return {
            "n-queens": {
                # n ∈ [4, 25] pentru rezolvare exactă
                "size": [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
                "objective": ["find_one", "find_all", "count_solutions"],
                "constraints": ["none", "forbidden_positions"]
            },
            
            "hanoi": {
                "towers": [3],  # Doar 3 tije pentru simulare mutări
                # n ∈ [1, 22] pentru Hanoi
                "disks": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22],
                "variant": ["standard", "weighted_disks", "limited_moves"]
            },
            
            "graph_coloring": {
                # n ∈ [5, 50] pentru graf general, exact
                "vertices": [5, 6, 7, 8, 9, 10, 12, 15, 18, 20, 22, 25, 28, 30, 35, 40, 45, 50],
                "graph_type": ["random", "planar", "bipartite", "complete", "sparse", "dense"],
                "density": [0.1, 0.2, 0.3, 0.5, 0.7, 0.9],
                "need_optimal": [True, False]
            },
            
            "knights_tour": {
                # n ∈ [5, 12] pentru backtracking exact
                "board_size": [5, 6, 7, 8, 9, 10, 11, 12],
                "tour_type": ["open", "closed"],
                "start_position": ["corner", "edge", "center"]
            },
            
            "game_theory": {
                "strategies_per_player": [2, 2, 2, 3, 3, 4],  # More 2x2 games
                "game_type": ["prisoners_dilemma", "battle_of_sexes", "coordination_game", 
                             "chicken", "matching_pennies", "stag_hunt", "random"],
                "has_pure_nash": [True, True, True, False],  # More with pure NE
                "has_dominant_strategy": [True, False, False, False]
            }
        }
    
    def _define_strategy_mappings(self) -> Dict[str, List[Tuple[Any, str]]]:
        """
        Definește mapări parametru -> strategie
        Format: [(condition, strategy), ...]
        Actualizat pentru domeniile: N-Queens [4,25], Hanoi [1,22], Graph [5,50], Knight [5,12]
        """
        return {
            "n-queens": [
                # Pentru n ∈ [4, 25]
                (lambda p: p["size"] <= 10, "backtracking"),
                (lambda p: 10 < p["size"] <= 18, "backtracking_with_heuristics"),
                (lambda p: p["size"] > 18, "csp_forward_checking"),
                (lambda p: p.get("objective") == "find_all" and p["size"] <= 12, "backtracking"),
                (lambda p: p.get("objective") == "find_all" and p["size"] > 12, "backtracking_with_heuristics"),
            ],
            
            "hanoi": [
                # Pentru n ∈ [1, 22] cu 3 tije
                (lambda p: p["towers"] == 3 and p["disks"] <= 15, "recursive_divide_conquer"),
                (lambda p: p["towers"] == 3 and p["disks"] > 15, "iterative"),
                (lambda p: p.get("variant") == "weighted_disks", "dynamic_programming"),
            ],
            
            "graph_coloring": [
                # Pentru n ∈ [5, 50]
                (lambda p: p.get("graph_type") == "bipartite", "greedy_basic"),
                (lambda p: p.get("graph_type") == "planar", "planar_4color"),
                (lambda p: p["vertices"] <= 20 and p.get("need_optimal"), "backtracking_with_bounds"),
                (lambda p: 20 < p["vertices"] <= 35, "greedy_dsatur"),
                (lambda p: p["vertices"] > 35, "welsh_powell"),
                (lambda p: p.get("density", 0.5) < 0.3, "greedy_dsatur"),
                (lambda p: p.get("density", 0.5) > 0.7, "welsh_powell"),
            ],
            
            "knights_tour": [
                # Pentru n ∈ [5, 12] - toate folosesc backtracking exact
                (lambda p: p["board_size"] <= 7, "backtracking_warnsdorff"),
                (lambda p: p["board_size"] > 7, "warnsdorff_heuristic"),
                (lambda p: p.get("tour_type") == "closed", "backtracking_warnsdorff"),
            ],
            
            "game_theory": [
                (lambda p: p.get("has_dominant_strategy", False), "dominance_elimination"),
                (lambda p: p.get("has_pure_nash", True) == False, "mixed_strategy_calculation"),
                (lambda p: p.get("strategies_per_player", 2) <= 2, "pure_strategy_enumeration"),
                (lambda p: p.get("strategies_per_player", 2) == 3, "best_response_analysis"),
                (lambda p: p.get("strategies_per_player", 2) >= 4, "dominance_elimination"),
                (lambda p: p.get("game_type") == "prisoners_dilemma", "dominance_elimination"),
                (lambda p: p.get("game_type") in ["coordination_game", "battle_of_sexes"], "pure_strategy_enumeration"),
            ]
        }
    
    def lookup_strategy(self, problem_type: str, params: Dict[str, Any]) -> str:
        """Găsește strategia optimă pentru parametrii dați"""
        mappings = self.strategy_mappings.get(problem_type, [])
        
        for condition_func, strategy in mappings:
            try:
                if condition_func(params):
                    return strategy
            except:
                continue
        
        # Default fallback
        return "backtracking"
    
    def generate_instance(self, problem_type: str, difficulty: str = "medium") -> Dict[str, Any]:
        """Generează o instanță aleatorie pentru problemă"""
        space = self.parameter_space.get(problem_type, {})
        
        if not space:
            return {}
        
        instance = {}
        
        # Difficulty-based selection
        difficulty_ranges = {
            "easy": (0, 0.3),
            "medium": (0.3, 0.7),
            "hard": (0.7, 1.0)
        }
        
        range_min, range_max = difficulty_ranges.get(difficulty, (0.3, 0.7))
        
        for param_name, param_values in space.items():
            if isinstance(param_values[0], (int, float)):
                # Numeric parameter - select based on difficulty
                sorted_values = sorted(param_values)
                start_idx = int(len(sorted_values) * range_min)
                end_idx = int(len(sorted_values) * range_max)
                end_idx = max(end_idx, start_idx + 1)
                instance[param_name] = random.choice(sorted_values[start_idx:end_idx])
            else:
                # Categorical parameter - random choice
                instance[param_name] = random.choice(param_values)
        
        return instance
    
    def generate_all_combinations(self, problem_type: str, max_combinations: int = None) -> List[Dict[str, Any]]:
        """Generează toate combinațiile posibile de parametri"""
        space = self.parameter_space.get(problem_type, {})
        
        if not space:
            return []
        
        # Generate all combinations
        param_names = list(space.keys())
        param_values = [space[name] for name in param_names]
        
        all_combinations = []
        for combination in itertools.product(*param_values):
            instance = dict(zip(param_names, combination))
            all_combinations.append(instance)
            
            if max_combinations and len(all_combinations) >= max_combinations:
                break
        
        return all_combinations
    
    def generate_questions_batch(self, problem_type: str, count: int = 10, difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generează un batch de întrebări"""
        questions = []
        
        for _ in range(count):
            instance = self.generate_instance(problem_type, difficulty)
            strategy = self.lookup_strategy(problem_type, instance)
            
            question = {
                "problem_type": problem_type,
                "instance": instance,
                "correct_strategy": strategy,
                "difficulty": difficulty
            }
            
            questions.append(question)
        
        return questions
    
    def generate_diverse_set(self, total_questions: int = 20) -> List[Dict[str, Any]]:
        """Generează un set divers de întrebări pentru toate problemele"""
        problems = list(self.parameter_space.keys())
        questions_per_problem = total_questions // len(problems)
        
        all_questions = []
        
        for problem in problems:
            # Mix difficulties
            easy_count = questions_per_problem // 3
            medium_count = questions_per_problem // 3
            hard_count = questions_per_problem - easy_count - medium_count
            
            all_questions.extend(self.generate_questions_batch(problem, easy_count, "easy"))
            all_questions.extend(self.generate_questions_batch(problem, medium_count, "medium"))
            all_questions.extend(self.generate_questions_batch(problem, hard_count, "hard"))
        
        # Shuffle pentru diversitate
        random.shuffle(all_questions)
        
        return all_questions
    
    def format_instance(self, problem_type: str, instance: Dict[str, Any]) -> str:
        """Formatează instanța pentru afișare în întrebare"""
        if problem_type == "n-queens":
            text = f"n = {instance.get('size', 'N/A')}"
            if instance.get('objective') and instance['objective'] != 'find_one':
                text += f", obiectiv: {instance['objective']}"
            if instance.get('constraints') and instance['constraints'] != 'none':
                text += f", cu constrângeri: {instance['constraints']}"
            return text
        
        elif problem_type == "hanoi":
            text = f"{instance.get('disks', 'N/A')} discuri, {instance.get('towers', 3)} turle"
            if instance.get('variant') and instance['variant'] != 'standard':
                text += f", variant: {instance['variant']}"
            return text
        
        elif problem_type == "graph_coloring":
            text = f"{instance.get('vertices', 'N/A')} noduri"
            if instance.get('graph_type'):
                text += f", tip: {instance['graph_type']}"
            if instance.get('density') is not None:
                text += f", densitate: {instance['density']:.1f}"
            return text
        
        elif problem_type == "knights_tour":
            text = f"tablă {instance.get('board_size', 'N/A')}×{instance.get('board_size', 'N/A')}"
            if instance.get('tour_type'):
                text += f", tură {instance['tour_type']}"
            if instance.get('start_position'):
                text += f", start: {instance['start_position']}"
            return text
        
        elif problem_type == "game_theory":
            game_type = instance.get('game_type', 'random')
            strats = instance.get('strategies_per_player', 2)
            game_names = {
                'prisoners_dilemma': 'Dilema Prizonierului',
                'battle_of_sexes': 'Bătălia Sexelor',
                'coordination_game': 'Joc de Coordonare',
                'chicken': 'Jocul Fricosului (Chicken)',
                'matching_pennies': 'Potrivirea Monedelor',
                'stag_hunt': 'Vânătoarea de Cerbi',
                'random': 'Joc Aleator'
            }
            text = f"joc {strats}x{strats}"
            if game_type != 'random':
                text += f" - {game_names.get(game_type, game_type)}"
            if instance.get('has_dominant_strategy'):
                text += ", cu strategie dominantă"
            if not instance.get('has_pure_nash', True):
                text += ", fără echilibru Nash pur"
            return text
        
        return str(instance)
    
    def get_reasoning(self, problem_type: str, instance: Dict[str, Any], strategy: str) -> str:
        """Generează justificare pentru strategie aleasă"""
        
        # Simple reasoning based on key parameters
        if problem_type == "n-queens":
            size = instance.get('size', 0)
            if size <= 8:
                return f"Pentru n = {size}, backtracking explorează complet spațiul în timp acceptabil O(n!)."
            elif size <= 25:
                return f"Pentru n = {size}, metodele CSP cu heuristici oferă cel mai bun compromis eficiență-completitudine."
            else:
                return f"Pentru n = {size}, doar local search scalează eficient, găsind soluții în O(n²) per iterație."
        
        elif problem_type == "hanoi":
            towers = instance.get('towers', 3)
            disks = instance.get('disks', 0)
            if towers == 3:
                return f"Pentru Hanoi clasic cu {disks} discuri, soluția recursivă produce numărul minim de mutări: 2^{disks} - 1."
            else:
                return f"Pentru {towers} turle, Frame-Stewart generalizează algoritmul clasic optimal."
        
        elif problem_type == "graph_coloring":
            vertices = instance.get('vertices', 0)
            graph_type = instance.get('graph_type', 'random')
            if graph_type == "planar":
                return "Teorema celor 4 culori garantează soluție cu maxim 4 culori pentru grafuri planare."
            elif vertices > 500:
                return f"Pentru {vertices} noduri, doar heuristicile de tip local search sunt scalabile."
            else:
                return f"Pentru {vertices} noduri, heuristici greedy oferă rezultate bune în timp polinomial."
        
        elif problem_type == "knights_tour":
            size = instance.get('board_size', 0)
            if size <= 6:
                return f"Pentru table mici ({size}×{size}), backtracking găsește rapid soluția cu heuristici."
            else:
                return f"Pentru table mari ({size}×{size}), heuristica Warnsdorff găsește soluții în O(n²) cu succes >99%."
        
        elif problem_type == "game_theory":
            game_type = instance.get('game_type', 'random')
            strats = instance.get('strategies_per_player', 2)
            has_dom = instance.get('has_dominant_strategy', False)
            has_pure = instance.get('has_pure_nash', True)
            
            if has_dom:
                return f"Există strategie dominantă în acest joc. Eliminarea strategiilor dominate (IESDS) simplifică analiza și conduce direct la echilibrul Nash."
            elif not has_pure:
                return f"Nu există echilibru Nash pur în acest joc (similar cu Matching Pennies). Trebuie calculat echilibrul în strategii mixte."
            elif strats <= 2:
                return f"Pentru un joc 2x2, enumerarea directă a celor 4 profiluri de strategie și verificarea best response-urilor este cea mai eficientă metodă."
            elif strats == 3:
                return f"Pentru un joc 3x3, analiza sistematică a best response-urilor identifică toate echilibrele Nash pure."
            else:
                return f"Pentru jocuri mai mari ({strats}x{strats}), prima etapă este eliminarea strategiilor dominate pentru a reduce dimensiunea problemei."
        
        return f"Strategia {strategy} este optimă pentru acești parametri."


def generate_parametric_question_text(problem_type: str, instance: Dict[str, Any], strategy: str) -> str:
    """Generează textul complet al întrebării"""
    
    problem_names = {
        "n-queens": "N-Queens",
        "hanoi": "Turnurile din Hanoi",
        "graph_coloring": "Colorarea Grafurilor",
        "knights_tour": "Turul Cavalerului",
        "game_theory": "Teoria Jocurilor (Formă Normală)"
    }
    
    generator = ParametricGenerator()
    instance_text = generator.format_instance(problem_type, instance)
    
    if problem_type == "game_theory":
        # Special formatting for game theory questions
        question = f"""
Problema: {problem_names.get(problem_type, problem_type)}
Instanță: {instance_text}

Pentru acest joc în formă normală (matriceală):
1. Există echilibru Nash în strategii pure? Dacă da, care este?
2. Care este cea mai bună metodă de analiză pentru a găsi echilibrul?

Opțiuni de analiză:
a) Enumerare directă a strategiilor pure
b) Analiza Best Response
c) Eliminare Iterativă a Strategiilor Dominate (IESDS)
d) Calculul echilibrului în strategii mixte

Justificați alegerea metodei considerând caracteristicile jocului.
"""
    else:
        question = f"""
Problema: {problem_names.get(problem_type, problem_type)}
Instanță: {instance_text}

Care este strategia de rezolvare cea mai potrivită pentru această instanță?

Opțiuni:
a) Backtracking (cu sau fără heuristici)
b) Local Search (Hill Climbing, Simulated Annealing)
c) Constraint Satisfaction cu Forward Checking
d) Divide & Conquer
e) Algoritmi specifici (Frame-Stewart, Warnsdorff, DSATUR, etc.)

Justificați alegerea considerând complexitatea computațională și caracteristicile instanței.
"""
    
    return question.strip()


if __name__ == "__main__":
    # Test the parametric generator
    generator = ParametricGenerator()
    
    print("=== PARAMETRIC QUESTION GENERATOR TEST ===\n")
    
    # Generate diverse set
    questions = generator.generate_diverse_set(12)
    
    for i, q in enumerate(questions[:6], 1):
        print(f"\n{'='*70}")
        print(f"ÎNTREBARE {i}")
        print('='*70)
        print(generate_parametric_question_text(q["problem_type"], q["instance"], q["correct_strategy"]))
        print(f"\nRăspuns corect: {q['correct_strategy']}")
        print(f"Dificultate: {q['difficulty']}")
        print(f"\nJustificare: {generator.get_reasoning(q['problem_type'], q['instance'], q['correct_strategy'])}")
    
    print(f"\n\n{'='*70}")
    print(f"Total întrebări generate: {len(questions)}")
    print(f"Distribuție probleme: {[q['problem_type'] for q in questions]}")
