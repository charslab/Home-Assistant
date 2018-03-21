#!/bin/sh

sudo apt install gcc g++ portaudio19-dev libatlas-base-dev \
				 libpcre3-dev libpython-dev libpython3-dev \
				 python3-dev mplayer

wget https://kent.dl.sourceforge.net/project/swig/swig/swig-3.0.12/swig-3.0.12.tar.gz
tar xf swig-3.0.12.tar.gz
cd swig-3.0.12
./configure
make -j4
sudo make install

cd ../snowboy/swig/Python3
make
cp _snowboydetect.so ../../../
