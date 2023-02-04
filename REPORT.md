# Sybil Shield

## About

SybilShield is an open-source project built for the StarkNet ecosystem that utilizes blockchain data to detect Sybil attack behaviors.

A Sybil attack is a type of attack where an attacker creates multiple fake identities (also known as Sybil nodes) in a network in order to gain control or disrupt the network's operation.

SybilShield is implemented using Apibara technology to explore on-chain data, allowing it to detect and mitigate Sybil attacks by identifying and isolating fake identities.

## Hacker House

We started from scratch, and we expected to have the following points:
- A front (hosted locally or on a server) which displays the node interactions around the targeted contract. The front-end technology will be in typescript react and we can use viz.js library for rendering or equivalent.
- A back (hosted locally or on a server) which fetches the starknet data (using apibara or equivalent), runs a model, and returns the result to the front using HTTP routes. The back-end technoology could be typescript or python according to available skills in the team.
- At least 1 model that provides a guilty score for each nodes

## Implementation

The team was composed of the following skills:
- 2 back-end developers `Bal7hazar` & `trangnv`
- 1 UX/UI designer `G2CARBZ`
- 1 front-end developer `schwepps`
- 1 data scientist `marissaposner`

So far, we have:
- Implemented the front-end as expected and deployed it on a server (paid by Carbonable).
- Setup the backend, create routes, model handler, main controller and hosted the back on a server (paid by Carbonable).
- Benchmarked on different apibara alternatives to workaround data gathering issues (checkpoint, starkscan).
- Benchmarked on sybil attacks models and plug it in our model handler (this latest point is still on going)

Issues we are facing:
- Gathering data takes too much time
- Processing data takes too much time
- Define relevant models takes much more time, since we need to iterate over model implementations
- Traversing a large graph network is computationally expensive

### Front pull requests

- https://github.com/carbonable-labs/sybil-shield-front/pull/2
- https://github.com/carbonable-labs/sybil-shield-front/pull/7
- https://github.com/carbonable-labs/sybil-shield-front/pull/8
- https://github.com/carbonable-labs/sybil-shield-front/pull/10
- https://github.com/carbonable-labs/sybil-shield-front/pull/11
- https://github.com/carbonable-labs/sybil-shield-front/pull/13
- https://github.com/carbonable-labs/sybil-shield-front/pull/15
- https://github.com/carbonable-labs/sybil-shield-front/pull/17

### Back-end pull requests

- https://github.com/carbonable-labs/sybil-shield/pull/15
- https://github.com/carbonable-labs/sybil-shield/pull/1
- https://github.com/carbonable-labs/sybil-shield/pull/2
- https://github.com/carbonable-labs/sybil-shield/pull/3
- https://github.com/carbonable-labs/sybil-shield/pull/4
- https://github.com/carbonable-labs/sybil-shield/pull/10
- https://github.com/carbonable-labs/sybil-shield/pull/12
- https://github.com/carbonable-labs/sybil-shield/pull/14
- https://github.com/carbonable-labs/sybil-shield/pull/16

### Checkpoint alternative exploration

- https://github.com/trangnv/checkpoint-briq/pull/2

## After the event

We need to explore more alternatives to workaround about our issues, what we have in mind is:
- use a blockchain sync database to improve data accessiblity and data processing
- pay for a Starkscan api key to use their api and fetch data from them
- continue to test and improve models to detect suspicious addresses

Final goal is to have a efficient way for a user to analyze relevantly any input contract
