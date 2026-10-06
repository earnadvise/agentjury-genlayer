import { createClient, createAccount } from 'genlayer-js';
import { studionet } from 'genlayer-js/chains';
import { defineChain } from 'viem';

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

window.GenLayerSDK = {
  createClient,
  createAccount,
  studionet: studioNext,
  defineChain
};
