import os
import uvicorn
from envar import DEPLOY_PORT

if __name__ == '__main__':
    port = int(os.getenv("DEPLOY_PORT", "7689"))

    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )