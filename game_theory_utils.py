"""
Game Theory Utilities for SmarTest
Provides functions for Nash equilibrium computation and game generation
NO AI/LLM - purely algorithmic implementations
"""

import random
from typing import Dict, List, Tuple, Any, Optional


# =============================================================================
# CLASSIC GAMES - Predefined games with known properties
# =============================================================================

CLASSIC_GAMES = {
    "prisoners_dilemma": {
        "name": "Dilema Prizonierului",
        "name_en": "Prisoner's Dilemma",
        "matrix": [
            [(-1, -1), (-3, 0)],
            [(0, -3), (-2, -2)]
        ],
        "row_strategies": ["Cooperate", "Defect"],
        "col_strategies": ["Cooperate", "Defect"],
        "has_pure_nash": True,
        "pure_nash": [(1, 1)],  # (Defect, Defect)
        "has_dominant_strategy": True,
        "dominant_strategies": {"row": 1, "col": 1},  # Defect is dominant for both
        "description": "Joc clasic cu dilemă socială - echilibrul Nash nu e optim Pareto"
    },
    
    "battle_of_sexes": {
        "name": "Bătălia Sexelor",
        "name_en": "Battle of the Sexes",
        "matrix": [
            [(3, 2), (0, 0)],
            [(0, 0), (2, 3)]
        ],
        "row_strategies": ["Opera", "Football"],
        "col_strategies": ["Opera", "Football"],
        "has_pure_nash": True,
        "pure_nash": [(0, 0), (1, 1)],  # (Opera, Opera) and (Football, Football)
        "has_dominant_strategy": False,
        "dominant_strategies": {},
        "description": "Joc de coordonare cu două echilibre Nash pure"
    },
    
    "coordination_game": {
        "name": "Joc de Coordonare",
        "name_en": "Coordination Game",
        "matrix": [
            [(2, 2), (0, 0)],
            [(0, 0), (1, 1)]
        ],
        "row_strategies": ["A", "B"],
        "col_strategies": ["A", "B"],
        "has_pure_nash": True,
        "pure_nash": [(0, 0), (1, 1)],  # Both (A,A) and (B,B)
        "has_dominant_strategy": False,
        "dominant_strategies": {},
        "description": "Joc de coordonare simplu cu echilibre Pareto-rankable"
    },
    
    "chicken": {
        "name": "Jocul Fricosului (Chicken)",
        "name_en": "Chicken / Hawk-Dove",
        "matrix": [
            [(0, 0), (-1, 1)],
            [(1, -1), (-5, -5)]
        ],
        "row_strategies": ["Swerve", "Straight"],
        "col_strategies": ["Swerve", "Straight"],
        "has_pure_nash": True,
        "pure_nash": [(0, 1), (1, 0)],  # Asymmetric equilibria
        "has_dominant_strategy": False,
        "dominant_strategies": {},
        "description": "Joc anti-coordonare cu echilibre asimetrice"
    },
    
    "matching_pennies": {
        "name": "Potrivirea Monedelor",
        "name_en": "Matching Pennies",
        "matrix": [
            [(1, -1), (-1, 1)],
            [(-1, 1), (1, -1)]
        ],
        "row_strategies": ["Heads", "Tails"],
        "col_strategies": ["Heads", "Tails"],
        "has_pure_nash": False,
        "pure_nash": [],
        "has_dominant_strategy": False,
        "dominant_strategies": {},
        "description": "Joc cu sumă zero fără echilibru Nash pur"
    },
    
    "stag_hunt": {
        "name": "Vânătoarea de Cerbi",
        "name_en": "Stag Hunt",
        "matrix": [
            [(4, 4), (0, 3)],
            [(3, 0), (2, 2)]
        ],
        "row_strategies": ["Stag", "Hare"],
        "col_strategies": ["Stag", "Hare"],
        "has_pure_nash": True,
        "pure_nash": [(0, 0), (1, 1)],  # (Stag, Stag) and (Hare, Hare)
        "has_dominant_strategy": False,
        "dominant_strategies": {},
        "description": "Joc de coordonare cu risc - echilibre Pareto-rankable"
    },
    
    "pure_coordination": {
        "name": "Coordonare Pură",
        "name_en": "Pure Coordination",
        "matrix": [
            [(1, 1), (0, 0)],
            [(0, 0), (1, 1)]
        ],
        "row_strategies": ["Left", "Right"],
        "col_strategies": ["Left", "Right"],
        "has_pure_nash": True,
        "pure_nash": [(0, 0), (1, 1)],
        "has_dominant_strategy": False,
        "dominant_strategies": {},
        "description": "Coordonare pură simetrică"
    },
    
    "dominant_strategy_game": {
        "name": "Joc cu Strategie Dominantă",
        "name_en": "Dominant Strategy Game",
        "matrix": [
            [(4, 3), (2, 1)],
            [(3, 4), (1, 2)]
        ],
        "row_strategies": ["Up", "Down"],
        "col_strategies": ["Left", "Right"],
        "has_pure_nash": True,
        "pure_nash": [(0, 0)],  # (Up, Left)
        "has_dominant_strategy": True,
        "dominant_strategies": {"row": 0, "col": 0},  # Up dominates Down, Left dominates Right
        "description": "Joc simplu cu strategii dominante pentru ambii jucători"
    }
}


