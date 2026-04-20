---
type: issue
state: open
created: 2026-04-19T10:52:10Z
updated: 2026-04-19T10:52:10Z
author: bernhard-42
author_url: https://github.com/bernhard-42
url: https://github.com/MorePET/mat/issues/84
comments: 0
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-04-20T04:51:02.701Z
---

# [Issue 84]: [[DISCUSSION] How to integrate with build123d and ocp vscode now?](https://github.com/MorePET/mat/issues/84)

### Description

I am very impressed about what you achieved in the last few days. However, I must admit I don't understand how things work any more. Tried to read read through your docs, PRs, and code, but decided asking might be better:

- Is it correct that with `mat` and `mat-vis-client` one doesn't need `threejs-materials` any more? (which is completely OK for me)
- Do we still need a `Material` class in `build123d`, or would `shape.material:pymat.Material` be sufficient (would be OK for me if materials all come from one side)
- Found `<material>.vis` with lazy texture options, but how do I chose one option (e.g. brushed) and when will the textures be loaded?
- How do I apply a material from pymat with textures to build123d now and how does `node.material.pbr_source` get set.

I am sure it is noted somewhere, but we have 3 repos and quite some PRs currently ...



### Context / Motivation

Integration into build123d

### Options / Alternatives

_No response_

### Open Questions

_No response_

### Related Issues

_No response_

### Changelog Category

No changelog needed
