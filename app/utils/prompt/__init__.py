import os

def load_prompt(prompt_name: str) -> str:
    """ load the prompt from the prompts directory """

    dir = os.path.dirname(__file__)
    prompt_path = os.path.join(dir, f"{prompt_name}.md")
    
    try:
        with open(prompt_path, 'r') as f:
            prompt = f.read().strip()
    
    except FileNotFoundError:
        raise FileNotFoundError(f"Prompt file {prompt_path} not found.")

    return prompt

