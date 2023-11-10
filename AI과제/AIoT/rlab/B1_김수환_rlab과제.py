import time
from collections import defaultdict
from typing import DefaultDict

from router_lab import NodeCustomBase, is_valid_ip


class DBFRoutingPacket: # 노드 간에 라우팅 정보를 교환
    def __init__(self, src: str, routing_table: dict[str, float]):
        self.src = src
        self.routing_table: dict[str, float] = routing_table

    def to_bytes(self) -> bytes:
        return (
            b"routing\n"
            + self.src.encode()
            + b"\n"
            + b"\n".join(f"{dst} {cost}".encode() for dst, cost in self.routing_table.items())
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "DBFRoutingPacket":
        lines = data.split(b"\n")
        src = lines[1].decode()
        routing_table = {}
        for line in lines[2:]:
            if not line:
                continue
            dst, cost = line.decode().split()
            assert is_valid_ip(dst), "Invalid IP, maybe bit corruption!"
            routing_table[dst] = float(cost)
        return cls(src, routing_table)


class DataPacket: # 노드 간 데이터를 전송하는 데 사용되는 데이터 패킷
    def __init__(self, src: str, dst: str, hop: int, data: bytes):
        self.src = src
        self.dst = dst
        self.hop = hop
        self.data = data

    def to_bytes(self) -> bytes:
        return (
            b"data\n"
            + self.src.encode()
            + b"\n"
            + self.dst.encode()
            + b"\n"
            + str(self.hop).encode()
            + b"\n"
            + self.data
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "DataPacket":
        lines = data.split(b"\n")
        src = lines[1].decode()
        dst = lines[2].decode()
        hop = int(lines[3].decode())
        data = lines[4]
        return cls(src, dst, hop, data)

class NullPacket: # ACK 패킷을 나타냄
    def __init__(self, is_ack: bool, timestamp: float):
            self.is_ack = is_ack
            self.timestamp = timestamp

    def to_bytes(self) -> bytes:
        return b"null\n" + str(int(self.is_ack)).encode() + b"\n" + str(self.timestamp).encode()

    @classmethod
    def from_bytes(cls, data: bytes) -> "NullPacket":
        lines = data.split(b"\n")
        is_ack = bool(int(lines[1].decode()))
        timestamp = float(lines[2].decode())
        return cls(is_ack, timestamp)


class DistributedBellmanFordNodeImpl(NodeCustomBase):
    async def every_1s(self):
        # log routing table
        for dst, (next_hop, cost) in self.routing_table.items():
            self.record_table(dst, next_hop=next_hop, cost=cost)

        # 10부터 30초까지 20초 동안 거리 벡터를 전송.
        if self.send_vector_timer >= 10 and self.send_vector_timer <= 30:
            await self.broadcast(
                DBFRoutingPacket(
                    self.ip, {dst: cost for dst, (next_hop, cost) in self.routing_table.items()}
                ).to_bytes()
            )
        elif self.send_vector_timer < 10: # 10 미만인 경우 NullPacket 전송
            await self.broadcast(NullPacket(False, time.time()).to_bytes())
        self.send_vector_timer += 1

    async def main(self):# 라우팅 테이블을 초기화하고 인접 딜레이를 설정 후 NullPacket 전송.
        self.routing_table: DefaultDict[str, tuple[str, float]] = defaultdict(
            lambda: ("", float("inf"))
        )
        self.routing_table[self.ip] = (self.ip, 0.0) # 내 자신의 ip는 0이다 cost X
        self.adjacent_delay: dict[str, float] = {}
        await self.broadcast(NullPacket(False, time.time()).to_bytes())
# 수신된 패킷에 대한 처리.
    async def on_recv(self, src_1hop: str, data: bytes):
        if data.startswith(b"routing"): #routing으로 시작하는 경우 DBFRoutingPacket으로 처리
            pkt = DBFRoutingPacket.from_bytes(data)
            if pkt.src not in self.routing_table:
                self.routing_table[pkt.src] = (src_1hop, self.adjacent_delay[src_1hop])
            for dst, cost in pkt.routing_table.items():
                if dst not in self.routing_table or self.routing_table[dst][1] > cost + self.adjacent_delay[src_1hop]:
                    self.routing_table[dst] = (src_1hop, cost + self.adjacent_delay[src_1hop])
        elif data.startswith(b"data"): # data로 시작하는 경우 DataPacket으로 처리.
            pkt = DataPacket.from_bytes(data)
            if pkt.dst == self.ip:
                self.log.info(f"Received from {pkt.src} with {pkt.hop} hops: {pkt.data}")
                self.record_stat(routed_hops = pkt.hop)
            else: #내가 목적지가 아니다,
                next_hop, cost = self.routing_table[pkt.dst] #로그 찍어줌, 확인 코드
                self.log.info(f"Sending to {pkt.dst} vis {next_hop} (cost: {cost})")
                await self.unicast(
                    next_hop, DataPacket(self.ip, pkt.dst, pkt.hop + 1, pkt.data).to_bytes()
                )
        elif data.startswith(b"null"): # null이 들어오면 NullPacket으로 처리한다.
            pkt = NullPacket.from_bytes(data)
            if pkt.is_ack:
                self.adjacent_delay[src_1hop] = time.time() - pkt.timestamp
            else:
                await self.unicast(src_1hop, NullPacket(True, time.time()).to_bytes())
        else:
            self.log.warning(f"Unknown packet type!")
    async def on_queue(self, dst: str, data: bytes): # 트래픽을 만들어낼때 어떻게 할지
        if dst in self.routing_table:
            next_hop, cost = self.routing_table[dst]
            self.log.info(f"Sendinf to {dst} via {next_hop} (cost: {cost})")
            await self.unicast(next_hop, DataPacket(self.ip, dst, 1, data).to_bytes())
        else:
            self.log.info(f"Cannot send to {dst} (no route!)")

    def on_start(self):
        self.send_vector_timer = 0

# 벨만포드 알고리즘을 가지고 동작하는 라우터를 구현
