# LibreChat with Custom Workflows

Run LangChain, AutoGen or any LLM chat in self-hosted client.

## Quick start

Clone the repository and create `.env` file from the `example.env` file. Provide API keys from providers of your choice and start docker compose when ready.

```
cp example.env .env
nano .env
docker-compose up
```

Go to `http://localhost:3080` for chat and register first user (you can then disable registration in .env file).

Dashboard is available after login on `http://localhost:8002`.


## API keys

Any API provider will work as workflow (see below). As for libre chat, see [LibreChat docs](https://www.librechat.ai/docs).

Some tested and suggested API providers:

- [Groq](https://console.groq.com)
- [OpenRouter](https://openrouter.ai)
- [DeepSeek](https://deepseek.com)
- [OpenAI](https://platform.openai.com/docs/api-reference/authentication)
- [HuggingFace](https://huggingface.co/docs/api)

As of today (May 2024), Groq is offering a **free API** and DeepSeek is offering 5 million **free tokens**. OpenRouter provides **free models**.

## Usage

Set the model spec **or** provider and model name in the UI.

Add custom endpoints and model specs by editing `librechat.yaml` file as described in [LibreChat Configuration Guide](https://www.librechat.ai/docs/configuration/librechat_yaml).


### Image analysis (a.k.a vision/multimodal)

Some providers (like OpenRouter) support image analysis by default for selected models (gpt-4/gpt4o, Gemini 1.5 pro/flash, LLaVa, Claude 3 etc.).

To use OpenAI directly, create an assistant first (on their platform or via LibreChat) and enable vision capabilities.

### File analysis and code execution (a.k.a. code interpreter)

Create an assistant with OpenAI key or use custom workflow with any model or API (see below).

### Image generation

Use **plugins** with OpenAI key to use DALL-E or StableDiffusion. LibreChat also supports native DALL-E API.

Custom worklows does not support image generation yet.

### Chat with documents

Use OpenAI assistants or custom workflows with LangChain or other tool utilizing RAG.

### Speech-to-text and text-to-speech

See [LibreChat docs](https://www.librechat.ai/docs/configuration/stt_tts#stt)

## LibreChat modifications

Since some features are not available in LibreChat, certain modifications has been made. The most significant ones are:

- `Conversation-Id` header is added to the request while using OpenAI API (not while using OpenRouter).
- `#modelSpec=model-spec-name` has been added as once suggested in [LibreChat issue](https://github.com/danny-avila/LibreChat/issues/2651)
- Added variables parsing before loading `librechat.yaml` file. Use `${env:VARIABLE_NAME}` format in `librechat.yaml` file to use environment variables.

## Custom workflows

This project comes with custom endpoint mimicking OpenAI API (`ai-workflows` image). Any `.py` file placed in `volumes/workflows` will be visible as a model in the UI.

Workflow file should implement `Workflow` class with `get_response_stream` method. Returned stream will be re-streamed to LibreChat and presented as AI response in real time. See `workflows/minimal-example-model.py`

### Example use cases

#### Group chat in the background

The `workflows/coding-duo.py` (available as `Custom Workspaces/coding-duo` in the UI) is an example of how to use LangChain to process the response before presenting it to the user. Another model can talk to the user int the mean time. This one is two LLM instances with different personas working on the code - e.g. Llama 3 70B is writing the code, DeepSeek Coder is reviewing, optimizing and fixing it.

#### Let me create files for you

The `workflows/xxxxxx-saver.py` will present a single command to create full directory tree and files locally after writing any code blocks. Code blocks are saved automatically to the conversation directory.

#### Code executors

The `workflows/xxxxxx-executor.py` models are saving all files and decide which ones should be executed. Failed executions (non-zero exit code) are provided as a feedback N (3 by default) times before giving up. The commands aren't run in sub-container for now, so any `apt-get` commands **will work and persist between chats**.

### Updating workflows

The `volumes/workflows` directory will be populated on first run with the default workflows. To update the workflows, pull the changes and copy contents of `workflow-runner/workflows` to `volumes/workflows`. You can also delete `volumes/workflows` and start fresh after updating `ai-workflows` image.

### Dashboard

Edit `volumes/dashboard/tiles.js` to customize the dashboard.
