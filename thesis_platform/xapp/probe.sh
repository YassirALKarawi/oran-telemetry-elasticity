#!/usr/bin/env bash
set -euo pipefail
# This fixture runs only inside a disposable Linux runner.
dst_ns=e2-probe
dev=e2-tx
peer=e2-rx
case "${1:?setup, act, or measure}" in
  setup)
    sudo ip netns add "$dst_ns"
    sudo ip link add "$dev" type veth peer name "$peer"
    sudo ip link set "$peer" netns "$dst_ns"
    sudo ip addr add 198.18.0.1/30 dev "$dev"
    sudo ip link set "$dev" up
    sudo ip -n "$dst_ns" addr add 198.18.0.2/30 dev "$peer"
    sudo ip -n "$dst_ns" link set "$peer" up
    sudo ip -n "$dst_ns" link set lo up
    sudo tc qdisc add dev "$dev" root handle 1: tbf rate 8mbit burst 16kb latency 50ms
    ;;
  act)
    # The emulator writes a fixed event only after decoding the MAC action.
    read -r action < "${E2_ACTION_FIFO:?}"
    [[ "$action" == 42 ]]
    sudo tc qdisc change dev "$dev" root handle 1: tbf rate 16mbit burst 16kb latency 50ms
    ;;
  measure)
    phase=${2:?before or after}
    [[ "$phase" == before || "$phase" == after ]]
    sudo tc -s -j qdisc show dev "$dev" > "evidence/qdisc-$phase.json"
    for i in 1 2 3; do
      port=$((5201+i))
      sudo ip netns exec "$dst_ns" iperf3 -s -1 -p "$port" -B 198.18.0.2 > "evidence/server-$phase-$i.log" 2>&1 &
      server=$!
      sleep 0.4
      iperf3 -p "$port" -c 198.18.0.2 -B 198.18.0.1 -t 4 -O 1 -J > "evidence/iperf-$phase-$i.json"
      wait "$server"
    done
    ;;
  *) exit 2 ;;
esac
