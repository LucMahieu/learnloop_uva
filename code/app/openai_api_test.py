import os
from dotenv import load_dotenv
from openai import OpenAI
import openai

def setup_openai_client():
    # Assuming your API key is set in your environment variables
    # Alternatively, you can set it directly here with openai.api_key = 'your-api-key'
    load_dotenv()
    OPENAI_API_KEY = os.getenv("OPENAI_API")
    print(OPENAI_API_KEY)
    return OpenAI(OPENAI_API_KEY)


def get_chat_response(openai_client, vraag, antwoord_student, echte_antwoord):
    role_prompt = None

    with open("./prompts/feedback_prompt.txt", "r") as f:
        role_prompt = f.read()
    
    prompt = f"""Input:\n
        Vraag: {vraag}\n
        Antwoord student: {antwoord_student}\n
        Beoordelingsrubriek: {echte_antwoord}\n
        Output:\n"""
            
    response = openai_client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=[
                {"role": "system", "content": role_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
    return response.choices[0].message.content


def main():
    OPENAI_API_KEY = os.getenv('OPENAI_API') # TODO: Clear the streamlit cache because currently the old api key is used
    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    vraag = "Wat is amnesie?"
    echte_antwoord = "Amnesie is een aandoening waarbij mensen moeite hebben met het opslaan en ophalen van herinneringen."

    while True:
        # antwoord_student = input(f"{vraag}: ")
        antwoord_student = input()
        if antwoord_student == 'exit':
            break

        response = get_chat_response(openai_client, vraag, antwoord_student, echte_antwoord)
        print(response)

if __name__ == "__main__":
    main()