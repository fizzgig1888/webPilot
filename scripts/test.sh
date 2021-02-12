#!/bin/bash

test(){
    status=$(systemctl status apache2)
    echo $status
}

test
