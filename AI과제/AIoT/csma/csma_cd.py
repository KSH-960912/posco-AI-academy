from mac.csma import CSMA_MAC 
from mac.base import simulation 
import numpy as np 
from utils import MyLogger

logger = MyLogger() 


class CSMA_CD_MAC(CSMA_MAC):
    def __init__(self, env, node, *args, **kwargs):
        super().__init__(env, node, *args, **kwargs)

        self.backoff = False 

    @simulation
    def on_collision_detected(self, link, packet):
        if self.is_transmitting:
            yield self.env.process(self.node.stop_transmit())

            self.node.send_jamming_signal()
            self.backoff = True

            # 여기 이후에 전송 오류로 처리가 되어서 아래의 on_transmission_failed 함수 실행

    @simulation
    def on_receive_jamming_signal(self):
        pass

    @simulation 
    def on_transmission_failed(self, link, packet, reason):
        if self.backoff:
            num_slots = np.random.randint(0, 2 ** self.tx_attempt)
            yield self.env.timeout(link.SLOT_TIME * num_slots)

        yield self.env.process(self.transmit_packet(link, packet))
        

    @simulation 
    def on_transmission_success(self, link, packet):
        self.backoff = False
    
    def on_receive_jamming_signal(self):
        yield self.env.process(self.node.stop_transmit())
        self.backoff = True


# 랜덤성 부여하여 충돌 최소화