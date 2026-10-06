import { createClient, createAccount } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';
import fs from 'fs';

const studioNext = {
  ...studionet,
  id: 61997,
  name: 'GenLayer Studio Next',
  rpcUrls: {
    default: {
      http: ['https://studio-dev.genlayer.com/api']
    }
  },
  defaultNumberOfInitialValidators: 5n,
  defaultConsensusMaxRotations: 3n
};

const account = createAccount();
console.log('Account address:', account.address);

const client = createClient({
  chain: studioNext,
  account: account
});

async function main() {
  const code = fs.readFileSync('./contracts/agent_jury.py', 'utf8');
  try {
    console.log('Deploying AgentJury contract to Studio Next (Chain 61997)...');
    const txHash = await client.deployContract({
      code: code,
      args: []
    });
    console.log('Deployment Tx Hash:', txHash);

    console.log('Waiting for receipt from validator consensus...');
    const receipt = await client.waitForTransactionReceipt({
      hash: txHash,
      status: 'ACCEPTED'
    });
    console.log('Receipt:', receipt);
    console.log('DEPLOYED CONTRACT ADDRESS:', receipt.data?.contractAddress || receipt.contractAddress || receipt.to || receipt.recipient);
  } catch (e) {
    console.error('Error:', e);
  }
}

main();
