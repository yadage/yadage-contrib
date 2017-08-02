# yadage-contrib
small-scale contributions to the yadage workflow engine

This repository is meant to hold small code examples / snippets that are interesting uses / extensions to yadage, but have not spun out yet as standalone packages with their own repo -- similar to [Flask Snippets](http://flask.pocoo.org/snippets/).

## Contributing

To contibute, please fork this repo, craete a new branch and commit your snippets / code to that branch. The structure is meant to be light-weight, just create a new apprpriately named directory (preferably with its own README). If you want you can add your contributions to this README with a short 
description. 

In the TOC add 

    * [First](#youranchor)

In the 
    
    ### <a name="youranchor"></a>  Your Contribution
    
    Short paragraph describing your contribution


## Contributions

* [ZeroMQ Tracker/Socket.IO Server](#zmq)
* [shields.io markdown badges](#badges)
* [Kubernetes Backend](#kubebackend)
* [Mounted Posix State](#mountedstate)

### <a name="zmq"></a>  ZeroMQ Tracker and socket.io server

A track that publishes onto a ZeroMQ socket and a small Flask-based server that subscribes to messages and updates a javascript-based view using vis.js


### <a name="badges"></a> shields io badges for workflows

A track that publishes onto a ZeroMQ socket and a small Flask-based server that subscribes to messages and updates a javascript-based view using vis.js


### <a name="kubebackend"></a> Kubernetes Backend

An initial stab at an Kubernetes Packtivity Backend

### <a name="mountedstate"></a> Mounted Posix State

An initial stab at an state representation that comes with mount specifications (e.g for different volume drivers to be used with the kubernetes backend)