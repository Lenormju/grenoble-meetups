---
title: "An introduction to the fabulous world of LeRobot 🤖"
description: "Emmanuel Virot (Wormsensing) introduces Hugging Face's LeRobot ecosystem and SpectRobot, a robot trained to identify hidden box contents by shaking them and reading tactile vibrations."
startDate: "2026-10-29"
startTime: "19:00"
groups: ["grenoble-data-science"]
location:
  name: "Cowork In Grenoble"
  address: "Cour Marcel Reymond, Rue des Minimes, Grenoble"
links:
  - url: "https://sites.google.com/view/grenobledatascience/#h.6er7hu3w0knd"
    label: "S'inscrire"
---

Not so long ago, training a robot to manipulate objects required a lab budget, proprietary hardware and a team of specialists. LeRobot, Hugging Face's open-source robotics library, is changing that. With a low-cost arm, a couple of webcams and a PC with a good GPU, anyone can now record demonstrations by teleoperation, share datasets on the Hugging Face Hub, and train state-of-the-art imitation learning policies.

This talk will be a gentle introduction to this ecosystem: how the hardware is set up, how demonstrations are collected and formatted, and which policies are available.

We'll then see how far the framework can be pushed with a concrete example: SpectRobot, our recent work (J. Rigal, E. Virot, C. Pascal, [arXiv:2609.24621](https://arxiv.org/abs/2609.24621)).

By turning vibration signals from a single tactile sensor into spectrograms that a vision encoder can read, we trained a robot arm to shake an opaque box and sort it by its hidden contents.

This is very much a story of learning by doing, and we hope sharing it will encourage others in the community to give it a try.

Speaker: Emmanuel Virot is an R&D engineer at Wormsensing. He graduated from École Centrale Paris (2011) and holds a PhD in mechanics from École Polytechnique, then continued his research at Harvard and later in startups. His work focuses on vibrations, biomechanics, haptics and signal processing, within both scientific and industrial projects.
