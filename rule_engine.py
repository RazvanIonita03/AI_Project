"""
Rule-Based Expert System pentru decizie strategie optimă
Folosește reguli logice pentru a determina cea mai bună strategie
"""

import re
from typing import Dict, List, Tuple, Any


class Rule:
    """Reprezentare a unei reguli de decizie"""
    
    def __init__(self, condition_func, conclusion: str, confidence: float, reasoning: str):
        self.condition_func = condition_func
        self.conclusion = conclusion
        self.confidence = confidence
        self.reasoning = reasoning
    
    def evaluate(self, problem_type: str, instance: Dict[str, Any]) -> bool:
        """Evaluează dacă regula se aplică pentru instanța dată"""
        try:
            return self.condition_func(problem_type, instance)
        except:
            return False


class RuleEngine:
    """Expert System cu reguli pentru selectarea strategiei"""
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> List[Rule]:
        """Inițializează setul de reguli pentru toate problemele"""
        rules = []
        
        # ===== N-QUEENS RULES =====
        rules.append(Rule(
            condition_func=lambda p, i: p == "n-queens" and i.get("size", 0) <= 8,
            conclusion="backtracking",
            confidence=0.95,
            reasoning="Pentru n ≤ 8, spațiul de căutare este suficient de mic pentru explorare completă. Backtracking garantează găsirea tuturor soluțiilor în timp rezonabil."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "n-queens" and 8 < i.get("size", 0) <= 15,
            conclusion="backtracking_with_heuristics",
            confidence=0.90,
            reasoning="Pentru 8 < n ≤ 15, backtracking simplu devine lent. Heuristicile (forward checking, MRV) reduc dramatic spațiul de căutare menținând completitudinea."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "n-queens" and 15 < i.get("size", 0) <= 25,
            conclusion="csp_forward_checking",
            confidence=0.85,
            reasoning="Pentru 15 < n ≤ 25, CSP cu forward checking oferă cel mai bun echilibru. Detectarea timpurie a inconsistențelor reduce backtracking-ul exponențial."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "n-queens" and 25 < i.get("size", 0) <= 50,
            conclusion="local_search",
            confidence=0.90,
            reasoning="Pentru 25 < n ≤ 50, metodele complete devin impracticabile. Local search (min-conflicts) găsește soluții în O(n²) cu probabilitate mare de succes."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "n-queens" and i.get("size", 0) > 50,
            conclusion="simulated_annealing",
            confidence=0.95,
            reasoning="Pentru n > 50, simulated annealing evită optimele locale și găsește soluții chiar pentru n = 1000+. Este singura metodă scalabilă la dimensiuni foarte mari."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "n-queens" and i.get("objective") == "find_all",
            conclusion="backtracking_with_heuristics",
            confidence=0.95,
            reasoning="Pentru a găsi TOATE soluțiile, trebuie folosită o metodă completă. Backtracking cu heuristici este cea mai eficientă pentru explorare exhaustivă."
        ))
        
        # ===== HANOI RULES =====
        rules.append(Rule(
            condition_func=lambda p, i: p == "hanoi" and i.get("towers", 3) == 3 and i.get("disks", 0) <= 20,
            conclusion="recursive_divide_conquer",
            confidence=1.0,
            reasoning="Pentru Hanoi clasic (3 turle) cu n ≤ 20, soluția recursivă este optimă matematică (2^n - 1 mutări). Este elegantă, corectă și eficientă pentru aceste dimensiuni."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "hanoi" and i.get("towers", 3) == 3 and i.get("disks", 0) > 20,
            conclusion="iterative",
            confidence=0.95,
            reasoning="Pentru n > 20, recursivitatea poate cauza stack overflow. Varianta iterativă produce aceleași 2^n - 1 mutări optime fără riscul de overflow."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "hanoi" and i.get("towers", 3) > 3 and i.get("disks", 0) <= 15,
            conclusion="frame_stewart_algorithm",
            confidence=0.90,
            reasoning="Pentru k > 3 turle, Frame-Stewart oferă soluția conjecturată optimă. Este mult mai eficient decât să folosim doar 3 turle din k disponibile."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "hanoi" and i.get("towers", 3) > 3 and i.get("disks", 0) > 15,
            conclusion="iterative",
            confidence=0.85,
            reasoning="Pentru combinație (k > 3 turle, n > 15), varianta iterativă este cea mai sigură pentru a evita problema stack-ului în implementările recursive complexe."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "hanoi" and i.get("has_costs", False),
            conclusion="dynamic_programming",
            confidence=0.90,
            reasoning="Când mutările au costuri diferite, problema devine de optimizare. Programarea dinamică găsește soluția cu cost minim prin memorarea subproblemelor."
        ))
        
        # ===== GRAPH COLORING RULES =====
        rules.append(Rule(
            condition_func=lambda p, i: p == "graph_coloring" and i.get("graph_type") == "bipartite",
            conclusion="greedy_basic",
            confidence=1.0,
            reasoning="Grafurile bipartite necesită EXACT 2 culori (dacă sunt conexe). Un algoritm greedy simplu le detectează și colorează optim în O(V+E)."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "graph_coloring" and i.get("graph_type") == "planar",
            conclusion="planar_4color",
            confidence=0.95,
            reasoning="Teorema celor 4 culori garantează că orice graf planar poate fi colorat cu max 4 culori. Algoritmi specifici găsesc această colorare în O(V)."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "graph_coloring" and i.get("vertices", 0) <= 30 and i.get("need_optimal", False),
            conclusion="backtracking_with_bounds",
            confidence=0.90,
            reasoning="Pentru grafuri mici (V ≤ 30) când avem nevoie de numărul cromatic exact, backtracking cu branch & bound este singura metodă care garantează optim."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "graph_coloring" and 30 < i.get("vertices", 0) <= 500,
            conclusion="greedy_dsatur",
            confidence=0.85,
            reasoning="Pentru grafuri medii, DSATUR oferă cele mai bune rezultate practice. Heuristica 'degree of saturation' produce colorări aproape-optime foarte rapid."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "graph_coloring" and i.get("vertices", 0) > 500,
            conclusion="local_search_tabu",
            confidence=0.90,
            reasoning="Pentru grafuri foarte mari (V > 500), doar local search scalează. Tabu search evită ciclarea și găsește soluții bune în timp polinomial."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "graph_coloring" and i.get("density", 0.5) < 0.3,
            conclusion="greedy_dsatur",
            confidence=0.85,
            reasoning="Pentru grafuri sparse (densitate < 0.3), DSATUR profită de numărul mic de muchii și găsește rapid colorări bune."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "graph_coloring" and i.get("density", 0.5) > 0.7,
            conclusion="welsh_powell",
            confidence=0.80,
            reasoning="Pentru grafuri dense, Welsh-Powell (sortare după grad descrescător) performează bine deoarece nodurile de grad înalt sunt colorate prioritar."
        ))
        
        # ===== KNIGHT'S TOUR RULES =====
        rules.append(Rule(
            condition_func=lambda p, i: p == "knights_tour" and i.get("board_size", 0) <= 6,
            conclusion="backtracking_warnsdorff",
            confidence=0.95,
            reasoning="Pentru table mici (n ≤ 6), backtracking cu Warnsdorff garantează găsirea soluției rapid. Warnsdorff ghidează căutarea, backtracking-ul asigură completitudinea."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "knights_tour" and 6 < i.get("board_size", 0) <= 20,
            conclusion="warnsdorff_heuristic",
            confidence=0.95,
            reasoning="Pentru n în [7, 20], heuristica Warnsdorff singură găsește soluție în >99% cazuri în O(n²). Este extrem de rapidă și practic întotdeauna reușește."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "knights_tour" and i.get("board_size", 0) > 20 and i.get("board_size", 0) % 2 == 0,
            conclusion="divide_conquer",
            confidence=0.90,
            reasoning="Pentru table mari pătrate (n > 20, n par), algoritmi divide & conquer construiesc soluția garantat în O(n²) fără căutare."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "knights_tour" and i.get("board_size", 0) > 50,
            conclusion="warnsdorff_heuristic",
            confidence=0.90,
            reasoning="Pentru table foarte mari, Warnsdorff rămâne cel mai eficient - liniar și practic întotdeauna găsește soluție pentru n mare."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "knights_tour" and i.get("tour_type") == "closed" and i.get("board_size", 0) <= 10,
            conclusion="backtracking_warnsdorff",
            confidence=0.90,
            reasoning="Pentru ture închise (Hamiltonian), constrângerea e mai strictă. Backtracking cu Warnsdorff asigură găsirea soluției când există."
        ))
        
        # ===== CROSS-PROBLEM RULES =====
        rules.append(Rule(
            condition_func=lambda p, i: i.get("time_constraint") == "very_strict",
            conclusion="greedy_or_local_search",
            confidence=0.80,
            reasoning="Cu constrângeri de timp foarte stricte, metodele greedy sau local search sunt singurele care garantează răspuns rapid, chiar dacă nu optim."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: i.get("memory_constraint") == "very_limited",
            conclusion="iterative_or_local",
            confidence=0.75,
            reasoning="Cu memorie foarte limitată, trebuie evitate metodele recursive (stack) și cele cu overhead mare (DP). Local search și iterative sunt preferabile."
        ))
        
        return rules
    
    def infer_strategy(self, problem_type: str, instance: Dict[str, Any]) -> Tuple[str, str, float]:
        """
        Inferă strategia optimă folosind forward chaining
        
        Returns:
            (strategy_name, reasoning, confidence)
        """
        applicable_rules = []
        
        # Find all applicable rules
        for rule in self.rules:
            if rule.evaluate(problem_type, instance):
                applicable_rules.append(rule)
        
        if not applicable_rules:
            # Default fallback
            return (
                "backtracking",
                "Nicio regulă specifică nu s-a aplicat. Backtracking este strategia generală sigură pentru majoritatea problemelor de căutare.",
                0.50
            )
        
        # Conflict resolution: select rule with highest confidence
        best_rule = max(applicable_rules, key=lambda r: r.confidence)
        
        return (best_rule.conclusion, best_rule.reasoning, best_rule.confidence)
    
    def get_all_applicable_rules(self, problem_type: str, instance: Dict[str, Any]) -> List[Tuple[str, str, float]]:
        """Returnează toate regulile aplicabile (pentru analiză comparativă)"""
        applicable = []
        
        for rule in self.rules:
            if rule.evaluate(problem_type, instance):
                applicable.append((rule.conclusion, rule.reasoning, rule.confidence))
        
        return applicable
    
    def explain_decision(self, problem_type: str, instance: Dict[str, Any]) -> str:
        """Generează o explicație detaliată a deciziei"""
        strategy, reasoning, confidence = self.infer_strategy(problem_type, instance)
        
        explanation = f"=== DECIZIE EXPERT SYSTEM ===\n\n"
        explanation += f"Problema: {problem_type}\n"
        explanation += f"Parametri instanță: {instance}\n\n"
        explanation += f"Strategie recomandată: {strategy}\n"
        explanation += f"Nivel de încredere: {confidence * 100:.1f}%\n\n"
        explanation += f"Justificare:\n{reasoning}\n\n"
        
        # Show alternative strategies if any
        all_applicable = self.get_all_applicable_rules(problem_type, instance)
        if len(all_applicable) > 1:
            explanation += "Alternative considerate:\n"
            for alt_strategy, alt_reasoning, alt_conf in all_applicable:
                if alt_strategy != strategy:
                    explanation += f"\n- {alt_strategy} (confidence: {alt_conf * 100:.1f}%)\n"
                    explanation += f"  {alt_reasoning[:100]}...\n"
        
        return explanation


