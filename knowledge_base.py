"""
Knowledge Base pentru probleme clasice de AI
Conține definițiile problemelor, strategii de rezolvare și criterii de decizie
"""

KNOWLEDGE_BASE = {
    "n-queens": {
        "name": "N-Queens",
        "description": "Plasarea a n regine pe o tablă de șah n×n astfel încât nicio regină să nu se atace reciproc",
        "complexity_class": "NP-Complete",
        
        "strategies": {
            "backtracking": {
                "name": "Backtracking",
                "time_complexity": "O(n!)",
                "space_complexity": "O(n)",
                "best_for": "instanțe mici (n ≤ 15)",
                "advantages": [
                    "găsește toate soluțiile posibile",
                    "garantează găsirea soluției optime",
                    "simplu de implementat și înțeles"
                ],
                "disadvantages": [
                    "exponențial în timp pentru n mare",
                    "ineficient pentru n > 20"
                ],
                "when_to_use": "când n ≤ 15 sau când avem nevoie de toate soluțiile"
            },
            
            "backtracking_with_heuristics": {
                "name": "Backtracking cu Heuristici",
                "time_complexity": "O(n!) dar mult mai rapid în practică",
                "space_complexity": "O(n)",
                "best_for": "instanțe medii (8 ≤ n ≤ 20)",
                "advantages": [
                    "forward checking reduce spațiul de căutare",
                    "most constrained variable heuristic",
                    "pruning agresiv"
                ],
                "disadvantages": [
                    "tot exponențial worst-case",
                    "mai complex de implementat"
                ],
                "when_to_use": "când 8 < n ≤ 20 și vrem soluție optimă"
            },
            
            "csp_forward_checking": {
                "name": "CSP cu Forward Checking",
                "time_complexity": "O(d^n) cu pruning semnificativ",
                "space_complexity": "O(n·d)",
                "best_for": "instanțe medii (10 ≤ n ≤ 25)",
                "advantages": [
                    "detectează eșecuri devreme",
                    "reduce dramatic numărul de backtrack-uri",
                    "poate fi combinat cu arc consistency"
                ],
                "disadvantages": [
                    "overhead de memorie pentru domenii",
                    "mai complex decât backtracking simplu"
                ],
                "when_to_use": "când 10 ≤ n ≤ 25 și vrem eficiență bună"
            },
            
            "local_search": {
                "name": "Local Search (Hill Climbing, Min-Conflicts)",
                "time_complexity": "O(n²) per iterație",
                "space_complexity": "O(n)",
                "best_for": "instanțe mari (n > 20)",
                "advantages": [
                    "foarte rapid pentru n mare",
                    "scalabil la n = 1000+",
                    "simplu de implementat"
                ],
                "disadvantages": [
                    "nu garantează soluția optimă",
                    "poate rămâne blocat în optim local",
                    "necesită restart random"
                ],
                "when_to_use": "când n > 20 și acceptăm soluții aproximative rapide"
            },
            
            "simulated_annealing": {
                "name": "Simulated Annealing",
                "time_complexity": "O(n²·k) unde k = nr iterații",
                "space_complexity": "O(n)",
                "best_for": "instanțe foarte mari (n > 50)",
                "advantages": [
                    "evită optimele locale",
                    "găsește soluții bune pentru n foarte mare",
                    "probabilistic complete"
                ],
                "disadvantages": [
                    "necesită tuning parametri (temperatură, cooling)",
                    "mai lent decât hill climbing simplu",
                    "nu garantează optimalitate"
                ],
                "when_to_use": "când n > 50 și hill climbing eșuează frecvent"
            }
        },
        
        "instance_parameters": {
            "size": [4, 6, 8, 10, 12, 15, 20, 30, 50, 100, 200],
            "constraints": ["standard", "forbidden_positions", "required_positions"],
            "objectives": ["find_one", "find_all", "count_solutions"]
        },
        
        "decision_rules": [
            {"condition": "n <= 8", "strategy": "backtracking", "confidence": 0.95},
            {"condition": "8 < n <= 15", "strategy": "backtracking_with_heuristics", "confidence": 0.90},
            {"condition": "15 < n <= 25", "strategy": "csp_forward_checking", "confidence": 0.85},
            {"condition": "25 < n <= 50", "strategy": "local_search", "confidence": 0.90},
            {"condition": "n > 50", "strategy": "simulated_annealing", "confidence": 0.95}
        ]
    },
    
    "hanoi": {
        "name": "Turnurile din Hanoi (Generalizat)",
        "description": "Mutarea a n discuri între k turle respectând regula că un disc mai mare nu poate fi pus peste unul mai mic",
        "complexity_class": "Exponențial",
        
        "strategies": {
            "recursive_divide_conquer": {
                "name": "Recursiv (Divide & Conquer)",
                "time_complexity": "O(2^n - 1) pentru 3 turle",
                "space_complexity": "O(n) - stack recursiv",
                "best_for": "Hanoi clasic (3 turle, n ≤ 20)",
                "advantages": [
                    "soluție optimă garantată",
                    "elegant și ușor de înțeles",
                    "număr minim de mutări: 2^n - 1"
                ],
                "disadvantages": [
                    "exponențial - impracticabil pentru n > 30",
                    "doar pentru 3 turle (clasic)"
                ],
                "when_to_use": "pentru Hanoi clasic (3 turle) cu n ≤ 20"
            },
            
            "frame_stewart_algorithm": {
                "name": "Frame-Stewart (pentru k turle)",
                "time_complexity": "O(2^n) dar mai eficient decât clasic",
                "space_complexity": "O(n·k)",
                "best_for": "Hanoi generalizat (k > 3 turle)",
                "advantages": [
                    "funcționează pentru k turle",
                    "soluție optimă conjecturată (nu dovedită)",
                    "foarte eficient pentru k = 4, 5"
                ],
                "disadvantages": [
                    "mai complex de implementat",
                    "optimalitatea nu e dovedită matematic pentru k > 3"
                ],
                "when_to_use": "când avem k > 3 turle și n ≤ 15"
            },
            
            "iterative": {
                "name": "Iterativ (folosind stiva)",
                "time_complexity": "O(2^n - 1)",
                "space_complexity": "O(n)",
                "best_for": "evitare overflow stack (n > 20)",
                "advantages": [
                    "evită stack overflow pentru n mare",
                    "mai eficient la memorie",
                    "același număr de mutări ca recursiv"
                ],
                "disadvantages": [
                    "cod mai verbos",
                    "mai greu de înțeles decât recursiv"
                ],
                "when_to_use": "când n > 20 și avem limitări de stack"
            },
            
            "dynamic_programming": {
                "name": "Programare Dinamică (pentru variante cu costuri)",
                "time_complexity": "O(n²·k²)",
                "space_complexity": "O(n·k)",
                "best_for": "variante cu costuri diferite ale mutărilor",
                "advantages": [
                    "optimal pentru probleme cu costuri",
                    "poate optimiza criterii multiple",
                    "memorare subprobleme"
                ],
                "disadvantages": [
                    "overhead mare de memorie",
                    "overkill pentru Hanoi clasic"
                ],
                "when_to_use": "când mutările au costuri diferite sau constrângeri speciale"
            }
        },
        
        "instance_parameters": {
            "towers": [3, 4, 5],
            "disks": [3, 5, 8, 10, 15, 20, 30, 40],
            "constraints": ["standard", "limited_moves", "weighted_disks"]
        },
        
        "decision_rules": [
            {"condition": "towers == 3 and disks <= 20", "strategy": "recursive_divide_conquer", "confidence": 1.0},
            {"condition": "towers == 3 and disks > 20", "strategy": "iterative", "confidence": 0.95},
            {"condition": "towers > 3 and disks <= 15", "strategy": "frame_stewart_algorithm", "confidence": 0.90},
            {"condition": "towers > 3 and disks > 15", "strategy": "iterative", "confidence": 0.85},
            {"condition": "has_costs or has_constraints", "strategy": "dynamic_programming", "confidence": 0.90}
        ]
    },
    
    "graph_coloring": {
        "name": "Colorarea Grafurilor",
        "description": "Atribuirea de culori nodurilor unui graf astfel încât noduri adiacente să aibă culori diferite, minimizând numărul total de culori",
        "complexity_class": "NP-Complete",
        
        "strategies": {
            "greedy_basic": {
                "name": "Greedy (ordonare simplă)",
                "time_complexity": "O(V + E)",
                "space_complexity": "O(V)",
                "best_for": "grafuri mici, aproximare rapidă",
                "advantages": [
                    "extrem de rapid",
                    "simplu de implementat",
                    "garantează soluție validă (nu neapărat optimă)"
                ],
                "disadvantages": [
                    "nu garantează număr minim de culori",
                    "calitate dependentă de ordonare"
                ],
                "when_to_use": "când viteza e mai importantă decât optimalitatea"
            },
            
            "greedy_dsatur": {
                "name": "DSATUR (Degree of Saturation)",
                "time_complexity": "O(V²)",
                "space_complexity": "O(V)",
                "best_for": "majoritatea grafurilor practice",
                "advantages": [
                    "heuristică foarte bună în practică",
                    "aproape optim pentru multe grafuri",
                    "rapid și ușor de implementat"
                ],
                "disadvantages": [
                    "tot greedy - nu garantează optim",
                    "mai lent decât greedy basic"
                ],
                "when_to_use": "pentru majoritatea grafurilor (10-1000 noduri)"
            },
            
            "backtracking_with_bounds": {
                "name": "Backtracking cu Branch & Bound",
                "time_complexity": "O(k^V) worst case, mult mai bun în practică",
                "space_complexity": "O(V)",
                "best_for": "grafuri mici când vrem soluție optimă (V ≤ 30)",
                "advantages": [
                    "găsește numărul cromatic exact",
                    "poate dovedi optimalitatea",
                    "pruning reduce dramatic spațiul"
                ],
                "disadvantages": [
                    "exponențial pentru grafuri mari",
                    "poate dura foarte mult pentru V > 50"
                ],
                "when_to_use": "când V ≤ 30 și avem nevoie de soluție optimă garantată"
            },
            
            "welsh_powell": {
                "name": "Welsh-Powell",
                "time_complexity": "O(V·log(V) + E)",
                "space_complexity": "O(V)",
                "best_for": "grafuri cu distribuție neuniformă a gradelor",
                "advantages": [
                    "foarte bun pentru grafuri cu noduri de grad înalt",
                    "rapid și eficient",
                    "rezultate bune pentru grafuri practice"
                ],
                "disadvantages": [
                    "tot aproximativ",
                    "necesită sortare inițială"
                ],
                "when_to_use": "când graful are noduri cu grade foarte diferite"
            },
            
            "planar_4color": {
                "name": "Algoritm specific pentru grafuri planare (4-Color)",
                "time_complexity": "O(V)",
                "space_complexity": "O(V)",
                "best_for": "grafuri planare",
                "advantages": [
                    "garantează maxim 4 culori",
                    "liniar în timp",
                    "optimal pentru grafuri planare"
                ],
                "disadvantages": [
                    "funcționează doar pentru grafuri planare",
                    "verificarea planarității costă O(V)"
                ],
                "when_to_use": "când știm că graful este planar"
            },
            
            "local_search_tabu": {
                "name": "Local Search cu Tabu Search",
                "time_complexity": "O(V²·k) per iterație",
                "space_complexity": "O(V + tabu_size)",
                "best_for": "grafuri foarte mari (V > 1000)",
                "advantages": [
                    "scalabil la grafuri enorme",
                    "evită ciclare prin tabu list",
                    "găsește soluții bune pentru instanțe mari"
                ],
                "disadvantages": [
                    "nu garantează optim",
                    "necesită tuning parametri",
                    "mai complex de implementat"
                ],
                "when_to_use": "când V > 1000 și metodele exacte sunt prea lente"
            }
        },
        
        "instance_parameters": {
            "vertices": [5, 10, 20, 30, 50, 100, 500, 1000],
            "graph_types": ["random", "planar", "bipartite", "complete", "sparse", "dense"],
            "density": [0.1, 0.3, 0.5, 0.7, 0.9]
        },
        
        "decision_rules": [
            {"condition": "graph_type == 'bipartite'", "strategy": "greedy_basic", "confidence": 1.0},
            {"condition": "graph_type == 'planar'", "strategy": "planar_4color", "confidence": 0.95},
            {"condition": "vertices <= 30 and need_optimal", "strategy": "backtracking_with_bounds", "confidence": 0.90},
            {"condition": "30 < vertices <= 500", "strategy": "greedy_dsatur", "confidence": 0.85},
            {"condition": "vertices > 500", "strategy": "local_search_tabu", "confidence": 0.90},
            {"condition": "density < 0.3", "strategy": "greedy_dsatur", "confidence": 0.85},
            {"condition": "density > 0.7", "strategy": "welsh_powell", "confidence": 0.80}
        ]
    },
    
    "knights_tour": {
        "name": "Tura Calului (Knight's Tour)",
        "description": "Găsirea unei secvențe de mutări ale calului pe o tablă de șah astfel încât să viziteze fiecare pătrățel exact o dată",
        "complexity_class": "NP-Complete (decizie), dar soluții polinomiale există pentru tablouri mari",
        
        "strategies": {
            "backtracking_naive": {
                "name": "Backtracking Naiv",
                "time_complexity": "O(8^(n²)) worst case",
                "space_complexity": "O(n²)",
                "best_for": "table foarte mici (n ≤ 6)",
                "advantages": [
                    "simplu de implementat",
                    "garantează găsirea soluției",
                    "găsește toate soluțiile"
                ],
                "disadvantages": [
                    "exponențial - impracticabil pentru n > 6",
                    "foarte lent chiar pentru n = 8"
                ],
                "when_to_use": "doar pentru table foarte mici sau scop didactic"
            },
            
            "warnsdorff_heuristic": {
                "name": "Heuristica Warnsdorff",
                "time_complexity": "O(n²)",
                "space_complexity": "O(n²)",
                "best_for": "table standard și mari (6 ≤ n ≤ 100)",
                "advantages": [
                    "liniar în practică!",
                    "găsește soluție în 99%+ cazuri pentru n ≥ 6",
                    "extrem de rapid",
                    "elegant și simplu"
                ],
                "disadvantages": [
                    "nu garantează 100% succes (mai ales n = 5)",
                    "poate necesita backtracking minimal"
                ],
                "when_to_use": "pentru majoritatea cazurilor practice (n ≥ 6)"
            },
            
            "backtracking_warnsdorff": {
                "name": "Backtracking cu Warnsdorff",
                "time_complexity": "O(n²) în practică cu Warnsdorff",
                "space_complexity": "O(n²)",
                "best_for": "garantare soluție pentru n = 5-12",
                "advantages": [
                    "combină viteza Warnsdorff cu completitudinea backtracking",
                    "garantează soluție",
                    "foarte rapid în practică"
                ],
                "disadvantages": [
                    "mai complex de implementat",
                    "overhead de backtracking când Warnsdorff eșuează"
                ],
                "when_to_use": "când avem nevoie de garanție 100% pentru n ≤ 12"
            },
            
            "divide_conquer": {
                "name": "Divide & Conquer (pentru table mari pătrate)",
                "time_complexity": "O(n²)",
                "space_complexity": "O(n²)",
                "best_for": "table foarte mari (n > 50) și pătrate",
                "advantages": [
                    "garantat pentru n par ≥ 6",
                    "constructiv - nu necesită căutare",
                    "foarte rapid pentru orice n"
                ],
                "disadvantages": [
                    "funcționează doar pentru anumite dimensiuni",
                    "necesită tablă pătrată",
                    "implementare mai complexă"
                ],
                "when_to_use": "pentru n foarte mare (> 50) și pătrată"
            },
            
            "neural_network_approach": {
                "name": "Abordare Neural Network (Takefuji-Lee)",
                "time_complexity": "O(n²·iterations)",
                "space_complexity": "O(n²)",
                "best_for": "cercetare, table foarte mari",
                "advantages": [
                    "paralelizabil",
                    "scalabil la dimensiuni mari",
                    "interesting approach"
                ],
                "disadvantages": [
                    "nu garantează soluție",
                    "overkill pentru problema simplă",
                    "necesită biblioteca de NN"
                ],
                "when_to_use": "raramente în practică - mai mult academic"
            }
        },
        
        "instance_parameters": {
            "board_size": [5, 6, 8, 10, 12, 16, 20, 50, 100],
            "start_position": ["corner", "edge", "center", "random"],
            "tour_type": ["open", "closed"],
            "board_shape": ["square", "rectangular"]
        },
        
        "decision_rules": [
            {"condition": "board_size <= 6", "strategy": "backtracking_warnsdorff", "confidence": 0.95},
            {"condition": "6 < board_size <= 20", "strategy": "warnsdorff_heuristic", "confidence": 0.95},
            {"condition": "board_size > 20 and board_size % 2 == 0", "strategy": "divide_conquer", "confidence": 0.90},
            {"condition": "board_size > 50", "strategy": "warnsdorff_heuristic", "confidence": 0.90},
            {"condition": "tour_type == 'closed' and board_size <= 10", "strategy": "backtracking_warnsdorff", "confidence": 0.90}
        ]
    }
}