# =============================================================================
# NASH EQUILIBRIUM COMPUTATION FUNCTIONS
# =============================================================================

def find_pure_nash_equilibria(matrix: List[List[Tuple[int, int]]]) -> List[Tuple[int, int]]:
    """
    Find all pure Nash equilibria in a 2-player normal form game.
    
    Args:
        matrix: Payoff matrix where matrix[i][j] = (row_payoff, col_payoff)
    
    Returns:
        List of (row, col) tuples representing pure Nash equilibria
    """
    if not matrix or not matrix[0]:
        return []
    
    num_rows = len(matrix)
    num_cols = len(matrix[0])
    
    equilibria = []
    
    for i in range(num_rows):
        for j in range(num_cols):
            # Check if (i, j) is a Nash equilibrium
            row_payoff, col_payoff = matrix[i][j]
            
            # Check if row player has no profitable deviation
            row_is_best = True
            for other_i in range(num_rows):
                if matrix[other_i][j][0] > row_payoff:
                    row_is_best = False
                    break
            
            # Check if column player has no profitable deviation
            col_is_best = True
            for other_j in range(num_cols):
                if matrix[i][other_j][1] > col_payoff:
                    col_is_best = False
                    break
            
            if row_is_best and col_is_best:
                equilibria.append((i, j))
    
    return equilibria


def find_best_responses_row(matrix: List[List[Tuple[int, int]]], col: int) -> List[int]:
    """
    Find all best responses for the row player given column player's strategy.
    
    Args:
        matrix: Payoff matrix
        col: Column player's strategy index
    
    Returns:
        List of row indices that are best responses
    """
    max_payoff = max(matrix[i][col][0] for i in range(len(matrix)))
    return [i for i in range(len(matrix)) if matrix[i][col][0] == max_payoff]


def find_best_responses_col(matrix: List[List[Tuple[int, int]]], row: int) -> List[int]:
    """
    Find all best responses for the column player given row player's strategy.
    
    Args:
        matrix: Payoff matrix
        row: Row player's strategy index
    
    Returns:
        List of column indices that are best responses
    """
    max_payoff = max(matrix[row][j][1] for j in range(len(matrix[0])))
    return [j for j in range(len(matrix[0])) if matrix[row][j][1] == max_payoff]


def find_dominated_strategies_row(matrix: List[List[Tuple[int, int]]]) -> List[int]:
    """
    Find strictly dominated strategies for row player.
    
    Returns:
        List of dominated row indices
    """
    num_rows = len(matrix)
    num_cols = len(matrix[0])
    dominated = []
    
    for i in range(num_rows):
        for other_i in range(num_rows):
            if i == other_i:
                continue
            # Check if other_i strictly dominates i
            dominates = True
            for j in range(num_cols):
                if matrix[other_i][j][0] <= matrix[i][j][0]:
                    dominates = False
                    break
            if dominates:
                dominated.append(i)
                break
    
    return dominated


