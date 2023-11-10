# csma/cd (Carrier Sense Multiple Access/Collision Detetion)
from mac.non_csma import NonCSMA_MAC
from mac.base import simulation 
from utils import MyLogger

logger = MyLogger() 



class CSMA_MAC(NonCSMA_MAC):
    def __init__(self, env, node, *args, **kwargs):
        super().__init__(env, node, *args, **kwargs)

    @simulation
    def transmit_packet(self, link, packet):
        yield self.env.process(self.node.wait_until_idle()) # 보내기전에 확인


        self.tx_attempt += 1

        if self.tx_attempt > self.RETRANSMIT_LIMIT: # 시도한 횟수가 16을 넘어가면
            yield self.env.timeout(0.0) # yield = return개념
        else :
            yield self.env.process(self.node.transmit(link, packet)) # 특정 링크에서 노드로 패킷을 전송하기 시작한다.
