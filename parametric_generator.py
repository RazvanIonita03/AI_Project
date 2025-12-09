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
                "size": [4, 6, 8, 10, 12, 15, 20, 25, 30, 50, 100],
                "objective": ["find_one", "find_all", "count_solutions"],
                "constraints": ["none", "forbidden_positions"]
            },
            
            "hanoi": {
                "towers": [3, 4, 5],
                "disks": [3, 5, 8, 10, 12, 15, 20, 25, 30],
                "variant": ["standard", "weighted_disks", "limited_moves"]
            },
            
            "graph_coloring": {
                "vertices": [5, 10, 20, 30, 50, 100, 200, 500, 1000],
                "graph_type": ["random", "planar", "bipartite", "complete", "sparse", "dense"],
                "density": [0.1, 0.2, 0.3, 0.5, 0.7, 0.9],
                "need_optimal": [True, False]
            },
            
            "knights_tour": {
                "board_size": [5, 6, 8, 10, 12, 16, 20, 50, 100],
                "tour_type": ["open", "closed"],
                "start_position": ["corner", "edge", "center"]
            }
        }
    
    def _define_strategy_mappings(self) -> Dict[str, List[Tuple[Any, str]]]:
        """
        Definește mapări parametru -> strategie
        Format: [(condition, strategy), ...]
        """
        return {
            "n-queens": [
                (lambda p: p["size"] <= 8, "backtracking"),
                (lambda p: 8 < p["size"] <= 15, "backtracking_with_heuristics"),
                (lambda p: 15 < p["size"] <= 25, "csp_forward_checking"),
                (lambda p: 25 < p["size"] <= 50, "local_search"),
                (lambda p: p["size"] > 50, "simulated_annealing"),
                (lambda p: p.get("objective") == "find_all", "backtracking_with_heuristics"),
            ],
            
            "hanoi": [
                (lambda p: p["towers"] == 3 and p["disks"] <= 20, "recursive_divide_conquer"),
                (lambda p: p["towers"] == 3 and p["disks"] > 20, "iterative"),
                (lambda p: p["towers"] > 3 and p["disks"] <= 15, "frame_stewart_algorithm"),
                (lambda p: p["towers"] > 3 and p["disks"] > 15, "iterative"),
                (lambda p: p.get("variant") == "weighted_disks", "dynamic_programming"),
            ],
            
            "graph_coloring": [
                (lambda p: p.get("graph_type") == "bipartite", "greedy_basic"),
                (lambda p: p.get("graph_type") == "planar", "planar_4color"),
                (lambda p: p["vertices"] <= 30 and p.get("need_optimal"), "backtracking_with_bounds"),
                (lambda p: 30 < p["vertices"] <= 500, "greedy_dsatur"),
                (lambda p: p["vertices"] > 500, "local_search_tabu"),
                (lambda p: p.get("density", 0.5) < 0.3, "greedy_dsatur"),
                (lambda p: p.get("density", 0.5) > 0.7, "welsh_powell"),
            ],
            
            "knights_tour": [
                (lambda p: p["board_size"] <= 6, "backtracking_warnsdorff"),
                (lambda p: 6 < p["board_size"] <= 20, "warnsdorff_heuristic"),
                (lambda p: p["board_size"] > 20 and p["board_size"] % 2 == 0, "divide_conquer"),
                (lambda p: p["board_size"] > 50, "warnsdorff_heuristic"),
                (lambda p: p.get("tour_type") == "closed" and p["board_size"] <= 10, "backtracking_warnsdorff"),
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
        
        return f"Strategia {strategy} este optimă pentru acești parametri."


def generate_parametric_question_text(problem_type: str, instance: Dict[str, Any], strategy: str) -> str:
    """Generează textul complet al întrebării"""
    
    problem_names = {
        "n-queens": "N-Queens",
        "hanoi": "Turnurile din Hanoi",
        "graph_coloring": "Colorarea Grafurilor",
        "knights_tour": "Tura Calului"
    }
    
    generator = ParametricGenerator()
    instance_text = generator.format_instance(problem_type, instance)
    
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