def find_dominated_strategies_col(matrix: List[List[Tuple[int, int]]]) -> List[int]:
    """
    Find strictly dominated strategies for column player.
    
    Returns:
        List of dominated column indices
    """
    num_rows = len(matrix)
    num_cols = len(matrix[0])
    dominated = []
    
    for j in range(num_cols):
        for other_j in range(num_cols):
            if j == other_j:
                continue
            # Check if other_j strictly dominates j
            dominates = True
            for i in range(num_rows):
                if matrix[i][other_j][1] <= matrix[i][j][1]:
                    dominates = False
                    break
            if dominates:
                dominated.append(j)
                break
    
    return dominated


def has_dominant_strategy(matrix: List[List[Tuple[int, int]]]) -> Dict[str, Optional[int]]:
    """
    Check if either player has a dominant strategy.
    
    Returns:
        Dict with 'row' and 'col' keys, values are strategy indices or None
    """
    num_rows = len(matrix)
    num_cols = len(matrix[0])
    result = {"row": None, "col": None}
    
    # Check row player
    for i in range(num_rows):
        is_dominant = True
        for other_i in range(num_rows):
            if i == other_i:
                continue
            for j in range(num_cols):
                if matrix[i][j][0] <= matrix[other_i][j][0]:
                    is_dominant = False
                    break
            if not is_dominant:
                break
        if is_dominant:
            result["row"] = i
            break
    
    # Check column player
    for j in range(num_cols):
        is_dominant = True
        for other_j in range(num_cols):
            if j == other_j:
                continue
            for i in range(num_rows):
                if matrix[i][j][1] <= matrix[i][other_j][1]:
                    is_dominant = False
                    break
            if not is_dominant:
                break
        if is_dominant:
            result["col"] = j
            break
    
    return result


# =============================================================================
# MATRIX GENERATION FUNCTIONS
# =============================================================================

def generate_random_matrix(rows: int = 2, cols: int = 2, 
                          min_payoff: int = -5, max_payoff: int = 5) -> List[List[Tuple[int, int]]]:
    """
    Generate a random payoff matrix.
    
    Args:
        rows: Number of strategies for row player
        cols: Number of strategies for column player
        min_payoff: Minimum payoff value
        max_payoff: Maximum payoff value
    
    Returns:
        Random payoff matrix
    """
    matrix = []
    for i in range(rows):
        row = []
        for j in range(cols):
            row_payoff = random.randint(min_payoff, max_payoff)
            col_payoff = random.randint(min_payoff, max_payoff)
            row.append((row_payoff, col_payoff))
        matrix.append(row)
    return matrix


def generate_matrix_with_pure_nash(rows: int = 2, cols: int = 2,
                                   num_equilibria: int = 1) -> Tuple[List[List[Tuple[int, int]]], List[Tuple[int, int]]]:
    """
    Generate a matrix guaranteed to have specified number of pure Nash equilibria.
    
    Returns:
        Tuple of (matrix, list of equilibria positions)
    """
    # Start with random matrix
    matrix = generate_random_matrix(rows, cols)
    
    # Force specific cells to be Nash equilibria
    equilibria = []
    attempts = 0
    
    while len(equilibria) < num_equilibria and attempts < 100:
        # Pick random cell to make an equilibrium
        eq_row = random.randint(0, rows - 1)
        eq_col = random.randint(0, cols - 1)
        
        if (eq_row, eq_col) in equilibria:
            attempts += 1
            continue
        
        # Get current payoffs
        row_payoff, col_payoff = matrix[eq_row][eq_col]
        
        # Ensure row_payoff is highest in its column for row player
        for i in range(rows):
            if i != eq_row:
                current_row_p, current_col_p = matrix[i][eq_col]
                if current_row_p >= row_payoff:
                    matrix[i][eq_col] = (row_payoff - 1, current_col_p)
        
        # Ensure col_payoff is highest in its row for column player
        for j in range(cols):
            if j != eq_col:
                current_row_p, current_col_p = matrix[eq_row][j]
                if current_col_p >= col_payoff:
                    matrix[eq_row][j] = (current_row_p, col_payoff - 1)
        
        equilibria.append((eq_row, eq_col))
        attempts += 1
    
    return matrix, equilibria


