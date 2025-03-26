CMAKE_ARGS = '-DLLAMA_METAL=on' # flag to use mac's GPU
import llama_cpp

llm = llama_cpp.Llama(
    model_path='src/query/llm_model',
    verbose=False
)


