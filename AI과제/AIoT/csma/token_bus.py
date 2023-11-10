from mac.base import BaseMAC, simulation


class TokenBusMAC(BaseMAC):
    RETRANSMIT_LIMIT = 16 

    def __init__(self, env, node, *args, **kwargs):
        super().__init__(env, node, *args, **kwargs) 
    
    @simulation
    def transmit_packet(self, link, packet):
        # 현재 토큰을 가지고 있으면 미디어에 접근해서 전송한다.
        # 토큰을 가지고 있지 않으면 토큰이 올 때까지 대기한다.
        yield self.env.process(self.node.wait_until_token_received())
        yield self.env.process(super().transmit_packet(link, packet))

    @simulation 
    def on_token_expired(self):
        # 현재 전송이 끝날때까지 기다렸다가 pass_token이라는 토큰 넘겨주는 함수를 실행
        yield self.env.process(self.node.pass_token())

# 공정하게