# Templates pentru generarea întrebărilor
QUESTION_TEMPLATES = {
    "standard": [
        "Pentru problema {problem_name} cu {instance_description}, care este strategia de rezolvare cea mai potrivită? Justificați alegerea.",
        "Considerați problema {problem_name} pentru instanța: {instance_description}. Alegeți între strategiile disponibile și explicați de ce este alegerea dvs. optimă.",
        "Analizați problema {problem_name} având parametrii: {instance_description}. Ce metodă de rezolvare recomandați și din ce motive?"
    ],
    
    "comparative": [
        "Pentru {problem_name} cu {instance_description}, comparați eficiența următoarelor strategii: {strategy_list}. Care este alegerea optimă?",
        "În contextul problemei {problem_name} (instanța: {instance_description}), evaluați avantajele și dezavantajele folosirii {strategy_a} versus {strategy_b}.",
        "Problema {problem_name} cu {instance_description} poate fi rezolvată prin {strategy_list}. Clasificați aceste strategii în ordinea eficienței și justificați."
    ],
    
    "scenario": [
        "Într-un sistem de timp real, trebuie să rezolvați {problem_name} pentru {instance_description} în maximum {time_limit}. Ce strategie alegeți?",
        "Aveți la dispoziție {memory_limit} memorie pentru a rezolva {problem_name} cu {instance_description}. Argumentați alegerea strategiei potrivite.",
        "Pentru un examen cu timp limitat, vi se cere să rezolvați {problem_name} ({instance_description}) cât mai rapid posibil. Ce abordare alegeți și de ce?"
    ],
    
    "theoretical": [
        "Din punct de vedere al complexității computaționale, care este cea mai eficientă strategie pentru {problem_name} când {instance_description}? Demonstrați cu analiza Big-O.",
        "Pentru {problem_name} cu {instance_description}, analizați trade-off-ul timp-spațiu pentru principalele strategii de rezolvare.",
        "Explicați de ce {strategy_name} este (sau nu este) alegerea optimă pentru {problem_name} având {instance_description}."
    ]
}


# Justificări template pentru răspunsuri
REASONING_TEMPLATES = {
    "size_based": "Pentru dimensiunea {size}, strategia {strategy} este optimă deoarece {reason}. Complexitatea {complexity} este acceptabilă în acest caz.",
    
    "comparison": "{strategy_chosen} este superioară față de {alternative_strategy} în acest caz pentru că: {reason}. Deși {alternative_strategy} are avantajul că {alternative_advantage}, {strategy_chosen} este mai potrivită datorită {chosen_advantage}.",
    
    "constraint_based": "Având în vedere constrângerile {constraints}, {strategy} este singura alegere viabilă deoarece {reason}.",
    
    "theoretical": "Din punct de vedere teoretic, {strategy} oferă complexitatea optimă {complexity} pentru acest tip de instanță. {additional_reasoning}"
}
