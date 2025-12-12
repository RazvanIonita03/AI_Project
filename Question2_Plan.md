# Plan: Add Game Theory (Normal Form) Problem Type

## Overview

Add a new "Game Theory (Normal Form)" problem to the SmarTest quiz system, following the existing architecture. Questions will ask whether a pure Nash equilibrium exists for a given payoff matrix and what it is.

---

## Steps

### 1. Add problem definition to `knowledge_base.py`
Create a new `"game_theory"` entry in `KNOWLEDGE_BASE` with:
- **Strategies**: `pure_strategy_enumeration`, `best_response_analysis`, `dominance_elimination`, `mixed_strategy_calculation`
- **Instance parameters**: `num_players`, `strategies_per_player`, `has_dominant_strategy`, `has_pure_nash`, `game_type`, `matrix`
- **Decision rules** mapping conditions to optimal strategies

### 2. Create utility module `game_theory_utils.py`
Add helper functions for:
- Generating payoff matrices with known Nash equilibrium properties
- Computing pure Nash equilibria from a matrix
- Checking for dominant strategies
- Predefined classic games (Prisoner's Dilemma, Battle of Sexes, Coordination Game, Chicken) for easy/medium difficulty
- Random matrix generation with computed NE for hard difficulty

### 3. Add rules to `rule_engine.py`
Create a `# ===== GAME THEORY RULES =====` section in `_initialize_rules()` with ~8-10 rules mapping instance parameters to optimal strategies:
- Small 2x2 games → enumeration
- Dominated strategies present → dominance elimination
- No pure NE → mixed strategy calculation

### 4. Add parametric generation to `parametric_generator.py`
Update:
- `_define_parameter_space()` - game theory parameters
- `_define_strategy_mappings()` - strategy selection logic
- `_format_instance()` - inline ASCII matrix formatting
- `_generate_reasoning()` - game theory specific reasoning

### 5. Update question generator in `question_generator.py`
- Add `"game_theory"` to random problem selection
- Update `_generate_rich_instance()` - use classic games for easy/medium
- Update `_generate_boundary_instance()` - random generated matrices for hard

### 6. Add answer evaluation in `answer_evaluator.py`
- Add strategy synonyms for game theory strategies
- Update `_check_problem_specific_reasoning()` with game theory terms (Nash equilibrium, dominant strategy, payoff, best response, etc.)

---

## Implementation Details

### Matrix Display Format
Display payoff matrices inline in ASCII/text format for clarity:
```
            Player 2
            L      R
Player 1 U (3,3)  (0,5)
         D (5,0)  (1,1)
```

### Game Mix Strategy
- **Easy/Medium**: Use predefined classic games:
  - Prisoner's Dilemma
  - Battle of Sexes
  - Coordination Game
  - Chicken/Hawk-Dove
  - Matching Pennies
  
- **Hard**: Randomly generate 3x3 or larger matrices with algorithmically computed Nash equilibria

### Nash Equilibrium Verification
The `game_theory_utils.py` module will contain pure algorithmic functions (no AI/LLM) to:
- Find all pure Nash equilibria by checking best responses
- Identify dominated strategies
- Validate that generated instances have correct answers

---

## Files to Modify

| File | Changes |
|------|---------|
| `game_theory_utils.py` | NEW - utility functions for NE computation |
| `knowledge_base.py` | Add `"game_theory"` to KNOWLEDGE_BASE |
| `rule_engine.py` | Add game theory rules section |
| `parametric_generator.py` | Add parameter space and mappings |
| `question_generator.py` | Add game_theory to problem selection |
| `answer_evaluator.py` | Add strategy synonyms and terms |

---

## Strategies Details

| Strategy Key | Name | Best For | Complexity |
|--------------|------|----------|------------|
| `pure_strategy_enumeration` | Pure Strategy Enumeration | Small games (2x2, 2x3) | O(m×n) |
| `best_response_analysis` | Best Response Analysis | Finding NE directly | O(m×n) |
| `dominance_elimination` | Dominance Elimination (IESDS) | Games with dominated strategies | O(m²×n²) |
| `mixed_strategy_calculation` | Mixed Strategy Calculation | When no pure NE exists | O(m×n) for 2-player |

---

## Status: ✅ COMPLETED

- [x] Save plan to file
- [x] Create game_theory_utils.py
- [x] Update knowledge_base.py
- [x] Update rule_engine.py
- [x] Update parametric_generator.py
- [x] Update question_generator.py
- [x] Update answer_evaluator.py
- [x] Test implementation

## Implementation Summary

The Game Theory (Normal Form) problem type has been successfully added to the SmarTest quiz system. The implementation includes:

1. **game_theory_utils.py** (~800 lines) - Complete utility module with:
   - 8 classic games (Prisoner's Dilemma, Battle of Sexes, etc.)
   - Nash equilibrium computation algorithms
   - Matrix generation with known properties
   - ASCII matrix formatting

2. **knowledge_base.py** - Added `"game_theory"` entry with 4 strategies

3. **rule_engine.py** - Added 8 game theory rules for strategy selection

4. **parametric_generator.py** - Full game theory parameter space and mappings

5. **question_generator.py** - Special handling for game theory with matrix display

6. **answer_evaluator.py** - Strategy synonyms and problem-specific terms

7. **main.py** & **interactive_quiz.py** - Updated to include game_theory in default problems
