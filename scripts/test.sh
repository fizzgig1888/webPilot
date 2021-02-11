#!/bin/bash

test(){
    (service apache2 restart) &
}

test