def generate_matrix_without_pure_nash(rows: int = 2, cols: int = 2) -> List[List[Tuple[int, int]]]:
    """
    Generate a matrix guaranteed to have no pure Nash equilibrium.
    Uses a matching pennies-like structure.
    
    Returns:
        Payoff matrix with no pure Nash equilibrium
    """
    if rows == 2 and cols == 2:
        # Use matching pennies structure
        a = random.randint(1, 5)
        matrix = [
            [(a, -a), (-a, a)],
            [(-a, a), (a, -a)]
        ]
        return matrix
    
    # For larger matrices, create a cyclic structure
    matrix = []
    for i in range(rows):
        row = []
        for j in range(cols):
            # Create payoffs such that best responses cycle
            if (i + j) % 2 == 0:
                row.append((random.randint(1, 5), random.randint(-5, -1)))
            else:
                row.append((random.randint(-5, -1), random.randint(1, 5)))
        matrix.append(row)
    
    return matrix


def generate_matrix_with_dominant_strategy(rows: int = 2, cols: int = 2,
                                           dominant_for: str = "both") -> List[List[Tuple[int, int]]]:
    """
    Generate a matrix where one or both players have a dominant strategy.
    
    Args:
        rows: Number of row strategies
        cols: Number of column strategies
        dominant_for: "row", "col", or "both"
    
    Returns:
        Payoff matrix with dominant strategy structure
    """
    matrix = generate_random_matrix(rows, cols, min_payoff=0, max_payoff=5)
    
    if dominant_for in ["row", "both"]:
        # Make row 0 strictly dominant
        dominant_row = 0
        for j in range(cols):
            max_other = max(matrix[i][j][0] for i in range(rows) if i != dominant_row)
            current = matrix[dominant_row][j]
            matrix[dominant_row][j] = (max_other + random.randint(1, 3), current[1])
    
    if dominant_for in ["col", "both"]:
        # Make column 0 strictly dominant
        dominant_col = 0
        for i in range(rows):
            max_other = max(matrix[i][j][1] for j in range(cols) if j != dominant_col)
            current = matrix[i][dominant_col]
            matrix[i][dominant_col] = (current[0], max_other + random.randint(1, 3))
    
    return matrix


# =============================================================================
# FORMATTING FUNCTIONS
# =============================================================================

def format_matrix_ascii(matrix: List[List[Tuple[int, int]]],
                        row_strategies: Optional[List[str]] = None,
                        col_strategies: Optional[List[str]] = None) -> str:
    """
    Format payoff matrix as ASCII table.
    
    Args:
        matrix: Payoff matrix
        row_strategies: Names for row strategies (optional)
        col_strategies: Names for column strategies (optional)
    
    Returns:
        Formatted ASCII string representation
    """
    num_rows = len(matrix)
    num_cols = len(matrix[0])
    
    # Default strategy names
    if row_strategies is None:
        row_strategies = [f"R{i+1}" for i in range(num_rows)]
    if col_strategies is None:
        col_strategies = [f"C{j+1}" for j in range(num_cols)]
    
    # Calculate column widths
    cell_width = max(
        len(f"({p1},{p2})") for row in matrix for p1, p2 in row
    )
    cell_width = max(cell_width, max(len(s) for s in col_strategies))
    
    row_label_width = max(len(s) for s in row_strategies)
    
    lines = []
    
    # Header row with column player label
    lines.append(f"{'':>{row_label_width + 12}}Jucător 2 (Coloane)")
    
    # Column strategy names
    col_header = " " * (row_label_width + 12)
    for s in col_strategies:
        col_header += f"{s:^{cell_width + 2}}"
    lines.append(col_header)
    
    # Separator
    lines.append(" " * (row_label_width + 12) + "-" * ((cell_width + 2) * num_cols))
    
    # Data rows
    for i, row in enumerate(matrix):
        if i == 0:
            row_label = f"Jucător 1 {row_strategies[i]:>{row_label_width}} |"
        else:
            row_label = f"{'':>10}{row_strategies[i]:>{row_label_width}} |"
        
        cells = []
        for p1, p2 in row:
            cells.append(f"({p1:>2},{p2:>2})")
        
        lines.append(row_label + "  ".join(f"{c:^{cell_width}}" for c in cells))
    
    return "\n".join(lines)


