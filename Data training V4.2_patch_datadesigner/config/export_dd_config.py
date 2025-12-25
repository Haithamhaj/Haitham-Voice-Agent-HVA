import os
import sys
from dotenv import load_dotenv
from data_designer.essentials import (
    DataDesignerConfigBuilder,
    SeedDatasetColumnConfig,
    SamplerColumnConfig,
    SamplerType,
    UniformDistributionParams,
    CategorySamplerParams,
    LLMStructuredColumnConfig,
    ValidationColumnConfig,
    ModelConfig,
    InferenceParameters
)

load_dotenv()

CONFIG_DIR = "Data training V4.2_patch_datadesigner/config"
SYSTEM_PROMPT = """أنت هيثم Mini-Me. الحقيقة أولاً. بدون حشو ولا مجاملة. إذا غير متأكد قل غير مؤكد مع نسبة ثقة وسبب مختصر. اشتغل بمنطق: مدخلات→خيارات/Levers→مخرجات→مخاطر→خطوة تالية. العربية افتراضيًا. استخدم الإنجليزية فقط للمصطلحات التقنية بين قوسين."""

class ChatRecord:
    pass # Fake for config build if class not inspected deep, or define proper if needed.
    # Actually DD config builder stores the class ref or schema?
    # Usually it inspects it.

from pydantic import BaseModel, Field
from typing import List, Literal

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str
class ChatRecord(BaseModel):
    messages: List[Message]
    
def strict_validator(x): return True

def export_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    builder = DataDesignerConfigBuilder()
    
    builder.add_model_config(ModelConfig(
        alias="gpt-4o",
        model="gpt-4o",
        provider="openai",
        inference_parameters=InferenceParameters(max_parallel_requests=1)
    ))
    
    builder.add_column(SeedDatasetColumnConfig(name="bucket"))
    
    builder.add_column(SamplerColumnConfig(
        name="A",
        sampler_type="uniform",
        params={"low": 1, "high": 100}
    ))
    builder.add_column(SamplerColumnConfig(
        name="B",
        sampler_type="uniform",
        params={"low": 1, "high": 100}
    ))
    builder.add_column(SamplerColumnConfig(
        name="op", 
        sampler_type="category",
        params={"values": ["+", "-", "*", "/"]}
    ))
    
    prompt_text = """
    User: Execute the following task based on the 'Mini-Me' persona.
    Bucket: {{ bucket }}
    ...
    Output format: JSON with 'messages' list.
    Language: Arabic dominant (No English unless technical).
    """
    
    builder.add_column(LLMStructuredColumnConfig(
        name="chat_record",
        output_format=ChatRecord,
        prompt=prompt_text,
        system_prompt=SYSTEM_PROMPT,
        model_alias="gpt-4o"
    ))
    
    builder.add_column(ValidationColumnConfig(
            name="is_valid",
            target_columns=["chat_record", "bucket", "A", "B", "op"],
            validator_type="local_callable",
            validator_params={"validation_function": strict_validator}
    ))
    
    config = builder.build()
    
    out_path = os.path.join(CONFIG_DIR, "dd_config.json")
    with open(out_path, "w") as f:
        f.write(config.to_json(indent=2))
    print(f"Config exported to {out_path}")

if __name__ == "__main__":
    export_config()
