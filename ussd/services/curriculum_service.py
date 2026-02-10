"""
Curriculum alignment service for BrilliantAfrica.
Maps questions to curriculum standards: WAEC, NECO, KCSE, Ethiopian, Cambridge.
"""

import logging
from typing import List, Dict, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class CurriculumStandard(Enum):
    """Supported curriculum standards"""
    WAEC = "waec"  # West African Examination Council
    NECO = "neco"  # National Examination Council (Nigeria)
    KCSE = "kcse"  # Kenya Certificate of Secondary Education
    ETHIOPIAN = "ethiopian"
    CAMBRIDGE = "cambridge"
    CUSTOM = "custom"


class Subject(Enum):
    """Common subjects across African curricula"""
    MATHEMATICS = "mathematics"
    ENGLISH = "english"
    BIOLOGY = "biology"
    CHEMISTRY = "chemistry"
    PHYSICS = "physics"
    HISTORY = "history"
    GEOGRAPHY = "geography"
    ECONOMICS = "economics"
    ACCOUNTING = "accounting"
    COMPUTER_SCIENCE = "computer_science"
    LITERATURE = "literature"
    CIVIC_EDUCATION = "civic_education"


# WAEC - West African Examination Council (Ghana, Nigeria, Liberia, Sierra Leone, Gambia)
WAEC_SUBJECTS = {
    "mathematics": {
        "codes": ["WAEC_MATH", "WAEC_MAT"],
        "topics": [
            "Number systems", "Indices and logarithms", "Surds", "Polynomials",
            "Quadratic equations", "Linear equations", "Sequences and series",
            "Trigonometry", "Calculus", "Vectors", "Statistics", "Probability",
            "Geometry", "Matrices"
        ],
        "exam_boards": ["WAEC"]
    },
    "english": {
        "codes": ["WAEC_ENG"],
        "topics": [
            "Grammar", "Comprehension", "Essay writing", "Creative writing",
            "Poetry analysis", "Prose analysis", "Drama analysis", "Vocabulary",
            "Oral English"
        ],
        "exam_boards": ["WAEC"]
    },
    "biology": {
        "codes": ["WAEC_BIO"],
        "topics": [
            "Cell structure", "Cell division", "Photosynthesis", "Respiration",
            "Enzymes", "Nutrition", "Digestion", "Transport", "Excretion",
            "Reproduction", "Genetics", "Evolution", "Ecology", "Public health"
        ],
        "exam_boards": ["WAEC"]
    },
    "chemistry": {
        "codes": ["WAEC_CHEM"],
        "topics": [
            "Atomic structure", "Bonding", "States of matter", "Chemical kinetics",
            "Equilibrium", "Acid-base chemistry", "Redox reactions", "Electrochemistry",
            "Organic chemistry", "Inorganic chemistry", "Thermochemistry"
        ],
        "exam_boards": ["WAEC"]
    }
}

# NECO - National Examination Council (Nigeria)
NECO_SUBJECTS = {
    "mathematics": {
        "codes": ["NECO_MATH"],
        "topics": WAEC_SUBJECTS["mathematics"]["topics"],  # Similar to WAEC
        "exam_boards": ["NECO"]
    },
    "english": {
        "codes": ["NECO_ENG"],
        "topics": WAEC_SUBJECTS["english"]["topics"],
        "exam_boards": ["NECO"]
    }
}

# KCSE - Kenya Certificate of Secondary Education
KCSE_SUBJECTS = {
    "mathematics": {
        "codes": ["KCSE_MATH", "KCSE_MAT"],
        "topics": [
            "Number patterns", "Algebra", "Logarithms", "Trigonometry",
            "Geometry", "Matrices", "Vectors", "Statistics", "Probability",
            "Calculus", "Financial mathematics"
        ],
        "exam_boards": ["KNEC"]
    },
    "english": {
        "codes": ["KCSE_ENG"],
        "topics": [
            "Reading comprehension", "Written expression", "Grammar",
            "Literature in English", "Oral skills", "Listening skills"
        ],
        "exam_boards": ["KNEC"]
    },
    "biology": {
        "codes": ["KCSE_BIO"],
        "topics": [
            "Cell structure and organisation", "Transport across membranes",
            "Photosynthesis and respiration", "Nutrition", "Digestion and absorption",
            "Excretion", "Coordination and response", "Reproduction",
            "Inheritance", "Ecology", "Population and community", "Parasites",
            "Immune system"
        ],
        "exam_boards": ["KNEC"]
    }
}

# Ethiopian Curriculum
ETHIOPIAN_SUBJECTS = {
    "mathematics": {
        "codes": ["ETH_MATH"],
        "topics": [
            "Number theory", "Algebra", "Geometry", "Trigonometry",
            "Calculus", "Statistics", "Probability", "Linear programming"
        ],
        "exam_boards": ["Ethiopian Ministry of Education"]
    },
    "english": {
        "codes": ["ETH_ENG"],
        "topics": [
            "Communication skills", "Reading comprehension", "Writing skills",
            "Grammar", "Vocabulary development"
        ],
        "exam_boards": ["Ethiopian Ministry of Education"]
    }
}

