"""
Interactive Quiz - Mod simplu pentru utilizatori
Răspunde la întrebări și primește feedback instant
"""

from main import SmarTest, Question
import os


def clear_screen():
    """Curăță ecranul consolei"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_separator(char="=", length=80):
    """Print separator line"""
    print(char * length)


def get_user_answer():
    """
    Obține răspunsul utilizatorului în format structurat
    
    Returns:
        str: Răspunsul formatat cu Strategie și Justificare
    """
    print("\n📝 Scrie răspunsul tău:")
    print("-" * 60)
    
    # Get strategy
    print("\n1. Care este STRATEGIA optimă?")
    print("   Exemple: backtracking, simulated_annealing, greedy, etc.")
    strategy = input("   Strategie: ").strip()
    
    # Get justification
    print("\n2. JUSTIFICĂ alegerea (explică de ce e optimă):")
    print("   Menționează: complexitate, caracteristici problemă, trade-offs")
    print("   (Scrie răspunsul și apasă Enter de 2 ori când termini)")
    
    justification_lines = []
    empty_count = 0
    
    while empty_count < 2:
        line = input("   ")
        if line.strip() == "":
            empty_count += 1
        else:
            empty_count = 0
            justification_lines.append(line)
    
    justification = "\n".join(justification_lines)
    
    # Format answer
    answer_text = f"""Strategie: {strategy}

Justificare: {justification}
"""
    
    return answer_text


def show_question(question: Question, number: int, total: int):
    """Afișează o întrebare formatată"""
    print_separator()
    print(f"ÎNTREBAREA {number}/{total}")
    print_separator()
    print()
    
    # Problem info
    if hasattr(question, 'problem_type'):
        problem_names = {
            'n-queens': 'N-Queens',
            'hanoi': 'Turnurile din Hanoi',
            'graph_coloring': 'Colorarea Grafurilor',
            'knights_tour': 'Tura Calului'
        }
        print(f"📚 Problemă: {problem_names.get(question.problem_type, question.problem_type)}")
    
    if hasattr(question, 'difficulty'):
        diff_ro = {'easy': 'Ușoară', 'medium': 'Medie', 'hard': 'Dificilă'}
        print(f"⭐ Dificultate: {diff_ro.get(question.difficulty, question.difficulty)}")
    
    print()
    print(question.text)
    print()


def show_result(result: dict, show_answer: bool = True):
    """Afișează rezultatul evaluării"""
    score = result['score']
    
    print("\n" + "="*80)
    print("📊 REZULTAT")
    print("="*80)
    
    # Overall score
    if score >= 90:
        emoji = "🌟"
        message = "EXCELENT!"
    elif score >= 70:
        emoji = "✅"
        message = "BINE!"
    elif score >= 50:
        emoji = "⚠️"
        message = "ACCEPTABIL"
    else:
        emoji = "❌"
        message = "INSUFICIENT"
    
    print(f"\n{emoji} {message} - Punctaj: {score}/100\n")
    
    # Breakdown
    print(f"  • Strategie: {result['strategy_score']}/100 {'✅' if result['strategy_correct'] else '❌'}")
    print(f"  • Justificare: {result['reasoning_score']}/100")
    
    if show_answer:
        print("\n" + "-"*80)
        print("📖 FEEDBACK:")
        print("-"*80)
        print(result['feedback'])
    
    print("\n" + "="*80)


def main():
    """Modul interactiv principal"""
    
    # Welcome
    clear_screen()
    print("="*80)
    print("🎓 SMARTEST - Quiz Interactiv AI")
    print("="*80)
    print("\nTestează-ți cunoștințele despre strategii de rezolvare pentru probleme AI!")
    print()
    
    # Configuration
    print("⚙️ CONFIGURARE")
    print("-"*60)
    
    try:
        num_questions = int(input("Câte întrebări vrei să rezolvi? (1-10): ").strip() or "3")
        num_questions = max(1, min(10, num_questions))
    except ValueError:
        num_questions = 3
        print(f"Folosesc default: {num_questions} întrebări")
    
    try:
        difficulty = input("Dificultate (easy/medium/hard/mixed) [mixed]: ").strip().lower() or "mixed"
        if difficulty not in ["easy", "medium", "hard", "mixed"]:
            difficulty = "mixed"
    except:
        difficulty = "mixed"
    
    print(f"\n✅ Configurare: {num_questions} întrebări, dificultate {difficulty}")
    input("\nApasă Enter pentru a începe...")
    
    # Initialize app
    app = SmarTest()
    
    # Generate questions
    print("\n🔄 Generare întrebări...")
    questions = app.generate_test(
        num_questions=num_questions,
        problems=["n-queens", "hanoi", "graph_coloring", "knights_tour"],
        difficulty=difficulty
    )
    
    # Save test PDF
    pdf_file = app.save_test_pdf(questions)
    print(f"📕 Test salvat în: {pdf_file}")
    
    # Quiz loop
    answers = []
    results = []
    
    for i, question in enumerate(questions, 1):
        clear_screen()
        
        # Show question
        show_question(question, i, len(questions))
        
        # Get answer
        answer_text = get_user_answer()
        answers.append(answer_text)
        
        # Evaluate immediately
        print("\n⏳ Evaluare în curs...")
        result = app.evaluate_answer(question, answer_text)
        results.append(result)
        
        # Show result
        show_result(result, show_answer=True)
        
        if i < len(questions):
            input("\nApasă Enter pentru următoarea întrebare...")
    
    # Final results
    clear_screen()
    print("="*80)
    print("🏆 REZULTATE FINALE")
    print("="*80)
    
    total_score = sum(r['score'] for r in results)
    avg_score = total_score / len(results)
    max_score = len(results) * 100
    
    print(f"\n📊 Punctaj Total: {total_score:.0f}/{max_score}")
    print(f"📊 Medie: {avg_score:.2f}/100")
    print(f"📝 Întrebări: {len(results)}")
    
    # Grade
    if avg_score >= 90:
        grade = "10 - Excelent! 🌟"
    elif avg_score >= 80:
        grade = "9 - Foarte bine! 🎉"
    elif avg_score >= 70:
        grade = "8 - Bine! ✅"
    elif avg_score >= 60:
        grade = "7 - Satisfăcător 👍"
    elif avg_score >= 50:
        grade = "6 - Suficient ⚠️"
    else:
        grade = "Sub 6 - Insuficient ❌"
    
    print(f"\n🎯 Notă estimată: {grade}")
    
    # Detailed breakdown
    print("\n📋 Detalii pe întrebare:")
    print("-"*80)
    
    for i, (result, question) in enumerate(zip(results, questions), 1):
        status = "✅" if result['score'] >= 60 else "❌"
        strat_status = "✓" if result['strategy_correct'] else "✗"
        print(f"{status} Întrebarea {i}: {result['score']}/100 "
              f"(Strategie: {strat_status} {result['strategy_score']}, "
              f"Justificare: {result['reasoning_score']})")
    
    # Save evaluation
    print("\n💾 Salvare rezultate...")
    evaluation = {
        "total_score": total_score,
        "average_score": avg_score,
        "max_score": max_score,
        "num_questions": len(results),
        "results": results
    }
    
    app.save_evaluation(evaluation)
    app.save_evaluation_pdf(evaluation, questions)
    
    print("✅ Evaluare salvată în PDF!")
    print("\n" + "="*80)
    print("Mulțumim că ai folosit SMARTEST! 🎓")
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Quiz întrerupt. La revedere!")
    except Exception as e:
        print(f"\n❌ Eroare: {e}")
        import traceback
        traceback.print_exc()
