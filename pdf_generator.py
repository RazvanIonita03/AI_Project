"""
PDF Generator pentru SmarTest
Generează PDF-uri pentru teste și răspunsuri
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
from typing import List, Dict, Any
import os
import unicodedata


class PDFGenerator:
    """Generator de PDF-uri pentru teste și răspunsuri"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    @staticmethod
    def remove_diacritics(text: str) -> str:
        """
        Elimină diacriticele din text pentru compatibilitate PDF
        
        Args:
            text: Text cu diacritice
            
        Returns:
            Text fără diacritice
        """
        if not text:
            return text
            
        # Mapare manuală pentru caractere românești
        replacements = {
            'ă': 'a', 'Ă': 'A',
            'â': 'a', 'Â': 'A',
            'î': 'i', 'Î': 'I',
            'ș': 's', 'Ș': 'S',
            'ţ': 't', 'Ţ': 'T',
            'ț': 't', 'Ț': 'T',
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    def _setup_custom_styles(self):
        """Configurează stiluri personalizate pentru PDF"""
        
        # Titlu principal
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=20,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitlu
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        # Întrebare
        self.styles.add(ParagraphStyle(
            name='QuestionTitle',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        ))
        
        # Text întrebare
        self.styles.add(ParagraphStyle(
            name='QuestionText',
            parent=self.styles['BodyText'],
            fontSize=11,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leading=14
        ))
        
        # Răspuns
        self.styles.add(ParagraphStyle(
            name='AnswerText',
            parent=self.styles['BodyText'],
            fontSize=10,
            textColor=colors.HexColor('#006600'),
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leading=13
        ))
        
        # Metadata
        self.styles.add(ParagraphStyle(
            name='Metadata',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            spaceAfter=6
        ))
    
    def generate_test_pdf(self, 
                         questions: List[Any],
                         filename: str,
                         include_answers: bool = False) -> str:
        """
        Generează PDF pentru test
        
        Args:
            questions: Listă de Question objects
            filename: Nume fișier de ieșire
            include_answers: Include răspunsurile corecte
        
        Returns:
            Path la fișierul generat
        """
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Header
        story.append(Paragraph(self.remove_diacritics("SMARTEST"), self.styles['CustomTitle']))
        story.append(Paragraph(self.remove_diacritics("Test Inteligenta Artificiala"), self.styles['CustomSubtitle']))
        
        # Metadata
        metadata_text = f"Generat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>"
        metadata_text += f"Numar intrebari: {len(questions)}"
        if include_answers:
            metadata_text += "<br/><b>Include raspunsuri corecte (BAREM)</b>"
        
        story.append(Paragraph(self.remove_diacritics(metadata_text), self.styles['Metadata']))
        story.append(Spacer(1, 0.5*cm))
        
        # Linie separator
        story.append(self._create_separator())
        story.append(Spacer(1, 0.5*cm))
        
        # Întrebări
        for i, question in enumerate(questions, 1):
            # Titlu întrebare
            question_header = f"INTREBAREA {i}"
            if hasattr(question, 'difficulty'):
                difficulty_ro = {
                    'easy': 'Usoara',
                    'medium': 'Medie',
                    'hard': 'Dificila'
                }.get(question.difficulty, question.difficulty)
                question_header += f" (Dificultate: {difficulty_ro})"
            
            story.append(Paragraph(self.remove_diacritics(question_header), self.styles['QuestionTitle']))
            
            # Informații problemă
            if hasattr(question, 'problem_type'):
                problem_name = self._get_problem_name(question.problem_type)
                story.append(Paragraph(self.remove_diacritics(f"<b>Problema:</b> {problem_name}"), self.styles['Metadata']))
            
            # Text întrebare
            question_text = self._format_text_for_pdf(question.text)
            story.append(Paragraph(self.remove_diacritics(question_text), self.styles['QuestionText']))
            
            # Spațiu pentru răspuns
            if not include_answers:
                story.append(Spacer(1, 0.3*cm))
                story.append(Paragraph(self.remove_diacritics("<i>Raspuns:</i>"), self.styles['Metadata']))
                story.append(Spacer(1, 3*cm))  # Spațiu pentru scris
                story.append(self._create_thin_separator())
            else:
                # Include răspunsul corect
                story.append(Spacer(1, 0.3*cm))
                story.append(Paragraph(self.remove_diacritics("<b>RASPUNS CORECT:</b>"), self.styles['QuestionTitle']))
                
                # Strategie
                strategy_text = f"<b>Strategie:</b> {question.correct_strategy}"
                story.append(Paragraph(self.remove_diacritics(strategy_text), self.styles['AnswerText']))
                
                # Justificare
                story.append(Paragraph(self.remove_diacritics("<b>Justificare:</b>"), self.styles['Metadata']))
                reasoning_text = self._format_text_for_pdf(question.reasoning)
                story.append(Paragraph(self.remove_diacritics(reasoning_text), self.styles['AnswerText']))
                
                story.append(Spacer(1, 0.3*cm))
                story.append(self._create_thin_separator())
            
            story.append(Spacer(1, 0.5*cm))
            
            # Page break după fiecare 2 întrebări (dacă nu e ultima)
            if i % 2 == 0 and i < len(questions):
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        return filename
    
    def generate_evaluation_pdf(self,
                                evaluation: Dict[str, Any],
                                questions: List[Any],
                                filename: str) -> str:
        """
        Generează PDF cu rezultatele evaluării
        
        Args:
            evaluation: Dict cu rezultate evaluare
            questions: Listă întrebări
            filename: Nume fișier
        
        Returns:
            Path la fișier
        """
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Header
        story.append(Paragraph(self.remove_diacritics("SMARTEST"), self.styles['CustomTitle']))
        story.append(Paragraph(self.remove_diacritics("Rezultat Evaluare Test"), self.styles['CustomSubtitle']))
        
        # Metadata
        metadata_text = f"Evaluat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        story.append(Paragraph(self.remove_diacritics(metadata_text), self.styles['Metadata']))
        story.append(Spacer(1, 0.5*cm))
        
        # Scor total - tabel
        total_score = evaluation['total_score']
        max_score = evaluation['max_score']
        average = evaluation['average_score']
        
        score_data = [
            [self.remove_diacritics('Metrica'), self.remove_diacritics('Valoare')],
            [self.remove_diacritics('Punctaj Total'), f"{total_score:.0f}/{max_score}"],
            [self.remove_diacritics('Medie pe Intrebare'), f"{average:.2f}/100"],
            [self.remove_diacritics('Numar Intrebari'), str(evaluation['num_questions'])]
        ]
        
        score_table = Table(score_data, colWidths=[8*cm, 8*cm])
        score_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        
        story.append(score_table)
        story.append(Spacer(1, 1*cm))
        story.append(self._create_separator())
        story.append(Spacer(1, 0.5*cm))
        
        # Detalii pe întrebare
        story.append(Paragraph(self.remove_diacritics("Detalii pe Intrebare"), self.styles['CustomSubtitle']))
        story.append(Spacer(1, 0.3*cm))
        
        for i, (result, question) in enumerate(zip(evaluation['results'], questions), 1):
            # Header întrebare
            score = result['score']
            status = "CORECT" if score >= 60 else "INCORECT"
            color = colors.HexColor('#006600') if score >= 60 else colors.HexColor('#cc0000')
            
            question_title = f"Intrebarea {i}: {score}/100 - <font color='{color.hexval()}'>{status}</font>"
            story.append(Paragraph(self.remove_diacritics(question_title), self.styles['QuestionTitle']))
            
            # Breakdown
            breakdown_text = f"<b>Strategie:</b> {result['strategy_score']}/100 "
            breakdown_text += f"({'Corecta' if result['strategy_correct'] else 'Incorecta'})<br/>"
            breakdown_text += f"<b>Justificare:</b> {result['reasoning_score']}/100"
            story.append(Paragraph(self.remove_diacritics(breakdown_text), self.styles['QuestionText']))
            
            # Feedback (primele 300 caractere)
            feedback = result['feedback'].replace('\n', '<br/>')
            if len(feedback) > 500:
                feedback = feedback[:500] + "..."
            story.append(Paragraph(self.remove_diacritics(f"<i>{feedback}</i>"), self.styles['Metadata']))
            
            story.append(Spacer(1, 0.5*cm))
            story.append(self._create_thin_separator())
            story.append(Spacer(1, 0.3*cm))
            
            # Page break la fiecare 3 întrebări
            if i % 3 == 0 and i < len(questions):
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        return filename
    
    def _create_separator(self):
        """Creează o linie separator groasă"""
        return Table([['']], colWidths=[16*cm], rowHeights=[0.1*cm],
                    style=[('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#0066cc'))])
    
    def _create_thin_separator(self):
        """Creează o linie separator subțire"""
        return Table([['']], colWidths=[16*cm], rowHeights=[0.05*cm],
                    style=[('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#cccccc'))])
    
    def _format_text_for_pdf(self, text: str) -> str:
        """Formatează text pentru PDF (escape HTML, păstrează formatare)"""
        # Replace newlines cu <br/>
        text = text.replace('\n', '<br/>')
        
        # Escape some problematic characters
        text = text.replace('&', '&amp;')
        text = text.replace('<br/>', '<br/>').replace('<BR/>', '<br/>')
        
        return text
    
    def _get_problem_name(self, problem_type: str) -> str:
        """Returnează numele complet al problemei"""
        names = {
            'n-queens': 'N-Queens',
            'hanoi': 'Turnurile din Hanoi',
            'graph_coloring': 'Colorarea Grafurilor',
            'knights_tour': 'Tura Calului'
        }
        return names.get(problem_type, problem_type)


if __name__ == "__main__":
    # Test PDF generator
    print("=== TEST PDF GENERATOR ===\n")
    
    from question_generator import HybridQuestionGenerator
    
    # Generate sample questions
    generator = HybridQuestionGenerator()
    questions = generator.generate_test(num_questions=3)
    
    # Create PDF generator
    pdf_gen = PDFGenerator()
    
    # Test 1: Generate test PDF without answers
    print("1. Generare PDF test (fara raspunsuri)...")
    pdf_file1 = pdf_gen.generate_test_pdf(questions, "test_pdf_sample.pdf", include_answers=False)
    print(f"   Generat: {pdf_file1}")
    
    # Test 2: Generate test PDF with answers (barem)
    print("\n2. Generare PDF barem (cu raspunsuri)...")
    pdf_file2 = pdf_gen.generate_test_pdf(questions, "barem_pdf_sample.pdf", include_answers=True)
    print(f"   Generat: {pdf_file2}")
    
    print("\n=== PDF-uri generate cu succes! ===")
