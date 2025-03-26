import llama_cpp

llm = llama_cpp.Llama(
    model_path='src/query/llm/qwen2-1_5b-instruct-q8_0.gguf',
    n_ctx=32768,
    verbose=False # dont give extra non user centric rubbish output
)


