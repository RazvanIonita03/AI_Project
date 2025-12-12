"""
PDF Generator pentru SmarTest
Generează PDF-uri pentru teste și răspunsuri
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import re
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
        
        # Monospace style for matrices and code
        self.styles.add(ParagraphStyle(
            name='MonospaceText',
            parent=self.styles['Normal'],
            fontSize=9,
            fontName='Courier',
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=8,
            spaceBefore=4,
            leading=11,
            alignment=TA_LEFT
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
            
            # Text întrebare - handle matrix specially for game theory
            question_text = question.text
            if hasattr(question, 'problem_type') and question.problem_type == 'game_theory':
                # Split text into parts: before matrix, matrix, after matrix
                story.extend(self._format_game_theory_question(question_text))
            else:
                formatted_text = self._format_text_for_pdf(question_text)
                story.append(Paragraph(self.remove_diacritics(formatted_text), self.styles['QuestionText']))
            
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
            
            # Tipul problemei
            problem_type = getattr(question, 'problem_type', 'unknown')
            problem_names = {
                'n-queens': 'N-Queens',
                'hanoi': 'Turnurile din Hanoi',
                'graph_coloring': 'Colorarea Grafurilor',
                'knights_tour': 'Turul Cavalerului',
                'game_theory': 'Teoria Jocurilor'
            }
            problem_name = problem_names.get(problem_type, problem_type)
            story.append(Paragraph(self.remove_diacritics(f"<b>Tip problema:</b> {problem_name}"), self.styles['QuestionText']))
            
            # Breakdown - tabel cu detalii
            breakdown_data = [
                [self.remove_diacritics('Componenta'), self.remove_diacritics('Punctaj'), self.remove_diacritics('Status')],
                [self.remove_diacritics('Strategie (40%)'), f"{result['strategy_score']}/100", 
                 self.remove_diacritics('Corecta' if result['strategy_correct'] else 'Incorecta')],
                [self.remove_diacritics('Justificare (60%)'), f"{result['reasoning_score']}/100", 
                 self.remove_diacritics(self._get_reasoning_status(result['reasoning_score']))],
            ]
            
            breakdown_table = Table(breakdown_data, colWidths=[6*cm, 4*cm, 6*cm])
            breakdown_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4a90d9')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (2, 1), (2, 1), colors.HexColor('#90EE90') if result['strategy_correct'] else colors.HexColor('#FFB6C1')),
                ('BACKGROUND', (2, 2), (2, 2), self._get_reasoning_color(result['reasoning_score'])),
            ]))
            story.append(breakdown_table)
            story.append(Spacer(1, 0.3*cm))
            
            # Răspunsul utilizatorului
            story.append(Paragraph(self.remove_diacritics("<b>Raspunsul tau:</b>"), self.styles['QuestionText']))
            if 'user_answer' in result:
                user_answer = result.get('user_answer', 'N/A')
                story.append(Paragraph(self.remove_diacritics(f"<i>{user_answer[:300]}{'...' if len(user_answer) > 300 else ''}</i>"), self.styles['Metadata']))
            
            # Răspunsul corect
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph(self.remove_diacritics("<b>Raspuns corect:</b>"), self.styles['QuestionText']))
            correct_strategy = result.get('correct_strategy', getattr(question, 'correct_answer', 'N/A'))
            story.append(Paragraph(self.remove_diacritics(f"<b>Strategie:</b> {correct_strategy}"), self.styles['Metadata']))
            
            correct_reasoning = result.get('correct_reasoning', getattr(question, 'correct_reasoning', ''))
            if correct_reasoning:
                reasoning_clean = correct_reasoning.replace('\n', ' ')[:400]
                if len(correct_reasoning) > 400:
                    reasoning_clean += "..."
                story.append(Paragraph(self.remove_diacritics(f"<b>Justificare model:</b> {reasoning_clean}"), self.styles['Metadata']))
            
            # Feedback detaliat din evaluare
            story.append(Spacer(1, 0.3*cm))
            story.append(Paragraph(self.remove_diacritics("<b>Feedback evaluare:</b>"), self.styles['QuestionText']))
            
            reasoning_details = result.get('reasoning_details', '')
            if reasoning_details:
                # Formatare detalii evaluare
                details_lines = reasoning_details.split('\n')
                for line in details_lines[:10]:  # Primele 10 linii
                    if line.strip():
                        line_clean = line.replace('<', '&lt;').replace('>', '&gt;')
                        story.append(Paragraph(self.remove_diacritics(line_clean), self.styles['Metadata']))
            
            story.append(Spacer(1, 0.5*cm))
            story.append(self._create_thin_separator())
            story.append(Spacer(1, 0.5*cm))
            
            # Page break la fiecare 2 întrebări pentru mai mult spațiu
            if i % 2 == 0 and i < len(questions):
                story.append(PageBreak())
        
        # Build PDF
        doc.build(story)
        return filename
    
    def _get_reasoning_status(self, score: int) -> str:
        """Returnează statusul pentru scorul de justificare"""
        if score >= 90:
            return "Excelent"
        elif score >= 70:
            return "Bun"
        elif score >= 50:
            return "Acceptabil"
        else:
            return "Insuficient"
    
    def _get_reasoning_color(self, score: int):
        """Returnează culoarea pentru scorul de justificare"""
        if score >= 90:
            return colors.HexColor('#90EE90')  # Light green
        elif score >= 70:
            return colors.HexColor('#FFFFE0')  # Light yellow
        elif score >= 50:
            return colors.HexColor('#FFE4B5')  # Light orange
        else:
            return colors.HexColor('#FFB6C1')  # Light red
    
    def _create_separator(self):
        """Creează o linie separator groasă"""
        return Table([['']], colWidths=[16*cm], rowHeights=[0.1*cm],
                    style=[('LINEABOVE', (0, 0), (-1, 0), 2, colors.HexColor('#0066cc'))])
    
    def _create_thin_separator(self):
        """Creează o linie separator subțire"""
        return Table([['']], colWidths=[16*cm], rowHeights=[0.05*cm],
                    style=[('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.HexColor('#cccccc'))])
    
    def _format_game_theory_question(self, text: str) -> List:
        """
        Special formatting for game theory questions with matrix.
        Renders the matrix as a proper PDF table for correct alignment.
        
        Handles multiple formats:
        1. "Considerați următorul joc în formă normală (matriceală):" ... matrix ... "Întrebări:"
        2. "Matricea de plăți:" ... matrix ... " poate fi rezolvată"
        """
        elements = []
        
        # Try to find matrix by looking for "Jucător 2 (Coloane)" or the payoff pattern
        # Matrix lines contain patterns like "( 5,-5)" or "(-1, 2)"
        
        lines = text.split('\n')
        matrix_start_idx = None
        matrix_end_idx = None
        
        # Find matrix boundaries
        for i, line in enumerate(lines):
            # Matrix starts with "Jucător 2" header or column headers
            if 'Juc' in line and '2' in line and ('Coloane' in line or 'Col' in line):
                matrix_start_idx = i
            # Or starts with column strategy names line (before payoffs)
            elif matrix_start_idx is None and re.search(r'^\s+\w+\s+\w+\s*$', line) and i < len(lines) - 1:
                # Check if next line has separator or payoffs
                next_line = lines[i + 1] if i + 1 < len(lines) else ""
                if '---' in next_line or '(' in next_line:
                    matrix_start_idx = i
            
            # Matrix ends after last row with payoffs
            if matrix_start_idx is not None and '(' in line and ')' in line:
                matrix_end_idx = i
        
        # If no matrix found, try alternative approach
        if matrix_start_idx is None:
            # Look for "Matricea de plăți:" marker
            for i, line in enumerate(lines):
                if 'Matrice' in line and 'pl' in line.lower():
                    matrix_start_idx = i + 1  # Matrix starts after this line
                    break
        
        if matrix_start_idx is not None and matrix_end_idx is not None:
            # Extract parts
            before_lines = lines[:matrix_start_idx]
            matrix_lines = lines[matrix_start_idx:matrix_end_idx + 1]
            after_lines = lines[matrix_end_idx + 1:]
            
            before_text = '\n'.join(before_lines).strip()
            matrix_text = '\n'.join(matrix_lines)
            after_text = '\n'.join(after_lines).strip()
            
            # Add text before matrix
            if before_text:
                formatted_before = self._format_text_for_pdf(before_text)
                elements.append(Paragraph(self.remove_diacritics(formatted_before), self.styles['QuestionText']))
            
            elements.append(Spacer(1, 0.3*cm))
            
            # Create matrix table from ASCII representation
            matrix_table = self._create_matrix_table_from_ascii(matrix_text)
            if matrix_table:
                elements.append(matrix_table)
            else:
                # Fallback: use preformatted text
                matrix_clean = self.remove_diacritics(matrix_text)
                elements.append(Preformatted(matrix_clean, self.styles['MonospaceText']))
            
            elements.append(Spacer(1, 0.3*cm))
            
            # Add text after matrix
            if after_text:
                formatted_after = self._format_text_for_pdf(after_text)
                elements.append(Paragraph(self.remove_diacritics(formatted_after), self.styles['QuestionText']))
        else:
            # Fallback: render entire text normally
            formatted_text = self._format_text_for_pdf(text)
            elements.append(Paragraph(self.remove_diacritics(formatted_text), self.styles['QuestionText']))
        
        return elements
    
    def _create_matrix_table_from_ascii(self, ascii_matrix: str) -> Table:
        """
        Parsează matricea ASCII și creează un tabel PDF frumos formatat.
        """
        lines = ascii_matrix.strip().split('\n')
        
        if len(lines) < 3:
            return None
        
        # Parse the matrix structure
        # Expected format:
        # Line 0: "                            Jucător 2 (Coloane)"
        # Line 1: "             C1      C2" (column headers)
        # Line 2: " ----------------" (separator)
        # Line 3+: "Jucător 1  R1 |  (x,y)  (x,y)" (data rows)
        
        try:
            table_data = []
            col_strategies = []
            row_strategies = []
            payoff_rows = []
            
            # Find column headers line (contains strategy names like C1, C2 or Cooperate, etc.)
            header_line_idx = None
            for i, line in enumerate(lines):
                # Skip "Jucător 2" title line and separator
                if 'Juc' in line and '2' in line and 'Coloane' in line:
                    continue
                if '---' in line:
                    continue
                # Look for column headers (line with strategy names but no payoffs)
                if '(' not in line and line.strip() and not line.strip().startswith('Juc'):
                    # This is likely the header row
                    parts = line.split()
                    col_strategies = [self.remove_diacritics(p) for p in parts if p.strip()]
                    header_line_idx = i
                    break
            
            # Parse data rows (lines with payoffs in parentheses)
            for line in lines:
                if '(' in line and ')' in line:
                    # Extract row label
                    row_label = ""
                    if '|' in line:
                        label_part = line.split('|')[0]
                        # Get the last word before | which is the strategy name
                        label_words = label_part.split()
                        if label_words:
                            row_label = label_words[-1]
                    
                    # Extract payoffs
                    payoffs = re.findall(r'\(\s*-?\d+\s*,\s*-?\d+\s*\)', line)
                    
                    if payoffs:
                        row_strategies.append(self.remove_diacritics(row_label))
                        payoff_rows.append([self.remove_diacritics(p) for p in payoffs])
            
            if not payoff_rows or not col_strategies:
                return None
            
            # Build table data
            # First row: empty corner + column headers
            header_row = [''] + col_strategies
            table_data.append(header_row)
            
            # Data rows: row label + payoffs
            for i, (row_label, payoffs) in enumerate(zip(row_strategies, payoff_rows)):
                row = [row_label] + payoffs
                table_data.append(row)
            
            # Calculate column widths
            num_cols = len(header_row)
            col_width = 2.5 * cm
            first_col_width = 2 * cm
            col_widths = [first_col_width] + [col_width] * (num_cols - 1)
            
            # Create table
            table = Table(table_data, colWidths=col_widths)
            
            # Style the table
            style = TableStyle([
                # Header row styling
                ('BACKGROUND', (1, 0), (-1, 0), colors.HexColor('#e6f2ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0066cc')),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                
                # First column styling (row labels)
                ('BACKGROUND', (0, 1), (0, -1), colors.HexColor('#e6f2ff')),
                ('TEXTCOLOR', (0, 1), (0, -1), colors.HexColor('#0066cc')),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                
                # Data cells
                ('FONTNAME', (1, 1), (-1, -1), 'Courier'),
                ('FONTSIZE', (1, 1), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # Grid
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#0066cc')),
                
                # Padding
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ])
            
            table.setStyle(style)
            return table
            
        except Exception as e:
            # If parsing fails, return None to use fallback
            print(f"Matrix parsing error: {e}")
            return None
    
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
            'knights_tour': 'Turul Cavalerului',
            'game_theory': 'Teoria Jocurilor'
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
