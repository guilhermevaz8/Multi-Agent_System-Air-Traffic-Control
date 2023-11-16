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
        self.routes = {}
        self.sector = 0

    
    def change_isFree_status(self, value):
        self.isFree = value

    def rng_badWeather(self):
        rng = np.random.uniform()
        if rng >= 0.05:
            self.badWeather = False
        else:
            self.badWeather = True


    async def send_answer(self, recieverJID, answer, request):
        msg = Message()
        msg.to = str(recieverJID)
        msg.sender = str(self.agent.jid)
        msg.body = request + "rejected" if answer == "no" else request + "accepted"
        msg.set_metadata("request_answer",answer)
        msg.set_metadata("request_type", request)

        await self.send(msg)


    async def setup(self):
        template = Template()
        template.to = str(self.jid)
        template.set_metadata("request","Landing")

        self.add_behaviour(self.AeroportoBehaviour(),template)

    class AeroportoBehaviour(spade.behaviour.CyclicBehaviour):
        async def run(self):
            msg = await self.receive() # wait for a message for 10 seconds

            request_type = msg.metadata["request"]
            if request_type == "Landing":
                answer = "no" if self.agent.badWeather or not self.agent.isFree else "yes"
                if answer == "yes":
                    self.agent.change_isFree_status(False)
            else:
                answer = "no" if self.agent.badWeather else "yes"
                if answer == "yes":
                    self.agent.change_isFree_status(True)
            self.agent.send_answer(msg.sender, answer, request_type)
                    
