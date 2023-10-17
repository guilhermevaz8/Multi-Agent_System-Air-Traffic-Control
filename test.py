import spade

class Agent(spade.agent.Agent):
    
    async def setup(self):
        self.fuel = 50

        
        print("Hello world")


async def main():
    dummy=Agent("admin@localhost","1234")
    await dummy.start()

if __name__=="__main__":
    spade.run(main())