
from django.conf import settings
from ussd.models import Parent, Role, SchoolAdmin, Student, Teacher
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import google.generativeai as genai
import africastalking
from django.core.cache import cache

sandbox_username = settings.AFRICASTALKING_SANDBOX_USERNAME
sandbox_api_key = settings.AFRICASTALKING_SANDBOX_API_KEY

live_username = settings.AFRICASTALKING_LIVE_USERNAME
live_api_key = settings.AFRICASTALKING_LIVE_API_KEY
# Initialize Africa's Talking
africastalking.initialize(username="sandbox", api_key="atsk_your_key")
sms = africastalking.SMS

GEMINI_API_KEY = settings.GEMINI_API_KEY
# Initialize Google Generative AI
genai.configure(api_key="AI_API_KEY")
model = genai.GenerativeModel("gemini-2.0-flash")



def build_ai_prompt(user_message):
    """Builld a specialized prompt for the AI models based on user commands"""
    system_prompt = (
        "You are an AI tutor for African students using 2G (SMS-based) system."
        "Your answers must be concise, clear, and easy to understand."
        "Break dow complex topics into simple steps. Avoid jargon."
        "Format responses for  basic text. Do not use markdown like ** or * for emphasis."
    )
    message_upper = user_message.upper()
    if message_upper.startswith("QUIZME "):
        topic = user_message[7:]
        prompt = (
            f"{system_prompt} Generate a short, multiple-choice quiz (1-3 questions) "
            f"on the topic: {topic}. Provide the quetions first, then the "
            "answers cleary at the  very end, like ANSWERS: 1. A, 2. C"
        )
    elif message_upper.startswith("GUIDE "):
        topic = user_message[6:]
        prompt = (
            f"{system_prompt} Explain the follwing topic in simple terms: {topic}. "
            "Use simple african based analogies if possible"
        )
    else:
        prompt = f"{system_prompt} Answer the following question: {user_message}"
    return prompt
