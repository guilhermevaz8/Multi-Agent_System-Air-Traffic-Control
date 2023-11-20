from imports import *

class GestorEspaco(Agent):
    def __init__(self, jid, password, environment):
        super().__init__(jid, password)
        self.environment = environment
        self.count=0

    async def setup(self):
        t=Template()
        t.set_metadata("request","update_position")
        self.add_behaviour(self.ReceivePositionUpdates(), template=t)

    class ReceivePositionUpdates(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=5)  # Esperar por uma mensagem por um tempo limite
            if msg:
                print(f"posicao recebida: {msg.body}")
                position = msg.body.replace('(', '').replace(')', '').replace(' ', '')
                x_str, y_str = position.split(',')
                x = int(x_str)
                y = int(y_str)
                self.agent.environment.update_position(str(msg.sender), x,y) 
                self.agent.count+=1
            if self.agent.count==5:
                self.agent.count=0
                self.agent.environment.save_aircraft_positions()
