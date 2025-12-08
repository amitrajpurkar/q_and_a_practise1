"""
Dependency injection setup for Q&A Practice Application.

Configures and registers all services in the DI container following SOLID principles.
"""

import logging
from pathlib import Path
from typing import Optional

from src.utils.container import DIContainer, get_container
from src.utils.config import AppConfig, get_app_config
from src.utils.logging_config import setup_logging, get_logger
from src.models.question_bank import QuestionBank
from src.services.csv_parser import CSVParserService
from src.services.question_repository import QuestionRepository
from src.services.question_service import QuestionService, register_question_service
from src.services.session_service import SessionService
from src.services.score_service import ScoreService
from src.services.interfaces import (
    IQuestionRepository, IQuestionService, 
    ISessionService, IScoreService
)
from src.utils.exceptions import ConfigurationError


class DISetup:
    """
    Dependency injection setup manager.
    
    Follows Single Responsibility principle by handling
    only DI container configuration.
    """
    
    def __init__(self, config: AppConfig) -> None:
        """
        Initialize DI setup.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.logger = get_logger(__name__)
        self.container = get_container()
    
    def setup_dependencies(self) -> DIContainer:
        """
        Set up all dependencies in the container.
        
        Returns:
            Configured DI container
        """
        try:
            # Setup logging first
            setup_logging(self.config)
            
            # Register configuration
            self.container.register_instance(AppConfig, self.config)
            
            # Register logger
            self.container.register_instance(logging.Logger, self.logger)
            
            # Setup question bank
            question_bank = self._setup_question_bank()
            self.container.register_instance(QuestionBank, question_bank)
            
            # Setup CSV parser
            csv_parser = CSVParserService(self.logger)
            self.container.register_instance(CSVParserService, csv_parser)
            
            # Setup repositories
            self._setup_repositories(question_bank)
            
            # Setup services
            self._setup_services()
            
            self.logger.info("Dependency injection setup completed successfully")
            return self.container
            
        except Exception as e:
            self.logger.error(f"Failed to setup dependencies: {str(e)}")
            raise ConfigurationError(f"Failed to setup dependencies: {str(e)}")
    
    def _setup_question_bank(self) -> QuestionBank:
        """
        Setup question bank with sample data.
        
        Returns:
            Configured question bank
        """
        try:
            # For now, create a question bank with sample data
            # In a real application, this would load from CSV
            from src.models.question import Question
            
            sample_questions = [
                Question(
                    id="physics_1",
                    topic="Physics",
                    question_text="What is the speed of light in vacuum?",
                    option1="299,792,458 m/s",
                    option2="150,000,000 m/s",
                    option3="3,000,000 m/s",
                    option4="1,000,000 m/s",
                    correct_answer="299,792,458 m/s",
                    difficulty="Easy",
                    tag="Physics-Easy"
                ),
                Question(
                    id="physics_2",
                    topic="Physics",
                    question_text="What is Newton's second law of motion?",
                    option1="F = ma",
                    option2="E = mc²",
                    option3="V = IR",
                    option4="PV = nRT",
                    correct_answer="F = ma",
                    difficulty="Easy",
                    tag="Physics-Easy"
                ),
                Question(
                    id="physics_14",
                    topic="Physics",
                    question_text="What is the acceleration due to gravity on Earth?",
                    option1="9.8 m/s²",
                    option2="10 m/s²",
                    option3="8.5 m/s²",
                    option4="12 m/s²",
                    correct_answer="9.8 m/s²",
                    difficulty="Easy",
                    tag="Physics-Easy"
                ),
                Question(
                    id="physics_15",
                    topic="Physics",
                    question_text="What is the SI unit of energy?",
                    option1="Joule",
                    option2="Watt",
                    option3="Newton",
                    option4="Pascal",
                    correct_answer="Joule",
                    difficulty="Easy",
                    tag="Physics-Easy"
                ),
                Question(
                    id="physics_16",
                    topic="Physics",
                    question_text="What is the formula for momentum?",
                    option1="p = mv",
                    option2="p = ma",
                    option3="p = Fd",
                    option4="p = KE",
                    correct_answer="p = mv",
                    difficulty="Easy",
                    tag="Physics-Easy"
                ),
                Question(
                    id="physics_17",
                    topic="Physics",
                    question_text="What is the law of inertia?",
                    option1="Objects at rest stay at rest unless acted upon",
                    option2="Energy is conserved in all processes",
                    option3="Force equals mass times acceleration",
                    option4="For every action there is an equal reaction",
                    correct_answer="Objects at rest stay at rest unless acted upon",
                    difficulty="Easy",
                    tag="Physics-Easy"
                ),
                Question(
                    id="physics_3",
                    topic="Physics",
                    question_text="What is the unit of electric current?",
                    option1="Ampere",
                    option2="Volt",
                    option3="Ohm",
                    option4="Watt",
                    correct_answer="Ampere",
                    difficulty="Medium",
                    tag="Physics-Medium"
                ),
                Question(
                    id="physics_5",
                    topic="Physics",
                    question_text="What is the formula for kinetic energy?",
                    option1="KE = 1/2 mv²",
                    option2="KE = mgh",
                    option3="KE = Fd",
                    option4="KE = Pt",
                    correct_answer="KE = 1/2 mv²",
                    difficulty="Medium",
                    tag="Physics-Medium"
                ),
                Question(
                    id="physics_6",
                    topic="Physics",
                    question_text="What is the SI unit of force?",
                    option1="Newton",
                    option2="Joule",
                    option3="Watt",
                    option4="Pascal",
                    correct_answer="Newton",
                    difficulty="Medium",
                    tag="Physics-Medium"
                ),
                Question(
                    id="physics_7",
                    topic="Physics",
                    question_text="What is the law of conservation of energy?",
                    option1="Energy cannot be created or destroyed",
                    option2="Energy flows from hot to cold",
                    option3="Energy is proportional to mass",
                    option4="Energy is always conserved in motion",
                    correct_answer="Energy cannot be created or destroyed",
                    difficulty="Medium",
                    tag="Physics-Medium"
                ),
                Question(
                    id="physics_8",
                    topic="Physics",
                    question_text="What is the speed of sound in air at room temperature?",
                    option1="343 m/s",
                    option2="500 m/s",
                    option3="150 m/s",
                    option4="1000 m/s",
                    correct_answer="343 m/s",
                    difficulty="Medium",
                    tag="Physics-Medium"
                ),
                Question(
                    id="physics_9",
                    topic="Physics",
                    question_text="What is the gravitational constant G?",
                    option1="6.67 × 10^-11 N⋅m²/kg²",
                    option2="9.8 m/s²",
                    option3="3.0 × 10^8 m/s",
                    option4="1.6 × 10^-19 C",
                    correct_answer="6.67 × 10^-11 N⋅m²/kg²",
                    difficulty="Medium",
                    tag="Physics-Medium"
                ),
                Question(
                    id="physics_10",
                    topic="Physics",
                    question_text="What is the unit of magnetic flux?",
                    option1="Weber",
                    option2="Tesla",
                    option3="Henry",
                    option4="Farad",
                    correct_answer="Weber",
                    difficulty="Medium",
                    tag="Physics-Medium"
                ),
                Question(
                    id="physics_11",
                    topic="Physics",
                    question_text="What is the principle of superposition?",
                    option1="Net force is vector sum of individual forces",
                    option2="Energy is conserved in all interactions",
                    option3="Momentum is conserved in collisions",
                    option4="Angular momentum is conserved",
                    correct_answer="Net force is vector sum of individual forces",
                    difficulty="Medium",
                    tag="Physics-Medium"
                ),
                Question(
                    id="physics_12",
                    topic="Physics",
                    question_text="What is the relationship between wavelength and frequency?",
                    option1="c = λf",
                    option2="E = hf",
                    option3="p = mv",
                    option4="F = ma",
                    correct_answer="c = λf",
                    difficulty="Medium",
                    tag="Physics-Medium"
                ),
                Question(
                    id="physics_13",
                    topic="Physics",
                    question_text="What is the work-energy theorem?",
                    option1="Work done equals change in kinetic energy",
                    option2="Energy is conserved in all processes",
                    option3="Power is work divided by time",
                    option4="Momentum is conserved in collisions",
                    correct_answer="Work done equals change in kinetic energy",
                    difficulty="Medium",
                    tag="Physics-Medium"
                ),
                Question(
                    id="physics_4",
                    topic="Physics",
                    question_text="What is the Planck constant?",
                    option1="6.626 × 10^-34 J⋅s",
                    option2="1.602 × 10^-19 C",
                    option3="9.109 × 10^-31 kg",
                    option4="1.672 × 10^-27 kg",
                    correct_answer="6.626 × 10^-34 J⋅s",
                    difficulty="Hard",
                    tag="Physics-Hard"
                ),
                Question(
                    id="chemistry_1",
                    topic="Chemistry",
                    question_text="What is the chemical symbol for gold?",
                    option1="Au",
                    option2="Ag",
                    option3="Fe",
                    option4="Cu",
                    correct_answer="Au",
                    difficulty="Easy",
                    tag="Chemistry-Easy"
                ),
                Question(
                    id="chemistry_2",
                    topic="Chemistry",
                    question_text="What is the atomic number of carbon?",
                    option1="6",
                    option2="8",
                    option3="12",
                    option4="14",
                    correct_answer="6",
                    difficulty="Easy",
                    tag="Chemistry-Easy"
                ),
                Question(
                    id="chemistry_3",
                    topic="Chemistry",
                    question_text="What is the chemical formula for water?",
                    option1="H2O",
                    option2="CO2",
                    option3="O2",
                    option4="NaCl",
                    correct_answer="H2O",
                    difficulty="Easy",
                    tag="Chemistry-Easy"
                ),
                Question(
                    id="chemistry_4",
                    topic="Chemistry",
                    question_text="What is the molecular weight of glucose (C6H12O6)?",
                    option1="180.16 g/mol",
                    option2="150.13 g/mol",
                    option3="200.18 g/mol",
                    option4="120.10 g/mol",
                    correct_answer="180.16 g/mol",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="chemistry_5",
                    topic="Chemistry",
                    question_text="What is the equilibrium constant expression for the reaction: A + B ⇌ C + D?",
                    option1="K = [C][D]/[A][B]",
                    option2="K = [A][B]/[C][D]",
                    option3="K = [C]/[A]",
                    option4="K = [D]/[B]",
                    correct_answer="K = [C][D]/[A][B]",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="chemistry_6",
                    topic="Chemistry",
                    question_text="What is the Gibbs free energy equation?",
                    option1="ΔG = ΔH - TΔS",
                    option2="ΔG = ΔH + TΔS",
                    option3="ΔG = TΔS - ΔH",
                    option4="ΔG = ΔH × TΔS",
                    correct_answer="ΔG = ΔH - TΔS",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="chemistry_7",
                    topic="Chemistry",
                    question_text="What is the rate law for a second-order reaction?",
                    option1="rate = k[A]²",
                    option2="rate = k[A]",
                    option3="rate = k[A][B]",
                    option4="rate = k",
                    correct_answer="rate = k[A]²",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="chemistry_8",
                    topic="Chemistry",
                    question_text="What is the Henderson-Hasselbalch equation?",
                    option1="pH = pKa + log([A-]/[HA])",
                    option2="pH = pKa - log([A-]/[HA])",
                    option3="pH = pKa + log([HA]/[A-])",
                    option4="pH = pKa - log([HA]/[A-])",
                    correct_answer="pH = pKa + log([A-]/[HA])",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="chemistry_9",
                    topic="Chemistry",
                    question_text="What is the Nernst equation?",
                    option1="E = E° - (RT/nF)lnQ",
                    option2="E = E° + (RT/nF)lnQ",
                    option3="E = E° - (nF/RT)lnQ",
                    option4="E = E° + (nF/RT)lnQ",
                    correct_answer="E = E° - (RT/nF)lnQ",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="chemistry_10",
                    topic="Chemistry",
                    question_text="What is the relationship between Ka and Kb?",
                    option1="Ka × Kb = Kw",
                    option2="Ka + Kb = Kw",
                    option3="Ka / Kb = Kw",
                    option4="Ka - Kb = Kw",
                    correct_answer="Ka × Kb = Kw",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="chemistry_11",
                    topic="Chemistry",
                    question_text="What is the ideal gas law?",
                    option1="PV = nRT",
                    option2="P = nRT/V",
                    option3="V = nRT/P",
                    option4="T = PV/nR",
                    correct_answer="PV = nRT",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="chemistry_12",
                    topic="Chemistry",
                    question_text="What is the definition of entropy?",
                    option1="Measure of disorder in a system",
                    option2="Measure of energy in a system",
                    option3="Measure of temperature in a system",
                    option4="Measure of pressure in a system",
                    correct_answer="Measure of disorder in a system",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="chemistry_13",
                    topic="Chemistry",
                    question_text="What is the Arrhenius equation?",
                    option1="k = Ae^(-Ea/RT)",
                    option2="k = Ae^(Ea/RT)",
                    option3="k = A + e^(-Ea/RT)",
                    option4="k = A - e^(-Ea/RT)",
                    correct_answer="k = Ae^(-Ea/RT)",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="chemistry_14",
                    topic="Chemistry",
                    question_text="What is the definition of molarity?",
                    option1="Moles of solute per liter of solution",
                    option2="Grams of solute per liter of solution",
                    option3="Moles of solute per kilogram of solvent",
                    option4="Grams of solute per kilogram of solvent",
                    correct_answer="Moles of solute per liter of solution",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="chemistry_15",
                    topic="Chemistry",
                    question_text="What is the relationship between pH and pOH?",
                    option1="pH + pOH = 14",
                    option2="pH - pOH = 14",
                    option3="pH × pOH = 14",
                    option4="pH / pOH = 14",
                    correct_answer="pH + pOH = 14",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="chemistry_16",
                    topic="Chemistry",
                    question_text="What is the definition of enthalpy?",
                    option1="Heat content of a system at constant pressure",
                    option2="Heat content of a system at constant volume",
                    option3="Total energy of a system",
                    option4="Work done by a system",
                    correct_answer="Heat content of a system at constant pressure",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="chemistry_17",
                    topic="Chemistry",
                    question_text="What is the Clausius-Clapeyron equation used for?",
                    option1="Calculating vapor pressure at different temperatures",
                    option2="Calculating reaction rates",
                    option3="Calculating equilibrium constants",
                    option4="Calculating activation energy",
                    correct_answer="Calculating vapor pressure at different temperatures",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="chemistry_18",
                    topic="Chemistry",
                    question_text="What is the definition of a buffer solution?",
                    option1="Solution that resists pH changes upon addition of small amounts of acid or base",
                    option2="Solution with pH exactly 7",
                    option3="Solution with high ionic strength",
                    option4="Solution that conducts electricity well",
                    correct_answer="Solution that resists pH changes upon addition of small amounts of acid or base",
                    difficulty="Hard",
                    tag="Chemistry-Hard"
                ),
                Question(
                    id="math_1",
                    topic="Math",
                    question_text="What is the derivative of x²?",
                    option1="2x",
                    option2="x",
                    option3="x²",
                    option4="2",
                    correct_answer="2x",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_4",
                    topic="Math",
                    question_text="What is the integral of sin(x)?",
                    option1="-cos(x) + C",
                    option2="cos(x) + C",
                    option3="sin(x) + C",
                    option4="-sin(x) + C",
                    correct_answer="-cos(x) + C",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_5",
                    topic="Math",
                    question_text="What is the limit of sin(x)/x as x approaches 0?",
                    option1="1",
                    option2="0",
                    option3="∞",
                    option4="-1",
                    correct_answer="1",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_6",
                    topic="Math",
                    question_text="What is the derivative of e^x?",
                    option1="e^x",
                    option2="xe^x",
                    option3="e^(x-1)",
                    option4="ln(x)",
                    correct_answer="e^x",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_7",
                    topic="Math",
                    question_text="What is the second derivative of x³?",
                    option1="6x",
                    option2="3x²",
                    option3="6",
                    option4="x",
                    correct_answer="6x",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_8",
                    topic="Math",
                    question_text="What is the integral of 1/x?",
                    option1="ln|x| + C",
                    option2="log(x) + C",
                    option3="1/x² + C",
                    option4="x + C",
                    correct_answer="ln|x| + C",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_9",
                    topic="Math",
                    question_text="What is the derivative of ln(x)?",
                    option1="1/x",
                    option2="x",
                    option3="ln(x)",
                    option4="1/x²",
                    correct_answer="1/x",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_10",
                    topic="Math",
                    question_text="What is the limit of (1 + 1/n)^n as n approaches infinity?",
                    option1="e",
                    option2="1",
                    option3="∞",
                    option4="0",
                    correct_answer="e",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_11",
                    topic="Math",
                    question_text="What is the derivative of cos(x)?",
                    option1="-sin(x)",
                    option2="sin(x)",
                    option3="cos(x)",
                    option4="-cos(x)",
                    correct_answer="-sin(x)",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_12",
                    topic="Math",
                    question_text="What is the integral of x²?",
                    option1="x³/3 + C",
                    option2="x³ + C",
                    option3="2x + C",
                    option4="x² + C",
                    correct_answer="x³/3 + C",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_13",
                    topic="Math",
                    question_text="What is the derivative of tan(x)?",
                    option1="sec²(x)",
                    option2="cos²(x)",
                    option3="sin²(x)",
                    option4="tan²(x)",
                    correct_answer="sec²(x)",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_14",
                    topic="Math",
                    question_text="What is the limit of x² as x approaches 2?",
                    option1="4",
                    option2="2",
                    option3="∞",
                    option4="0",
                    correct_answer="4",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_15",
                    topic="Math",
                    question_text="What is the derivative of a constant?",
                    option1="0",
                    option2="1",
                    option3="The constant itself",
                    option4="Undefined",
                    correct_answer="0",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_16",
                    topic="Math",
                    question_text="What is the integral of e^x?",
                    option1="e^x + C",
                    option2="xe^x + C",
                    option3="e^(x+1) + C",
                    option4="ln(x) + C",
                    correct_answer="e^x + C",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_17",
                    topic="Math",
                    question_text="What is the derivative of x^n?",
                    option1="nx^(n-1)",
                    option2="x^(n+1)",
                    option3="n^x",
                    option4="x^n",
                    correct_answer="nx^(n-1)",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_18",
                    topic="Math",
                    question_text="What is the limit of sin(x)/x as x approaches π?",
                    option1="0",
                    option2="1",
                    option3="∞",
                    option4="-1",
                    correct_answer="0",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_19",
                    topic="Math",
                    question_text="What is the derivative of log(x) (base 10)?",
                    option1="1/(x ln(10))",
                    option2="1/x",
                    option3="ln(x)",
                    option4="log(x)",
                    correct_answer="1/(x ln(10))",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_20",
                    topic="Math",
                    question_text="What is the integral of 1/(1+x²)?",
                    option1="arctan(x) + C",
                    option2="ln(1+x²) + C",
                    option3="x/(1+x²) + C",
                    option4="1/x + C",
                    correct_answer="arctan(x) + C",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_21",
                    topic="Math",
                    question_text="What is the derivative of arcsin(x)?",
                    option1="1/√(1-x²)",
                    option2="√(1-x²)",
                    option3="1/(1+x²)",
                    option4="-1/√(1-x²)",
                    correct_answer="1/√(1-x²)",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_22",
                    topic="Math",
                    question_text="What is the limit of (sin(x) - x)/x³ as x approaches 0?",
                    option1="-1/6",
                    option2="1/6",
                    option3="0",
                    option4="∞",
                    correct_answer="-1/6",
                    difficulty="Medium",
                    tag="Math-Medium"
                ),
                Question(
                    id="math_2",
                    topic="Math",
                    question_text="What is the value of π (pi) to two decimal places?",
                    option1="3.14",
                    option2="3.41",
                    option3="2.71",
                    option4="1.61",
                    correct_answer="3.14",
                    difficulty="Easy",
                    tag="Math-Easy"
                ),
                Question(
                    id="math_3",
                    topic="Math",
                    question_text="What is the square root of 144?",
                    option1="12",
                    option2="14",
                    option3="10",
                    option4="16",
                    correct_answer="12",
                    difficulty="Easy",
                    tag="Math-Easy"
                )
            ]
            
            question_bank = QuestionBank.from_questions(sample_questions)
            self.logger.info(f"Created question bank with {len(question_bank)} questions")
            
            return question_bank
            
        except Exception as e:
            self.logger.error(f"Failed to setup question bank: {str(e)}")
            raise ConfigurationError(f"Failed to setup question bank: {str(e)}")
    
    def _setup_repositories(self, question_bank: QuestionBank) -> None:
        """
        Setup repository implementations.
        
        Args:
            question_bank: Question bank instance
        """
        try:
            # Question repository
            question_repository = QuestionRepository(question_bank, self.logger)
            self.container.register_instance(IQuestionRepository, question_repository)
            
            self.logger.info("Repositories setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup repositories: {str(e)}")
            raise ConfigurationError(f"Failed to setup repositories: {str(e)}")
    
    def _setup_services(self) -> None:
        """
        Setup service implementations.
        """
        try:
            # Get repository from container
            question_repository = self.container.resolve(IQuestionRepository)
            
            # Question service
            register_question_service(self.container, question_repository)
            
            # Get question service for other services
            question_service = self.container.resolve(IQuestionService)
            
            # Create session service first (without score service for now)
            session_service = SessionService(
                question_service=question_service,
                score_service=None,  # Will be set later
                logger=self.logger
            )
            self.container.register_instance(ISessionService, session_service)
            
            # Create score service
            score_service = ScoreService(
                session_service=session_service,
                question_service=question_service,
                logger=self.logger
            )
            self.container.register_instance(IScoreService, score_service)
            
            # Update session service with score service reference
            session_service.score_service = score_service
            
            self.logger.info("Services setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup services: {str(e)}")
            raise ConfigurationError(f"Failed to setup services: {str(e)}")


def setup_dependency_injection(config: Optional[AppConfig] = None) -> DIContainer:
    """
    Set up dependency injection for the application.
    
    Args:
        config: Optional application configuration
        
    Returns:
        Configured DI container
    """
    if config is None:
        config = get_app_config()
    
    di_setup = DISetup(config)
    return di_setup.setup_dependencies()


def get_configured_container() -> DIContainer:
    """
    Get the configured DI container.
    
    Returns:
        Configured DI container
        
    Raises:
        ConfigurationError: If container is not configured
    """
    container = get_container()
    
    # Check if container is configured by trying to resolve a key service
    try:
        container.resolve(IQuestionService)
        return container
    except ValueError:
        raise ConfigurationError("DI container not configured. Call setup_dependency_injection() first.")
