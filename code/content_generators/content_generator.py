from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class Module:
    def __init__(self, module_name, transcript_path, glossary_path, content_path, batch_size):
        self.module_name = module_name
        self.transcript_path = transcript_path
        self.glossary_path = glossary_path
        self.content_path = content_path
        self.batch_size = batch_size


    def openai_call(self, system_message, user_message, formatting="text", model='gpt-3.5-turbo-1106', temp=0.0):
        message = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        
        response = client.chat.completions.create(model=model, temperature=temp, messages=message, response_format={"type": formatting})
        
        return response.choices[0].message.content


    def batch_generator(self, glossary):
        lines = ""
        # Strip all blank lines from the glossary
        glossary = "\n".join([line for line in glossary.split("\n") if line.strip() != ""])

        glossary_lines = glossary.split("\n")
        for i, line in enumerate(glossary_lines):
            lines += line
            if (i + 1) % self.batch_size == 0 and i != 0: # i plus 1 because of zero indexing
                yield lines
                lines = ""


    def add_response_to_json_file(self, json_response_string, module_name, export_path):
        # Turn json string into python object
        json_response = json.loads(json_response_string)
        
        if os.path.exists(export_path):
            # Open json file to read existing content
            with open(export_path, "r") as f:
                content = json.load(f)
            
            # Check if 'segments' key already exists
            if 'segments' in content:
                # Add the new segments to the existing segments
                content['segments'].extend(json_response['segments'])
            else:
                # Create the 'module name' key and assign the module name
                content['module_name'] = module_name
                # Create 'segments' key and assign the new segments
                content['segments'] = json_response['segments']
        else:
            # Create json file with the module name and response
            content = {}
            content['module_name'] = module_name
            content['segments'] = json_response['segments']

        # Write the new content to the json file
        with open(export_path, "w") as f:
            json.dump(content, f, indent=4)


    def generate_glossary(self):
        """Generates a glossary of topics from the lecture transcript and stores 
        them as attribute for further processing."""
        print("Generating glossary")
        with open("./prompts/transcript_to_glossary.txt", "r") as f:
            system_message = f.read()
        
        # Open the transcript file and use it as input for the user message
        with open(f"{self.transcript_path}", "r") as f:
            transcript = f.read()
        
        user_message = f"""
            Input:
            {transcript}
            
            Output:
        """
        response = self.openai_call(system_message, user_message, model='gpt-4-1106-preview', temp=0.7)

        # Export the glossary to a file
        with open(self.glossary_path, "w") as f:
            f.write(response)


    def generate_content(self):
        """Generates content for the module based on the generated glossary."""

        # Load glossary from lecture path txt file
        with open(f"{self.glossary_path}", "r") as f:
            glossary = f.read()

        for i, batch in enumerate(self.batch_generator(glossary)):
            print(f"Generating content for batch {i + 1}")
            # Load instructions for content generator
            with open("./prompts/generate_content.txt", "r") as f:
                system_message = f.read()
            
            # Input study materials
            user_message = f""" 
                Input: 
                {batch}
                
                Output:
            """

            json_response = self.openai_call(system_message, user_message, formatting="json_object", model='gpt-4-1106-preview', temp=0.7)

            # Export the json response to a json file
            self.add_response_to_json_file(json_response, export_path=content_path, module_name=self.module_name) #TODO: Change module name to be variable


if __name__ == "__main__":
    module_name = "test_slide_transcript_chemie"
    transcript_path = f"./raw_materials/{module_name}.txt"
    glossary_path = f"./glossaries/{module_name}.txt"
    content_path = f"./modules/{module_name}.json"

    new_module = Module(module_name, transcript_path, glossary_path, content_path, batch_size=2)
    new_module.generate_glossary()
    new_module.generate_content()