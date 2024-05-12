import sys
import asyncio
from wfrun import WorkflowManager, Message


async def print_stream(stream):
    print("Streaming response:\n---")
    async for chunk in stream:
        print(chunk, end="")
        sys.stdout.flush()
    print("\n---")

async def main():
    # first program argument:
    wfName = sys.argv[1]
    text = sys.argv[2]
    messages = [
        Message(role="user", content=text),
    ]
    try:
        wfm = WorkflowManager("workflows")
        wf = wfm.create_workflow("workflows/" + wfName + ".py")
        stream = await wf.get_response_stream(messages, None)
        await print_stream(stream)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())
