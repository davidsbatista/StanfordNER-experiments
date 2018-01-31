import sys
import re

wiki_url = 'http://pt.wikipedia.org/wiki/'

def main():
    with open(sys.argv[1], 'rt') as f_input:
        for line in f_input:
            line = line.replace(wiki_url,'').strip()
            line = re.sub(r'_\((.*?)\)','',line,re.UNICODE)
            line = line.replace("_"," ")
            print("{}\t{}".format("LOC", line))

if __name__== "__main__":
  main()