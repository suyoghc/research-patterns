'''POINT AN ITEM IN A DICTIONARY TO ANOTHER ITEM IN THE SAME DICTIONARY????'''
'''Should I add a score to each relationship???'''
#you might find text.collocations() useful - pair of words that often occur together


import nltk
import re

brown=nltk.corpus.brown

'''Dictionary that stores expression information read from the ConfigFile'''
effectExp={}

'''To take care of cases such as ego-\ndepletion, etc.'''
def stripNewLine(sent):
    
    #print "stripNewLine"
    #print sent
    #removing words hyphenated at the end
    sent= re.sub('\s(?P<a>.*)-[\n\r\v]+(?P<b>.*)\s',' \g<a>\g<b> ',sent )
    
    #removing words hyphenated at the beginning
    sent= re.sub('\s(?P<a>.*)[\n\r\v]+-(?P<b>.*)\s',' \g<a>\g<b> ',sent )
  

    #stripping the other new lines.. with spaces before, after
    sent= re.sub('\s(?P<a>.*\s?)[\n\r\v]+(?P<b>\s?.*)\s',' \g<a> \g<b> ',sent )
    
    #for the stubborn ones
    #tokens = nltk.word_tokenize(sent)
    
    #print sent
    return sent    
    
    
    
    
'''Convert phrases mentioned in ConfigFile to expressions that that can be used with search'''
def getRegex(str):
    str=str.replace('X','([^\.]+)')
    str=str.replace('Y','([^\.]+)')
    return str

'''The ConfigFile consists of possible phrases that denote presence of IVs and DVs, and the relationships between them'''
def readConfigFile():
    f=open("DependencyPhrases.txt",'r')
    tmpStr=f.readline()
    cat=''

    while tmpStr:
        if(tmpStr[0]=='#'):
            cat=tmpStr[1:-2]
            print cat
            effectExp[cat]=[]
        elif tmpStr!='\n' and tmpStr!='\r':
            print tmpStr
            effectExp[cat].append(tmpStr[:-2])
        
        tmpStr=f.readline()
    
    #why were you getting '' at the end of every list?!
    #this will take care of it now :
    for key in effectExp.keys():
        effectExp[key]=effectExp[key][:-1]
    
    print effectExp        
    
    #demo
    print "-- read from file"
    raw_input()
    return


'''Data Structure to store variables, their relationships with other variables, and score wrt the certainty of it being one'''
class candidateVar:
    
    def __init__(self):
        self.candidateDict={}
        
    def addVar(self,varName,score=0.,affects=[],affected_by=[],features=[]):
        if(varName in self.candidateDict.keys()):
            self.candidateDict[varName]['score']+=score
            self.candidateDict[varName]['affects'].extend(affects)
            self.candidateDict[varName]['affected_by'].extend(affected_by)
            self.candidateDict[varName]['features'].extend(features)
        else:
            self.candidateDict[varName]={}
            self.candidateDict[varName]['score']=score
            self.candidateDict[varName]['affects']=affects
            self.candidateDict[varName]['affected_by']=affected_by
            self.candidateDict[varName]['features']=features
            
        
    def printCandidates(self):
        '''
        #without sorting for scores.
        for candidate in self.candidateDict:
            print candidate
            print self.candidateDict[candidate]
            print
        '''
        
        '''Sorting the dictionary based on its values - works?!'''
        for key, value in sorted(self.candidateDict.iteritems(), key=lambda (k,v): (v,k)):
            print key
            print value
            print
        


'''Extract items listed under Keywords in Papers.'''
def extractKeywords(filecontent):
    m = re.search('Keywords\n[^\n]*', filecontent)
    keywords=str(m.group(0))
    keywords=keywords[len('Keywords\n'):]
    keywords=keywords.split(', ')
    return keywords


'''Test Module'''
if __name__=='__main_':

    tmpStr1="abcd abd abc-\nabc abcd"
    tmpStr2="abcde\nabcd" # and both are words!!

    print stripNewLine(tmpStr1)


