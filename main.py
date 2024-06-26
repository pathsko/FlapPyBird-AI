import asyncio
import sys
from src.flappy import Flappy

if __name__ == "__main__":
    asyncio.run(Flappy().start(sys.argv))
