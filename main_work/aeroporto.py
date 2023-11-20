from imports import *

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
        if rng >= 0.1:
            self.badWeather = False
        else:
            self.badWeather = True


    async def send_answer(self, msg_sender, answer, request_type):
        msg = Message()
        msg.to = str(msg_sender)
        msg.sender = str(self.agent.jid)
        msg.body = request_type + " rejected" if answer == "no" else request_type + " accepted"
        msg.set_metadata("request_answer",answer)
        msg.set_metadata("request", request_type)
        await self.send(msg)



    async def setup(self):
        self.add_behaviour(self.AeroportoBehaviour())

    class AeroportoBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=3) # wait for a message for 10 seconds
            if msg:
                print(f"Message received by {self.agent.jid}: {msg}")
                request_type = msg.metadata["request"]
                if request_type == "landing":
                    answer = "no" if self.agent.badWeather or not self.agent.isFree else "yes"
                    if answer == "yes":
                        self.agent.change_isFree_status(False)
                else:
                    answer = "no" if self.agent.badWeather else "yes"
                    if answer == "yes":
                        self.agent.change_isFree_status(True)
                receiver=str(msg.sender)
                msg = Message()
                msg.to = receiver
                msg.sender = str(self.agent.jid)
                msg.body = request_type + " rejected" if answer == "no" else request_type + " accepted"
                msg.set_metadata("request_answer",answer)
                msg.set_metadata("request", request_type)
                print(f"Message sent: {msg}")
                await self.send(msg)
                
