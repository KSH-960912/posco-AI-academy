#!/usr/bin/env python
# coding: utf-8

# In[4]:


from scapy.all import *
import socket
import sys


# In[ ]:


def select_iface():
    iface_list = socket.if_nameindex() # 사용 가능한 인터페이스 목록을 가져옴.
    # iface가 없을때
    if len(iface_list) == 0:
        print("NO!!!!!!!")
        sys.exit()
    print("Available Network Interfaces:")
    # 사용 가능한 목록을 나타내고 인터페이스 번호를 사용자로부터 입력받음.
    for iface in iface_list:
        i, face = iface
        print(f"{i}: {face}")
    i = int(input(f"\nSelect network interface number to capture [1-{len(iface_list)}]: ")
           )
    return iface_list[i-1][1]
def process_packet(file_name, packet): # 캡처한 패킷을 처리.
    wrpcap(filename=file_name, pkt = packet, append=True) # 패킷을 지정된 파일에 저장및 기존 파일에 패킷을 추가한다.
def main():
    file_name = str(sys.argv[1])
    duration = int(sys.argv[2])
    iface = select_iface()
    # 지정된 인터페이스에서 패킷을 캡처
    sniff(iface=iface, filter = "tcp", prn = lambda pkt: process_packet(file_name,pkt),
         timeout=duration, )
    print("DONE")
    print(f"{iface}에서 했어요 {duration}동안 캡쳐했어요. 그리고")
    print(f"{file_name}에 저장했어요")
if __name__ == "__main__":
    main()
