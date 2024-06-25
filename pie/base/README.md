The `./requirements.txt` in this folder are the needed requirements to tag a file with pie.

The `./pie/requirements.txt` in the `pie/` folder below are needed to train pie. This needs to install a lot more pytorch & cuda stuff (because unlike just tagging a file, we need a GPU to train). We don't want this to pollute the docker container, so instead we use the lighter `./requirements.txt`.