def format_matrix_simple(matrix: List[List[Tuple[int, int]]]) -> str:
    """
    Format payoff matrix in a simple, compact format.
    """
    lines = []
    for i, row in enumerate(matrix):
        cells = [f"({p1},{p2})" for p1, p2 in row]
        lines.append(f"  Row {i+1}: " + "  ".join(cells))
    return "\n".join(lines)


def format_nash_equilibria(equilibria: List[Tuple[int, int]],
                           row_strategies: Optional[List[str]] = None,
                           col_strategies: Optional[List[str]] = None) -> str:
    """
    Format Nash equilibria as human-readable string.
    """
    if not equilibria:
        return "Nu există echilibru Nash pur."
    
    if row_strategies is None:
        row_strategies = [f"R{i+1}" for i in range(max(e[0] for e in equilibria) + 1)]
    if col_strategies is None:
        col_strategies = [f"C{j+1}" for j in range(max(e[1] for e in equilibria) + 1)]
    
    eq_strs = []
    for row, col in equilibria:
        eq_strs.append(f"({row_strategies[row]}, {col_strategies[col]})")
    
    if len(eq_strs) == 1:
        return f"Echilibrul Nash pur: {eq_strs[0]}"
    else:
        return f"Echilibre Nash pure: {', '.join(eq_strs)}"


# =============================================================================
# GAME INSTANCE GENERATION
# =============================================================================

def get_classic_game(game_type: str) -> Dict[str, Any]:
    """
    Get a predefined classic game.
    
    Args:
        game_type: Key from CLASSIC_GAMES
    
    Returns:
        Game dictionary with matrix and metadata
    """
    if game_type in CLASSIC_GAMES:
        return CLASSIC_GAMES[game_type].copy()
    
    # Default to Prisoner's Dilemma if not found
    return CLASSIC_GAMES["prisoners_dilemma"].copy()


def generate_game_instance(difficulty: str = "medium",
                          force_pure_nash: Optional[bool] = None,
                          force_dominant: Optional[bool] = None) -> Dict[str, Any]:
    """
    Generate a game theory instance based on difficulty.
    
    Args:
        difficulty: "easy", "medium", or "hard"
        force_pure_nash: If True, force pure NE to exist; if False, no pure NE
        force_dominant: If True, force dominant strategy to exist
    
    Returns:
        Dict with game instance data
    """
    if difficulty == "easy":
        # Use simple classic games
        game_types = ["prisoners_dilemma", "pure_coordination", "dominant_strategy_game"]
        game = get_classic_game(random.choice(game_types))
        game["difficulty"] = "easy"
        return game
    
    elif difficulty == "medium":
        # Use more complex classic games or small generated matrices
        if random.random() < 0.6:
            game_types = ["battle_of_sexes", "chicken", "stag_hunt", "coordination_game"]
            game = get_classic_game(random.choice(game_types))
        else:
            # Generate 2x2 matrix
            if force_pure_nash is False:
                matrix = generate_matrix_without_pure_nash()
                equilibria = []
            elif force_dominant:
                matrix = generate_matrix_with_dominant_strategy(dominant_for="row")
                equilibria = find_pure_nash_equilibria(matrix)
            else:
                matrix, equilibria = generate_matrix_with_pure_nash(2, 2, num_equilibria=random.randint(1, 2))
            
            game = {
                "name": "Joc Generat",
                "name_en": "Generated Game",
                "matrix": matrix,
                "row_strategies": ["Sus", "Jos"],
                "col_strategies": ["Stânga", "Dreapta"],
                "has_pure_nash": len(equilibria) > 0,
                "pure_nash": equilibria,
                "has_dominant_strategy": has_dominant_strategy(matrix)["row"] is not None or 
                                        has_dominant_strategy(matrix)["col"] is not None,
                "dominant_strategies": has_dominant_strategy(matrix),
                "description": "Joc generat aleator"
            }
        
        game["difficulty"] = "medium"
        return game
    
    else:  # hard
        # Generate larger matrices (2x3, 3x2, or 3x3)
        rows = random.choice([2, 3, 3])
        cols = random.choice([3, 2, 3])
        
        if force_pure_nash is False or random.random() < 0.3:
            matrix = generate_matrix_without_pure_nash(rows, cols) if rows == cols else generate_random_matrix(rows, cols)
            equilibria = find_pure_nash_equilibria(matrix)
        elif force_dominant:
            matrix = generate_matrix_with_dominant_strategy(rows, cols, dominant_for="row")
            equilibria = find_pure_nash_equilibria(matrix)
        else:
            matrix, equilibria = generate_matrix_with_pure_nash(rows, cols, num_equilibria=random.randint(1, 2))
        
        row_strats = ["A", "B", "C"][:rows]
        col_strats = ["X", "Y", "Z"][:cols]
        
        game = {
            "name": "Joc Complex",
            "name_en": "Complex Game",
            "matrix": matrix,
            "row_strategies": row_strats,
            "col_strategies": col_strats,
            "has_pure_nash": len(equilibria) > 0,
            "pure_nash": equilibria,
            "has_dominant_strategy": has_dominant_strategy(matrix)["row"] is not None or 
                                    has_dominant_strategy(matrix)["col"] is not None,
            "dominant_strategies": has_dominant_strategy(matrix),
            "description": f"Joc {rows}x{cols} generat aleator",
            "difficulty": "hard"
        }
        
        return game


