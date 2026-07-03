#!/usr/bin/env bash
# net_fingerprint.sh — capture a normalized snapshot of the network config so a
# DR restore can be proven identical. Run on the SOURCE before backup, then on
# the TARGET after a COMPLETE restore + reboot, then `diff` the two outputs.
#
#   sudo bash scripts/net_fingerprint.sh > /tmp/net_source.txt      # on source
#   sudo bash scripts/net_fingerprint.sh > /tmp/net_target.txt      # on target
#   diff /tmp/net_source.txt /tmp/net_target.txt && echo "RESEAU IDENTIQUE"
#
# Output is sorted/normalized so only real config differences show up.
set -uo pipefail

section() { printf '\n===== %s =====\n' "$1"; }

section "INTERFACES IPv4 (physiques + vlan/vxlan)"
# br-/docker/veth/lo excluded: not part of the appliance network identity
ip -br -4 addr 2>/dev/null \
  | grep -vE '^(lo|docker|br-|veth|vmnet|virbr)' \
  | awk '{print $1, $3, $4, $5}' | sort

section "VLAN"
ip -d link show type vlan 2>/dev/null \
  | grep -E 'vlan|^[0-9]+:' \
  | sed -E 's/^[0-9]+: //; s/ *$//' | sort

section "VXLAN"
ip -d link show type vxlan 2>/dev/null \
  | grep -E 'vxlan|^[0-9]+:' \
  | sed -E 's/^[0-9]+: //; s/ *$//' | sort

section "ROUTE PAR DEFAUT"
# strip the NM-assigned route metric (auto-increments on reactivation, not config)
ip route show default 2>/dev/null | sed -E 's/ metric [0-9]+//' | sort

section "PROFILS NetworkManager (id / type / interface / ip / vlan)"
for f in /etc/NetworkManager/system-connections/*.nmconnection; do
  [ -f "$f" ] || continue
  id=$(grep -m1 '^id='             "$f" | cut -d= -f2-)
  ty=$(grep -m1 '^type='           "$f" | cut -d= -f2-)
  ifn=$(grep -m1 '^interface-name=' "$f" | cut -d= -f2-)
  mth=$(grep -m1 '^method='        "$f" | cut -d= -f2-)
  a1=$(grep -m1 '^address1='       "$f" | cut -d= -f2-)
  gw=$(grep -m1 '^gateway='        "$f" | cut -d= -f2-)
  par=$(grep -m1 '^parent='        "$f" | cut -d= -f2-)
  [ -z "$id$ty$ifn" ] && continue   # skip empty/placeholder profiles
  echo "id=$id type=$ty if=$ifn method=$mth addr=$a1 gw=$gw parent=$par"
done | sort

section "DNS (/etc/resolv.conf)"
grep -E '^nameserver' /etc/resolv.conf 2>/dev/null | sort

section "INTERFACE DB (ifname / name / is_main)"
cd /asguard/asguard 2>/dev/null && python3 manage.py shell -c "
from backend.network.models import Interface
for i in Interface.objects.order_by('ifname'):
    print(f'ifname={i.ifname} name={i.name_interface} main={i.is_main}')
" 2>/dev/null | grep '^ifname=' | sort

section "REGLES FIREWALL -> INTERFACE (sanity)"
cd /asguard/asguard 2>/dev/null && python3 manage.py shell -c "
from backend.rules.models import Rule
seen=set()
for r in Rule.objects.select_related('interface'):
    n=getattr(r.interface,'ifname',None) or getattr(r.interface,'name_interface',None)
    if n: seen.add(n)
print('interfaces_referenced=' + ','.join(sorted(seen)))
" 2>/dev/null | grep '^interfaces_referenced=' | sort
