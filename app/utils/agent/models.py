from config import logger
from langchain_core.language_models import BaseLanguageModel

def create_groq_model(model_name: str, temperature: float)-> BaseLanguageModel:
    from langchain_groq import ChatGroq

    try:
        return ChatGroq(model_name=model_name, 
                        temperature=temperature, 
                        max_tokens=2048)
        
    except Exception as e:
        raise Exception(f"Error: Failed to initialize Groq model: {str(e)}.")
    
def create_ollama_model(base_url: str, model_name: str, temperature: float) -> BaseLanguageModel:
    from langchain_community.chat_models import ChatOllama
    try:
        model = ChatOllama(
            base_url=base_url,
            model=model_name,
            keep_alive="1h",
            num_predict=4096,
            temperature=temperature,
            format="json",
        )
        model.generate("") #preload the model
    except Exception as e:
        raise Exception(f"Error: Failed to initialize Ollama model: {str(e)}")
    
    return model
    
def create_openai_model(temperature: float) -> BaseLanguageModel:
    from langchain_openai import ChatOpenAI
    try:
        return ChatOpenAI(model_name="gpt-4o-2024-08-06", temperature=temperature, max_tokens=4096)
        
    except Exception as e:
        raise Exception(f"Error: Failed to initialize Openai model: {str(e)}")

def create_mistral_model(temperature: float)-> BaseLanguageModel:
    from langchain_mistralai.chat_models import ChatMistralAI
    try:
        return ChatMistralAI(model_name="mistral-large-latest", temperature=temperature)
    except Exception as e:
        raise Exception(f"Error: Failed to initialize Openai model: {str(e)}")

def create_google_model(temperature: float)-> BaseLanguageModel:
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    try:
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=temperature)
    except Exception as e:
        raise Exception(f"Error: Failed to initialize Google model: {str(e)}")
    
def create_anthropic_model(temperature: float)-> BaseLanguageModel:
    from langchain_anthropic import ChatAnthropic
    try:
        return ChatAnthropic(model_name="claude-3-5-sonnet-20240620", 
                                temperature=temperature,
                                max_tokens_to_sample=512
                                )
    except Exception as e:
        raise Exception(f"Error: Failed to initialize Anthropic model: {str(e)}")
        