# pie tagger
`base/` provides a base docker image from which the specific pie models derive.
The base image provides the needed runtime (python, packages, `process.py`, etc.). A pie model simply has to derive from the base image and copy the .tar model, renamed to `model.tar`.