# Cambridge International Examinations (A Level, IGCSE)
CAMBRIDGE_SUBJECTS = {
    "mathematics": {
        "codes": ["CAMBRIDGE_O", "CAMBRIDGE_A", "CAMBRIDGE_IGCSE_MATH"],
        "topics": [
            "Functions", "Trigonometry", "Vectors", "Complex numbers",
            "Differential calculus", "Integral calculus", "Algebra",
            "Coordinate geometry", "Series", "Matrices"
        ],
        "exam_boards": ["Cambridge International Examinations"]
    },
    "physics": {
        "codes": ["CAMBRIDGE_IGCSE_PHY", "CAMBRIDGE_A_PHY"],
        "topics": [
            "Motion", "Forces", "Energy", "Waves", "Electricity",
            "Magnetism", "Atomic and nuclear physics", "Thermodynamics"
        ],
        "exam_boards": ["Cambridge International Examinations"]
    }
}

# Curriculum mappings
CURRICULUM_DATA = {
    CurriculumStandard.WAEC: WAEC_SUBJECTS,
    CurriculumStandard.NECO: NECO_SUBJECTS,
    CurriculumStandard.KCSE: KCSE_SUBJECTS,
    CurriculumStandard.ETHIOPIAN: ETHIOPIAN_SUBJECTS,
    CurriculumStandard.CAMBRIDGE: CAMBRIDGE_SUBJECTS,
}


class CurriculumService:
    """Service for curriculum alignment and topic mapping"""
    
    @staticmethod
    def get_subject_topics(curriculum: str, subject: str) -> Optional[List[str]]:
        """Get all topics for a subject in a specific curriculum"""
        try:
            curriculum_enum = CurriculumStandard(curriculum.lower())
            curriculum_data = CURRICULUM_DATA.get(curriculum_enum, {})
            subject_data = curriculum_data.get(subject.lower(), {})
            return subject_data.get("topics", [])
        except (ValueError, KeyError):
            logger.warning(f"Curriculum {curriculum} or subject {subject} not found")
            return None
    
    @staticmethod
    def get_available_subjects(curriculum: str) -> List[str]:
        """Get all available subjects for a curriculum"""
        try:
            curriculum_enum = CurriculumStandard(curriculum.lower())
            curriculum_data = CURRICULUM_DATA.get(curriculum_enum, {})
            return list(curriculum_data.keys())
        except ValueError:
            return []
    
    @staticmethod
    def get_all_curricula() -> Dict[str, str]:
        """Get all supported curricula"""
        return {
            "waec": "WAEC (West Africa)",
            "neco": "NECO (Nigeria)",
            "kcse": "KCSE (Kenya)",
            "ethiopian": "Ethiopian Curriculum",
            "cambridge": "Cambridge International",
        }
    
    @staticmethod
    def map_question_to_curriculum(question_text: str, curriculum: str, 
                                   subject: str) -> Dict[str, any]:
        """
        Analyze a question and map it to curriculum standards.
        Returns metadata about the question's curriculum alignment.
        """
        topics = CurriculumService.get_subject_topics(curriculum, subject)
        
        if not topics:
            return {"error": "Curriculum/subject not found"}
        
        # Simple keyword matching (in production, use NLP/ML)
        matching_topics = []
        question_lower = question_text.lower()
        
        for topic in topics:
            if any(keyword in question_lower for keyword in topic.lower().split()):
                matching_topics.append(topic)
        
        return {
            "curriculum": curriculum,
            "subject": subject,
            "matching_topics": matching_topics,
            "aligned": len(matching_topics) > 0,
            "difficulty_level": CurriculumService._estimate_difficulty(
                question_text, curriculum, subject
            )
        }
    
    @staticmethod
    def _estimate_difficulty(question_text: str, curriculum: str, 
                            subject: str) -> int:
        """Estimate difficulty level (1-5) based on question characteristics"""
        # Simple heuristic (in production, use ML model)
        difficulty = 1
        
        # Check for advanced keywords
        advanced_keywords = [
            "derive", "prove", "analyze", "complex", "advanced",
            "integrate", "differentiate", "theorem", "hypothesis"
        ]
        
        question_lower = question_text.lower()
        for keyword in advanced_keywords:
            if keyword in question_lower:
                difficulty = min(5, difficulty + 1)
        
        return difficulty
    
    @staticmethod
    def get_study_path(curriculum: str, subject: str, 
                       grade_level: int) -> Dict[str, any]:
        """
        Get recommended study path based on curriculum and grade.
        Returns suggested topics in order of difficulty.
        """
        topics = CurriculumService.get_subject_topics(curriculum, subject)
        
        if not topics:
            return {"error": "Subject not found"}
        
        # In production, this would use proper curriculum sequencing
        return {
            "curriculum": curriculum,
            "subject": subject,
            "grade_level": grade_level,
            "recommended_topics": topics[:5],  # First 5 topics
            "total_topics": len(topics),
            "estimated_hours": len(topics) * 2,  # 2 hours per topic estimate
        }
    
    @staticmethod
    def get_curriculum_info(curriculum: str) -> Dict[str, any]:
        """Get detailed information about a curriculum"""
        info = {
            "waec": {
                "name": "West African Examination Council",
                "countries": ["Ghana", "Nigeria", "Liberia", "Sierra Leone", "Gambia"],
                "grade_levels": ["Junior WAEC (JSS3)", "Senior WAEC (SSIII)"],
                "subjects_count": len(WAEC_SUBJECTS),
                "description": "Common examination board for West African countries"
            },
            "neco": {
                "name": "National Examination Council",
                "countries": ["Nigeria"],
                "grade_levels": ["Junior NECO (JSS3)", "Senior NECO (SSIII)"],
                "subjects_count": len(NECO_SUBJECTS),
                "description": "Nigeria's national examination body"
            },
            "kcse": {
                "name": "Kenya Certificate of Secondary Education",
                "countries": ["Kenya"],
                "grade_levels": ["Form 1-4"],
                "subjects_count": len(KCSE_SUBJECTS),
                "description": "Kenya's secondary school examination"
            },
            "ethiopian": {
                "name": "Ethiopian National Curriculum",
                "countries": ["Ethiopia"],
                "grade_levels": ["Grade 9-12"],
                "subjects_count": len(ETHIOPIAN_SUBJECTS),
                "description": "Ethiopia's national education curriculum"
            },
            "cambridge": {
                "name": "Cambridge International Examinations",
                "countries": ["Multiple (International)"],
                "grade_levels": ["IGCSE (Grade 10-11)", "A Level (Grade 12-13)"],
                "subjects_count": len(CAMBRIDGE_SUBJECTS),
                "description": "International examination board"
            }
        }
        
        return info.get(curriculum.lower(), {"error": "Curriculum not found"})


