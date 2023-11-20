import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State
from spade.message import Message
from random import randint
import numpy as np

STATE_ONE = "takeoff"
STATE_TWO = "moving"
STATE_THREE = "landing"

class ExampleFSMBehaviour(FSMBehaviour):

    async def on_start(self):
        print(f"FSM starting at initial state {self.current_state}")

    async def on_end(self):
        print(f"FSM finished at state {self.current_state}")
        await self.agent.stop()



class StateOne(State):
    async def run(self):
        print("1.\t->Estou a tentar levantar")
        msg = Message(to=str(self.agent.jid))
        msg.body = "msg_from_state_one_to_state_three"
        rng = randint(1,10)
        while rng <= 3:
            print("1.\t->A tentar outra vez...")
            rng = randint(1,10)
        self.set_next_state(STATE_TWO)


class StateTwo(State):
    async def run(self):
        print("2.\t->Estou a mover-me")
        rng = randint(1,10)
        while rng <= 8:
            print("2.\t->Continuo a mover-me...")
            rng = randint(1,10)
        self.set_next_state(STATE_THREE)



class StateThree(State):
    async def run(self):
        print("3.\t->Estou a tentar aterrar")
        rng = randint(1,10)
        if rng >=9:
            print("3.\t->Não consegui aterrar, vou para outro aeroporto...")
            self.set_next_state(STATE_TWO)
            return
        print("3.\t->A aterrar, levantar daqui a pouco")
        self.set_next_state(STATE_ONE)
        # no final state is setted, since this is a final state


class FSMAgent(Agent):
    async def setup(self):
        fsm = ExampleFSMBehaviour()
        fsm.add_state(name=STATE_ONE, state=StateOne(), initial=True)
        fsm.add_state(name=STATE_TWO, state=StateTwo())
        fsm.add_state(name=STATE_THREE, state=StateThree())
        fsm.add_transition(source=STATE_ONE, dest=STATE_TWO)
        fsm.add_transition(source=STATE_TWO, dest=STATE_THREE)
        fsm.add_transition(source=STATE_THREE, dest=STATE_ONE)
        fsm.add_transition(source=STATE_THREE, dest=STATE_TWO)
        self.add_behaviour(fsm)


async def main():
    fsmagent = FSMAgent("fsmagent@localhost", "your_password")
    await fsmagent.start(auto_register=True)

    await spade.wait_until_finished(fsmagent)
    await fsmagent.stop()
    print("Agent finished")

if __name__ == "__main__":
    spade.run(main())