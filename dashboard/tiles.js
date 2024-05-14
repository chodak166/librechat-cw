// var baseUrl = 'http://localhost:3080';
var baseUrl = 'https://ai.nixlab.in';

var tiles = [
   {"url": baseUrl + "/c/new#modelSpec=ort-claude-3-opus", "image": "img/claude.jpg", "title": "Claude 3 Opus",
   "description": "Claude 3 Opus is Anthropic's most powerful model for highly complex tasks ($15/M in, $75/1M out, 200k context)"},

   {"url": baseUrl + "/c/new#modelSpec=ort-gpt-4-turbo", "image": "img/gpt-4.jpg", "title": "GPT-4 Turbo",
   "description": "Upgraded GPT-4 with vision, function calling and large context window. $10/M in, $30/M out, 130k context."},

   {"url": baseUrl + "/c/new#modelSpec=ort-gpt-4o", "image": "img/gpt-4.jpg", "title": "GPT-4o",
   "description": "OpenAI's flagship model - a large-scale multimodal model capable of solving difficult problems. $5/M in, $15/M out, 128K context."},

   {"url": baseUrl + "/c/new#modelSpec=ort-gpt-3.5-turbo", "image": "img/gpt-3.5.jpg", "title": "GPT-3.5 Turbo",
   "description": "OpenAI's fastest model optimized for chat and traditional tasks. $0.5/M in, $1.5/M out, 16k context."},

   {"url": baseUrl + "/c/new#modelSpec=ort-gemini-1.5-pro", "image": "img/google-gemini.jpg", "title": "Gemini Pro 1.5 (preview)",
   "description": "Google's latest multimodal model, supporting image and video in text or chat prompts. $2.5/M in, $7.5/M out, 128k-1M context."},

   {"url": baseUrl + "/c/new#modelSpec=ort-mixtral-8x22b-instruct", "image": "img/mistral.jpg", "title": "Mixtral 8x22B Instruct",
   "description": "Mistral's official instruct fine-tuned version of Mixtral 8x22B. $0.65/M in, $0.65/M out, 66k context."},

   {"url": baseUrl + "/c/new#modelSpec=groq-llama3-70b", "image": "img/meta-llama-3.jpg", "title": "Llama 3 70B on Groq",
   "description": "Meta's latest high-performance model. 8.2K context. Free on Groq. SUPER FAST."},

   {"url": baseUrl + "/c/new#modelSpec=ort-llama-3-70b-instruct", "image": "img/meta-llama-3.jpg", "title": "Llama 3 70B on Meta",
   "description": "Meta's latest high-performance model. $0.59/M in, $0.79/M out, 8.2K context."},

   {"url": baseUrl + "/c/new#modelSpec=deepseek-coder-generic", "image": "img/deepseekcoder.jpg", "title": "DeepSeek Coder",
   "description": "Model for coding tasks.  Trained on 2T tokens, 87% code and 13% linguistic data. $0.14/M in, $0.28/M out, 16k context."},

   {"url": baseUrl + "/c/new#modelSpec=deepseek-coder-solid", "image": "img/deepseek-solid.jpg", "title": "DeepsSeek SOLID Coder",
   "description": "DeepSeek Coder instructed to give clean code with little explanation and no comments."},

   {"url": baseUrl + "/c/new#modelSpec=groq-solid-llama3-70b", "image": "img/llama-solid.jpg", "title": "Llama 3 70B SOLID Coder ",
   "description": "Llama 3 70B instructed to give clean code with little explanation and no comments. Free and fast by Groq."},

   {"url": baseUrl + "/c/new#modelSpec=groq-crazy-llama3-70b", "image": "img/crazy-llama.jpg", "title": "Crazy Llama 3 70B",
   "description": "Highly creative Llama 3 70B with high temperature and top_p/k parameters. Hosted on Groq."},

   {"url": baseUrl + "/c/new#modelSpec=ort-claude-3-opus-solid", "image": "img/opus-coder.jpg", "title": "Claude 3 Opus SOLID Coder",
   "description": "Claude 3 Opus instructed to give clean code with little explanation and no comments."},

   {"url": "", "image": "img/llama-deepseek-01.jpg", "title": "Advanced Coding Duo",
   "description": "AutoGen workflow with DeepSeek Coder and Llama 3 70B code review."},

   {"url": "#", "image": "img/coding-duo-02.jpg", "title": "Advanced Senior Coding Duo",
   "description": "Advanced and expensive workflow with Claude 3 Opus code reviewed by GPT-4 Turbo."},

   {"url": "#", "image": "img/generic-ai.jpg", "title": "Dummy chat model",
   "description": "Chat for testing custom setup."},

  // {"url": baseUrl + "/c/new#modelSpec=", "image": "img/llama-robo.jpg", "title": "Title 1", "description": "Description 1"},
];