# =============================================================================
# STRATEGY RECOMMENDATION
# =============================================================================

def recommend_strategy(game: Dict[str, Any]) -> Tuple[str, str, float]:
    """
    Recommend the best strategy for analyzing a game.
    
    Returns:
        Tuple of (strategy_key, reasoning, confidence)
    """
    matrix = game["matrix"]
    num_rows = len(matrix)
    num_cols = len(matrix[0])
    
    dominant = has_dominant_strategy(matrix)
    has_dom_row = dominant["row"] is not None
    has_dom_col = dominant["col"] is not None
    
    dominated_rows = find_dominated_strategies_row(matrix)
    dominated_cols = find_dominated_strategies_col(matrix)
    has_dominated = len(dominated_rows) > 0 or len(dominated_cols) > 0
    
    pure_nash = find_pure_nash_equilibria(matrix)
    has_pure = len(pure_nash) > 0
    
    # Decision logic - CORECTATĂ pentru a respecta teoria jocurilor
    
    # PRIORITATE 1: Dacă nu există echilibru Nash pur, trebuie strategii mixte
    # (ex: Matching Pennies, Rock-Paper-Scissors)
    if not has_pure:
        return (
            "mixed_strategy_calculation",
            f"Acest joc NU are echilibru Nash în strategii pure. "
            f"Pentru jocuri fără echilibru pur (precum Matching Pennies), "
            f"singura soluție este calculul echilibrului în strategii mixte, "
            f"unde jucătorii aleg aleatoriu cu probabilități specifice. "
            f"Complexitate: O(n) pentru 2x2, necesită rezolvarea unui sistem de ecuații.",
            0.95
        )
    
    # PRIORITATE 2: Strategii dominante → eliminare iterativă
    if has_dom_row or has_dom_col:
        return (
            "dominance_elimination",
            f"Există strategie dominantă {'pentru ambii jucători' if has_dom_row and has_dom_col else 'pentru un jucător'}. "
            f"Eliminarea iterativă a strategiilor dominate (IESDS) simplifică analiza și conduce direct la echilibru. "
            f"Complexitate: O(m²×n + n²×m) pentru eliminare completă.",
            0.95
        )
    
    # PRIORITATE 3: Strategii dominate (nu dominante) care pot fi eliminate
    if has_dominated:
        return (
            "dominance_elimination",
            f"Există strategii strict dominate care pot fi eliminate iterativ (IESDS). "
            f"Aceasta reduce dimensiunea jocului și facilitează găsirea echilibrului. "
            f"Complexitate: O(m²×n + n²×m) pentru eliminare completă.",
            0.90
        )
    
    # PRIORITATE 4: Jocuri mici (2x2) cu echilibru pur → enumerare directă
    if num_rows <= 2 and num_cols <= 2 and has_pure:
        return (
            "pure_strategy_enumeration",
            f"Pentru un joc 2x2 cu echilibru Nash pur, enumerarea tuturor profilurilor de strategie "
            f"(doar 4 combinații) este cea mai directă metodă. "
            f"Verificăm fiecare celulă pentru a fi best response mutual. "
            f"Complexitate: O(m×n) = O(4) pentru 2x2.",
            0.95
        )
    
    # PRIORITATE 5: Jocuri medii (3x3) → analiza best response
    if num_rows <= 3 and num_cols <= 3:
        return (
            "best_response_analysis",
            f"Pentru un joc {num_rows}x{num_cols} cu echilibru pur, analiza best response este eficientă. "
            f"Marcăm best response-urile fiecărui jucător și căutăm celulele cu ambele marcate. "
            f"Complexitate: O(m×n) pentru marcarea best responses.",
            0.90
        )
    
    # DEFAULT: Pentru jocuri mai mari
    return (
        "best_response_analysis",
        f"Analiza best response este metoda generală recomandată pentru jocuri de dimensiune {num_rows}x{num_cols}. "
        f"Identificăm răspunsurile optime ale fiecărui jucător și găsim punctele de intersecție. "
        f"Complexitate: O(m×n) pentru identificarea echilibrelor.",
        0.85
    )


