"""
Multi-language support service for BrilliantAfrica.
Supports: English, Swahili, Yoruba, Hausa, Amharic, French
"""

import json
import os
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Translation dictionaries for USSD/SMS responses
TRANSLATIONS = {
    'en': {
        'welcome': "Welcome to BrilliantAfrica! Your AI tutor is ready.",
        'main_menu': """Select an option:
1. Ask AI Tutor
2. My Progress
3. Take Quiz
4. Buy Subscription
5. Help
6. About""",
        'ask_question': "What would you like to learn about? Reply with your question.",
        'question_received': "Thank you! Processing your question...",
        'no_subscription': "This feature requires a subscription. Reply 4 to upgrade.",
        'subscription_menu': """Subscription Plans:
1. Basic - $5/month
2. Premium - $10/month
3. School - $20/month
4. Back""",
        'help': """Commands:
NEXT - See more
QUIZ - Take a quiz
GUIDE - Get study guide
EXPLAIN - Deeper explanation
PROGRESS - Your stats""",
        'quiz_start': "Quiz started! Answer correctly to pass.",
        'quiz_question': "Question {num}/{total}: {question}",
        'quiz_result': "Your score: {score}%. {result}",
        'progress_header': "Your Progress",
        'progress_stats': """Questions asked: {total_questions}
Quizzes taken: {quizzes_taken}
Quizzes passed: {quizzes_passed}
Overall grade: {grade}
Last active: {last_date}""",
        'error': "Sorry, something went wrong. Please try again.",
        'invalid_input': "Invalid input. Please select a valid option.",
    },
    
    'sw': {  # Swahili
        'welcome': "Karibu BrilliantAfrica! Mwalimu AI wako yupo tayari.",
        'main_menu': """Chagua chaguo:
1. Uliza AI
2. Maendeleo Yangu
3. Fanya Mtihani
4. Nunua Mraba wa Abiria
5. Msaada
6. Kuhusu""",
        'ask_question': "Ungependa kujifunza nini? Jibu kwa swali lako.",
        'question_received': "Asante! Tunachagua swali lako...",
        'no_subscription': "Hii huduma inahitaji kura. Jibu 4 kukamatia.",
        'subscription_menu': """Mipango ya Kura:
1. Msingi - $5/mwezi
2. Kuu - $10/mwezi
3. Shule - $20/mwezi
4. Nyuma""",
        'help': """Amri:
NEXT - Ona zaidi
QUIZ - Fanya mtihani
GUIDE - Pata mwongozo
EXPLAIN - Maelezo zaidi
PROGRESS - Takwimu zako""",
        'quiz_start': "Mtihani umeanzia! Jibu vizuri kupita.",
        'quiz_question': "Swali {num}/{total}: {question}",
        'quiz_result': "Alama yako: {score}%. {result}",
        'progress_header': "Maendeleo Yako",
        'progress_stats': """Maswali yaliyoibiwa: {total_questions}
Mitihani iliyochukuliwa: {quizzes_taken}
Mitihani iliyopita: {quizzes_passed}
Daraja lako: {grade}
Mwisho upo hai: {last_date}""",
        'error': "Pole, kitu kilichotokea. Jaribu tena.",
        'invalid_input': "Ingizo bathfu. Tafadhali chagua chaguo halali.",
    },
    
    'yo': {  # Yoruba
        'welcome': "Kaabo si BrilliantAfrica! A-filologu AI rẹ ti sete.",
        'main_menu': """Yan ookan:
1. Beere Alfabeti
2. Iwa-mi
3. Kiri Idaniloju
4. Ra Subscription
5. Iranlowo
6. Nipa""",
        'ask_question': "Kini ni awon nkan ti o fe loni? Dahun pelu ibeere rẹ.",
        'question_received': "E dupe! A nse ibeere rẹ...",
        'no_subscription': "Irinrin yi nilo subscription. Dahun 4 lati gbe.",
        'subscription_menu': """Awon ero idisita:
1. Alapu - $5/osù
2. Olokuku - $10/osù
3. Ile-eko - $20/osù
4. Pada""",
        'help': """Awon asin:
NEXT - Wo diẹ sii
QUIZ - Ṣe idaniloju
GUIDE - Gba itoju
EXPLAIN - Arosọrọ diẹ sii
PROGRESS - Awon nọmba rẹ""",
        'quiz_start': "Idaniloju ti bẹrẹ! Dahun tọ tọ lati pari.",
        'quiz_question': "Ibeere {num}/{total}: {question}",
        'quiz_result': "Alafo rẹ: {score}%. {result}",
        'progress_header': "Iwa-mi",
        'progress_stats': """Awon ibeere ti a beere: {total_questions}
Awon idaniloju ti a ṣe: {quizzes_taken}
Idaniloju ti kira: {quizzes_passed}
Laisi-ẹ: {grade}
Isale ti a ṣe: {last_date}""",
        'error': "Jẹ ki a ma lo. Jigbe lẹẹkansi.",
        'invalid_input': "Ẹri ibadandun. Jọ yan ookan ti o ye.",
    },
    
    'ha': {  # Hausa
        'welcome': "Sannu ga BrilliantAfrica! Malamai AI ka shi.",
        'main_menu': """Zaɓi:",
1. Tambaya Malamai
2. Ci gaba
3. Jaribawa
4. Saya Jiya
5. Taimako
6. Game""",
        'ask_question': "Me kina son koyo? Amsa da tambaya.",
        'question_received': "Na gode! Yana warware tambayarka...",
        'no_subscription': "Butun nan yana bukatarsu jiya. Amsa 4 don saita.",
        'subscription_menu': """Shirin jiya:
1. Kaura - $5/wata
2. Babbar - $10/wata
3. Makaranta - $20/wata
4. Koma""",
        'help': """Sanar:
NEXT - Ga gida
QUIZ - Yi jaribawa
GUIDE - Dawo shidi
EXPLAIN - Asali
PROGRESS - Ka lambobi""",
        'quiz_start': "Jaribawa ya fara! Amsa daidai don izini.",
        'quiz_question': "Tambaya {num}/{total}: {question}",
        'quiz_result': "Ka iya: {score}%. {result}",
        'progress_header': "Ci Gabanka",
        'progress_stats': """Tambayi da aka yi: {total_questions}
Jaraba da aka yi: {quizzes_taken}
Jaraba da aka yi nasara: {quizzes_passed}
Matakin ka: {grade}
Karshen lokacin: {last_date}""",
        'error': "Don allah, abu ya faru. Sake gwada.",
        'invalid_input': "Sakaci ba daidai. Jira zaɓi daidai.",
    },
    
    'am': {  # Amharic
        'welcome': "ወደ BrilliantAfrica እንኳን ደህና መጡ! የእርስዎ ሰው AI አስተዳደር ዘጋቢ ነው።",
        'main_menu': """ምርጫ ይምረጡ:
1. ሰውን መጠይቅ
2. እኔ ሁሉም
3. ፈተናን ይውሰዱ
4. ግዢ ግብዓት
5. እርዳታ
6. ስለ""",
        'ask_question': "ምን ማወቅ ይፈልጋሉ? ጥያቄዎ ይመልሱ።",
        'question_received': "ምስጋና! ጥያቄዎ በሂደት ላይ...",
        'no_subscription': "ይህ ሙሉ መጠን ያስፈልገዋል። 4 ወደ ግዢ።",
        'subscription_menu': """የግብዓት ታቦት:
1. መሰረታዊ - $5/ወር
2. ዋና - $10/ወር
3. ትምህርት ቤት - $20/ወር
4. ተመለስ""",
        'help': """ትዕዛዞች:
NEXT - ተጨማሪ ይመልከቱ
QUIZ - ፈተናን ይውሰዱ
GUIDE - ስርጭት ያግኙ
EXPLAIN - ተጨማሪ ማብራሪያ
PROGRESS - የእርስዎ ስታቲስቲክስ""",
        'quiz_start': "ፈተና ተጀምሯል! ለመጨረስ በትክክል ይመልሱ።",
        'quiz_question': "ጥያቄ {num}/{total}: {question}",
        'quiz_result': "ነጥብዎ: {score}%. {result}",
        'progress_header': "እርስዎ ሁሉም",
        'progress_stats': """ጥያቄዎች ለይተው: {total_questions}
ፈተናዎች ነውበ: {quizzes_taken}
ፈተናዎች አልፈ: {quizzes_passed}
አጠቃላይ ክፍል: {grade}
የመጨረሻ ጊዜ: {last_date}""",
        'error': "ይቅርታ፣ ስህተት ተከስቷል። እንደገና ይሞክሩ።",
        'invalid_input': "ልክ ያልሆነ ግብዓት። እባክዎ ትክክለኛ ምርጫ ይምረጡ።",
    },
    
    'fr': {  # French
        'welcome': "Bienvenue à BrilliantAfrica! Votre tuteur IA est prêt.",
        'main_menu': """Sélectionnez une option:
1. Poser une question
2. Ma progression
3. Passer un quiz
4. Acheter un abonnement
5. Aide
6. À propos""",
        'ask_question': "Que souhaitez-vous apprendre? Répondez avec votre question.",
        'question_received': "Merci! Traitement de votre question...",
        'no_subscription': "Cette fonction nécessite un abonnement. Répondez 4 pour mettre à jour.",
        'subscription_menu': """Plans d'abonnement:
1. Basique - $5/mois
2. Premium - $10/mois
3. Établissement - $20/mois
4. Retour""",
        'help': """Commandes:
NEXT - Voir plus
QUIZ - Passer un test
GUIDE - Obtenir un guide
EXPLAIN - Explication plus profonde
PROGRESS - Vos statistiques""",
        'quiz_start': "Quiz commencé! Répondez correctement pour réussir.",
        'quiz_question': "Question {num}/{total}: {question}",
        'quiz_result': "Votre note: {score}%. {result}",
        'progress_header': "Votre progression",
        'progress_stats': """Questions posées: {total_questions}
Quiz effectués: {quizzes_taken}
Quiz réussis: {quizzes_passed}
Note globale: {grade}
Dernière activité: {last_date}""",
        'error': "Désolé, quelque chose s'est mal passé. Réessayez.",
        'invalid_input': "Entrée invalide. Sélectionnez une option valide.",
    },
}