class QuestionAnalyzer:
    """Analyze and tag questions with curriculum metadata"""
    
    @staticmethod
    def analyze_question(question_text: str, student_curriculum: str, 
                        student_subject: str) -> Dict[str, any]:
        """
        Comprehensive question analysis for curriculum alignment.
        """
        curriculum_mapping = CurriculumService.map_question_to_curriculum(
            question_text, student_curriculum, student_subject
        )
        
        if "error" in curriculum_mapping:
            # Fall back to generic analysis
            return {
                "question": question_text,
                "needs_curriculum_mapping": True,
                "suggested_subject": student_subject,
                "analysis_available": False
            }
        
        return {
            "question": question_text,
            "curriculum_alignment": curriculum_mapping,
            "difficulty": curriculum_mapping.get("difficulty_level", 1),
            "topics_covered": curriculum_mapping.get("matching_topics", []),
            "analysis_available": True,
            "study_resources_available": len(curriculum_mapping.get("matching_topics", [])) > 0
        }
    
    @staticmethod
    def get_related_topics(curriculum: str, subject: str, 
                          current_topic: str) -> List[str]:
        """Get related topics that should be studied together"""
        all_topics = CurriculumService.get_subject_topics(curriculum, subject)
        
        if not all_topics or current_topic not in all_topics:
            return []
        
        idx = all_topics.index(current_topic)
        related = []
        
        # Get previous topic (prerequisite)
        if idx > 0:
            related.append(all_topics[idx - 1])
        
        # Get next topic (progression)
        if idx < len(all_topics) - 1:
            related.append(all_topics[idx + 1])
        
        return related


# Quiz topic templates for each curriculum
QUIZ_TEMPLATES = {
    "waec": {
        "mathematics": {
            "number_systems": {
                "num_questions": 10,
                "time_limit": 900,  # 15 minutes
                "difficulty": 2,
                "passing_score": 70
            },
            "trigonometry": {
                "num_questions": 8,
                "time_limit": 900,
                "difficulty": 3,
                "passing_score": 70
            }
        },
        "english": {
            "comprehension": {
                "num_questions": 5,
                "time_limit": 600,  # 10 minutes
                "difficulty": 2,
                "passing_score": 70
            },
            "grammar": {
                "num_questions": 10,
                "time_limit": 600,
                "difficulty": 2,
                "passing_score": 70
            }
        }
    },
    "kcse": {
        "biology": {
            "photosynthesis": {
                "num_questions": 10,
                "time_limit": 1200,  # 20 minutes
                "difficulty": 2,
                "passing_score": 70
            }
        }
    }
}


def get_quiz_template(curriculum: str, subject: str, topic: str) -> Optional[Dict]:
    """Get quiz template for a curriculum/subject/topic combination"""
    return QUIZ_TEMPLATES.get(curriculum, {}).get(subject, {}).get(topic)
