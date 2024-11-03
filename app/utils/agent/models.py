from config import logger
from typing import Optional
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
    from langchain_ollama import ChatOllama
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
    
def create_openai_model(model_name: Optional[str]=None, temperature: float=0.8) -> BaseLanguageModel:
    from langchain_openai import ChatOpenAI
    model_name = "gpt-4o" if not model_name else model_name
    
    try:
        return ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=4096)
        
    except Exception as e:
        raise Exception(f"Error: Failed to initialize Openai model: {str(e)}")

def create_mistral_model(model_name: Optional[str]=None, temperature: float=0.8) -> BaseLanguageModel:
    from langchain_mistralai.chat_models import ChatMistralAI
    model_name = "mistral-large-latest" if not model_name else model_name
    
    try:
        return ChatMistralAI(model_name=model_name, temperature=temperature)
    except Exception as e:
        raise Exception(f"Error: Failed to initialize Openai model: {str(e)}")

def create_google_model(model_name: Optional[str]=None, temperature: float=0.8) -> BaseLanguageModel:
    from langchain_google_genai import ChatGoogleGenerativeAI
    model_name = "gemini-1.5-pro" if not model_name else model_name
    
    try:
        return ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
    except Exception as e:
        raise Exception(f"Error: Failed to initialize Google model: {str(e)}")
    
def create_anthropic_model(model_name: Optional[str]=None, temperature: float=0.8) -> BaseLanguageModel:
    from langchain_anthropic import ChatAnthropic
    model_name = "claude-3-5-sonnet-20241022" if not model_name else model_name
    
    try:
        return ChatAnthropic(model_name=model_name, temperature=temperature)
    except Exception as e:
        raise Exception(f"Error: Failed to initialize Anthropic model: {str(e)}")
        