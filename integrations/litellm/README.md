# DDG × LiteLLM

A LiteLLM custom provider that routes `ddg/<model>` through DDG's OpenAI-compatible
x402 gateway and pays per call automatically. Because LiteLLM sits under LangChain,
CrewAI, and AutoGen, this puts DDG in those agents' execution path.

```bash
pip install "ddg-agent-services-mcp[openai]" litellm
export DDG_AGENT_ID=my-agent
export DDG_PRIVATE_KEY=0x<funded Base USDC key>   # needed for metered routes
```
```python
import litellm
from ddg_litellm import register
register()
resp = litellm.completion(model="ddg/glm-4.5-air",
                          messages=[{"role": "user", "content": "hi"}])
print(resp.choices[0].message.content)
```
See `ddg_litellm.py`. Models: any DDG alias (see `GET /v1/model-catalog`).
