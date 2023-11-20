from math import dist
import spade
from spade.agent import Agent
from spade.behaviour import FSMBehaviour, State, CyclicBehaviour
from spade.message import Message
import numpy as np
import asyncio
import json
from random import randint
import random
from spade.template import Template
from a import a_star_search