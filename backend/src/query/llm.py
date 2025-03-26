CMAKE_ARGS = '-DLLAMA_METAL=on' # flag to use mac's GPU
import llama_cpp

llm = llama_cpp.Llama(
    model_path='src/query/llm_model/qwen2-1_5b-instruct-q8_0.gguf',
    n_ctx=32768,
    verbose=False,
    CMAKE_ARGS = '-DLLAMA_METAL=on' # for macOS to use GPU
)


