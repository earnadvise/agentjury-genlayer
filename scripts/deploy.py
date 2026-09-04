"""
AgentJury Deployment Guide & Helper Script for GenLayer Testnet
"""

import sys
import os

def print_deployment_guide():
    print("""
======================================================================
  AGENTJURY DEPLOYMENT GUIDE (GENLAYER TESTNET & STUDIO)
======================================================================

Option 1: Deploy via GenLayer Studio (Recommended & Instant)
-------------------------------------------------------------
1. Open https://studio.genlayer.com
2. Click 'Create Contract' and select Python (GenVM).
3. Paste the contents of `contracts/agent_jury.py`.
4. Click 'Deploy to Testnet'.
5. Copy your deployed contract address and paste it into `frontend/app.js`.

Option 2: Deploy via GenLayer CLI
---------------------------------
1. Ensure Node.js and Python 3.12+ are installed.
2. Install GenLayer CLI:
   npm install -g @genlayer/cli
3. Deploy the contract:
   genlayer deploy --contract contracts/agent_jury.py --network testnet
4. Interact with your contract:
   genlayer call --contract <CONTRACT_ADDRESS> --method list_bounties

======================================================================
"""
)

if __name__ == "__main__":
    print_deployment_guide()
