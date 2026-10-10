#!/usr/bin/env bash
# Sweep OSF for Caviola questionnaires / supplementary materials.
# OSF's public API needs no key. Run from your machine (not sandboxed).
set -uo pipefail

API=https://api.osf.io/v2

# Preprint ids come from the DOIs: 10.31234/osf.io/<id>
IDS=(
  sntva   # AI Consciousness Will Divide Society (Caviola 2026)
  wvbya   # Digital sentience skepticism (Ladak & Caviola 2025)
  38a6j   # Reluctance to Harm AI (Allen & Caviola 2025)
)

for id in "${IDS[@]}"; do
  echo "=============================================================="
  echo "PREPRINT $id"
  curl -s "$API/preprints/$id/" \
    | jq -r '.data.attributes | "  title: \(.title)\n  date:  \(.date_published)"'

  # the supplemental project node is where materials usually live
  node=$(curl -s "$API/preprints/$id/" | jq -r '.data.relationships.node.data.id // empty')
  if [ -n "$node" ]; then
    echo "  supplemental node: $node  ->  https://osf.io/$node/"
    echo "  --- files in that node ---"
    curl -s "$API/nodes/$node/files/osfstorage/?page[size]=100" \
      | jq -r '.data[]? | "    \(.attributes.kind)  \(.attributes.name)  \(.links.download // "")"'
    echo "  --- wiki pages (sometimes hold the instrument) ---"
    curl -s "$API/nodes/$node/wikis/" \
      | jq -r '.data[]? | "    \(.attributes.name)"'
  else
    echo "  no linked supplemental node"
  fi

  echo "  --- files attached to the preprint itself ---"
  curl -s "$API/preprints/$id/files/osfstorage/?page[size]=100" \
    | jq -r '.data[]? | "    \(.attributes.name)"'
done

echo
echo "=============================================================="
echo "ALL PUBLIC OSF NODES BY CAVIOLA (materials often live in a bare project)"
uid=$(curl -s "$API/users/?filter\[full_name\]=Lucius%20Caviola" | jq -r '.data[0].id // empty')
if [ -n "$uid" ]; then
  echo "  osf user id: $uid  ->  https://osf.io/$uid/"
  curl -s "$API/users/$uid/nodes/?page[size]=100" \
    | jq -r '.data[]? | "    \(.id)  \(.attributes.title)"'
else
  echo "  no public OSF user profile matched"
fi
