#!/bin/sh
sudo add-apt-repository ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install python2.6 python2.6-dev fonts-ipafont-gothic fonts-vlgothic libjpeg8-dev libfreetype6-dev

mkdir src/blockdiag/tests/truetype
cp /usr/share/fonts/truetype/vlgothic/VL-PGothic-Regular.ttf src/blockdiag/tests/truetype

pip install --use-mirrors --upgrade detox misspellings
find src/ -name "*.py" | misspellings -f -
detox