# function to query AI model
def query_ai_model(prompt):
    """
    Queries the Google Generative AI model with the given prompt..
    it returns the generated response.
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error querying AI model: {e}")
        return HttpResponse("I am sorry, but I am currently unable to process your request. Please try again later.")


# Function to split long messages into chunks of 160 characters
def split_message(message, chunk_size=160, command="NEXT"):
    """ 
    Splits a long message into sequential chunks of specified size wih a command at the end of each."""
    messages = []
    i = 0
    while i < len(message):
        chunk = message[i:i + chunk_size].rstrip()
        # Append command
        chunk += f"[{command}]"
        messages.append(chunk)
        i += chunk_size
    
    return messages
    # return [message[i:i + chunk_size] for i in range(0, len(message), chunk_size)]

def smart_split_message(message: str, chunk_size=150, command_str=" (NEXT)"):
    messages = []
    if len(message) <= chunk_size + len(command_str):
        messages.append(message)
        return messages
    
    start = 0
    while start < len(message):
        # calculate the ideal end point
        end = start + chunk_size
        
        # if we're near the end of the  message, just take the rst
        if end >= len(message):
            messages.append(message[start:].strip())
            break
        
        # Find the last space *before* the ideal end point
        last_space = message.rfind(' ', start, end)
        
        # If no space is found (very long word), cut at the chunk_size
        if last_space == -1 or last_space <= start:
            chunk = message[start:last_space].strip()
            start = end
        else:
            # Otherwise, cut at the last spce
            chunk = message[start:last_space].strip()
            start = last_space + 1 # Start the next chunk after the space
        
        if chunk: # Avoid adding empty chunks
            messages.append(chunk)
    return messages

def send_sms_chunk(phone_number, message):
    try:
        response = sms.send(message, [phone_number])
        print(f"SMS chunk sent to {phone_number}: {response}")
    except Exception as e:
        print(f"Error sending SMS chunk: {e}")


def initiate_paginated_sms(phone_number, full_message, command_str=" (NEXT)"):
    chunks = smart_split_message(full_message)
    
    if not chunks:
        return # Nothing to send
    # Send first chunk
    first_chunk = chunks[0]
    
    if len(chunks) > 1:
        # More chunks remain, add (NEXT) command and cache  them
        first_chunk += command_str
        
        # create cache data 
        cache_key = f"sms_session_{phone_number}"
        session_data = {
            'chunks': chunks,
            'current_index': 1 # We've sent index 0, next is 1
        }
        cache.set(cache_key, session_data, timeout=3600) # cache for 1 hour
    send_sms_chunk(phone_number, first_chunk)
# Funtion to send SMS via Africa's Talking
def send_sms(phone_number, message, command="NEXT"):
    """
    Sends an SMS to the specified phone number using Africa's Talking API.
    If the message exceeds 160 characters, it splits it into multiple messages.
    """
    try:
        messages = split_message(message, command=command)
        
        for msg in messages:
            # sms.send(msg, [phone_number])
            response = sms.send(msg, [phone_number])
            print(f"SMS sent to {phone_number}: {response}")
    except Exception as e:
        print(f"Error sending SMS: {e}")

def send_sms_async(phone_number, message):
    """
    Sends an SMS asynchronously to the specified phone number using Africa's Talking API.
    If the message exceeds 160 characters, it splits it into multiple messages.
    """
    import threading

    thread = threading.Thread(target=send_sms, args=(phone_number, message))
    thread.start()

# USSD Callback View for handling USSD requests
@csrf_exempt
def ussd_callback(request):
    session_id = request.POST.get('sessionId', None)
    service_code = request.POST.get('serviceCode', None)  
    phone_number = request.POST.get('phoneNumber', None)
    text = request.POST.get('text', '')

    response = ""
    input_parts = text.split('*') if text else []

    # Check User Role
    role = Role.objects.filter(phone_number=phone_number).first()
    student = Student.objects.filter(phone_number=phone_number).first()
    teacher = Teacher.objects.filter(phone_number=phone_number).first()
    school_admin = SchoolAdmin.objects.filter(phone_number=phone_number).first()
    parent = Parent.objects.filter(phone_number=phone_number).first()

    if role:
        if role.role == 'student':
            if text == "":
                response = "CON Welcome to BrilliantAfrica Tutor!\n"
                response += "1. AI  Tutor\n"
                response += "2. Performance\n"
                response += "3. Subscriptions & Payments\n"
                response += "4. Help & Support\n"
                response += "5. About BrilliantAfrica\n"
            
            elif text == "1":
                response = "CON Choose AI Tutor Subject:\n"
                response += "1. Start Learning\n"  # This will trigger AI Tutor
                response += "2. How to use\n"
                response += "3. Commands\n"
            
            elif text == "1*1":
                response = "CON Enter Your Question."
            
            elif input_parts[0] == "1":
                question = input_parts[-1]
                # ai_response = query_ai_model(question)
                # send_sms(phone_number, ai_response) 
                
                # 1. Build the prompt
                prompt = build_ai_prompt(question)
                
                # 2. Query the AI
                ai_response = query_ai_model(prompt)
                
                # 3. Send the paginated response
                # send_sms(phone_number, ai_response) 
                initiate_paginated_sms(phone_number, ai_response) 
                response = f"END Your Question is being processed. You'll receive an SMS shortly."
            
            elif text == "1*2":
                response = "END Still under development."
            
            elif text == "1*3":
                response = "END Still under development."
            
            elif text == "2":
                response = "CON Choose Performance Option:\n"
                response += "1. View Grades\n"
                # response += "2. View Attendance\n"  # For teachers or schools and parents role
            
            elif text == "3":
                # Handle subscriptions and must keep track of them in the database
                response = "CON Subscriptions & Payments:\n"
                response += "1. Subscribe to a plan\n"
                response += "2. View Payment History\n"
            
            elif text.startswith("3*"):
                # handle subscription selection, e.g. "3*1"
                response = "CON Choose a Subscription Plan:\n"
                response += "1. Individual Plan - $5/month\n" # can pay manually, or set auto-renewal
                response += "2. Family Plan - $10/month\n"
                response += "3. School Plan - $20/month\n"
            
            elif text == "4":
                response = "CON Help & Support:\n"
                response += "1. Contact Support\n"
                response += "2. FAQs\n"
            
            elif text.startswith("4*1"):
                response = "END For support, call +256707758612 or email hanmas669@gmail.com"
            elif text.startswith("4*2"):
                response = "END FAQs still in development."
            else:
                response = "END Invalid choice. Please try again."
        else:
            # If there are other role types in the future, handle here
            response = "END Your role does not have a USSD menu yet."
    else:
        # Unregistered user flows
        if text == "":
            response = "CON Welcome to BrilliantAfrica Tutor!\n"
            response += "1. Register as Student\n"
            response += "2. Register as Teacher\n"
            response += "3. Register as Parent\n"
            response += "4. Register as School Admin\n"
        
        elif text == "1":
            response = "CON Enter First Name:"
        
        # elif text.startswith("1*"):
        #     # # parse only the portion after the first '*'
        #     # name = text.split('*', 1)[1]
        #     # Student.objects.create(name=name, phone_number=phone_number)
        #     Role.objects.create(phone_number=phone_number, role='student')
        #     response = "END You have been registered as a Student."
        elif len(input_parts) == 2 and input_parts[0] == '1':
            # parse only the portion after the first '*'
            # first_name = text.split('*', 1)[1]
            # last_n = text.split('*', 1)[1]
            # Student.objects.create(first_name=first_name, phone_number=phone_number)
            # Role.objects.create(phone_number=phone_number, role='student')
            
            # User entered "1*FirstName"
            response = "CON Enter your Last Name:"
        elif len(input_parts) == 3 and input_parts[0] == '1':
            # User entered "1*FirstName*LastName*OtherName"
            response = "CON Enter your Other Name(Optional, press 0 to skipe):"
        
        elif len(input_parts) == 4 and input_parts[0] == '1':
            # User entered "1*FirstName*LastName*OtherName" (or "1*...*0")
            
            first_name = input_parts[1]
            last_name = input_parts[2]
            other_name_input = input_parts[3]
            other_name = other_name_input if other_name_input != '0' else None
            
            # create Student and Role
            try:
                student = Student.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    other_name=other_name,
                    phone_number=phone_number,
                )
                Role.objects.create(phone_number=phone_number, role='student')
                response = f"END Thank you, {first_name}! You are registered as a Student. Dial again to start learning."
            except Exception as e:
                print(f"Error during resgistration: {e}")
                response = "END An error occured. Please try registering again."

        # Other registration options under development
        elif text == "2":
            response = "END Teacher registration is currently unavailable."
        elif text == "3":
            response = "END Parent registration is currently unavailable."
        elif text == "4":
            response = "END School Admin registration is currently unavailable."
        elif text == "5":
            response = "END BrilliantAfrica is a 2G education Supervised AI tool for students with low resources."
        else:
            response = "END Invalid input. Please try again."

    return HttpResponse(response, content_type='text/plain')


# Function to handle incoming SMS for AI Tutor
@csrf_exempt
def sms_reply_handler(request):
    if request.method == 'POST':
        # phone_number = request.POST.get('from', None)
        phone_number = request.POST.get('from')
        message = request.POST.get('text', '')

        # Check if sender is a registered student
        role = Role.objects.filter(phone_number=phone_number, role='student').first()
        if role:
            # Query AI model
            ai_response = query_ai_model(message)
            # Send response via SMS
            # send_sms(phone_number, ai_response)
            send_sms_async(phone_number, ai_response)
            return HttpResponse("SMS processed", status=200)
        else:
            return HttpResponse("You are not registered as a student.", status=403)
    else:
        return HttpResponse("Invalid request method.", status=405)