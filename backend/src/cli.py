from dotenv import load_dotenv
from langchain_core.messages import (
    HumanMessage
)
from envar import (
    IMAP_HOST,
    IMAP_USER,
    IMAP_PASSWORD
)
import graph as node

if __name__ == "__main__":
    try:
        if not all([
            IMAP_HOST,
            IMAP_USER,
            IMAP_PASSWORD
        ]):
            raise ValueError(
                "Missing IMAP configuration. Check your .env file."
            )

        print("\n================================")
        print("       Noi STARTED")
        print("================================")
        print("IMAP Host:", IMAP_HOST)
        print("IMAP User:", IMAP_USER)

        state = {
            "messages": []
        }

        print("\nType an instruction or 'quit' to exit.\n")

        while True:
            user_message = input("You: ").strip()
            if user_message.lower() == "quit":
                print("\nNoi shutting down.")
                break

            if not user_message:
                continue

            state["messages"].append(
                HumanMessage(content=user_message)
            )

            try:
                state = node.graph.invoke(state)
                response = state["messages"][-1]
                print("\nNoi:", response.content)
            except Exception as e:
                print("\n[ERROR]", str(e))
    except KeyboardInterrupt:
        print("\nInterrupted by user. Shutting down safely.")
    except Exception as e:
        print("\n[FATAL ERROR]", str(e))