'''The real main'''
if __name__=="__main__":
    
    '''open paper/s for reading'''
    f=open("output.txt",'r')
    filecontent=f.read()

    '''Object of candidate variables created. Empty when created'''
    '''Through the course of the program, you add to candidate variables. Assign scores, relationships, etc.'''
    candidates=candidateVar()    


    '''Step 1. Looking for explicitly specified keywords. Done.'''
    keywordList= extractKeywords(filecontent)

    for keyword in keywordList:
        candidates.addVar(keyword,score=2.,features=['keyword'])
    
    candidates.printCandidates()

    
    #for demo
    if __debug__:
        print "-- step 1. keywords\n"
        raw_input()
    #@

    #######done###########



    '''Step 2.'''
    '''it contains dependency phrases'''
    readConfigFile()
    
        
    '''convert dependency phrases into regular expressions for search'''
    for key in effectExp.keys():
        for i in range (len(effectExp[key])):
            effectExp[key][i]=getRegex(effectExp[key][i])
    
    
    #output, testing if keywords are stored in the dictionary..
    for key in effectExp.keys():
        print key
        print effectExp[key]#which is a list
        print
   
 
    #remove
    #demo
    if __debug__:
        print "-- 2.1 File phrased to regex. Will use flags in the headings.."
        raw_input()
    #@


    '''Find the variables. Based on category of dependency, place variables found into appropriate slots in the dictionary.'''
    for key in effectExp.keys():
        expClass=key[-3:]
        print expClass
        
        #######this looks complex but I tried to get the (?P<>...) on re to work on this 
        xpos=-1
        ypos=-1
        if(expClass[0]=='Y'):
            ypos=0
        elif(expClass[0]=='X'):
            xpos=0
            
        if(expClass[1]=='Y'):
            ypos=1
        elif(expClass[1]=='X'):
            xpos=1
        ##################
        
        
        for i in range (len(effectExp[key])):
            effectExp[key][i]=getRegex(effectExp[key][i])
            print i
            exp=effectExp[key][i]
            
            
            x=re.findall(exp,filecontent)
        
            '''x will contain segments that match. searching for only x or only y returns a string.
            searching for both returns a tuple'''
            
            #print
            #print key
            
            
            print exp
            print x
            if len(x)>0:
                print "xpos = "+str(xpos)
                print "ypos = "+str(ypos)
                
                if isinstance(x[0],tuple):
                    #have to still add affects, affected-by, etc.
                    for tup in x:
                        candidates.addVar(stripNewLine(tup[xpos]),score=0.5,affected_by=stripNewLine(tup[ypos]),features=['phrase'])
                        
                        #candidates.addVar(stripNewLine(tup[xpos]),score=0.5,features=['phrase'])
                        candidates.addVar(stripNewLine(tup[ypos]),score=0.5,affected_by=stripNewLine(tup[xpos]),features=['phrase'])
                    #have to still strip down using chunker.
                    #tmpStr=stripNewLine(x[0][xpos])
                    #candidates.addVar(tmpStr,score=0.5,features=['phrase'])
                    
                    
                    #put x in xpos
                    #put y in ypos
                else:
                    #it's a string
                    if xpos==-1:
                        candidates.addVar(stripNewLine(x[ypos]),score=0.5,features=['phrase'])
                    else:
                        candidates.addVar(stripNewLine(x[xpos]),score=0.5,features=['phrase'])

                
                
            #raw_input()

    raw_input()

    '''Step 3. stem word approach --- pos tagging the sentences found'''
    '''#MAYBE YOU'D WANT TO DO THIS BEFORE ADDING INTO THE DICTIONARY ITSELF??'''
    
    
    
    candidates.printCandidates()
    
    x=re.findall('[^\.]* manipulat.* [^\.]*\.',filecontent)
    
    print len(x)
    for i in range(len(x)):
        tokens=nltk.word_tokenize(x[i])
        x[i]=nltk.pos_tag(tokens)
        print x[i]
        #can also train taggers - Bigram,Trigram --- on sentences
   
    #find regex for np around the key-word which might be incorrectly tagged
    #DT-NNs-word-DT-NNs
    
    
    #x=re.findall('([^\.]+) manipulated ([^\.]+)',filecontent)
    #tokens=nltk.word_tokenize(filecontent)
    #text=nltk.Text(tokens)
    #print text[1]

    #readConfigFile()
    raw_input()
    