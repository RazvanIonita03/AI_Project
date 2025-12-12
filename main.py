"""
SmarTest - Aplicație principală
Generare și evaluare întrebări pentru examen AI
"""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from question_generator import HybridQuestionGenerator, Question, GenerationMode
from answer_evaluator import AnswerEvaluator, evaluate_from_text
from pdf_generator import PDFGenerator


class SmarTest:
    """Aplicație principală pentru generare și evaluare teste"""
    
    def __init__(self, output_dir: str = "generated_tests"):
        self.generator = HybridQuestionGenerator()
        self.evaluator = AnswerEvaluator()
        self.pdf_generator = PDFGenerator()
        self.output_dir = output_dir
        self.current_test = None
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_test(self, 
                     num_questions: int = 10,
                     problems: Optional[List[str]] = None,
                     difficulty: str = "mixed") -> List[Question]:
        """
        Generează un test nou
        
        Args:
            num_questions: Numărul de întrebări
            problems: Listă de probleme (None = toate)
            difficulty: "easy", "medium", "hard", sau "mixed"
        
        Returns:
            Listă de Questions
        """
        print(f"🎯 Generare test cu {num_questions} întrebări...")
        
        # Setup problem distribution
        if problems is None:
            problems = ["n-queens", "hanoi", "graph_coloring", "knights_tour", "game_theory"]
        
        # 40% game_theory, restul împărțit egal între celelalte probleme
        problem_distribution = {}
        if "game_theory" in problems:
            game_theory_count = max(1, int(num_questions * 0.4))  # 40% game theory
            other_problems = [p for p in problems if p != "game_theory"]
            remaining = num_questions - game_theory_count
            
            if other_problems:
                per_problem = remaining // len(other_problems)
                extra = remaining % len(other_problems)
                
                for i, p in enumerate(other_problems):
                    problem_distribution[p] = per_problem + (1 if i < extra else 0)
            
            problem_distribution["game_theory"] = game_theory_count
        else:
            # Fără game_theory - distribuție egală
            problem_distribution = {p: num_questions // len(problems) for p in problems}
            problem_distribution[problems[0]] += num_questions % len(problems)
        
        # Setup difficulty distribution
        if difficulty == "mixed":
            difficulty_distribution = {"easy": 0.3, "medium": 0.4, "hard": 0.3}
        else:
            difficulty_distribution = {difficulty: 1.0}
        
        # Generate
        questions = self.generator.generate_test(
            num_questions=num_questions,
            problem_distribution=problem_distribution,
            difficulty_distribution=difficulty_distribution
        )
        
        self.current_test = questions
        
        print(f"✅ Test generat cu succes!")
        print(f"   Probleme: {list(problem_distribution.keys())}")
        print(f"   Dificultate: {difficulty}")
        
        return questions
    
    def save_test(self, 
                  questions: List[Question],
                  filename: Optional[str] = None,
                  include_answers: bool = False) -> str:
        """
        Salvează testul în format JSON
        
        Args:
            questions: Listă de întrebări
            filename: Nume fișier (None = auto-generate)
            include_answers: Include răspunsurile corecte
        
        Returns:
            Path la fișierul salvat
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Convert questions to dict
        test_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "num_questions": len(questions),
                "includes_answers": include_answers
            },
            "questions": []
        }
        
        for q in questions:
            q_dict = q.to_dict()
            
            if not include_answers:
                # Remove correct answers
                q_dict.pop("correct_strategy", None)
                q_dict.pop("reasoning", None)
            
            test_data["questions"].append(q_dict)
        
        # Save
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Test salvat în: {filepath}")
        return filepath
    
    def save_test_text(self, 
                       questions: List[Question],
                       filename: Optional[str] = None) -> str:
        """
        Salvează testul în format text citibil
        
        Args:
            questions: Listă de întrebări
            filename: Nume fișier (None = auto-generate)
        
        Returns:
            Path la fișierul salvat
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_{timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("SMARTEST - TEST INTELIGENȚĂ ARTIFICIALĂ\n")
            f.write(f"Generat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Număr întrebări: {len(questions)}\n")
            f.write("="*80 + "\n\n")
            
            for i, q in enumerate(questions, 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"ÎNTREBAREA {i}\n")
                f.write(f"{'='*80}\n\n")
                f.write(q.text)
                f.write("\n\n")
                f.write("-"*80)
                f.write("\n\nRĂSPUNS:\n\n\n")
                f.write("-"*80)
                f.write("\n\n")
        
        print(f"📄 Test text salvat în: {filepath}")
        return filepath
    
    def save_test_pdf(self,
                     questions: List[Question],
                     filename: Optional[str] = None) -> str:
        """
        Salvează testul în format PDF
        
        Args:
            questions: Listă de întrebări
            filename: Nume fișier (None = auto-generate)
        
        Returns:
            Path la fișierul salvat
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_{timestamp}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Generate PDF
        self.pdf_generator.generate_test_pdf(questions, filepath, include_answers=False)
        
        print(f"📕 Test PDF salvat în: {filepath}")
        return filepath
    
    def save_answers(self, 
                    questions: List[Question],
                    filename: Optional[str] = None) -> str:
        """
        Salvează răspunsurile corecte separat (barem)
        
        Args:
            questions: Listă de întrebări
            filename: Nume fișier (None = auto-generate)
        
        Returns:
            Path la fișierul salvat
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"barem_{timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("SMARTEST - BAREM RĂSPUNSURI CORECTE\n")
            f.write(f"Generat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            for i, q in enumerate(questions, 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"ÎNTREBAREA {i}\n")
                f.write(f"{'='*80}\n\n")
                
                f.write(f"Problemă: {q.problem_type}\n")
                f.write(f"Instanță: {q.instance}\n")
                f.write(f"Dificultate: {q.difficulty}\n\n")
                
                f.write("--- RĂSPUNS CORECT ---\n")
                f.write(f"Strategie: {q.correct_strategy}\n\n")
                
                f.write("--- JUSTIFICARE ---\n")
                f.write(q.reasoning)
                f.write("\n\n")
        
        print(f"📋 Barem salvat în: {filepath}")
        return filepath
    
    def save_answers_pdf(self,
                        questions: List[Question],
                        filename: Optional[str] = None) -> str:
        """
        Salvează răspunsurile corecte în format PDF (barem)
        
        Args:
            questions: Listă de întrebări
            filename: Nume fișier (None = auto-generate)
        
        Returns:
            Path la fișierul salvat
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"barem_{timestamp}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Generate PDF with answers
        self.pdf_generator.generate_test_pdf(questions, filepath, include_answers=True)
        
        print(f"📗 Barem PDF salvat în: {filepath}")
        return filepath
    
    def evaluate_answer(self,
                       question: Question,
                       answer_text: str) -> Dict[str, Any]:
        """
        Evaluează un răspuns pentru o întrebare
        
        Args:
            question: Question object
            answer_text: Text răspuns utilizator
        
        Returns:
            Dict cu rezultatul evaluării
        """
        result = evaluate_from_text(question.to_dict(), answer_text)
        return result
    
    def evaluate_test(self,
                     questions: List[Question],
                     answers: List[str]) -> Dict[str, Any]:
        """
        Evaluează un test complet
        
        Args:
            questions: Listă întrebări
            answers: Listă răspunsuri utilizator
        
        Returns:
            Dict cu rezultate evaluare
        """
        if len(questions) != len(answers):
            raise ValueError("Numărul de răspunsuri nu corespunde cu numărul de întrebări")
        
        results = []
        total_score = 0
        
        for i, (question, answer_text) in enumerate(zip(questions, answers), 1):
            print(f"Evaluare întrebare {i}/{len(questions)}...")
            result = self.evaluate_answer(question, answer_text)
            results.append(result)
            total_score += result["score"]
        
        avg_score = total_score / len(questions)
        
        return {
            "total_score": total_score,
            "average_score": avg_score,
            "max_score": len(questions) * 100,
            "num_questions": len(questions),
            "results": results
        }
    
    def save_evaluation(self,
                       evaluation: Dict[str, Any],
                       filename: Optional[str] = None) -> str:
        """
        Salvează rezultatul evaluării
        
        Args:
            evaluation: Dict cu rezultate
            filename: Nume fișier
        
        Returns:
            Path la fișier
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluare_{timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("SMARTEST - REZULTAT EVALUARE\n")
            f.write(f"Evaluat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"📊 PUNCTAJ TOTAL: {evaluation['total_score']:.0f}/{evaluation['max_score']}\n")
            f.write(f"📊 MEDIE: {evaluation['average_score']:.2f}/100\n")
            f.write(f"📝 Număr întrebări: {evaluation['num_questions']}\n\n")
            
            for i, result in enumerate(evaluation['results'], 1):
                f.write(f"\n{'='*80}\n")
                f.write(f"ÎNTREBAREA {i} - Punctaj: {result['score']}/100\n")
                f.write(f"{'='*80}\n\n")
                f.write(result['feedback'])
                f.write("\n\n")
        
        print(f"📊 Evaluare salvată în: {filepath}")
        return filepath
    
    def save_evaluation_pdf(self,
                           evaluation: Dict[str, Any],
                           questions: List[Question],
                           filename: Optional[str] = None) -> str:
        """
        Salvează rezultatul evaluării în format PDF
        
        Args:
            evaluation: Dict cu rezultate
            questions: Listă întrebări (pentru context)
            filename: Nume fișier
        
        Returns:
            Path la fișier
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluare_{timestamp}.pdf"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Generate PDF evaluation
        self.pdf_generator.generate_evaluation_pdf(evaluation, questions, filepath)
        
        print(f"📘 Evaluare PDF salvată în: {filepath}")
        return filepath
    
    def print_test(self, questions: List[Question], include_answers: bool = False):
        """Afișează testul în consolă"""
        print("\n" + "="*80)
        print("SMARTEST - TEST INTELIGENȚĂ ARTIFICIALĂ")
        print(f"Număr întrebări: {len(questions)}")
        print("="*80 + "\n")
        
        for i, q in enumerate(questions, 1):
            print(f"\n{'='*80}")
            print(f"ÎNTREBAREA {i}")
            print(f"Problemă: {q.problem_type} | Dificultate: {q.difficulty}")
            print('='*80 + "\n")
            print(q.text)
            
            if include_answers:
                print(f"\n--- RĂSPUNS CORECT ---")
                print(f"Strategie: {q.correct_strategy}")
                print(f"\n{q.reasoning}")
            
            print("\n")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Returnează statistici despre generare"""
        stats = self.generator.get_statistics()
        return stats


def interactive_test():
    """
    Mod interactiv - utilizatorul răspunde la întrebări
    """
    print("🎓 SMARTEST - MOD INTERACTIV")
    print("="*80)
    print("Vei primi întrebări despre strategii AI și trebuie să răspunzi.")
    print("Format răspuns:")
    print("  Strategie: <nume_strategie>")
    print("  Justificare: <explicația ta>")
    print("="*80)
    
    app = SmarTest()
    
    # Ask user for test parameters
    print("\n⚙️ CONFIGURARE TEST")
    try:
        num_q = int(input("Câte întrebări vrei? (1-20): ").strip() or "5")
        num_q = max(1, min(20, num_q))
    except:
        num_q = 5
        print(f"Folosesc default: {num_q} întrebări")
    
    try:
        difficulty = input("Dificultate (easy/medium/hard/mixed): ").strip().lower() or "mixed"
        if difficulty not in ["easy", "medium", "hard", "mixed"]:
            difficulty = "mixed"
    except:
        difficulty = "mixed"
    
    print(f"\n✅ Generare test cu {num_q} întrebări, dificultate: {difficulty}")
    
    # Generate questions
    questions = app.generate_test(
        num_questions=num_q,
        problems=["n-queens", "hanoi", "graph_coloring", "knights_tour", "game_theory"],
        difficulty=difficulty
    )
    
    # Save test PDF (without answers)
    pdf_file = app.save_test_pdf(questions)
    print(f"\n📕 Test salvat în: {pdf_file}")
    print("Poți deschide PDF-ul și să răspunzi pe hârtie, sau să răspunzi aici în consolă.\n")
    
    # Collect answers
    answers = []
    
    for i, question in enumerate(questions, 1):
        print("\n" + "="*80)
        print(f"ÎNTREBAREA {i}/{len(questions)}")
        print("="*80)
        print(question.text)
        print()
        
        print("Răspunsul tău (scrie 'Strategie:' pe prima linie, apoi 'Justificare:'):")
        print("Când termini de scris, apasă Enter pe o linie goală.")
        print("-"*80)
        
        answer_lines = []
        while True:
            try:
                line = input()
                if line.strip() == "":
                    break
                answer_lines.append(line)
            except EOFError:
                break
        
        answer_text = "\n".join(answer_lines)
        answers.append(answer_text)
        
        print(f"\n✅ Răspuns {i} salvat!")
    
    # Evaluate all answers
    print("\n\n" + "="*80)
    print("📊 EVALUARE RĂSPUNSURI")
    print("="*80)
    
    evaluation = app.evaluate_test(questions, answers)
    
    # Save evaluation
    app.save_evaluation(evaluation)
    app.save_evaluation_pdf(evaluation, questions)
    
    # Display results
    print("\n" + "="*80)
    print("🎯 REZULTATE FINALE")
    print("="*80)
    print(f"Punctaj total: {evaluation['total_score']:.0f}/{evaluation['max_score']}")
    print(f"Medie: {evaluation['average_score']:.2f}/100")
    print(f"Număr întrebări: {evaluation['num_questions']}")
    
    print("\n📋 Detalii pe întrebare:")
    for i, result in enumerate(evaluation['results'], 1):
        status = "✅ CORECT" if result['score'] >= 60 else "❌ GREȘIT"
        print(f"  {i}. {status} - {result['score']}/100 (Strategie: {result['strategy_score']}/100, Justificare: {result['reasoning_score']}/100)")
    
    print("\n📄 Evaluare completă salvată în PDF!")
    print("="*80)


def main_demo():
    """Demonstrație a funcționalității aplicației"""
    
    print("🎓 SMARTEST - Aplicație Generare și Evaluare Teste AI")
    print("="*80)
    
    # Initialize
    app = SmarTest()
    
    # 1. Generate test
    print("\n1️⃣ GENERARE TEST")
    print("-"*80)
    questions = app.generate_test(
        num_questions=6,
        problems=["n-queens", "hanoi", "graph_coloring", "knights_tour", "game_theory"],
        difficulty="mixed"
    )
    
    # 2. Display test
    print("\n2️⃣ AFIȘARE TEST")
    print("-"*80)
    app.print_test(questions[:2], include_answers=False)  # Show only first 2
    
    # 3. Save test
    print("\n3️⃣ SALVARE TEST (PDF)")
    print("-"*80)
    
    # Generate only PDF versions
    pdf_test_file = app.save_test_pdf(questions)
    pdf_barem_file = app.save_answers_pdf(questions)
    
    print("\n✅ Fișiere PDF generate:")
    print(f"  - Test PDF: {os.path.basename(pdf_test_file)}")
    print(f"  - Barem PDF: {os.path.basename(pdf_barem_file)}")
    
    # 4. Demo evaluation
    print("\n4️⃣ DEMO EVALUARE")
    print("-"*80)
    
    # Simulate user answer for first question
    sample_question = questions[0]
    
    print(f"\nÎntrebare demo:")
    print(sample_question.text)
    
    print(f"\nRăspuns utilizator (simulat):")
    sample_answer = f"""
    Strategie: {sample_question.correct_strategy}
    
    Justificare: Pentru această instanță, strategia aleasă este optimă deoarece
    complexitatea este acceptabilă și garantează găsirea soluției. Având în vedere
    parametrii problemei, această abordare oferă cel mai bun raport eficiență-calitate.
    """
    print(sample_answer)
    
    # Evaluate
    result = app.evaluate_answer(sample_question, sample_answer)
    
    print("\n📊 REZULTAT EVALUARE:")
    print(result['feedback'])
    
    # 5. Statistics
    print("\n5️⃣ STATISTICI")
    print("-"*80)
    stats = app.get_statistics()
    print(f"Total întrebări generate: {stats['total']}")
    print(f"Distribuție probleme: {stats['by_problem']}")
    print(f"Distribuție dificultate: {stats['by_difficulty']}")
    print(f"Distribuție mod generare: {stats['by_mode']}")
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLET!")
    print("="*80)


if __name__ == "__main__":
    import sys
    
    # Check if user wants interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_test()
    else:
        print("\n💡 TIP: Pentru mod interactiv, rulează: python main.py interactive\n")
        main_demo()
