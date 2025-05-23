from .LLMEnums import LLMEnums
from .providers import CohereProvider ,OpenAIProvider,OllamaProvider


class LLMProviderFactory:
    
    def __init__(self,config : dict ):
        
        self.config =config 
        
    def create(self, provider: str):
        if provider == LLMEnums.OPENAI.value:
            return OpenAIProvider(
                
                api_key = self.config.OPENAI_API_KEY,
                api_url = self.config.OPENAI_API_URL,
                default_input_max_characters =self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens = self.config.DEFAULT_GENERATION_MAX_OUTPUT_TOKENS,
                default_generation_temperature = self.config.DEFAULT_GENERATION_TEMPERATURE,
                
            )
        
        if provider == LLMEnums.COHERE.value:
            return CohereProvider(
                
                api_key = self.config.COHERE_API_KEY,
                default_input_max_characters = self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens = self.config.DEFAULT_GENERATION_MAX_OUTPUT_TOKENS,
                default_generation_temperature = self.config.DEFAULT_GENERATION_TEMPERATURE
                
            )
            
        if provider == LLMEnums.OLLAMA.value:
            return OllamaProvider(
                generation_api_key = self.config.OPENAI_API_KEY,
                generation_api_url = self.config.OPENAI_API_URL,
                embedding_api_key = self.config.OPENAI_API_KEY,
                embedding_api_url =self.config.EMBEDDING_API_URL,
                default_input_max_characters = self.config.DEFAULT_INPUT_MAX_CHARACTERS,
                default_generation_max_output_tokens = self.config.DEFAULT_GENERATION_MAX_OUTPUT_TOKENS,
                default_generation_temperature = self.config.DEFAULT_GENERATION_TEMPERATURE
                
            )
            
        
        return None