class LanguageService:
    """Service for handling multi-language translations"""
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'sw': 'Swahili',
        'yo': 'Yoruba',
        'ha': 'Hausa',
        'am': 'Amharic',
        'fr': 'French',
    }
    
    @staticmethod
    def get_translation(key: str, language: str = 'en', **kwargs) -> str:
        """
        Get translated text.
        Args:
            key: Translation key (e.g., 'welcome', 'main_menu')
            language: Language code (e.g., 'en', 'sw')
            **kwargs: Variables to format into the translation
        Returns:
            Translated text with variables substituted
        """
        try:
            if language not in TRANSLATIONS:
                language = 'en'  # Fallback to English
            
            text = TRANSLATIONS[language].get(key, TRANSLATIONS['en'].get(key, ''))
            
            # Format with provided variables
            if kwargs:
                text = text.format(**kwargs)
            
            return text
            
        except Exception as e:
            logger.error(f"Translation error for key '{key}': {str(e)}")
            return TRANSLATIONS['en'].get(key, 'Error retrieving message')
    
    @staticmethod
    def detect_language_preference(student) -> str:
        """
        Detect or return student's preferred language.
        If student has preference, use it. Otherwise, try to infer from phone number.
        """
        if hasattr(student, 'preferred_language') and student.preferred_language:
            return student.preferred_language
        
        # Try to infer from phone number
        phone = student.phone_number
        if phone.startswith('254'):  # Kenya
            return 'sw'  # Swahili
        elif phone.startswith('256'):  # Uganda
            return 'sw'
        elif phone.startswith('234'):  # Nigeria
            return 'yo'  # Yoruba
        elif phone.startswith('233'):  # Ghana
            return 'en'  # English more common
        elif phone.startswith('251'):  # Ethiopia
            return 'am'  # Amharic
        
        return 'en'  # Default to English
    
    @staticmethod
    def format_ussd_response(text: str, max_length: int = 160) -> str:
        """
        Format text for USSD (Unstructured Supplementary Service Data).
        USSD has strict length limits (usually 160 characters).
        """
        if len(text) <= max_length:
            return text
        
        # Truncate and add ellipsis
        return text[:max_length-3] + "..."
    
    @staticmethod
    def format_sms_response(text: str, max_length: int = 150) -> str:
        """
        Format text for SMS.
        SMS responses should be concise and split into multiple messages if needed.
        """
        if len(text) <= max_length:
            return text
        
        # SMS will be split at punctuation or word boundaries
        messages = []
        current_message = ""
        words = text.split()
        
        for word in words:
            if len(current_message) + len(word) + 1 <= max_length:
                current_message += word + " "
            else:
                if current_message:
                    messages.append(current_message.strip())
                current_message = word + " "
        
        if current_message:
            messages.append(current_message.strip())
        
        return messages
    
    @staticmethod
    def get_supported_languages() -> Dict[str, str]:
        """Get list of supported languages"""
        return LanguageService.SUPPORTED_LANGUAGES
    
    @staticmethod
    def translate_error(error_code: str, language: str = 'en') -> str:
        """Translate common error messages"""
        errors = {
            'en': {
                'NETWORK_ERROR': 'Network error. Please try again.',
                'INVALID_PHONE': 'Invalid phone number. Please check and try again.',
                'PAYMENT_FAILED': 'Payment failed. Please try another method.',
                'QUIZ_ERROR': 'Error loading quiz. Please try later.',
                'SERVER_ERROR': 'Server error. Please contact support.',
            },
            'sw': {
                'NETWORK_ERROR': 'Hitilafu ya mtandao. Jaribu tena.',
                'INVALID_PHONE': 'Namba ya simu batfu. Tafadhali jaribu tena.',
                'PAYMENT_FAILED': 'Malipo yamefeli. Jaribu njia nyingine.',
                'QUIZ_ERROR': 'Hitilafu katika kupakia mtihani.',
                'SERVER_ERROR': 'Hitilafu ya seva. Wasiliana na msaada.',
            },
            'yo': {
                'NETWORK_ERROR': 'Asise alaka. Jigbe lẹẹkansi.',
                'INVALID_PHONE': 'Namba simu aidun. Jigbe lẹẹkansi.',
                'PAYMENT_FAILED': 'Sisan kore. Gbiyanju ọna miiran.',
                'QUIZ_ERROR': 'Asise ni idaniloju.',
                'SERVER_ERROR': 'Asise oniwe. Pon pe ẹkó.',
            },
        }
        
        if language not in errors:
            language = 'en'
        
        return errors[language].get(error_code, 'An error occurred.')


# Context menu translations for teachers/admins
ADMIN_TRANSLATIONS = {
    'en': {
        'teacher_menu': 'Teacher Menu',
        'admin_menu': 'Admin Menu',
        'create_content': 'Create Content',
        'grade_students': 'Grade Students',
        'view_analytics': 'View Analytics',
        'manage_school': 'Manage School',
    },
    'sw': {
        'teacher_menu': 'Menyu ya Mwalimu',
        'admin_menu': 'Menyu ya Msimamizi',
        'create_content': 'Unda Maudhui',
        'grade_students': 'Ukutaje Wanafunzi',
        'view_analytics': 'Tazama Uchambuzi',
        'manage_school': 'Simamia Shule',
    },
}
