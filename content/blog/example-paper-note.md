---
title: "Notes on: Attention Is All You Need"
date: 2026-10-20
kind: paper
summary: The transformer paper — what it claims and why it mattered.
authors: Vaswani et al.
venue: NeurIPS 2017
paper_url: https://arxiv.org/abs/1706.03762
tags: [machine learning]
---

## The core idea

Replace recurrence entirely with **self-attention**, so every token can look
at every other token in a single step.

## What I found interesting

- It's highly parallel, which made training on huge data practical.
- Positional encodings are a surprisingly simple fix for losing word order.

## Open questions

What would a cognitively plausible version of attention look like?
