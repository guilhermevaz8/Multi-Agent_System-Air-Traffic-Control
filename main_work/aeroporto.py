import spade
from spade.agent import Agent
import numpy as np
from spade.message import Message
from spade.template import Template




class AeroportoAgent(Agent):
    def __init__(self, jid, password, environment, position):
        super().__init__(jid, password)
        self.environment = environment
        self.isFree = True
        self.position = position
        self.badWeather = False     

    
    def change_isFree_status(self, value):
        self.isFree = value

    def rng_badWeather(self):
        rng = np.random.uniform()
        if rng >= 0.05:
            self.badWeather = False
        else:
            self.badWeather = True

    def airplane_departure(self):
        self.rng_badWeather()
        if self.badWeather:
            # enviar mensagem a dizer que não pode levantar voo
            return
        #enviar mensagem a dizer que pode levantar
        self.change_isFree_status(True)

    async def refuse_landing(self, recieverJID):
        msg = Message()
        msg.to = str(recieverJID)
        msg.sender = str(self.agent.jid)
        msg.body = "Landing rejected"
        msg.set_metadata("request_answer","no")
        
        await self.send(msg)



    async def setup(self):
        template = Template()
        template.to = str(self.jid)
        template.set_metadata("request","landing")

        self.add_behaviour(self.AeroportoBehaviour(),template)

    class AeroportoBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5) # wait for a message for 10 seconds

            request_type = msg.metadata["request"]
            if request_type == "landing":
                if self.agent.badWeather:
                    self.refuse_landing(msg.sender)
                    
            



async def main():
    aeroporto = AeroportoAgent("ola@localhost","1234","ola",(1,2))
    await aeroporto.start(auto_register=True)

spade.run(main())

