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
        # Domeniu: n ∈ [4, 25]
        rules.append(Rule(
            condition_func=lambda p, i: p == "n-queens" and i.get("size", 0) <= 10,
            conclusion="backtracking",
            confidence=0.95,
            reasoning="Pentru n ≤ 10, spațiul de căutare este suficient de mic pentru explorare completă. Backtracking garantează găsirea tuturor soluțiilor în timp rezonabil."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "n-queens" and 10 < i.get("size", 0) <= 18,
            conclusion="backtracking_with_heuristics",
            confidence=0.90,
            reasoning="Pentru 10 < n ≤ 18, backtracking simplu devine lent. Heuristicile (forward checking, MRV) reduc dramatic spațiul de căutare menținând completitudinea."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "n-queens" and i.get("size", 0) > 18,
            conclusion="csp_forward_checking",
            confidence=0.85,
            reasoning="Pentru n > 18, CSP cu forward checking oferă cel mai bun echilibru. Detectarea timpurie a inconsistențelor reduce backtracking-ul exponențial."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "n-queens" and i.get("objective") == "find_all" and i.get("size", 0) <= 12,
            conclusion="backtracking",
            confidence=0.95,
            reasoning="Pentru a găsi TOATE soluțiile cu n ≤ 12, backtracking simplu este suficient de rapid pentru explorare exhaustivă completă."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "n-queens" and i.get("objective") == "find_all" and i.get("size", 0) > 12,
            conclusion="backtracking_with_heuristics",
            confidence=0.95,
            reasoning="Pentru a găsi TOATE soluțiile cu n > 12, trebuie folosită o metodă completă cu heuristici pentru eficiență."
        ))
        
        # ===== HANOI RULES =====
        # Domeniu: n ∈ [1, 22] cu 3 tije
        rules.append(Rule(
            condition_func=lambda p, i: p == "hanoi" and i.get("towers", 3) == 3 and i.get("disks", 0) <= 15,
            conclusion="recursive_divide_conquer",
            confidence=1.0,
            reasoning="Pentru Hanoi clasic (3 turle) cu n ≤ 15, soluția recursivă este optimă matematică (2^n - 1 mutări). Este elegantă, corectă și eficientă pentru aceste dimensiuni."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "hanoi" and i.get("towers", 3) == 3 and i.get("disks", 0) > 15,
            conclusion="iterative",
            confidence=0.95,
            reasoning="Pentru n > 15, recursivitatea poate cauza probleme de performanță. Varianta iterativă produce aceleași 2^n - 1 mutări optime mai eficient."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "hanoi" and i.get("has_costs", False),
            conclusion="dynamic_programming",
            confidence=0.90,
            reasoning="Când mutările au costuri diferite, problema devine de optimizare. Programarea dinamică găsește soluția cu cost minim prin memorarea subproblemelor."
        ))
        
        # ===== GRAPH COLORING RULES =====
        # Domeniu: n ∈ [5, 50]
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
            condition_func=lambda p, i: p == "graph_coloring" and i.get("vertices", 0) <= 20 and i.get("need_optimal", False),
            conclusion="backtracking_with_bounds",
            confidence=0.90,
            reasoning="Pentru grafuri mici (V ≤ 20) când avem nevoie de numărul cromatic exact, backtracking cu branch & bound este singura metodă care garantează optim."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "graph_coloring" and 20 < i.get("vertices", 0) <= 35,
            conclusion="greedy_dsatur",
            confidence=0.85,
            reasoning="Pentru grafuri medii, DSATUR oferă cele mai bune rezultate practice. Heuristica 'degree of saturation' produce colorări aproape-optime foarte rapid."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "graph_coloring" and i.get("vertices", 0) > 35,
            conclusion="welsh_powell",
            confidence=0.90,
            reasoning="Pentru grafuri mari (V > 35), Welsh-Powell (sortare după grad descrescător) este eficient și produce colorări bune în timp liniar."
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
        # Domeniu: n ∈ [5, 12] pentru backtracking exact
        rules.append(Rule(
            condition_func=lambda p, i: p == "knights_tour" and i.get("board_size", 0) <= 7,
            conclusion="backtracking_warnsdorff",
            confidence=0.95,
            reasoning="Pentru table mici (n ≤ 7), backtracking cu Warnsdorff garantează găsirea soluției rapid. Warnsdorff ghidează căutarea, backtracking-ul asigură completitudinea."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "knights_tour" and i.get("board_size", 0) > 7,
            conclusion="warnsdorff_heuristic",
            confidence=0.95,
            reasoning="Pentru n în [8, 12], heuristica Warnsdorff singură găsește soluție în >99% cazuri în O(n²). Este extrem de rapidă și practic întotdeauna reușește."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "knights_tour" and i.get("tour_type") == "closed",
            conclusion="backtracking_warnsdorff",
            confidence=0.90,
            reasoning="Pentru ture închise (Hamiltonian), constrângerea e mai strictă. Backtracking cu Warnsdorff asigură găsirea soluției când există."
        ))
        
        # ===== GAME THEORY RULES =====
        rules.append(Rule(
            condition_func=lambda p, i: p == "game_theory" and i.get("has_dominant_strategy", False),
            conclusion="dominance_elimination",
            confidence=0.95,
            reasoning="Când există strategii dominante, eliminarea iterativă (IESDS) simplifică dramatic analiza. Strategiile dominate nu vor fi jucate de agenți raționali."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "game_theory" and i.get("strategies_per_player", 2) <= 2 and not i.get("has_dominant_strategy", False),
            conclusion="pure_strategy_enumeration",
            confidence=0.95,
            reasoning="Pentru jocuri 2x2 fără strategii dominate, enumerarea directă a celor 4 profiluri de strategie este cea mai rapidă și clară metodă."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "game_theory" and i.get("strategies_per_player", 2) == 3 and not i.get("has_dominant_strategy", False),
            conclusion="best_response_analysis",
            confidence=0.90,
            reasoning="Pentru jocuri 3x3, analiza best response este sistematică și eficientă. Marcăm răspunsurile optime și identificăm celulele cu ambele marcate."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "game_theory" and i.get("has_pure_nash", False) == False,
            conclusion="mixed_strategy_calculation",
            confidence=0.95,
            reasoning="Când nu există echilibru Nash pur (precum în Matching Pennies), trebuie calculat echilibrul în strategii mixte folosind principiul indiferenței."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "game_theory" and i.get("game_type") == "zero_sum",
            conclusion="best_response_analysis",
            confidence=0.90,
            reasoning="În jocurile cu sumă zero, echilibrul Nash corespunde soluției minimax. Analiza best response identifică rapid strategiile optime."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "game_theory" and i.get("game_type") in ["coordination_game", "battle_of_sexes", "stag_hunt"],
            conclusion="pure_strategy_enumeration",
            confidence=0.90,
            reasoning="Jocurile de coordonare au de obicei echilibre Nash pure multiple. Enumerarea le identifică pe toate și permite analiza eficienței Pareto."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "game_theory" and i.get("strategies_per_player", 2) >= 4,
            conclusion="dominance_elimination",
            confidence=0.85,
            reasoning="Pentru jocuri mari (4+ strategii), prima etapă este eliminarea strategiilor dominate pentru a reduce dimensiunea problemei înainte de analiza detaliată."
        ))
        
        rules.append(Rule(
            condition_func=lambda p, i: p == "game_theory" and i.get("game_type") == "prisoners_dilemma",
            conclusion="dominance_elimination",
            confidence=0.95,
            reasoning="Dilema Prizonierului are strategie dominantă (Defect). Eliminarea strategiilor dominate conduce direct la echilibrul Nash unic."
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
