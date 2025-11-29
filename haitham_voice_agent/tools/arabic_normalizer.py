import logging
from typing import Optional
from haitham_voice_agent.config import Config
from haitham_voice_agent.llm_router import LLMRouter

logger = logging.getLogger(__name__)

async def normalize_arabic_text(text: str, mode: str = "command") -> str:
    """
    Normalize Arabic text using LLM to correct spelling and grammar.
    
    Args:
        text: The raw Arabic text from STT.
        mode: "command" or "session".
        
    Returns:
        Normalized text or original text if normalization is disabled/failed.
    """
    if not text:
        return text
        
    cfg = Config.AR_NORMALIZATION
    if not cfg.get("enabled", False):
        return text
        
    mode_cfg = cfg.get(f"mode_{mode}")
    if not mode_cfg or not mode_cfg.get("enabled", False):
        logger.debug(f"Arabic normalization disabled for mode: {mode}")
        return text
        
    # Check length limits
    if len(text) > mode_cfg.get("max_chars", 1000):
        logger.info(f"Text too long for normalization ({len(text)} chars). Skipping.")
        return text
        
    if len(text) < cfg.get("min_length_for_correction", 5):
        return text

    # Use LLM Router to get the configured model
    logical_model = mode_cfg.get("model_logical", "logical.nano")
    
    # We need to instantiate LLMRouter or use a singleton if available. 
    # Since LLMRouter is usually instantiated in HVA class, we might need to pass it in or create a new one.
    # Creating a new one is lightweight.
    llm_router = LLMRouter()
    
    # Resolve model name
    model_name = Config.resolve_model(logical_model)
    
    prompt = f"""
    Correct the spelling and grammar of the following Arabic text. 
    Output ONLY the corrected text. Do not add any explanations or extra punctuation.
    Keep the dialect if it's clear, but fix obvious STT errors.
    
    Text:
    {text}
    """
    
    try:
        logger.info(f"Normalizing Arabic text ({mode}) with {model_name}...")
        # We use generate_with_gpt but we want to target the specific model.
        # LLMRouter.generate_with_gpt uses Config.GPT_MODEL by default.
        # We should probably use the OpenAI client directly or add a model param to generate_with_gpt if supported.
        # Looking at LLMRouter (I recall it might not take model param in generate_with_gpt), 
        # let's assume we can use the client from llm_router.
        
        # Actually, let's just use the llm_router's client directly for control
        import openai
        client = openai.AsyncOpenAI(api_key=Config.OPENAI_API_KEY)
        
        response = await client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert Arabic editor."},
                {"role": "user", "content": prompt}
            ],
            temperature=mode_cfg.get("temperature", 0.1),
            max_tokens=len(text) * 2 # Safety margin
        )
        
        normalized = response.choices[0].message.content.strip()
        logger.info(f"Normalized: '{text}' -> '{normalized}'")
        return normalized
        
    except Exception as e:
        logger.error(f"Arabic normalization failed: {e}")
        return text
