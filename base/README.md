A tagger consist of implementation specific tagger software and a bottle server that acts as an interface between Galahad and the tagger software.

On startup (see startup.sh) the "tagger worker" launches a multiprocessing pool that (optionally) initializes the tagger software. It then monitors for any new input files that are put there by the webserver. If there are any, it processes them one by one by sending them to the tagger software. Because tagger software can be highly different, process.py interfaces them.

Each document the webserver receives gets a status object stored in the status/ folder. If a file is currently being processed by the tagger software, it gets a status object file in the process/ folder as well.

The webservice has various endpoints described in webservice.py. If an input is deleted while it is currently being processed by the tagger worker, the tagger worker kills the tagger software thread (from the multiprocessing pool) in order to stop the tagger (otherwise it would continue processing and subsequent documents would have to wait in the queue).