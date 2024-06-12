# Huggingface tagger
`base/` provides a base docker image from which the specific huggingface models derive.
The base image provides the needed runtime (python, packages, `process.py`, etc.). A huggingface model simply has to derive from the base image, copy a `model.config` and the files that model.config refers to.