def parse_condition_string(condition_str: str, problem_type: str, instance: Dict[str, Any]) -> bool:
    """
    Helper pentru a evalua condiții din string (pentru reguli din knowledge base)
    
    Exemple:
        "n <= 8" -> evaluat cu instance["size"]
        "towers == 3" -> evaluat cu instance["towers"]
    """
    # Replace variable names with actual values
    condition = condition_str
    
    # Map common variable names
    var_mapping = {
        'n': instance.get('size', instance.get('n', 0)),
        'size': instance.get('size', 0),
        'towers': instance.get('towers', 3),
        'disks': instance.get('disks', 0),
        'vertices': instance.get('vertices', 0),
        'board_size': instance.get('board_size', 0),
        'density': instance.get('density', 0.5),
        'graph_type': f'"{instance.get("graph_type", "")}"',
        'tour_type': f'"{instance.get("tour_type", "")}"',
        'has_costs': instance.get('has_costs', False),
        'has_constraints': instance.get('has_constraints', False),
        'need_optimal': instance.get('need_optimal', False)
    }
    
    # Replace variables in condition
    for var, value in var_mapping.items():
        condition = re.sub(rf'\b{var}\b', str(value), condition)
    
    try:
        # Safe evaluation
        return eval(condition, {"__builtins__": {}}, {})
    except:
        return False


if __name__ == "__main__":
    # Test the rule engine
    engine = RuleEngine()
    
    # Test cases
    test_cases = [
        ("n-queens", {"size": 8}),
        ("n-queens", {"size": 30}),
        ("hanoi", {"towers": 3, "disks": 10}),
        ("hanoi", {"towers": 4, "disks": 12}),
        ("graph_coloring", {"vertices": 20, "graph_type": "planar"}),
        ("graph_coloring", {"vertices": 1000, "density": 0.3}),
        ("knights_tour", {"board_size": 8}),
        ("knights_tour", {"board_size": 100}),
    ]
    
    print("=== TESTING RULE ENGINE ===\n")
    
    for problem, instance in test_cases:
        print(f"\n{'='*60}")
        print(engine.explain_decision(problem, instance))
