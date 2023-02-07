

# MultiAztertest

You can test the online version of MultiAzterTest at the address http://ixa2.si.ehu.eus/aztertest

Multiaztertest is an upgrade to the Aztertest application meant to evaluate texts in various languages by calculating multiple metrics and indicators of the texts' content and analyzing those results to determine the complexity level of those texts.

If you want more information about the metrics analyzed in MultiAzterTest you can read the preprint that we have uploaded to arxiv:

https://arxiv.org/abs/2109.04870


## Install

1. Download `multiaztertest.py` and the `data`, `corpus` and `wordembeddings` folders into the same directory
2. Create and activate python environment
3. Use the following commands to install the necessary python packages:

>**pip3 install stanfordnlp**
>
>**pip3 install wordfreq**
>
>**pip3 install pandas**
>
>**pip3 install sklearn**
>
>**pip3 install --upgrade scikit-learn==0.22.1**
>
>**pip3 install --upgrade gensim**
>
>**pip install textract**

4. Follow instructions from https://fracpete.github.io/python-weka-wrapper3/install.html to install the python wrapper for Weka

## Run

Once MultiAztertest has been installed, run it using the following parameters:
```
python3 multiaztertest.py -c -r -f $dir/*.txt -l language -m model -d /home/workdirectory
```
Currently available languages: english, spanish, basque

Currently available models: stanford, cube
