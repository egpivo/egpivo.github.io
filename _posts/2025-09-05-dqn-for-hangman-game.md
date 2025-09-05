---
layout: post
title: "(Draft) Hangman Game by Deep Q Learning with Transformer"
tags: [Machine Learning, Deep Learning, RL, NLP]
math: true
---

Hangman is a great example of a reinforcement learning problem: you only see part of the word, make sequential guesses, and choose from a small set of actions (the 26 letters). Deep Q-Networks (DQN) fit naturally here because they handle discrete actions well and can learn to avoid invalid guesses through action masking.

## RL Setups

In our RL setup, we model Hangman as an MDP \( M = (S, A, P, r, \gamma) \):

- **Actions:** The 26 letters of the alphabet, excluding those already guessed.
- **State:** Includes the current revealed word, guessed letters, remaining attempts, word length, and optionally a category.
- **Transitions:** Picking a letter reveals matching positions, updates the state, and reduces attempts if the guess was wrong.
- **Rewards:** You get positive rewards for revealing letters, $+10$ for winning, and $-5$ for losing.
- **Goal:** Maximize the expected sum of discounted rewards over time.

**Example.**  
Suppose the hidden word is `cat` with 6 attempts:

1. Start: `_ _ _`, attempts = 6.  
2. Guess `e`: wrong → still `_ _ _`, attempts = 5.  
3. Guess `a`: correct → `_ a _`, attempts = 5.  
4. Guess `c`: correct → `c a _`, attempts = 5.  
5. Guess `t`: correct → `c a t`, win with bonus reward.  

This illustrates how actions, states, transitions, and rewards are applied in practice.

## Q-Learning with Transformer

- **Q-function:** Estimates value for each letter given the current state.
- **Action selection:** Choose randomly among valid letters with probability `epsilon`, otherwise pick the letter with the highest Q-value.
- **Target calculation (Double DQN):** Use the target network to stabilize learning by selecting the best next action according to the online network.

    **Bellman target (Double DQN).**

    $$
    y_t \;=\; r_t \;+\; \gamma \,(1-\text{done}_{t+1})\,
    Q_{\bar{\theta}}\!\big(s_{t+1},\, \arg\max_{a' \in {A}_{t+1}} Q_{\theta}(s_{t+1}, a')\big)
    $$

*Masking:* the argmax and \(Q\) are computed only over valid, unguessed letters ${A}_{t+1}$. For vanilla DQN, replace the inner term with $$\max_{a' \in {A}_{t+1}} Q_{\bar{\theta}}(s_{t+1}, a')$$.

- **Loss:** Huber loss between predicted Q-values and targets.
- **Initialization:** Start with pretrained weights or seed Q-values based on letter presence probabilities.

### Core Transformer Model
The Transformer encoder processes the partially revealed word together with guessed letters, using bidirectional attention to capture both left and right context. This allows the model to treat blanks as “masked tokens” and learn which letters are most probable given surrounding evidence. The pooled state representation provides a rich feature vector that supports both supervised pretraining (letter presence and next-letter prediction) and reinforcement learning. In the Double DQN phase, this representation helps the Q-head assign sharper Q-values, effectively turning contextual probabilities into action values for stable decision-making.

```python
class CharTransformer(nn.Module):
    def __init__(self, d_model=128, nhead=4, nlayers=2, max_len=35):
        super().__init__()
        # Core embeddings
        self.emb = nn.Embedding(VOCAB_SIZE, d_model, padding_idx=PAD_ID)
        self.pos_enc = nn.Embedding(max_len, d_model)
        self.len_emb = nn.Embedding(max_len + 1, d_model)
        self.tried_proj = nn.Linear(26, d_model)  # A–Z one-hot → d_model
        # Encoder
        enc = nn.TransformerEncoderLayer(d_model, nhead, d_model * 4, dropout=0.0,
                                         batch_first=True, norm_first=True)
        self.transformer = nn.TransformerEncoder(enc, num_layers=nlayers)
        # Heads
        self.sup_heads = SupHeads(d_model)  # pretraining
        self.q_head = None                  # added for RL
    def add_q_head(self):
        self.q_head = DuelingQHead(self.d_model)
```

### Model Design & Training Nuances

We combine token, position, length, and guessed-letter embeddings, then pool them into a fixed state. The training happens in two steps: first supervised pretraining, then DQN fine-tuning with replay and action masking. To keep learning stable, we freeze parts of the model early, use Huber loss, apply different learning rates, and optionally guide exploration with the policy head.

## Training Setup

We trained on a large dictionary of ~227k English words, filtered by maximum length for curriculum stages. To make learning smoother:

- **Curriculum:** Start with short words (2–3 letters), then gradually include 4-letter, 5-letter, and mixed-length words. This helps the agent build strategies step by step.
- **Supervised pretraining:** For each word, generate partial masks and train the model to predict presence and next-letter targets. This creates millions of supervised samples cheaply.
- **Q-learning fine-tuning:** Run episodic Hangman games against the dictionary. Each episode contributes transitions $(s_t, a_t, r_t, s_{t+1}, done)$ stored in replay memory, sampled in batches for Double DQN updates.
- **Evaluation:** After each stage, test on a held-out set of words to track solved rate, average reward, and number of guesses.

This staged approach ensures stable optimization and avoids the agent collapsing into random guessing when faced with long words early on.

### Training Dynamics: Progress Curves and Convergence

The following plots show the learning progress across curriculum stages, comparing two different reward schemes:

<div style="text-align:center;">
  <img src="{{ site.url }}/assets/2025-09-05-dqn-for-hangman-game/avg_reward.png" width="800" height="400" alt="Average reward across curriculum">
  <figcaption>Fig. 1: Average reward across curriculum (aligned episodes)</figcaption>
</div>

<div style="text-align:center;">
  <img src="{{ site.url }}/assets/2025-09-05-dqn-for-hangman-game/solved_rate.png" width="800" height="400" alt="Solved rate across curriculum">
  <figcaption>Fig. 2: Solved rate across curriculum (aligned episodes)</figcaption>
</div>



---