# =============================================================================
# TEST
# =============================================================================

if __name__ == "__main__":
    print("=== GAME THEORY UTILS TEST ===\n")
    
    # Test 1: Classic game
    print("1. Prisoner's Dilemma:")
    pd = get_classic_game("prisoners_dilemma")
    print(format_matrix_ascii(pd["matrix"], pd["row_strategies"], pd["col_strategies"]))
    ne = find_pure_nash_equilibria(pd["matrix"])
    print(format_nash_equilibria(ne, pd["row_strategies"], pd["col_strategies"]))
    strategy, reasoning, conf = recommend_strategy(pd)
    print(f"Strategie recomandată: {strategy} (confidence: {conf})")
    print(f"Motivație: {reasoning}\n")
    
    # Test 2: Battle of Sexes
    print("2. Battle of the Sexes:")
    bos = get_classic_game("battle_of_sexes")
    print(format_matrix_ascii(bos["matrix"], bos["row_strategies"], bos["col_strategies"]))
    ne = find_pure_nash_equilibria(bos["matrix"])
    print(format_nash_equilibria(ne, bos["row_strategies"], bos["col_strategies"]))
    print()
    
    # Test 3: Matching Pennies (no pure NE)
    print("3. Matching Pennies:")
    mp = get_classic_game("matching_pennies")
    print(format_matrix_ascii(mp["matrix"], mp["row_strategies"], mp["col_strategies"]))
    ne = find_pure_nash_equilibria(mp["matrix"])
    print(format_nash_equilibria(ne, mp["row_strategies"], mp["col_strategies"]))
    strategy, reasoning, conf = recommend_strategy(mp)
    print(f"Strategie recomandată: {strategy}")
    print()
    
    # Test 4: Generate random game
    print("4. Generated Game (medium):")
    game = generate_game_instance("medium")
    print(format_matrix_ascii(game["matrix"], game.get("row_strategies"), game.get("col_strategies")))
    ne = find_pure_nash_equilibria(game["matrix"])
    print(format_nash_equilibria(ne, game.get("row_strategies"), game.get("col_strategies")))
    print()
    
    # Test 5: Generate hard game
    print("5. Generated Game (hard - 3x3):")
    game = generate_game_instance("hard")
    print(format_matrix_ascii(game["matrix"], game.get("row_strategies"), game.get("col_strategies")))
    ne = find_pure_nash_equilibria(game["matrix"])
    print(format_nash_equilibria(ne, game.get("row_strategies"), game.get("col_strategies")))
    strategy, reasoning, conf = recommend_strategy(game)
    print(f"Strategie recomandată: {strategy} (confidence: {conf})")
    
    print("\n=== ALL TESTS PASSED ===")
