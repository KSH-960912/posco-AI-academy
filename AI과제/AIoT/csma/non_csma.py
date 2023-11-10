from mac.base import BaseMAC, simulation
from utils import MyLogger


logger = MyLogger() 


class NonCSMA_MAC(BaseMAC):
    def __init__(self, env, node, *args, **kwargs):
        super().__init__(env, node, *args, **kwargs)

    @simulation
    def transmit_packet(self, link, packet):
        self.tx_attempt += 1

        if self.tx_attempt > self.RETRANSMIT_LIMIT: # 시도한 횟수가 16을 넘어가면
            yield self.env.timeout(0.0) # yield = return개념
        else :
            yield self.env.process(self.node.transmit(link, packet)) # 특정 링크에서 노드로 패킷을 전송하기 시작한다.

    @simulation 
    def on_transmission_failed(self, link, packet, reason): # 전송이 실패했을때
        yield self.env.process(self.transmit_packet(link, packet)) # 전송이 실패해도 다시 보낸다. 


# 네트워크 토폴로지를 간단하게 한다 = 노드 수 줄이는거
# 혼잡 낮춤 = packetrate 낮춤