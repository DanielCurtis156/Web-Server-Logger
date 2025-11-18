#!/usr/bin/env python3
import os, json, random, time, datetime, ipaddress
import urllib.request

API_KEY = os.getenv("INGEST_API_KEY", "secret123")
INGEST_URL = os.getenv("INGEST_URL", "http://localhost:8080/ingest")

services = ["nginx","sshd","postfix","app","suricata"]
protocols = ["tcp","udp","http","smtp"]
statuses = ["ok","ok","ok","ok","error","denied"]

#generates a random IP for the gen_event() function
def rand_ip(private=True):
    if private:
        blocks = [ipaddress.IPv4Network("10.0.0.0/8"), ipaddress.IPv4Network("192.168.0.0/16")]
        net = random.choice(blocks)
        # Pick a host address without materializing the entire network
        return str(net.network_address + random.randint(1, net.num_addresses - 2))
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

def gen_event():
    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    return {
        "ts": now,
        "source_host": random.choice(["web-1","web-2","api-1","db-1"]),
        "src_ip": rand_ip(),
        "dst_ip": rand_ip(private=False),
        "src_port": random.randint(1024, 65535),
        "dst_port": random.choice([22,80,443,25,53,3306]),
        "protocol": random.choice(protocols),
        "direction": random.choice(["inbound","outbound"]),
        "status": random.choice(statuses),
        "latency_ms": random.choice([None, random.randint(5, 500)]),
        "bytes_in": random.randint(0, 5000),
        "bytes_out": random.randint(0, 5000),
        "service": random.choice(services),
        "raw": "example raw line",
        "tags": {"env":"dev","region":"us-east-1"}
    }

def post_batch(batch):
    data = json.dumps(batch).encode("utf-8")
    req = urllib.request.Request(INGEST_URL, data=data, headers={
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY
    }, method="POST")
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode()

if __name__ == "__main__":
    print(f"Sending batches to {INGEST_URL} with key {API_KEY}")
    while True:
        batch = [gen_event() for _ in range(200)]
        try:
            resp = post_batch(batch)
            print("OK:", resp)
        except Exception as e:
            print("ERR:", e)
        time.sleep(2)
