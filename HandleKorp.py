import urllib.request as urllib2
import urllib
import re
import time
from random import shuffle
from copy import deepcopy
import sys
import os

import HandleXlsx2
import HandleXlsx4


from datetime import datetime


"""
PATHS
"""
outputPath = "C:\\Users\\Hege\\Työ\\Output"
annotatedPath = "C:\\Users\\Hege\\Työ\\Annotated\\partial1"
#annotatedPath = "C:\\Users\\Hege\\Työ\\Annotated\\partial2"
#annotatedPath = "C:\\Users\\Hege\\Työ\\Annotated"
#outputPath = "Z:"
pathSep = "\\"

binPath = "C:\\Users\\Hege\\Työ\\bin"
#binPath = "Z:"
lemmaPath = binPath + pathSep + "lemmas.txt"
originalsPath = "C:\\Users\\Hege\\Työ\\orig"
translationsPath = "C:\\Users\\Hege\\Työ\\translations"


def writeGoodAndBadSentencesFromFile(filename, 
                                     dictOriginals, \
                                     dictFees, \
                                     dictTranslations, \
                                     dictLemmas, \
                                     dictSearchResults, \
                                     dictMeta):

    lstGood = []
    lstBad = []
    
    lstGoodSearches, lstBadSearches = HandleXlsx4.listSearches(originalsPath, filename)
    
    for search in lstGoodSearches:
        rid = search[0]
        korp_id = search[1]

        frameText = dictOriginals[rid][0]
        frame = getValue(frameText, "frame")
        lexunit = getValue(frameText, "lexunit_name")
        finnishFee = dictFees[rid]

        searchWords, info = getSearchWordsAndDeprels(dictOriginals[rid], \
                                                    dictTranslations[rid])
        lstWords = searchWords.split("\t")[1:]
        lstDeprels = info.split("\t")[1:]
        feeLemmas = dictLemmas[frame + "_" + lexunit + "_" + " ".join(finnishFee)]
        
        try:
            examples = dictSearchResults[rid + "__" + korp_id]
        except:
            print("dictionarysta puuttuu :: " + rid + "__" + korp_id)
            raise Exception
            #return dictSearchResults
        
        meta = dictMeta[rid]

        for example in examples:
            #print(example[:30])
            searchMethod = getSearchMethod(lstWords, lstDeprels, feeLemmas, example, rid)
            #print(lstWords)

        #print("for käyty läpi")

        searchMethodPlus = "\t".join(searchMethod)
        lstGood.append("\t".join((rid, korp_id, searchMethodPlus)))
        #print("append käyty läpi")

    print("KOKO looppaus käyty läpi")
    print("goodFile 1 :: " + binPath + pathSep + "goodSearches.txt")
    fil = filename.split(pathSep)[-1]
    fil = ".".join(fil.split(".")[:-1])
    goodFile = open(binPath + pathSep + "goodSearches_" + fil + ".txt", "w", encoding="cp1252")
    print("goodFile :: " + str(goodFile))
    for good in lstGood:
        goodFile.write(good)
        goodFile.write("\n")
    goodFile.close()



    print("Kirjoitetaan hakumetodeineen huonot haut tiedostoon")
    for search in lstBadSearches:
        rid = search[0]
        korp_id = search[1]

        frameText = dictOriginals[rid][0]
        frame = getValue(frameText, "frame")
        lexunit = getValue(frameText, "lexunit_name")
        finnishFee = dictFees[rid]

        searchWords, info = getSearchWordsAndDeprels(dictOriginals[rid], \
                                                    dictTranslations[rid])
        lstWords = searchWords.split("\t")[1:]
        lstDeprels = info.split("\t")[1:]
        feeLemmas = dictLemmas[frame + "_" + lexunit + "_" + " ".join(finnishFee)]
        
        examples = dictSearchResults[rid + "__" + korp_id]
        meta = dictMeta[rid]

        for example in examples:
            searchMethod = getSearchMethod(lstWords, lstDeprels, feeLemmas, example, rid)

        searchMethodPlus = "\t".join(searchMethod)
        lstBad.append("\t".join((rid, korp_id, searchMethodPlus)))

    fil = filename.split(pathSep)[-1]
    fil = ".".join(fil.split(".")[:-1])
    badFile = open(binPath + pathSep + "badSearches_" + fil + ".txt", "w", encoding="cp1252")
    for bad in lstBad:
        badFile.write(bad)
        badFile.write("\n")
    badFile.close()


def getSentenceIDs():
    """
    Gets all the used search methods from all the annotated files and writes the results into files
    NOT TESTED!
    """

    print("Haetaan alkuperäisistä ja käännöksistä hakusanat ja deprelit")
    dictTranslations, dictOriginals, dictFees = getAllFrameLUs()

    dictFrameText = {}
    for key in dictOriginals.keys():
        frameText = getFrameText(dictOriginals[key][0])
        dictFrameText[frameText] = key

            
    #print("Haetaan annotoiduista tiedostoista kaikki hakutulokset")
    #lstGoodSearches, lstBadSearches = HandleXlsx4.listSearches(originalsPath, annotatedPath)
    print("Haetaan lähetetyistä tiedostoista kaikki hakutulokset")
    dictSearchResults, dictMeta = getSearchResultsFromFolder(dictFrameText)
    #return dictSearchResults, dictFrameText
    #lstGood = []
    #lstBad = []

    #return dictSearchResults, dictMeta
    
    print("Haetaan tiedostosta soveliaat lemmat")
    dictLemmas = getRealLemmasFromFile(lemmaPath)

    print("Haetaan annotoiduista tiedostoista kaikki hakutulokset")
    for filename in os.listdir(annotatedPath):
        if ((os.path.isdir(annotatedPath + "\\" + filename)) == False):
            print(filename)
            try:
                writeGoodAndBadSentencesFromFile(annotatedPath + pathSep + filename, \
                                             dictOriginals, \
                                             dictFees, \
                                             dictTranslations, \
                                             dictLemmas, \
                                             dictSearchResults, \
                                             dictMeta)
            except:
                return dictSearchResults, dictMeta
                pass
        else:
            pass



    """    
    print("Kirjoitetaan hakumetodeineen hyvät haut tiedostoon")
    for search in lstGoodSearches:
        rid = search[0]
        korp_id = search[1]

        frameText = dictOriginals[rid][0]
        frame = getValue(frameText, "frame")
        lexunit = getValue(frameText, "lexunit_name")
        finnishFee = dictFees[rid]

        

        searchWords, info = getSearchWordsAndDeprels(dictOriginals[rid], \
                                                    dictTranslations[rid])
        lstWords = searchWords.split("\t")[1:]
        lstDeprels = info.split("\t")[1:]
        feeLemmas = dictLemmas[frame + "_" + lexunit + "_" + finnishFee[0]]
        
        try:
            examples = dictSearchResults[rid + "__" + korp_id]
        except:
            print("dictionarysta puuttuu :: " + rid + "__" + korp_id)
            return dictSearchResults
        
        meta = dictMeta[rid]

        for example in examples:
            #print(example[:30])
            searchMethod = getSearchMethod(lstWords, lstDeprels, feeLemmas, example, rid)
            #print(lstWords)

        #print("for käyty läpi")

        searchMethodPlus = "\t".join(searchMethod)
        lstGood.append("\t".join((rid, korp_id, searchMethodPlus)))
        #print("append käyty läpi")

    print("KOKO looppaus käyty läpi")
    print("goodFile 1 :: " + binPath + pathSep + "goodSearches.txt")
    goodFile = open(binPath + pathSep + "goodSearches.txt", "w", encoding="cp1252")
    print("goodFile :: " + str(goodFile))
    for good in lstGood:
        goodFile.write(good)
        goodFile.write("\n")
    goodFile.close()



    print("Kirjoitetaan hakumetodeineen huonot haut tiedostoon")
    for search in lstBadSearches:
        rid = search[0]
        korp_id = search[1]

        frameText = dictOriginals[rid][0]
        frame = getValue(frameText, "frame")
        lexunit = getValue(frameText, "lexunit_name")
        finnishFee = dictFees[rid]

        searchWords, info = getSearchWordsAndDeprels(dictOriginals[rid], \
                                                    dictTranslations[rid])
        lstWords = searchWords.split("\t")[1:]
        lstDeprels = info.split("\t")[1:]
        feeLemmas = dictLemmas[frame + "_" + lexunit + "_" + finnishFee[0]]
        
        examples = dictSearchResults[rid + "__" + korp_id]
        meta = dictMeta[rid]

        for example in examples:
            searchMethod = getSearchMethod(lstWords, lstDeprels, feeLemmas, example, rid)

        searchMethodPlus = "\t".join(searchMethod)
        lstBad.append("\t".join((rid, korp_id, searchMethodPlus)))


    badFile = open(binPath + pathSep + "badSearches.txt", "w", encoding="cp1252")
    for bad in lstBad:
        badFile.write(bad)
        badFile.write("\n")
    badFile.close()
    """

def getSearchResultsFromFolder(dictFrameText):
    """
    Method for getting the metadata and the search results from multiple folders
    Returns a tuple of two dictionaries 1) dictSearchResults 2) dictMeta
      dictSearchResults[rid] = list of Korp sentences
      dictMeta[rid] = metadata
    NOT TESTED!
    """

    path = outputPath + pathSep
    #lstRids = []
    lstMeta = []
    lstSearchResults = []

    meta, searchResults = getSearchResultsFromTextFiles(dictFrameText, path + "utf8", encoding="utf8")
    lstMeta.extend(meta)
    lstSearchResults.extend(searchResults)
    
    meta, searchResults = getSearchResultsFromTextFiles(dictFrameText, path + "05-15")
    lstMeta.extend(meta)
    lstSearchResults.extend(searchResults)

    meta, searchResults = getSearchResultsFromTextFiles(dictFrameText, path + "16-50", "fixed")
    lstMeta.extend(meta)
    lstSearchResults.extend(searchResults)

    meta, searchResults = getSearchResultsFromTextFiles(dictFrameText, path + "comp")
    lstMeta.extend(meta)
    lstSearchResults.extend(searchResults)

    meta, searchResults = getSearchResultsFromTextFiles(dictFrameText, path + "nolla", "_nolla_")
    lstMeta.extend(meta)
    lstSearchResults.extend(searchResults)

    meta, searchResults = getSearchResultsFromTextFiles(dictFrameText, path + "nsubj_dobj")
    lstMeta.extend(meta)
    lstSearchResults.extend(searchResults)

    meta, searchResults = getSearchResultsFromTextFiles(dictFrameText, path + "poss")
    lstMeta.extend(meta)
    lstSearchResults.extend(searchResults)

    meta, searchResults = getSearchResultsFromTextFiles(dictFrameText, path + "preps")
    lstMeta.extend(meta)
    lstSearchResults.extend(searchResults)

    meta, searchResults = getSearchResultsFromTextFiles(dictFrameText, path + "sillsallad1")
    lstMeta.extend(meta)
    lstSearchResults.extend(searchResults)

    meta, searchResults = getSearchResultsFromTextFiles(dictFrameText, path + "sillsallad2")
    lstMeta.extend(meta)
    lstSearchResults.extend(searchResults)

    meta, searchResults = getSearchResultsFromTextFiles(dictFrameText, path + "varia")
    lstMeta.extend(meta)
    lstSearchResults.extend(searchResults)

    meta, searchResults = getSearchResultsFromTextFiles(dictFrameText, path + "varia2plus")
    lstMeta.extend(meta)
    lstSearchResults.extend(searchResults)

    #print(len(lstSearchResults))
    #print(lstSearchResults[0])
    
    dictMeta = {}
    dictSearchResults = {}
    
    try:    
        for searchResult in lstSearchResults:
            korpId = getValue(searchResult[1], "korpId")
            addToDict(dictSearchResults, \
                      searchResult[0] + "__" + korpId, \
                      searchResult[1], \
                      addCount=False, \
                      appendToList=True)
    except:
        print("")
        print("")
        print("* +")
        print(searchResult[0])
        print("** ++")
        #print(lstMeta[0][1][:30])
        print("*** +++")
        print(searchResult[1])
        print("**** ++++")
        #print(searchResult[1][1][:30])
        raise Exception
        #dictSearchResults[searchResult[0]] = searchResult[1]
    #print(len(dictSearchResults))    
    for meta in lstMeta:
        dictMeta[meta[0]] = meta[1]
    
    return dictSearchResults, dictMeta


def getSearchResultsFromTextFiles(dictFrameText, foldername, additionalReq = "", encoding="cp1252"):
    """
    Iterates through folder and parses all the files there
    Returns a tuple of 1) list of metadata 2) list of search results
      metadata[0]: rid
      metadata[1]: metadata
      searchResult[0]: rid
      searchResult[1]: a single sentence from Korp (incl. deprels and the works)
    NOT TESTED!
    """
    lstMeta = []
    lstSearchResults = []

    if os.path.isdir(foldername) == False:
        print("Polkua " + foldername + " ei löytynyt. Jatketaan silti.")
        return [], []
    
    for filename in os.listdir(foldername):
        #print(filename)
        if additionalReq in filename:

            f = open(foldername + pathSep +filename, "r", encoding=encoding, newline='')
            text = f.read()
            f.close()

            if "05-15" in foldername:
                # Muuta serial vastaamaan oikeasti sarjanumeroa
                serial = int(re.match("output_([0-9]+)\.txt", filename).groups()[0])
                if serial >= 5:
                    if "*** Tästä puuttuu metatietoja" in text:
                        new_examples = []
                        examples = []
                        exempla = re.split("([0-9]+frame)", text)
                        for exemplum in exempla:
                            if "*** Tästä puuttuu metatietoja" in exemplum:
                                nova_exempla = re.split("([0-9]+\*\*\* Tästä puuttuu metatietoja \*\*\*)", exemplum)
                                for nova_exemplum in nova_exempla:
                                    new_examples.append(nova_exemplum.replace("*** Tästä puuttuu metatietoja ***", "frame="))
                                    #print(nova_exemplum.replace("*** Tästä puuttuu metatietoja ***", "frame="))
                            else:
                                new_examples.append(exemplum)

                        for i in range(1, len(new_examples)):
                            if re.match("[0-9]+frame", new_examples[(i-1)]):
                                examples.append(new_examples[(i-1)] + new_examples[i])
                            
                        #examples = new_examples
                    else:
                        exempla = re.split("\n([0-9]+frame)", text)
                        examples = []
                        examples.append(exempla[0])
                        for i in range(2, len(exempla), 2):
                            examples.append(exempla[(i-1)] + exempla[i])
                elif filename == "output_1.txt":
                    # NB! Not the same as output_01.txt!
                    examples = text.split("\nframe=")
                    j = 0
                    for ex in examples:
                        # I know this is stupid, but I'm tired and just want this to finally work
                        if j != 0:
                            ex = "frame=" + ex
                        j += 1
                        
                else:                                      
                    examples = text.split("\nrid=")
                    
                
                
            elif "utf8" in foldername:
                #f = open(foldername + pathSep +filename, "r", encoding="cp1252", newline='')
                #text = f.read()
                #f.close()
                examples = text.split("\nrid=")
                #print("2 LENGTH OF EXAMPLES: " + str(len(examples)))
                #for ex in examples:
                #      print(ex[0:100].replace("\n", ";"))
                #for char in text[:100]:
                #    print(char + "\t" + str(ord(char)))
            else:
                examples = text.split("\nrid=")
                
               
            #if len(examples) == 1:
            #    print(filename)
            #    return examples, None
            #    print(filename)
            #    raise Exception

            ex_iteration = False
            
            for example in examples:
                #if "output_05" in filename:
                #    print("5-15")
                    
                if len(example) == 0:
                    continue

                ridMatch = re.match("[0-9]+", example)


                #if "output_05" in filename:
                    #if ridMatch is None:
                        #print(example)
                        #print(len(example))
                        #raise Exception
                        #continue
                    #if ridMatch.group() != "138756":
                    #    print(ridMatch)
                    #else:
                    #    raise Exception
                if ridMatch is None:
                    if example.startswith("rid="):
                        ridMatch = re.search("rid=([0-9]+)", example)
                    elif re.match('"[0-9]+"', example):
                        ridMatch = re.search("[^\d]+([0-9]+)", example)

                    if ridMatch is None:
                        examps = example.split("frame=")
                        if len(examps) == 1:
                            print(example)
                            print("len(example) = " + str(len(example)))
                            print(foldername + pathSep + filename)
                            print("Virhe: ridiä ei löytynyt Excelistä")
                            raise Exception
                        else:
                            ex_iteration = True
                            for ex in examps:
                                if len(ex) > 50:
                                    try:
                                        rid = getRids("frame=" + ex, dictFrameText)[0]
                                    except:
                                        print("*** *** *** *** ERROR *** *** *** ***")
                                        print(ex[0:100])
                                        raise Exception
                                    sentences = ex.split("KLK_FI_")
                                    for sentence in sentences[1:]:
                                        lstSearchResults.append((rid, sentence))
                                    lstMeta.append((rid, sentences[0]))
                    else:
                        rid = ridMatch.groups()[0]


                    #else:
                        #examps = example.split("frame=")
                        #if len(examps) == 1:
                        #    print(example)
                        #    print("len(example) = " + str(len(example)))
                        #    print(foldername + pathSep + filename)
                        #    print("Virhe: ridiä ei löytynyt Excelistä")
                        #    raise Exception
                        #else:
                        #    ex_iteration = True
                        #    for ex in examps:
                        #        if len(ex) > :
                                    #rid = getRids("frame=" + ex, dictFrameText)[0]
                        sentences = example.split("KLK_FI_")
                        for sentence in sentences[1:]:
                            lstSearchResults.append((rid, sentence))
                        lstMeta.append((rid, sentences[0]))
                                
                        
                        #raise Exception
                else:
                    rid = ridMatch.group()

                
                if ex_iteration == False:
                    #print("EX_ITERATION == FALSE")
                    #sentences = ex.split("KLK_FI_")
                    #else:
                    sentences = example.split("KLK_FI_")

                    #print(len(sentences))
                    for sentence in sentences[1:]:
                        #if rid == "78392":
                        #    print()
                        #    print("\t78392")
                        #    print(sentence[:40])
                        #    print("*****")
                
                        lstSearchResults.append((rid, sentence))
                    lstMeta.append((rid, sentences[0]))
                #if rid == "138756":
                #    raise Exception
    if lstSearchResults == []:
        print()
        print()
        print()
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print(lstSearchResults)
        raise Exception
    #print(len(lstSearchResults))
    #print("*")
    #print(lstMeta[0][0])
    #print("**")
    #print(lstMeta[0][1][:30])
    #print("***")
    #print(lstSearchResults[0][0])
    #print("****")
    #print(lstSearchResults[0][1][:30])
    return lstMeta, lstSearchResults


def getSearchMethod(lstWords, lstDeprels, feeLemmas, example, rid, retry=False):
    """
    Gets the same parameters as the search methods themselves, plus the returned Korp sentences
    Returns the code for the search method (1, 2, 3, 4left, 4right, 5left ... 11)
    NOT TESTED!
    """

    #lines = example.split("\r\n")
    lines = re.split("\r|\n|\s|\t", example)

    #print("+++++++++++++ +++ +++ +++++++++++++")
    #print()
    #print(lstWords)
    #print()
    #print(lstDeprels)
    #print()
    #print("+++++++++++++ +++ +++ +++++++++++++")
    
    # Oletusarvona kaikille hakukriteereille on True
    # Arvo muutetaan Falseksi, jos aihetta löytyy
    # OBS! Poikkeuksena partial_lemmas, joka toimii päinvastoin
    # Se taas johtuu laiskuudesta
    lc_deprels = True
    rc_deprels = True
    fee_deprels = True
    lc_words = True
    rc_words = True
    fee_words = True
    fee_lemmas = True
    partial_lemmas = False
    partial_words = False
    lc_deprels_partial = False
    rc_deprels_partial = False
    
    new_lines = []
    found = False
    feePos = 0
    orig_feePos = -999
    
    for line in lines:
        if line.startswith('"*"'):
            new_lines.append(line)
            found = True

    """
    if (len(new_lines) != example.replace("***", "").count("*")):
        #for char in new_lines[0]:
        #    print(str(char) + "::" + str(ord(char)))
        i = 1
        print("Asteriskit eivät täsmää rivien määrään.")
        for line in new_lines:
            print("___")
            print(i)
            print(line)
            print("---")
            print(example)
            i += 1
        raise Exception
    """        
    if found == False:
        for line in lines:
            print("****" + line + "*")
        print("****" + "\t" + "*****")
        for word in lstWords:
            print(word)
        print("****" + "\t" + "*****")
        for deprel in lstDeprels:
            print(deprel)
        print("****" + "\t" + "*****")
        print(feeLemmas)
        print("****" + "\t" + "*****")

        # Tällainenkin löytyi.
        return ("ASTERISKI PUUTTUU", "NA")

    
    # Skipataan tällaiset, niin se on aiemminkin tehty
    if len(lstWords) != len(lstDeprels):
        return None

    #print('*******')
    #print(lstWords)
    #print(lstDeprels)
    #print(feeLemmas)
    #print(rid)
    
    new_lstWords = []
    new_lstDeprels = []
    new_feeWords = []
    fee_passed = False
    lstLc_deprels = []
    lstRc_deprels = []
    lstLc_word_count = []
    lstRc_word_count = []
    switched_order = False
    
    if found:
        fee_length = 0
        for i in range(0,len(lstWords)):
            words = lstWords[i].split(" ")
            if lstDeprels[i].startswith("FEE"):
                fee_passed = True
                fee = lstWords[i].split(" ")
                #print(fee)
                #if "tölkillinen" in fee.lower():
                #    print(fee)
                for feeWrd in fee:
                    new_feeWords.append(feeWrd.lower())
                feePos = i
                if orig_feePos < 0:
                    orig_feePos = len(new_lstWords)

                if len(words) != 1:
                    if feePos == i:
                        fee_deprels = False
                        if (("empty" in lstWords[i]) == False):
                            fee_length += len(words)
                    elif feePos == 0:
                        lc_deprels = False
                    else:
                        rc_deprels = False
                
                    for word in words:
                        new_lstWords.append(word.lower())
                        new_lstDeprels.append("")
                else:
                    if (("empty" in lstWords[i]) == False):
                        fee_length += 1
                    new_lstWords.append(words[0])
                    new_lstDeprels.append(lstDeprels[i])
            else:
                for word in words:
                    new_lstWords.append(word.lower())
                    new_lstDeprels.append(lstDeprels[i])
                if fee_passed:
                    for word in words:
                        lstRc_deprels.append(lstDeprels[i])
                    lstRc_word_count.append(len(words))
                else:
                    for word in words:
                        lstLc_deprels.append(lstDeprels[i])
                    lstLc_word_count.append(len(words))
                    #lstLc_deprels.extend([lstDeprels[i]] * len(words))
                    
    lemmas = feeLemmas.split(" ")
    # Luodaan lemmas[], joka on samankokoinen kuin new_lstWords
    # Lemmoja hauissa on ollut ainoastaan FEE:ssä
    """
    lemmas = [""] * (orig_feePos -1)
    lemmas_split = feeLemmas.split(" ")
    lemmas.extend(lemmas_split)
    tmp_lemmas = [""] * (len(new_lstWords) - (orig_feePos + fee_length))
    
    for split_lemma in reversed(lemmas_split):
        try:
            lemmas[(orig_feePos -1)] = split_lemma
        except:
            print(lemmas)
            print("****")
            print(lemmas_split)
            print("****")
            print(orig_feePos)
            print("****")
            print(feeLemmas)
            print("****")
            print(lines)
            print("****")
            raise Exception
    """
    m = 0

    i = 0
    startPoint = -999
    AllesIstGut = False
    for k in range(0, len(new_lines)):
        line, word, lemma, deprel = getCriteriaFromSentFile(new_lines, k)

        if (i >= len(new_feeWords)):
            print(new_feeWords)
            print(i)
            print(new_lines)
            raise Exception
        
        elif ((i < len(lemmas)) and \
           ((lemma == lemmas[i]) or \
            (isPartialMatch(lemma, lemmas[i])) or \
            (word == new_feeWords[i]) or \
            (isPartialMatch(word, new_feeWords[i])))):

            
        #if (word == new_feeWords[i]) or (lemma == lemmas[i]) or \
        #   isPartialMatch(lemma, lemmas[i]) or \
        #   isPartialMatch(word, new_feeWords[i]):
            #print("\t*************")
            #print("\ti:    " + str(i))
            #print("\t " + "\n".join(new_lines))
            #print("\tk:    " + str(k))
            #print("\t " + "\n".join(new_feeWords))
            if startPoint < 0:
                if (word != new_feeWords[i]) and \
                   (len(new_lines) > (i+1)):
                    line, word2, lemma, deprel = getCriteriaFromSentFile(new_lines, (i+1))
                    if (word2 == new_feeWords[i]):
                        #print("NYT OSUI")
                        #print("OSUI; " + word + "; " + "* ".join(new_feeWords) + " " + str(i))
                        continue
                #print("OSU!" + word + "; " + "* ".join(new_feeWords) + " " + str(i))
                #print("\t" + " ----- ".join(lstWords))
                startPoint = k
                i = 0
                no_match = False
            elif (word == new_feeWords[i]) and \
                 (fee_words == False):
                # Hätäpurkka
                # Edellinen rivi on täsmäytynyt lemmalla, mutta seuraava täsmäytyykin itse sanalla
                startPoint = k
                i = 0
                no_match = False
                partial_words = False
                partial_lemmas = False
                fee_words = True
                fee_lemmas = True
                #print("OSUMA!")
                
            if (startPoint + fee_length) > len(new_lines):
                maxIter = len(new_lines)
            else:
                maxIter = (startPoint + fee_length)
            
            for l in range(startPoint, maxIter):
                try:
                    line, word, lemma, deprel = getCriteriaFromSentFile(new_lines, l)
                        
                except:
                    print(new_lines)
                    print(l)
                    print(startPoint)
                    print((startPoint + fee_length))
                    print(new_lstWords)
                    print(new_feeWords)
                    raise Exception

                # Osittaiset osumat
                if isPartialMatch(word, new_feeWords[i]):
                    partial_words = True
                    fee_words = False

                try:                       
                    if (len(lemmas) < (i + 1)):
                        # Lemmaan kuuluvia sanoja on vähemmän kuin FEE-osumassa
                        # Tällöin lemmat eivät ole voineet olla osumakriteeri
                        fee_lemmas = False
                        if (word != new_feeWords[i]):
                            #print("NO MATCH:" + word)
                            #print("NO MATCH 2: " + new_feeWords[i])
                            #print("NO MATCH 3: " + "; ".join(new_feeWords))
                            no_match = True
                    elif (word != new_feeWords[i]) and (lemma != lemmas[i]) and \
                       ((".*" in lemmas[i]) == True):
                        #print("NO MATCH:" + word)
                        #print("NO MATCH 2: " + new_feeWords[i])
                        #print("NO MATCH 3: " + "; ".join(new_feeWords))
                        #print("NO MATCH 4: " + lemma)
                        #print("NO MATCH 5: " + lemmas)
                        #no_match = True
                        if isPartialMatch(lemma, lemmas[i]):
                            partial_lemmas = True
                            fee_lemmas = False
                        else:
                            no_match = True

                    #print("Täällä ollaan")
                    #try:
                    # Osittaiset lemmat
                    if (len(lemmas) < (i + 1)):
                        fee_lemmas = False
                        #print("Täällä ollaan taas")
                    elif isPartialMatch(lemma, lemmas[i]):
                        partial_lemmas = True
                        fee_lemmas = False
                        #print("Täällä ollaan vieläkin,\tlemma = " + lemma)
                except:
                    print(i)
                    print(lemma)
                    print(lemmas)
                    print(new_feeWords)
                    raise Exception
                
                # Poistutaan sisemmästä luupista ja yritetään seuraavasta uudestaan
                if no_match:
                    i = 0
                    startPoint = -999
                    break
            
                # Viimeinenkin täsmää
                if (l == ((startPoint + fee_length) -1)):
                    if (len(new_feeWords) > (i+1)) and \
                       (word == new_feeWords[(i+1)]) and \
                        (fee_words == False):
                            print("OSUIKO")
                            print("* " + word)
                    else:
                        #print("AllesIstGut: " + word)
                        #print(fee_words)
                        #print(new_feeWords)
                        #print(i)
                        
                        AllesIstGut = True
                    
                i += 1
        else:
            #if (word == new_feeWords[i]) and \
            #    (fee_words == False):
            #    print("OSUI SITTENKIN")
            pass
            #if lemma = "repeytyä":
            #    for q in range(len(lemma)):
                    
            #print("\t*************")
            #print("\ti:    " + str(i))
            #print("\t " + "\n".join(new_lines))
            #print("\tk:    " + str(k))
            #print("\t " + "\n".join(new_feeWords))
            #print("\tlemma : " + lemma)
            #print("\tlemmas : " + "; ".join(lemmas))
            #print((i < len(lemmas)))
            #print("** 1 **")
            #print(((lemma == lemmas[i])))
            #print("** 2 **")
            #print(isPartialMatch(lemma, lemmas[i]))
            #print("** 3 **")
            #print((word == new_feeWords[i]))
            #print("** 4 **")
            #print((isPartialMatch(word, new_feeWords[i])))
            #print("** 5 **")
            #print((lemmas == lemmas[i]) or \
            #(isPartialMatch(lemma, lemmas[i])) or \
            #(word == new_feeWords[i]) or \
            #(isPartialMatch(word, new_feeWords[i])))
            #print()
        if AllesIstGut:
            
            left_context = new_lines[0:startPoint]
            right_context = new_lines[(startPoint + fee_length):]
            fee = new_lines[startPoint:(startPoint + fee_length)]
            #break
            
            #if (retry == False) and (len(left_context) > len(lstLc_deprels)):
            if (retry == False) and \
               (len(left_context) != sum(lstLc_word_count)):
                #print("RETRY1")
                line, word, lemma, deprel = getCriteriaFromSentFile(new_lines, (startPoint -1))
                #print(word)
                #print("1 *")
                #print("new_lines\n" + "\n".join(new_lines))
                #print("2 *")
                #print("feePos: " + str(feePos))
                #print("startPoint: " + str(startPoint))
                #print("3 *")
                #print("new_lstWords: " + "\n".join(new_lstWords))
                #print("4 *")
                #print("left_context: " + "\n".join(left_context))
                #print("5 *")
                #print("lstLc_deprels: " + "\n".join(lstLc_deprels))
                #print("6 *")
                #print("lstWords: " + "\n".join(lstWords))
                #raise Exception
                
                if word == new_lstWords[(startPoint)].lower():
                    #print("RETRY1,5")
                    line, word, lemma, deprel = getCriteriaFromSentFile(new_lines, startPoint)
                    #if (word == new_lstWords[(startPoint-1)].lower()):
                    if (word == new_lstWords[(startPoint-1)].lower()) or \
                       (isPartialMatch(word, new_lstWords[(startPoint-1)].lower())):
                        #print("\tRETRY2")
                        #print(lstDeprels)
                        #print(lstWords)
                        lstDeprels[(startPoint-1)], lstDeprels[startPoint] = \
                                                lstDeprels[startPoint], lstDeprels[(startPoint-1)]
                        lstWords[(startPoint-1)], lstWords[startPoint] = \
                                                  lstWords[startPoint], lstWords[(startPoint-1)]
                        #print(lstWords)
                        #print(lstDeprels)
                        #print(lstDeprels)
                        #print(new_lstWords)
                        searchMethod = getSearchMethod(lstWords, \
                                                       lstDeprels, \
                                                       feeLemmas, \
                                                       example, \
                                                       rid, \
                                                       True)
                        method = searchMethod[0] + "switched_order"
                        #searchMethod[0] = method
                        return method, searchMethod[1]
                #elif word.endswith(new_lstWords[startPoint]):
                #    if startPoint > 0:
                #        if word.startswith(new_lstWords[(startPoint-1)]):
                #            searchMethod = getSearchMethod(lstWords, \
                #                                       lstDeprels, \
                #                                       feeLemmas, \
                #                                       example, \
                #                                       rid, \
                #                                       True)
                                   
                elif (startPoint >= 2) and (word == new_lstWords[(startPoint -2)]):
                    #print("Offset Two")
                    line, word, lemma, deprel = getCriteriaFromSentFile(new_lines, (startPoint-2))
                    if word == new_lstWords[(startPoint)]:
                        line, word, lemma, deprel = getCriteriaFromSentFile(new_lines, (startPoint))
                        if word == new_lstWords[(startPoint-1)]:
                            print("RETRY: Offset Two")
                            lstDeprels[(startPoint-2)], lstDeprels[(startPoint-1)], lstDeprels[startPoint] = \
                                                                    lstDeprels[startPoint], \
                                                                    lstDeprels[(startPoint-2)], \
                                                                    lstDeprels[(startPoint-1)]
                            lstWords[(startPoint-2)], lstWords[(startPoint-1)], lstWords[startPoint] = \
                                                      lstWords[(startPoint)], lstWords[(startPoint-1)], lstWords[(startPoint-1)]
                            
                                
                                        
                            
                            searchMethod = getSearchMethod(lstWords, \
                                                       lstDeprels, \
                                                       feeLemmas, \
                                                       example, \
                                                       rid, \
                                                       True)
                            method = searchMethod[0] + "switched_order"
                            return method, searchMethod[1]
                elif word == new_lstWords[(startPoint+1)]:
                    #print("RETRY 5")
                    line, word, lemma, deprel = getCriteriaFromSentFile(new_lines, startPoint)
                    if word == new_lstWords[(startPoint-1)]:
                        print("RETRY 8")
                        lstDeprels[(startPoint+1)], lstDeprels[startPoint] = \
                                                lstDeprels[startPoint], lstDeprels[(startPoint+1)]
                        lstWords[(startPoint+1)], lstWords[startPoint] = \
                                                  lstWords[startPoint], lstWords[(startPoint+1)]
                        #print(lstDeprels)
                        #print(new_lstWords)
                        searchMethod = getSearchMethod(lstWords, \
                                                       lstDeprels, \
                                                       feeLemmas, \
                                                       example, \
                                                       rid, \
                                                       True)
                        method = searchMethod[0] + "switched_order"
                        #searchMethod[0] = method
                        return method, searchMethod[1]
                                          
                elif word == ",":
                    #print("RETRY comma")
                    line, word, lemma, deprel = getCriteriaFromSentFile(new_lines,(startPoint-2))
                    #print("word:" + word)
                    #print("new_lstWords: " + "; ".join(new_lstWords))
                    if new_lstWords[startPoint].startswith(word):
                        #print("RETRY comma 3")
                        line, word, lemma, deprel = getCriteriaFromSentFile(new_lines, (startPoint))
                        #print("word:" + word)
                        if word == new_lstWords[(startPoint-1)]:
                            print("RETRY comma 4")
                            lstDeprels[(startPoint-1)], lstDeprels[(startPoint)] = \
                                       lstDeprels[startPoint], lstDeprels[(startPoint-1)]
                            lstWords[(startPoint-1)], lstWords[startPoint] = \
                                       lstWords[startPoint], lstWords[(startPoint-1)]
                            #print(lstDeprels)
                            #print(lstWords)
                            searchMethod = getSearchMethod(lstWords, \
                                                           lstDeprels, \
                                                           feeLemmas, \
                                                           example, \
                                                           rid, \
                                                           True)
                            method = searchMethod[0] + "switched_order"
                            #searchMethod[0] = method
                            return method, searchMethod[1]
                        
               #(lstWords[feePos])
               # right_context, left_context = left_context, right_context
               # switched_order = True
            
            break
        
    if AllesIstGut != True:
        for wrd in lstWords:
            if ("-" in wrd) or (".*" in wrd):
            
                print("_*_*_*_*_*_*_*_*_*_*_*")
                #print("\tFAILED AllesIstGut")
                #print(example[:40])
                #print("_____")
                print("\t" + "\n\t".join(new_lines))
                print("_____")
                print(lstWords)
                print(startPoint)
                print(fee_length)
                #print(new_lstWords)
                #print("; ".join(word))
                print(i)
                print(new_feeWords)
                #print(lstWords)
                #print("\tlemma : " + lemma)
                print("\tlemmas : " + "; ".join(lemmas))            
                #print(lstDeprels)
                #print(feeLemmas)
                #print(lemmas)
                break        
        return ("FAIL\t" + word + "\t" + ";".join(lstWords), "N/A")
    
    #for k in range(new_feePos, (new_feePos + fee_length)):
    m = 0
    #k = startPoint
    k = orig_feePos
    for pos in range(0, len(fee)):
        try:
            line, word, lemma, deprel = getCriteriaFromSentFile(fee, pos)
        except:
            print("orig_feePos : " + str(orig_feePos))
            print("fee_length : " + str(fee_length))
            print("new_lines : \n\t")
            print(new_lines)
            print("new_lstWords : \n\t")
            print(new_lstWords)
            print("lstWords : \n\t")
            print(lstWords)
            print("fee : ")
            print(fee)
            #print("fee_line")
            #print(fee_line)
            raise Exception
        
        # Katsotaan ensin, kuinka FEE täsmäytyi
        
        #if word != new_lstWords[k]:
        #if (lemmas == ['ääri','myöten','täysi']) or \
        #   (new_lstWords == ['juovittamalla']) or \
        #   (lemmas == ['jalokivikoristeinen']):
        #if lemmas == ['sukkahousut']:
        #    print("FEE")
        #    print(fee)
        #    print(word)
        #    print(new_lstWords)
        #    print("*")
        #    print(deprel)
        #    print(lemma)
        #    print(new_lstDeprels)
        #    print(lemmas)
        #    print("**")
        #    #raise Exception
        if word != new_lstWords[k].lower():
            fee_words = False
            
        if new_lstDeprels[k].startswith("FEE|"):
            if deprel != new_lstDeprels[k][4:]:
                fee_deprels = False

        if (len(lemmas) < (m + 1)):
            fee_lemmas = False
        elif lemmas[m] != lemma:
            fee_lemmas = False
        m += 1
        k += 1


    m = 0
    j = 0
    #if new_feePos != 0:
    if len(left_context) != 0:
        lc_exists = True
        
        for k in range(0, len(left_context)):
            line, word, lemma, deprel = getCriteriaFromSentFile(left_context, k)
            
            
            if (word != new_lstWords[k].lower()):
                lc_words = False
            #if (deprel != new_lstDeprels[m]):
            #    lc_deprels = False
            try:
                if deprel != lstLc_deprels[j]:
                    lc_deprels = False
            except:
                print(lstLc_deprels)
                print(lstDeprels)
                print(k)
                print(left_context)
                print(new_lstWords)
                
                return ("FAIL", "N/A")
                #raise Exception
            #if (lc_deprels == False) and \
            #   (deprel == new_lstDeprels[m]) and \
            #   (k == (len(left_context) -1)):
            #    lc_deprels = False
            #    lc_deprels_partial = True
            #if (lc_deprels == False) and \
            #   (deprel == lstLc_deprels[j]) and \
            #   (k == (len(left_context) -1)):
            #    lc_deprels = False
            #    lc_deprels_partial = True
            if k <= (len(lstLc_deprels) -1):
                if (lc_deprels == False) and \
                   (deprel == lstLc_deprels[k]):
                    lc_deprels = False
                    lc_deprels_partial = True
                
            #if lemmas == ['jaaritella']:
            #    print()
            #    print()
            #    print()
            #    print("\tJAARITELLA")
            #    print(lc_deprels)
            #    print(lc_deprels_partial)
            #    print(left_context)
            #    print(lstLc_deprels)
            #    print(lstLc_word_count)
            #    print(j)
            #    print(k)
            #    print(m)
            #    print()
            #    print()
            #    print()
            #for k in range((new_feePos -1), (new_feePos -2)):
            #    # Seuraavaksi left context
            #    pass
            #if k == (m + lstLc_word_count[k]):
            if k == ((m + lstLc_word_count[j]) -1):
                m += lstLc_word_count[j]
                j += 1
    else:
        lc_words = False
        lc_deprels = False
        lc_exists = False

    #m = 0
    #if len(left_context) != 0:
    #    for k in range(0, len(lstLc_deprels)):
    #        depr = new_lstDeprels[m]        
    #        m += lstLc_word_count
    #if new_feePos + fee_length < len(new_lines):
    if len(right_context) != 0:
        rc_exists = True
        #line, word, lemma, deprel = getCriteriaFromSentFile(new_lines[k])
        #line, word, lemma, deprel = getCriteriaFromSentFile(right_context[-1])
        #for k in range((new_feePos + fee_length), len(new_lines)):
        for k in range(0, len(right_context)):
                       
            try:
                m = (k + orig_feePos + fee_length)
                line, word, lemma, deprel = getCriteriaFromSentFile(right_context, k)
            except:
                print(startPoint)
                print(fee_length)
                print(k)
                print(m)
                print(right_context)
                raise Exception
            
            try:

                if word != new_lstWords[m].lower():
                    rc_words = False

                #if deprel != new_lstDeprels[m]:
                #    rc_deprels = False
                if deprel != lstRc_deprels[k]:
                    rc_deprels = False
                elif (rc_deprels == True) and (k != 0):
                    rc_deprels = False
                    rc_deprels_partial = True
                # Lopuksi right context
                #pass
            except:
                print("EPIC FAIL")
                print("new_lines: \n\t" + "\n\t".join(new_lines))
                print("lstWords: " + ";".join(lstWords))
                print("lstDeprels: " + ";".join(lstDeprels))
                print("retry: " + str(retry))
                print("fee: " + "\n\t".join(fee))
                print("lstRc_deprels:\t" + "; ".join(lstRc_deprels))
                print("right_context: " + "\n\t".join(right_context))
                print("len(right_context): " + str(len(right_context)))
                print("orig_feePos: " + str(orig_feePos))
                print("startPoint: " + str(startPoint))
                print("k: " + str(k))
                print("m: " + str(m))
                print(right_context)
                print("CurWord: " + word)
                print("new_lstWords: " + ";".join(new_lstWords))
                print("*")
                print("CurDeprel: " + deprel)
                #print(lemma)
                print(new_lstDeprels)
                #print(lemmas[m])
                print("**")
                raise Exception
    else:
        rc_words = False
        rc_deprels = False
        rc_exists = False


    if fee_lemmas and fee_words and fee_deprels:
        if rc_words and lc_words:
            if rc_deprels and lc_deprels:
                searchMethod = "1"
            elif rc_deprels and lc_deprels_partial:
                searchMethod = "1_lc_deprels_partial"
            elif lc_deprels and rc_deprels_partial:
                searchMethod = "1_rc_deprels_partial"
            elif lc_deprels_partial and rc_deprels_partial:
                searchMethod = "1_both_deprels_partial"
            else:
                # Tästä puuttunee jotain
                searchMethod = "metodipuuttuu"
        elif rc_words:
            if rc_deprels:
                searchMethod = "4right"
            elif rc_deprels_partial:
                searchMethod = "4right_deprels_partial"
            else:
                searchMethod = "5right"
        elif lc_words:    
            if lc_deprels:
                searchMethod = "4left"
            elif lc_deprels_partial:
                searchMethod = "4left_deprels_partial"
            else:
                searchMethod = "5left"
        else:
            if rc_deprels and lc_deprels:
                searchMethod = "7"
            elif rc_deprels and lc_deprels_partial:
                searchMethod = "7_lc_deprels_partial"
            elif lc_deprels and rc_deprels_partial:
                searchMethod = "7_rc_deprels_partial"
            elif lc_deprels_partial and rc_deprels_partial:
                searchMethod = "7_both_deprels_partial"
            elif rc_deprels:
                searchMethod = "8right"
            elif rc_deprels_partial:
                searchMethod = "8right_deprels_partial"
            elif lc_deprels:
                searchMethod = "8left"
            elif lc_deprels_partial:
                searchMethod = "8left_deprels_partial"
            else:
                searchMethod = "9"
                
    #elif fee_lemmas and fee_words:
    elif fee_words:
        if fee_lemmas:
            if rc_words and lc_words:
                searchMethod = "2"
            elif rc_words:
                searchMethod = "5right"
            elif lc_words:
                searchMethod = "5left"
            elif rc_deprels and lc_deprels:
                searchMethod = "7_no_fee_deprels"
            elif rc_deprels and lc_deprels_partial:
                searchMethod = "7_no_fee_deprels_and_lc_deprels_partial"
            elif lc_deprels and rc_deprels_partial:
                searchMethod = "7_no_fee_deprels_and_rc_deprels_partial"
            elif lc_deprels_partial and rc_deprels_partial:
                searchMethod = "7_no_fee_deprels_and_both_deprels_partial"
            elif rc_deprels:
                searchMethod = "8right_no_fee_deprels"
            elif lc_deprels:
                searchMethod = "8left_no_fee_deprels"
            elif rc_deprels_partial:
                searchMethod = "8right_no_fee_deprels_and_rc_deprels_partial"
            elif lc_deprels_partial:
                searchMethod = "8left_no_fee_deprels_and_lc_deprels_partial"
            else:
                searchMethod = "10"
        else:
            if rc_words and lc_words:
                searchMethod = "2_no_lemmas"
            elif rc_words:
                searchMethod = "5right_no_lemmas"
            elif lc_words:
                searchMethod = "5left_no_lemmas"
            elif rc_deprels and lc_deprels:
                searchMethod = "7_no_fee_deprels_no_lemmas"
            elif rc_deprels and lc_deprels_partial:
                searchMethod = "7_no_fee_deprels_and_lc_deprels_partial_no_lemmas"
            elif lc_deprels and rc_deprels_partial:
                searchMethod = "7_no_fee_deprels_and_rc_deprels_partial_no_lemmas"
            elif lc_deprels_partial and rc_deprels_partial:
                searchMethod = "7_no_fee_deprels_and_both_deprels_partial_no_lemmas"
            elif rc_deprels:
                searchMethod = "8right_no_fee_deprels_no_lemmas"
            elif lc_deprels:
                searchMethod = "8left_no_fee_deprels_no_lemmas"
            elif rc_deprels_partial:
                searchMethod = "8right_no_fee_deprels_and_rc_deprels_partial_no_lemmas"
            elif lc_deprels_partial:
                searchMethod = "8left_no_fee_deprels_and_lc_deprels_partial_no_lemmas"
            elif fee_deprels:
                searchMethod = "10_fee_deprels_no_lemmas"
            else:
                searchMethod = "10_no_lemmas"

    elif partial_words:
        if fee_lemmas:
            if rc_words and lc_words:
                searchMethod = "2_partial_words"
            elif rc_words:
                searchMethod = "5right_partial_words"
            elif lc_words:
                searchMethod = "5left_partial_words"
            elif rc_deprels and lc_deprels:
                searchMethod = "7_partial_words_no_fee_deprels"
            elif rc_deprels and lc_deprels_partial:
                searchMethod = "7_partial_words_no_fee_deprels_and_lc_deprels_partial"
            elif lc_deprels and rc_deprels_partial:
                searchMethod = "7_partial_words_no_fee_deprels_and_rc_deprels_partial"
            elif lc_deprels_partial and rc_deprels_partial:
                searchMethod = "7_partial_words_no_fee_deprels_and_both_deprels_partial"
            elif rc_deprels:
                searchMethod = "8right_partial_words_no_fee_deprels"
            elif lc_deprels:
                searchMethod = "8left_partial_words_no_fee_deprels"
            elif rc_deprels_partial:
                searchMethod = "8right_partial_words_no_fee_deprels_and_rc_deprels_partial"
            elif lc_deprels_partial:
                searchMethod = "8left_partial_words_no_fee_deprels_and_lc_deprels_partial"
            else:
                searchMethod = "10_partial_words"
        else:
            if rc_words and lc_words:
                searchMethod = "2_partial_words_no_lemmas"
            elif rc_words:
                searchMethod = "5right_partial_words_no_lemmas"
            elif lc_words:
                searchMethod = "5left_partial_words_no_lemmas"
            elif rc_deprels and lc_deprels:
                searchMethod = "7_partial_words_no_fee_deprels_no_lemmas"
            elif rc_deprels and lc_deprels_partial:
                searchMethod = "7_partial_words_no_fee_deprels_and_lc_deprels_partial_no_lemmas"
            elif lc_deprels and rc_deprels_partial:
                searchMethod = "7_partial_words_no_fee_deprels_and_rc_deprels_partial_no_lemmas"
            elif lc_deprels_partial and rc_deprels_partial:
                searchMethod = "7_partial_words_no_fee_deprels_and_both_deprels_partial_no_lemmas"
            elif rc_deprels:
                searchMethod = "8right_partial_words_no_fee_deprels_no_lemmas"
            elif lc_deprels:
                searchMethod = "8left_partial_words_no_fee_deprels_no_lemmas"
            elif rc_deprels_partial:
                searchMethod = "8right_partial_words_no_fee_deprels_and_rc_deprels_partial_no_lemmas"
            elif lc_deprels_partial:
                searchMethod = "8left_partial_words_no_fee_deprels_and_lc_deprels_partial_no_lemmas"
            elif fee_deprels:
                searchMethod = "10_partial_words_fee_deprels_no_lemmas"
            else:
                searchMethod = "10_partial_words_no_lemmas"

#    elif fee_words:
#        if fee_deprels:
#            searchMethod = "10_fee_deprels_no_lemmas"
#        else:
#            searchMethod = "10_no_lemmas"
        
    elif fee_lemmas:
        if rc_words and lc_words:
            searchMethod = "3"
        elif rc_words:
            searchMethod = "6right"
        elif lc_words:
            searchMethod = "6left"
        elif (lc_deprels and lc_exists) or (rc_deprels and rc_exists):
            searchMethod = "11_plus_deprels"
        elif (lc_deprels_partial and lc_exists) or (rc_deprels_partial and rc_exists):
            searchMethod = "11_plus_deprels_partial"
        else:
            searchMethod = "11"

    elif partial_lemmas:
        if rc_words and lc_words:
            searchMethod = "3_partial"
        elif rc_words:
            searchMethod = "6right_partial"
        elif lc_words:
            searchMethod = "6left_partial"
        else:
            searchMethod = "11_partial"

    else:
            print("Ei natsannut.")
            print("\tnew_lines :")
            print(new_lines)
            print("\tlemmas:")
            print(lemmas)
            print("\tnew_lstDeprels:")
            print(new_lstDeprels)
            print("\tnew_lstWords")
            print(new_lstWords)
            print("\torig_feePos :")
            print(orig_feePos)
            print("\trid:")
            print(rid)
            searchMethod = "ERROR IN SEARCH METHOD"
            #raise Exception

    if switched_order:
        searchMethod += "_switched_order"
        
    if "FEE" in lstDeprels:
        fee_deprel_type = "N/A"
    else:
        fee_deprel_type = "Exists"
        
    return (searchMethod, fee_deprel_type)


def isPartialMatch(string1, string2):

    #print("\n\tstring1: " + string1 + "\n\tstring2: " + string2 + "\n")
    if (string1 == None) or (string2 == None):
        return False

    # OBS!
    if (string1 == string2):
        return False
    
    # Variantti yksi: tavuviiva
    if string2.startswith("-") and string2.endswith("-"):
        if string1.endswith(string2.replace("-", "")) and \
           string1.startswith(string2.replace("-", "")):
            return True
    elif string2.startswith("-"):
        if string1.endswith(string2.replace("-", "")):
            return True
    elif string2.endswith("-"):
        if string1.startswith(string2.replace("-", "")):
            return True

    # Variantti kaksi: .*
    if string2.startswith(".*") and string2.endswith(".*"):
        if string1.endswith(string2.replace(".*", "")) and \
           string1.startswith(string2.replace(".*", "")) :
            return True
    elif string2.startswith(".*"):
        if string1.endswith(string2.replace(".*", "")):
            return True
    elif string2.endswith(".*"):
        if string1.startswith(string2.replace(".*", "")):
            return True


    return False

        
def getCriteriaFromSentFile(lines, lineNumber):

    try:
        line = lines[lineNumber]
        cols = line.split('","')
        if len(cols) == 2:
            word = cols[1].lower()
            lemma = None
            deprel = None
        #elif (cols[3] == "Punct") and (len(lines) > (lineNumber+1)):
        #    print("!!!!!!\tPUNCT\t!!!!!!")
        #    return getCriteriaFromSentFile(lines, (lineNumber+1))
        #    #cols = lines[(lineNumber+1)].split('","')

        else:
            cols[0] = cols[0][1:]
            cols[-1] = cols[-1][:-1]
            word = cols[1].lower()
            lemma = cols[2].lower()
            deprel = cols[-2]

        if word.endswith('"'):
            word = word[:-1]
        if word.startswith('"'):
            word = word[1:]
            
    except:
        print("--------- Error in sent file!")
        print("*")
        print(lines)
        print(lineNumber)
        print("*******************")
        print(line)
        raise Exception
    
    return line, word, lemma, deprel


def troubleshootCqplist(rids):
    """
    Gets a list of rids (or a single rid) and prints out all the CQP clauses by various search methods.
    Returns dictTranslations, dictOriginals, dictLemmas
    """
    
    dictTranslations, dictOriginals, dictFees = getAllFrameLUs()
    dictLemmas = getRealLemmasFromFile(lemmaPath)
    
    if type(rids) == int:
        rid = str(rids)
        frameText = dictOriginals[rid][0]
        frame = getValue(frameText, "frame")
        lexunit = getValue(frameText, "lexunit_name")
        finnishFee = dictFees[rid]
        finnishLemma = dictLemmas[frame + "_" + lexunit + "_" + finnishFee[0]]
        printCqp(dictOriginals[rid], dictTranslations[rid], finnishLemma, rid)
    elif (type(rids) == list) or (type(rids) == tuple):
        for rid in rids:
            if type(rid) == int:
                frameText = dictOriginals[str(rid)][0]
                frame = getValue(frameText, "frame")
                lexunit = getValue(frameText, "lexunit_name")
                finnishFee = dictFees[str(rid)]
                finnishLemma = dictLemmas[frame + "_" + lexunit + "_" + finnishFee[0]]
                printCqp(dictOriginals[str(rid)], dictTranslations[str(rid)], finnishLemma, str(rid))
            else:
                frameText = dictOriginals[rid][0]
                frame = getValue(frameText, "frame")
                lexunit = getValue(frameText, "lexunit_name")
                finnishFee = dictFees[rid]
                finnishLemma = dictLemmas[frame + "_" + lexunit + "_" + finnishFee[0]]
                printCqp(dictOriginals[rid], dictTranslations[rid], finnishLemma, rid)
    else:
        frameText = dictOriginals[rid][0]
        frame = getValue(frameText, "frame")
        lexunit = getValue(frameText, "lexunit_name")
        finnishFee = dictFees[rid]
        finnishLemma = dictLemmas[frame + "_" + lexunit + "_" + finnishFee[0]]
        printCqp(dictOriginals[rid], dictTranslations[rid], finnishLemma, rid)

    return dictTranslations, dictOriginals, dictLemmas


def printCqp(orig, translation, feeLemmas, rid):
    """
    Gets some parameters and prints a variety of CQP sentences using different search methods
    """

    searchWords, info = getSearchWordsAndDeprels(orig, translation)
    lstWords = searchWords.split("\t")[1:]
    lstDeprels = info.split("\t")[1:]
    
    print("***************************")
    print("Rid :: " + rid)
    
    print("SearchWords:")
    for word in lstWords:
        print("\t" + word)

    print("Deprels:")
    for deprel in lstDeprels:
        print("\t" + deprel)

    print("Lemmas:")
    print("\t" + feeLemmas)
    
    cqpList = extractAllWordsAllDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 1 ***")
    print("All words, all deprels (where applicable), FEE lemmas:")
    print("\t" + "\t".join(cqpList))

    cqpList = extractAllWordsFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 2 ***")
    print("All words, FEE lemmas:")
    print("\t" + "\t".join(cqpList))
    
    cqpList = extractCoreWordsFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 3 ***")
    print("Core words, FEE lemmas")
    print("\t" + "\t".join(cqpList))
    
    cqpList = extractLeftWordsAllDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 4left ***")
    print("Left context + FEE, all deprels (where applicable, FEE lemmas:")
    print("\t" + "\t".join(cqpList))
    
    cqpList = extractRightWordsAllDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 4right ***")
    print("FEE + right context, all deprels (where applicable, FEE lemmas:")
    print("\t" + "\t".join(cqpList))
    
    cqpList = extractLeftWordsFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 5left ***")
    print("Left context + FEE, FEE lemmas:")
    print("\t" + "\t".join(cqpList))
    
    cqpList = extractRightWordsFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 5right ***")
    print("FEE + right context, FEE lemmas:")
    print("\t" + "\t".join(cqpList))
    
    cqpList = extractLeftCoreWordsFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 6left ***")
    print("Left core context, FEE lemmas:")
    print("\t" + "\t".join(cqpList))
    
    cqpList = extractRightCoreWordsFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 6right ***")
    print("Right core context, FEE lemmas:")
    print("\t" + "\t".join(cqpList))
    
    cqpList = extractFeeWordsAllDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 7 ***")
    print("All deprels, FEE, FEE lemmas:")
    print("\t" + "\t".join(cqpList))
    
    cqpList = extractFeeWordsLeftDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 8left ***")
    print("Left deprels, FEE, FEE lemmas:")
    print("\t" + "\t".join(cqpList))
    
    cqpList = extractFeeWordsRightDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 8right ***")
    print("FEE, right deprels, FEE lemmas:")
    print("\t" + "\t".join(cqpList))
    
    cqpList = extractFeeWordsFeeDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 9 ***")
    print("FEE words, FEE deprels, FEE lemmas:")
    print("\t" + "\t".join(cqpList))
    
    cqpList = extractFeeWordsFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 10 ***")
    print("FEE, FEE lemmas:")
    print("\t" + "\t".join(cqpList))
    
    cqpList = extractFeeLemmas(lstWords, lstDeprels, feeLemmas)
    print(" *** Search method 11 ***")
    print("FEE lemmas:")
    print("\t" + "\t".join(cqpList))

    
def listUnannotatedButSentFiles():
    """
    List all the files, that have been sent for annotation, but haven't been annotated
    Writes the filenames into a file.
    Not tested.
    Returns a list of filenames
    """

    text = getLatest(path=binPath, prefix="Situation")

    lines = text.split("\r\n")
    sentFiles = []
    for line in lines:
        cols = line.split("\t")
        if (int(cols[9]) != 0) and \
           (int(cols[10]) == 0):
            sentFiles.append(cols[7])

    outfile = binPath + pathSep + "UnannotatedFiles.txt"
    for filename in sentFiles:
        outfile.write(filename)
        outfile.write("\n")
    outfile.close()
    
    return sentFiles


def listPreviouslyAnnotatedFiles():
    """
    List all the annotated files. Not tested.
    Returns a list of annotated filenames
    """
    text = getLatest(path=binPath, prefix="Situation")

    lines = text.split("\r\n")
    annotatedFiles = []

    for line in lines:
        cols = line.split("\t")
        if cols[8] != "":
            annotatedFiles.append(cols[8])

    annotatedFiles.append("output_5-15_00.xlsx")
    annotatedFiles.append("output_5-15_01.xlsx")
    annotatedFiles.append("output_5-15_02.xlsx")
    annotatedFiles.append("output_5-15_03.xlsx")
    
    return annotatedFiles
    


                                   

def getAnnotatedRidsFromFile(writeIntoFile=True, annotationLimit=0):
    """
    Gets the rids of the annotated examples latest Situation-file
    Special handling for files with infix 'varia'
    writeIntoFile: True/False
    annotationLimit: no new searches for frame+FILU, if # of annotations is higher than this
    Returns a list of rids
    """
    
    text = getLatest(prefix="Situation")

    dictAnnotated = {}
    dictRids = {}
    dictOnceSent = {}
    lstRet = []
    
    lines = text.split("\r\n")
    text = getLatest(prefix="Situation")
    for line in lines:
        
        cols = line.split("\t")
        rid = cols[0]
        if len(cols) < 2:
            continue
        
        key = cols[1] + "__" + cols[2]
        
        sent = cols[9]
        if sent == "":
            sent = 0
        sent = int(sent)
        annotated = cols[10]

        # cols[13] = bumerangit so. käyty läpi, mutta hylätty
        if ("varia" in cols[7]) and (cols[9] != cols[13]):
            addToDict(dictAnnotated, key, sent, addCount=True, appendToList=False)
        else:
            addToDict(dictAnnotated, key, int(annotated), addCount=True, appendToList=False)
            if sent != 0 and (cols[9] != cols[13]):
                addToDict(dictOnceSent, rid, sent, addCount=True, appendToList=False)
                
        addToDict(dictRids, key, rid, addCount=False, appendToList=True)
    lstTmp = []

    


    # Otetaan tuloksiin
    # A) kaikki ne, joista yhtään ei vielä ole kirjoitettu
    # B) ne, joista on jotain jo kertaalleen lähetetty,
    #    paitsi jos kaikista esimerkeistä on lähetetty jo jotain
    for key in dictAnnotated.keys():
        if dictAnnotated[key] > annotationLimit:
            lstTmp = dictRids[key]
            lstRet.extend(lstTmp)
        else:
            lstTmp = dictRids[key]
            for tmp in lstTmp:
                if tmp in dictOnceSent.keys():
                    lstRet.append(tmp)
            
            

    if writeIntoFile:         
        f = open (binPath + pathSep + "annotatedRids_FrameFILU.txt", "w", encoding="cp1252")
        for rid in lstRet:
            f.write(rid)
            f.write("\n")
        f.close()
        
    return lstRet



def getLatest(path=binPath, prefix=""):
    """
    Opens the last file (alphabetical order) from the path
    path: the path to seek files from
    prefix: the string which a valid file has to start with
    """

    filename = [filename for filename in os.listdir(path) \
                if filename.startswith(prefix)]

    filename.sort()
    f = open(path + pathSep +filename[-1], "r", encoding="utf-8", newline="")
    text = f.read()
    print("Avattiin tiedosto :: " + path + pathSep +filename[-1])
    f.close()

    return text


def getFigures():
    """
    Opens the latest Situation file and extracts the necessary figures from it
    """
    text = getLatest(prefix="Situation")

    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    
    frames = {}
    frameENLUs = {}
    frameFILUs = {}
    ENLUs = {}
    FILUs = {}
    examples = {}
    exampleSentences = {}
    
    frames_sent = {}
    frameENLUs_sent = {}
    frameFILUs_sent = {}
    ENLUs_sent = {}
    FILUs_sent = {}
    examples_sent = {}
    #exampleSentences_sent = {}
    
    frames_annotated = {}
    frameENLUs_annotated = {}
    frameFILUs_annotated = {}
    ENLUs_annotated = {}
    FILUs_annotated = {}
    examples_annotated = {}
    #exampleSentences_annotated = {}

    examples_counter = {}
    examples_metaphors = {}
    #exampleSentences_counter = {}

    examples_disqualified = {}
    examples_justSent = {}
    
    dictAnnotatedRids = {}

    rows = text.split("\n")
    for row in rows:
        cols = row.split("\t")

        if len(cols) > 2:
            rid = cols[0]
            frame = cols[1]
            FILU = cols[2]
            ENLU = cols[3]
            left_context = cols[4]
            FEE = cols[5]
            right_context = cols[6]
            sentFile = cols[7]
            annotatedFile = cols[8]
            sent = cols[9]
            annotated = cols[10]
            metaphors = cols[11]
            counter_examples = cols[12]
            disqualified = cols[13]
            frameFILUsSent = cols[14]
            frameFILUsAnnotated = cols[15]

            if sent == "":
                sent = 0
            else:
                sent = int(sent)

            if annotated == "":
                annotated = 0
            else:
                annotated = int(annotated)

            if disqualified == "":
                disqualified = 0
            else:
                disqualified = int(disqualified)

            if counter_examples == "":
                counter_examples = 0
            else:
                counter_examples = int(counter_examples)

            addToDict(frames, frame, 1)
            addToDict(frameENLUs, frame + "__" + ENLU, 1)
            addToDict(frameFILUs, frame + "__" + FILU, 1)
            addToDict(ENLUs, ENLU, 1)
            addToDict(FILUs, FILU, 1)
            addToDict(examples, rid, 1)
            

            if sent != 0:
                addToDict(frames_sent, frame, 1)
                addToDict(frameENLUs_sent, frame + "__" + ENLU, 1)
                addToDict(frameFILUs_sent, frame + "__" + FILU, 1)
                addToDict(ENLUs_sent, ENLU, 1)
                addToDict(FILUs_sent, FILU, 1)
                addToDict(examples_sent, rid, 1)
                addToDict(exampleSentences, "sent", sent)
                
            if (sent != 0) and (annotated == 0):
                #addToDict(exampleSentences, "just_sent", sent)
                if disqualified != sent:
                    addToDict(examples_justSent, rid, 1)
                    addToDict(exampleSentences, "just_sent", sent)
                
            if annotated != 0:
                addToDict(frames_annotated, frame, 1)
                addToDict(frameENLUs_annotated, frame + "__" + ENLU, 1)
                addToDict(frameFILUs_annotated, frame + "__" + FILU, 1)
                addToDict(ENLUs_annotated, ENLU, 1)
                addToDict(FILUs_annotated, FILU, 1)
                addToDict(examples_annotated, rid, 1)
                addToDict(exampleSentences, "annotated", annotated)

            if metaphors != 0:
                addToDict(examples_metaphors, rid, 1)
                addToDict(exampleSentences, "metaphors", metaphors)
                
            if disqualified != 0:
                addToDict(examples_disqualified, rid, 1)
                addToDict(exampleSentences, "disqualified", disqualified)
                
            if counter_examples != 0:
                addToDict(examples_counter, rid, 1)
                addToDict(exampleSentences, "counter", counter_examples)

            
                
            dictAnnotatedRids[rid] = frame, ENLU, left_context, FEE, right_context, \
                                     FILU, sentFile, annotatedFile, sent, annotated, metaphors, \
                                     counter_examples, disqualified


    
    
    framesTotal = len(frames)
    frameENLUsTotal = len(frameENLUs)
    frameFILUsTotal = len(frameFILUs)
    ENLUsTotal = len(ENLUs)
    FILUsTotal = len(FILUs)
    examplesTotal = len(examples)
    
    framesTotal_sent = len(frames_sent)
    frameENLUsTotal_sent = len(frameENLUs_sent)
    frameFILUsTotal_sent = len(frameFILUs_sent)
    ENLUsTotal_sent = len(ENLUs_sent)
    FILUsTotal_sent = len(FILUs_sent)
    examplesTotal_sent = len(examples_sent)
    exampleSentencesTotal_sent = exampleSentences["sent"]
    
    framesTotal_annotated = len(frames_annotated)
    frameENLUsTotal_annotated = len(frameENLUs_annotated)
    frameFILUsTotal_annotated = len(frameFILUs_annotated)
    ENLUsTotal_annotated = len(ENLUs_annotated)
    FILUsTotal_annotated = len(FILUs_annotated)
    examplesTotal_annotated = len(examples_annotated)
    exampleSentencesTotal_annotated = exampleSentences["annotated"]

    examplesTotal_counter = len(examples_counter)
    exampleSentencesTotal_counter = exampleSentences["counter"]

    examplesTotal_metaphors = len(examples_metaphors)
    exampleSentencesTotal_metaphors = exampleSentences["metaphors"]

    examplesTotal_disqualified = len(examples_disqualified)
    exampleSentencesTotal_disqualified = exampleSentences["disqualified"]

    framesTotal_unsent = (framesTotal - framesTotal_sent)
    frameENLUsTotal_unsent = (frameENLUsTotal - frameENLUsTotal_sent)
    frameFILUsTotal_unsent = (frameFILUsTotal - frameFILUsTotal_sent)
    examplesTotal_unsent = (examplesTotal - examplesTotal_sent)
    #exampleSentencesTotal_unsent = (exampleSentencesTotal - exampleSentencesTotal_sent)
    
    framesTotal_unannotated = (framesTotal - framesTotal_annotated)
    frameENLUsTotal_unannotated = (frameENLUsTotal - frameENLUsTotal_annotated)
    frameFILUsTotal_unannotated = (frameFILUsTotal - frameFILUsTotal_annotated)
    #examplesTotal_unannotated = len(examples_disqualified)
    #examplesTotal_unannotated = (examplesTotal - examplesTotal_annotated)
    exampleSentencesTotal_justSent = exampleSentences["just_sent"]

    framesTotal_justSent = (framesTotal_sent - framesTotal_annotated)
    frameENLUsTotal_justSent = (frameENLUsTotal_sent - frameENLUsTotal_annotated)
    frameFILUsTotal_justSent = (frameFILUsTotal_sent - frameFILUsTotal_annotated)
    #examplesTotal_justSent = (examplesTotal_sent - examplesTotal_annotated)
    #examplesTotal_justSent = (examplesTotal_sent - examplesTotal_annotated)
    examplesTotal_justSent = len(examples_justSent)
    #examplesTotal_justSent -= examplesTotal_disqualified
    #exampleSentencesTotal_justSent = (exampleSentencesTotal_sent - exampleSentencesTotal_annotated)
    
    #figuresText = getLatest(prefix="Figures")
    #lines = figuresText.split("\r\n")

    outfile = open(binPath + pathSep + "Figures_" + timestamp + ".txt", "w", encoding="cp1252")
    outLine = formatOutput(outfile, "Kehyksiä", framesTotal)
    outLine = formatOutput(outfile, "Toimitettuja kehyksiä", framesTotal_sent)
    outLine = formatOutput(outfile, "Toimittamattomia kehyksiä", framesTotal_unsent)
    outLine = formatOutput(outfile, "Annotoituja kehyksiä", framesTotal_annotated)
    outLine = formatOutput(outfile, "Annotoimattomia kehyksiä", framesTotal_unannotated)
    outLine = formatOutput(outfile, "Toimitettuja mutta annotoimattomia kehyksiä", framesTotal_justSent)
    outfile.write("\n")
    
    outLine = formatOutput(outfile, "ENLU+kehys yhteensä", frameENLUsTotal)
    outLine = formatOutput(outfile, "Toimitettuja ENLU+kehys -pareja", frameENLUsTotal_sent)
    outLine = formatOutput(outfile, "Toimittamattomia ENLU+kehys -pareja", frameENLUsTotal_unsent)
    outLine = formatOutput(outfile, "Annotoituja ENLU+kehys -pareja", frameENLUsTotal_annotated)
    outLine = formatOutput(outfile, "Annotoimattomia ENLU+kehys -pareja", frameENLUsTotal_unannotated)
    outLine = formatOutput(outfile, "Toimitettuja mutta annotoimattomia ENLU+kehys -pareja", frameENLUsTotal_justSent)
    outfile.write("\n")
    
    outLine = formatOutput(outfile, "FILU+kehys yhteensä", frameFILUsTotal)
    outLine = formatOutput(outfile, "Toimitettuja FILU+kehys -pareja", frameFILUsTotal_sent)
    outLine = formatOutput(outfile, "Toimittamattomia FILU+kehys -pareja", frameFILUsTotal_unsent)
    outLine = formatOutput(outfile, "Annotoituja FILU+kehys -pareja", frameFILUsTotal_annotated)
    outLine = formatOutput(outfile, "Annotoimattomia FILU+kehys -pareja", frameFILUsTotal_unannotated)
    outLine = formatOutput(outfile, "Toimitettuja mutta annotoimattomia FILU+kehys -pareja", frameFILUsTotal_justSent)
    outfile.write("\n")
    
    outLine = formatOutput(outfile, "Esimerkkejä yhteensä",examplesTotal)
    outLine = formatOutput(outfile, "Toimitettuja esimerkkejä", examplesTotal_sent)
    outLine = formatOutput(outfile, "Toimittamattomia esimerkkejä", examplesTotal_unsent)
    outLine = formatOutput(outfile, "Annotoituja esimerkkejä", examplesTotal_annotated)
    outLine = formatOutput(outfile, "Läpikäytyjä annotoimattomia esimerkkejä", examplesTotal_disqualified)
    outLine = formatOutput(outfile, "Toimitettuja läpikäymättömiä esimerkkejä", examplesTotal_justSent)
    outLine = formatOutput(outfile, "Vastaesimerkkejä", examplesTotal_counter)
    outfile.write("\n")
    
    #outLine = formatOutput(outfile, "Esimerkkilauseita yhteensä", exampleSentencesTotal)
    outLine = formatOutput(outfile, "Toimitettuja esimerkkilauseita", exampleSentencesTotal_sent)
    #outLine = formatOutput(outfile, "Toimittamattomia esimerkkilauseita", exampleSentencesTotal_unsent)
    outLine = formatOutput(outfile, "Annotoituja esimerkkilauseita", exampleSentencesTotal_annotated)
    #outLine = formatOutput(outfile, "Läpikäytyjä annotoimattomia esimerkkejä", exampleSentencesTotal_unannotated)
    outLine = formatOutput(outfile, "Toimitettuja läpikäymättömiä esimerkkilauseita", exampleSentencesTotal_justSent)
    
    outLine = formatOutput(outfile, "Vastaesimerkkilauseita", exampleSentencesTotal_counter)
    outLine = formatOutput(outfile, "Metaforisia lauseita", exampleSentencesTotal_metaphors)
    outfile.close()


def formatOutput(outfile, header, figure):
    """
    Helper function for writing neatly figures
    outfile: open file for writing
    header: string
    figure: int
    """
    outfile.write(header + " :\t\t" + str(figure))
    outfile.write("\n")

    return True


def makeRidExcel():
    """
    Parses through all the annotated, sent and original files,
    and creates an Excel file containing reference information for all the examples
    """

    lstAnnotatedRids = HandleXlsx2.listAnnotations()
    lstSentRids = HandleXlsx2.listSentRids()
    dictLemmas = getRealLemmasFromFile(lemmaPath)
    
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    
    dictAnnotatedRids = {}
    dictSentRids = {}
    dictAllRids = {}
    dictFees = {}
    
    
    for annotatedRid in lstAnnotatedRids:
        rid = annotatedRid[0]
        frame = annotatedRid[1]
        ENLU = annotatedRid[2]
        left_context = annotatedRid[3]
        FEE = annotatedRid[4]
        right_context = annotatedRid[5]
        #FILU = annotatedRid[6]
        annotatedFile = annotatedRid[7]
        sent = annotatedRid[8]
        annotated = annotatedRid[9]
        metaphors = annotatedRid[10]
        counter_examples = annotatedRid[11]
        disqualified = annotatedRid[12]
        if rid in dictAnnotatedRids.keys():
            tmpAnnotatedFile = dictAnnotatedRids[rid][6]
            if tmpAnnotatedFile != "":
                annotatedFile = tmpAnnotatedFile + "; " + annotatedFile
            sent += dictAnnotatedRids[rid][7]
            annotated += dictAnnotatedRids[rid][8]
            metaphors += dictAnnotatedRids[rid][9]
            counter_examples += dictAnnotatedRids[rid][10]
            disqualified += dictAnnotatedRids[rid][11]
            
        if FEE in dictLemmas.keys():
            FILU = dictLemmas[FEE]
        else:
            FILU = ""

        dictAnnotatedRids[rid] = frame, ENLU, left_context, FEE, right_context, \
                                 FILU, annotatedFile, sent, annotated, metaphors, \
                                 counter_examples, disqualified
        

    for sentRid in lstSentRids:
        rid = sentRid[0]
        sent = sentRid[1]
        if sent == "":
            sent = 0
        else:
            sent = int(sent)
            
        sentFile = sentRid[2]
        if rid in dictSentRids.keys():
            tmpSentFile = dictSentRids[rid][1]
            if tmpSentFile != "":
                sentFile = tmpSentFile + "; " + sentFile
            tmpSent = dictSentRids[rid][0]
            if tmpSent != "":
                sent += int(tmpSent)
        dictSentRids[rid] = sent, sentFile
        
    path = translationsPath        
    for filename in os.listdir(path):
        
        lstFees = parseFees(path + pathSep +filename)
        for fee in lstFees:
            dictFees[fee[0]] = " ".join(fee[1])
            
        f = open(path + pathSep +filename, "r", encoding="utf8")
        text = f.read()
        f.close()
        examples = text.split("-------------------- END OF SENTENCE --------------------")
        for example in examples[:-1]:
            frame = getValue(example, "frame")
            ENLU = getValue(example, "lexunit_name")
            rid = getValue(example, "rid")

            altFEE = dictFees[rid]

            searchWords = getCoreSearchWords(example)
            left_context = searchWords[0]
            FEE = searchWords[1]
            right_context = searchWords[2]
            if (frame + "_" + ENLU + "_" + FEE) in dictLemmas.keys():
                FILU = dictLemmas[frame + "_" + ENLU + "_" + FEE]
            elif (frame + "_" + ENLU + "_" + altFEE) in dictLemmas.keys():
                if (("empty" in altFEE) == False):
                    FEE = altFEE
                    FILU = dictLemmas[frame + "_" + ENLU + "_" + altFEE]
                else:
                    FILU = ""

            if rid in dictAnnotatedRids.keys():
                annotatedRid = dictAnnotatedRids[rid]
                
                #frame = annotatedRid[0]
                #ENLU = annotatedRid[1]
                #left_context = annotatedRid[2]
                #FEE = annotatedRid[3]
                #right_context = annotatedRid[4]
                #FILU = annotatedRid[5]
                annotatedFilename = annotatedRid[6]
                
                sent = annotatedRid[7]
                annotated = annotatedRid[8]
                metaphors = annotatedRid[9]
                counter_examples = annotatedRid[10]
                disqualified = annotatedRid[11]
                #FILU = dictLemmas[FEE]
                
                if rid in dictSentRids.keys():
                    sentFilename = dictSentRids[rid][1]
                else:
                    sentFilename = ""
                    
            elif rid in dictSentRids.keys():
                sentRid = dictSentRids[rid]
                sent = sentRid[0]
                sentFilename = sentRid[1]
                annotatedFilename = ""
                annotated = 0
                metaphors = 0
                counter_examples = 0
                disqualified = 0

            else:
                sent = 0
                sentFilename = ""
                annotatedFilename = ""
                annotated = 0
                metaphors = 0
                counter_examples = 0
                disqualified = 0
                
            dictAllRids[rid] = frame, ENLU, left_context, FEE, right_context, \
                               FILU, sentFilename, annotatedFilename, sent, \
                               annotated, metaphors, \
                               counter_examples, disqualified
        


    sentFrameFILU = {}
    annotatedFrameFILU = {}
    
    for rid in dictAllRids.keys():
        items = dictAllRids[rid]
        frame = items[0]
        FILU = items[5]

        sent = items[8]
        if sent == "":
            sent = 0
        else:
            sent = int(sent)

        annotated = items[9]
        if annotated == "":
            annotated = 0
        else:
            annotated = int(annotated)
        
        if sent != 0:
            addToDict(sentFrameFILU, frame + "_" + FILU, sent)
        if annotated != 0:
            addToDict(annotatedFrameFILU, frame + "_" + FILU, annotated)


    outputLines = []
    
    for rid in dictAllRids.keys():
        items = dictAllRids[rid]
        frame = items[0]
        ENLU = items[1]
        left_context = items[2]
        FEE = items[3]
        right_context = items[4]
        FILU = items[5]
        sentFilename = items[6]
        annotatedFilename = items[7]
        sent = items[8]
        annotated = items[9]
        metaphors = items[10]
        counter_examples = items[11]
        disqualified = items[12]

        if (frame + "_" + FILU) in sentFrameFILU.keys():
            frameFILUsSent = sentFrameFILU[frame + "_" + FILU]
        else:
            frameFILUsSent = 0

        if (frame + "_" + FILU) in annotatedFrameFILU.keys():
            frameFILUsAnnotated = annotatedFrameFILU[frame + "_" + FILU]
        else:
            frameFILUsAnnotated = 0
            
        outputLine = rid, frame, FILU, ENLU, left_context, FEE, right_context, \
                     sentFilename, annotatedFilename, \
                     str(sent), str(annotated), str(metaphors), str(counter_examples), \
                     str(disqualified), str(frameFILUsSent), str(frameFILUsAnnotated)
        outputLines.append(outputLine)

    outfile = open(binPath + pathSep + "Situation_" + timestamp + ".txt", \
                   "w", \
                   encoding="utf8")
    
    for outputLine in sorted(outputLines):
        outfile.write("\t".join(outputLine))
        outfile.write("\n")
                      
    outfile.close()



def getCoreSearchWords(example):
    """
    Gets an example from the original files
    Returns a tuple of 1) left context, 2) FEE, 3) right context.
    Only Core elements will be returned
    """
    left_add = True
    leftWords = []
    rightWords = []
    FEE = ""
    
    elems = example.split("<elem ")
    for elem in elems[1:]:
        fe_core_type = getValue(elem, "fe_core_type")
        searchMatch = re.search(">(.*)<", elem)
        if searchMatch is None:
            searchMatch = re.search(">(.*)<", elem.replace("\n",""))
        searchWord = searchMatch.group()[1:-1]
            
                                   
        elemtype = getValue(elem, "elemtype")
        if elemtype.startswith("fee"):
            
            # Verinen helvetti.
            # FEE voi olla myös jaettu kahteen osaan, esim. rid="151815"
            # dry [things] up
            if (searchWord == "") or \
               ("empty" in searchWord):
                pass
            else:
                if FEE == "":
                    FEE = searchWord
                else:
                    FEE += (" " + searchWord)
                left_add = False
                
        elif fe_core_type == "Core":
            if (searchWord != "") and \
               (("empty" in searchWord) == False):
                if left_add:
                    leftWords.append(searchWord)
                else:
                    rightWords.append(searchWord)

    leftPhrase = " ".join(leftWords)
    rightPhrase = " ".join(rightWords)

    try:
        return leftPhrase, FEE, rightPhrase
    except:
        print("Error :: getCoreSearchWords")
        print(example)
        
        raise Exception

        
def getRidsWithInfix(path, infix):
    """
    Searches through all the files in a folder containing the supplied infix and outputs the rids
    """

    lstRids = []
    for filename in os.listdir(path):
        if ("output_" + infix + "_") in filename:
            f = open (path + pathSep +filename, \
                      "r", \
                      encoding="cp1252")
            text = f.read()
            f.close()
            rids = getRids(text)
            print(filename + " :: " + str(len(rids)))
            lstRids.extend(rids)

    f = open (binPath + pathSep + "rids_" + infix + ".txt", \
              "w", \
              encoding="cp1252")
              
    for rid in lstRids:
        f.write(rid)
        f.write("\n")
    f.close()
    
    print("Yhteensä: " + str(len(lstRids)))

    

        
    
    
def getRealLemmasFromFile(filename):
    """
    Gets a file and parses through it getting the (semi-manually decided) lemma
    filename: tab-separated file
    col[0] = frame
    col[1] = lexunit (English)
    col[2] = FEE (Finnish)
    col[last non-empty] = lemma
    Returns dict in format:
    dict[frame_lexunit_FEE] = lemma
    """

    dictLemmas = {}
    
    f = open(filename, "r", encoding="cp1252", newline="")
    wholeText = f.read()
    f.close()
    i = 0
    lines = wholeText.split("\n")
    for line in lines:
        if line == "":
            continue
        
        i += 1
        
        
        if '"' in line:
            line = line.replace('"','')
            
        cols = line.split("\t")    
        try:
            key = cols[0] + "_" + cols[1] + "_" + cols[2]
            
            if cols[-1] == "":
                cols[-1] = cols[-2]
                
            if (key in dictLemmas) and \
               (dictLemmas[key] != cols[-1]):
                print(cols)
                print(dictLemmas[key])
                raise Exception
            dictLemmas[key] = cols[-1]
            

        except:
            print(i)
            print("kosahti")
            raise Exception


    return dictLemmas




    
def getNumbers():
    """
    Retrieves statistics from annotated and sent files.
    Should be obsolete by now.
    """
    timestamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
    xmloutfile = open(binPath + pathSep + "Käsittelemättä" + timestamp + ".xml", "w", encoding="utf8")

    xmlHeader = '<?xml version="1.0" encoding="utf-8"?>'
    xmlRoot = '<Root>\n'
    xmlFrames = '<FRAMES>'
    
    deliveredRids = getRidsFromFile(binPath + pathSep + "rids.txt")

    # MUUTTUNUT 2014-10-24:
    # Tapahtuu kokonaan HandleXlsx:ssä
    # Täytyi reorganisoida koodia, jotta muistia ei käytettäisi koko ajan tappiin asti.
    dictFrameLexunits, dictCounterExamples, \
                       dictMetaphors, \
                       dictFrameElements, \
                       lstUnsentRids, \
                       lstAnnotatedFrames, \
                       lstAnnotatedFrameLexunits, \
                       lstAnnotatedRids, \
                       = HandleXlsx2.countAnnotations()


    
        
    
    # Alustetaan muuttujia

    # Koko aineiston yhteiset muuttujat
    countTotalSentences = 0
    countTotalSentences_sent = 0
    countTotalSentences_unsent = 0
    countTotalSentences_annotated = 0
    countTotalSentences_unannotated = 0


    # dictionaries & lists

    # lstTranslations = [rid, [lauseke1,lauseke2...]]
    lstTranslations = []
    # dictTranslations = { rid : [lauseke1,lauseke2...]}
    dictTranslations = {}
    # dictOriginals { rid : [frametext] }
    dictOriginals = {}
    # dictRidLemmans = { rid,  lemma }
    dictRidLemmas = {}
    
    # lstFees = [rid, lauseke1]
    lstFees = []
    # dictFees { rid : [lauseke1] }
    dictFees = {}
    # dictLemmas { rid : [lemma] }
    dictLemmas = {}

    # KEY = frame, VALUE = # of sentences
    frames = {}
    frames_sent = {}
    frames_annotated = {}

    # frames_ENLUs_content { frame_ENLU : [coreword1, coreword2...], [deprel1, deprel2...] }
    frames_ENLUs_content = {}
    # frames_ENLUs_content { frame_lemma : [coreword1, coreword2...], [deprel1, deprel2...] }
    frames_FILUs_content = {}

    # KEY = frame + ENLU, VALUE = # of sentences
    frames_ENLUs = {}
    frames_ENLUs_sent = {}
    frames_ENLUs_annotated = {}
    
    # KEY = frame + FILU, VALUE = # of sentences
    frames_FILUs = {}
    frames_FILUs_sent = {}
    frames_FILUs_annotated = {}

    # KEY = ENLU, VALUE = # of sentences
    ENLUs = {}
    ENLUs_sent = {}
    ENLUs_annotated = {}

    # KEY = FILU, VALUE = # of sentences
    FILUs = {}
    FILUs_sent = {}
    FILUs_annotated = {}

    

    print("***** Aloitetaan failien skannaus ******")
    for j in range(1,103):
        jStr = ("000" + str(j))[-3:]
        
        tmpList = parseTranslations(translationsPath + pathSep + \
                                            "frames_" + jStr + ".xml")
        lstTranslations += tmpList

        tmpDict = parseOriginals(originalsPath + pathSep + \
                                       "frames_" + jStr + ".xml")
        dictOriginals.update(tmpDict)

        tmpListFees = parseFees(translationsPath + pathSep + \
                            "frames_" + jStr + ".xml")
        lstFees += tmpListFees

    print("***** Aloitetaan lemmojen luku ******")
    dictLemmas = getRealLemmasFromFile(lemmaPath)

    for fee in lstFees:
        dictFees[fee[0]] = fee[1]
        
    for translation in lstTranslations:
        dictTranslations[translation[0]] = translation[1]

    success = 0
    missingLemmas = []
    for rid in dictOriginals.keys():
        frameText = dictOriginals[rid][0]
        frame = getValue(frameText, "frame")
        ENLU = getValue(frameText, "lexunit_name")
        fee = dictFees[rid][0]

        try:
            if "empty" in fee:
                lemma = "EMPTY"
            else:
                lemma = dictLemmas[frame + "_" + ENLU + "_" + fee]
        except:
            missingLemmas.append(frame + "\t" + ENLU + "\t" + fee)
            continue
        
        if ".*" in lemma:
            lemma = lemma.replace(".*", "-")

        if lemma == "":
            print("KOSH!")
            print(frame)
            print(ENLU)
            print(fee)
            raise Exception
        
        dictRidLemmas[rid] = lemma
            
        searchWords, info = getSearchWordsAndDeprels(dictOriginals[rid], dictTranslations[rid])
        ridContents = searchWords, info[1:]

        # Content = corewords + deprels within lexunit
        addToDict(frames_ENLUs_content, frame + "_" + ENLU, ridContents, addCount = False, appendToList = True)
        addToDict(frames_FILUs_content, frame + "_" + lemma, ridContents, addCount = False, appendToList = True)
        

        # NB! 'sentences' == examples from original files
        #
        # frames = total number of sentences in frames
        # frames_ENLUs = total number of sentences in frame_lexunits
        # ENLUs = total number of sentences in lexunits (never mind the frames)
        # frames_FILUs = total number of sentences in frame+FI_LU -pairs
        # FILUs = total number of sentences in Finnish lexunits
        addToDict(frames, frame, 1)
        addToDict(frames_ENLUs, frame + "_" + ENLU, 1)
        addToDict(ENLUs, ENLU, 1)
        addToDict(frames_FILUs, frame + "_" + lemma, 1)
        addToDict(FILUs, lemma, 1)
        countTotalSentences += 1
        
        # frames_sent = number of already sent sentences in frames
        # frames_ENLUs_sent = number of sent sentences in frame_lexunits
        # ENLUs_sent = number of sent sentences in lexunits
        # frames_FILUs_sent = number of sent sentences in frame+FI_LU -pairs
        # FILUs_sent = number of sent sentences grouped by lemma in Finnish
        if rid in deliveredRids:
            addToDict(frames_sent, frame, 1)
            addToDict(frames_ENLUs_sent, frame + "_" + ENLU, 1)
            addToDict(ENLUs_sent, ENLU, 1)
            addToDict(frames_FILUs_sent, frame + "_" + lemma, 1)
            addToDict(FILUs_sent, lemma, 1)
            countTotalSentences_sent += 1
        else:
            countTotalSentences_unsent += 1

        # frames_annotated = number of annotated sentences in frames
        # frames_ENLUs_annotated = number of annotated sentences in frame_lexunits
        # ENLUs_annotated = number of annotated sentences in lexunits
        # frames_FILUs_annotated = number of annotated sentences in frame+FI_LU -pairs
        # FILUs_annotated = number of annotated sentences grouped by FEE in Finnish
        if rid in lstAnnotatedRids:
            addToDict(frames_annotated, frame, 1)
            addToDict(frames_ENLUs_annotated, frame + "_" + ENLU, 1)
            addToDict(ENLUs_annotated, ENLU, 1)
            addToDict(frames_FILUs_annotated, frame + "_" + lemma, 1)
            addToDict(FILUs_annotated, lemma, 1)
            countTotalSentences_annotated += 1
        else:
            countTotalSentences_unannotated += 1

    
    
    # countTotal... = kaikki yhteenlaskettuna
    # Frame
    countTotalFrames = len(frames)
    countTotalFrames_sent = len(frames_sent)
    countTotalFrames_unsent = (countTotalFrames - \
                              countTotalFrames_sent)
    countTotalFrames_annotated = len(frames_annotated)
    countTotalFrames_unannotated = (countTotalFrames - \
                                    countTotalFrames_annotated)

    # Frame + (EN) Lexicalunits
    countTotalFrameENLUs = len(frames_ENLUs)
    countTotalFrameENLUs_sent = len(frames_ENLUs_sent)
    countTotalFrameENLUs_unsent = (countTotalFrameENLUs - \
                                   countTotalFrameENLUs_sent)
    countTotalFrameENLUs_annotated = len(frames_ENLUs_annotated)
    countTotalFrameENLUs_unannotated = (countTotalFrameENLUs - \
                                        countTotalFrameENLUs_annotated)

    # (EN) Lexicalunits
    countTotalENLUs = len(ENLUs)
    countTotalENLUs_sent = len(ENLUs_sent)
    countTotalENLUs_unsent = (countTotalENLUs - \
                              countTotalENLUs_sent)
    countTotalENLUs_annotated = len(ENLUs_annotated)
    countTotalENLUs_unannotated = (countTotalENLUs - \
                                   countTotalENLUs_annotated)

    # Frame + (FI) Lexicalunits
    countTotalFrameFILUs = len(frames_FILUs)
    countTotalFrameFILUs_sent = len(frames_FILUs_sent)
    countTotalFrameFILUs_unsent = (countTotalFrameFILUs - \
                                   countTotalFrameFILUs_sent)
    countTotalFrameFILUs_annotated = len(frames_FILUs_annotated)
    countTotalFrameFILUs_unannotated = (countTotalFrameFILUs - \
                                        countTotalFrameFILUs_annotated)


    # (FI) Lexicalunits
    countTotalFILUs = len(FILUs)
    countTotalFILUs_sent = len(FILUs_sent)
    countTotalFILUs_unsent = (countTotalFILUs - \
                              countTotalFILUs_sent)
    countTotalFILUs_annotated = len(FILUs_annotated)
    countTotalFILUs_unannotated = (countTotalFILUs - \
                                   countTotalFILUs_annotated)

    for frame in sorted(frames):

        pleaseWrite = False
        if frame not in frames_sent.keys():
            pleaseWrite = True

        countFrameENLUs = 0
        countFrameENLUs_sent = 0
        countFrameENLUs_unsent = 0
        countFrameENLUs_annotated = 0
        countFrameENLUs_unannotated = 0

        countFrameFILUs = 0
        countFrameFILUs_sent = 0
        countFrameFILUs_unsent = 0
        countFrameFILUs_annotated = 0
        countFrameFILUs_unannotated = 0
        
        countSentences = 0
        countSentences_sent = 0
        countSentences_unsent = 0
        countSentences_annotated = 0
        countSentences_unannotated = 0
 
        countENLUs = 0
        countFILUs = 0


        # lexunit on oikeastaan Frame-lexunit -pari
        frameENLUs = [lexunit for lexunit in frames_ENLUs.keys() if lexunit.startswith(frame)]
        for frameENLU in frameENLUs:
            countFrameENLUs += 1
            countSentences += frames_ENLUs[frameENLU]
            if frameENLU in frames_ENLUs_sent.keys():
                countFrameENLUs_sent += 1
                countSentences_sent += frames_ENLUs_sent[frameENLU]
            else:
                countFrameENLUs_unsent += 1

            if frameENLU in frames_ENLUs_annotated.keys():
                countFrameENLUs_annotated += 1
                countSentences_annotated += frames_ENLUs_annotated[frameENLU]
            else:
                countFrameENLUs_unannotated += 1


        frameFILUs = [lexunit for lexunit in frames_FILUs.keys() if lexunit.startswith(frame)]
        for frameFILU in frameFILUs:
            countFrameFILUs += 1
            countSentences += frames_FILUs[frameFILU]
            if frameFILU in frames_FILUs_sent.keys():
                countFrameFILUs_sent += 1
            else:
                countFrameFILUs_unsent += 1

            if frameFILU in frames_FILUs_annotated.keys():
                countFrameFILUs_annotated += 1
            else:
                countFrameENLUs_unannotated += 1

                
        if pleaseWrite:
            xmlFrames += "<FRAME name=\"" + frame + "\">\n"
            xmlFrames += addToXml("existingFrameENLUs", countFrameENLUs)
            xmlFrames += addToXml("existingFrameFILUs", countFrameFILUs)
            xmlFrames += addToXml("existingSentences", countSentences)
            xmlFrames += addToXml("sentENLUs", countFrameENLUs_sent)
            xmlFrames += addToXml("sentFILUs", countFrameFILUs_sent)
            xmlFrames += addToXml("sentSentences", countSentences_sent)
            xmlFrames += addToXml("annotatedENLUs", countFrameENLUs_annotated)
            xmlFrames += addToXml("annotatedFILUs", countFrameFILUs_annotated)
            xmlFrames += addToXml("annotatedSentences", countSentences_annotated)



            for FILU in frameFILUs:
                if FILU in frames_FILUs.keys():
                    countSentences = frames_FILUs[FILU]
                else:
                    countSentences = 0

                if FILU not in frames_FILUs_sent.keys():
                    xmlFrames += "<FrameFILU name=\"" + FILU + "\">\n"
                    xmlFrames += addToXml("existingSentences", countSentences)
                    xmlFrames += "<sentences>\n"
                    
                    for content1, content2 in frames_FILUs_content[FILU]:

                        xmlFrames += "<sentence>\n"
                        xmlFrames += "<words>\n"
                        
                        cont1 = content1.split("\t")
                        for cont in cont1:
                            if ((cont != "") and (("EMPTY" in cont) == False)):
                                if "&APOS;" in cont:
                                    cont = cont.replace("&APOS;", "'")
                                   
                                countSentences_unsent += 1

                                xmlFrames += addToXml("word", cont)

                        xmlFrames += "</words>\n"
                        xmlFrames += "<deprels>\n"

                        cont2 = content2.split("\t")
                        for cont in cont2:
                            if cont != "":
                                xmlFrames += addToXml("deprel", cont)
                        xmlFrames += "</deprels\n>"

                        xmlFrames += "</sentence>\n"


                    xmlFrames += "</sentences>\n"
                    xmlFrames += "</FILU>\n"
            xmlFrames += "</FRAME>\n"

    xmlFrames += '</FRAMES>\n'
    
    xmlNumbers = "<NUMBERS>\n"
    xmlNumbers += addToXml("FrameCount", countTotalFrames)
    xmlNumbers += addToXml("AnnotatedFrameCount", countTotalFrames_annotated)
    xmlNumbers += addToXml("NotAnnotatedFrameCount", countTotalFrames_unannotated)
    xmlNumbers += addToXml("FrameENLUCount", countTotalFrameENLUs)
    xmlNumbers += addToXml("FrameFILUCount", countTotalFrameFILUs)
    xmlNumbers += addToXml("ENLUCount", countTotalENLUs)
    xmlNumbers += addToXml("FILUCount", countTotalFILUs)

    FILUsPerFrame = (countTotalFrameFILUs / countTotalFrames)
    ENLUsPerFrame = (countTotalFrameENLUs / countTotalFrames)
    xmlNumbers += addToXml("ENLUsPerFrame", ENLUsPerFrame)
    xmlNumbers += addToXml("FILUsPerFrame", FILUsPerFrame)

    xmlNumbers += addToXml("AnnotatedFrameENLUCount", countTotalFrameENLUs_annotated)
    xmlNumbers += addToXml("AnnotatedFrameFILUCount", countTotalFrameFILUs_annotated)

    xmlNumbers += addToXml("NotAnnotatedFrameENLUCount", countTotalFrameENLUs_unannotated)
    xmlNumbers += addToXml("NotAnnotatedFrameFILUCount", countTotalFrameFILUs_unannotated)

    xmlNumbers += addToXml("SentenceCount", countTotalSentences)
    xmlNumbers += addToXml("UnsentFrameCount", countTotalFrames_unsent)
    xmlNumbers += addToXml("UnsentFrameENLUCount", countTotalFrameENLUs_unsent)
    xmlNumbers += addToXml("UnsentFrameFILUCount", countTotalFrameFILUs_unsent)
    xmlNumbers += addToXml("UnsentENLUCount", countTotalENLUs_unsent)
    xmlNumbers += addToXml("UnsentFILUCount", countTotalFILUs_unsent)
    xmlNumbers += addToXml("UnsentSentenceCount", countSentences_unsent)
    xmlNumbers += "</NUMBERS>\n"

    xmlRoot = addToXml("Root", xmlNumbers + xmlFrames)

    writeOutput(xmloutfile, xmlHeader, "xmlHeader")
    writeOutput(xmloutfile, xmlRoot, "xmlRoot")

    xmloutfile.close()


    # Tehdään erillinen tiedosto, jotta saadaan tulokset valmiiksi esityskelpoiseen muotoon
    # ilman xml-tageja
    numbersOutput = open(binPath + pathSep + "Tilanne_" + timestamp + ".xml", "w", encoding="utf8")

    numbers = formatNumbers("Kehyksiä yhteensä:", countTotalFrames)
    numbers += formatNumbers("Toimitettuja kehyksiä:", countTotalFrames_sent)
    numbers += formatNumbers("Toimittamattomia kehyksiä:", countTotalFrames_unsent)
    numbers += formatNumbers("Annotoituja kehyksiä:", countTotalFrames_annotated)
    numbers += formatNumbers("Annotoimattomia kehyksiä:", countTotalFrames_unannotated)
    numbers += "\n"

    numbers += formatNumbers("EnLU+kehys yhteensä:", countTotalFrameENLUs)
    numbers += formatNumbers("EnLU yhteensä:", countTotalENLUs)
    numbers += formatNumbers("EnLU/Kehys keskimäärin:", ENLUsPerFrame)
    numbers += formatNumbers("Toimitettuja EnLU+kehys -pareja:", countTotalFrameENLUs_sent)
    numbers += formatNumbers("Toimittamattomia EnLU+kehys -pareja:", countTotalFrameENLUs_unsent)
    numbers += formatNumbers("Annotoituja EnLU+kehys -pareja:", countTotalFrameENLUs_annotated)
    numbers += formatNumbers("Annotoimattomia EnLU+kehys -pareja:", countTotalFrameENLUs_unannotated)
    numbers += "\n"
    
    numbers += formatNumbers("FiLU+Kehys yhteensä:", countTotalFrameFILUs)
    numbers += formatNumbers("FiLU yhteensä:", countTotalFILUs)
    numbers += formatNumbers("FiLU/Kehys keskimäärin:", FILUsPerFrame)
    numbers += formatNumbers("Toimitettuja FiLU+kehys -pareja:", countTotalFrameFILUs_sent)
    numbers += formatNumbers("Toimittamattomia FiLU+kehys -pareja:", countTotalFrameFILUs_unsent)
    numbers += formatNumbers("Annotoituja FiLU+kehys -pareja:", countTotalFrameFILUs_annotated)
    numbers += formatNumbers("Annotoimattomia FiLU+kehys -pareja:", countTotalFrameFILUs_unannotated)
    numbers += "\n"

    numbers += formatNumbers("Esimerkkilauseita yhteensä:", countTotalSentences)
    numbers += formatNumbers("Toimitettuja esimerkkilauseita yhteensä:", countTotalSentences_sent)
    numbers += formatNumbers("Toimittamattomia esimerkkilauseita yhteensä:", countTotalSentences_unsent)
    numbers += formatNumbers("Annotoituja esimerkkilauseita yhteensä:", countTotalSentences_annotated)
    numbers += formatNumbers("Annotoimattomia esimerkkilauseita yhteensä:", countTotalSentences_unannotated)
    numbers += "\n"
 
    numbersOutput.write(numbers)
    numbersOutput.close()
    

def writeSentences(writeFile, rid, original, lstSentences, translatedWords):
    """
    Korpista saatujen tietojen tallennukseen
    writeFile = avoinna oleva kirjoitustiedosto
    rid = alkuperäisen tiedoston esimerkkilauseen yksilöivä tunnus
    original = määrämittainen lista:
       original[0] = metatieto tekstinä (frame, lexunit_name...)
       original[1] = lista elementeistä (elemtype, type, core_type, word)
       original[2] = lista alkuperäistiedoston sanoista, alkaa kahdella pilkulla
    lstSentences = lista Korpista saaduista lauseista
    translatedWords = lista käännöstiedoston sanoista, indeksit täsmäävät original[2]:n kanssa
    """

    # 1. Ensin rid
    writeFile.write("rid=" + str(rid) + "\n")

    writeOutput(writeFile, original[0], "metatieto")
    writeFile.write("\n\n")


    # 2. Kaikki metatiedot
    for elem in original[1]:
        for text in elem:
            writeOutput(writeFile, text, "elementti", suffix = ",")
        writeFile.write("\n")
    writeFile.write("\n")


    # 3. Alkuperäiset fe:t ja fee:t, niiden perään käännökset
    i = 0
    for elem in original[2]:
        writeOutput(writeFile, elem, "alkuperäisteksti", prefix = ",,")
        writeFile.write(",")
        writeOutput(writeFile, translatedWords[i], "käännösteksti", prefix = ",")
        writeFile.write("\n")
        i += 1
    writeFile.write("\n")

    # Valitaan lauseista satunnaisesti (enintään) 15
    if len(lstSentences) > 15:
        lstSentences = selectRandomSentences(lstSentences, 15)

    # 4. Kirjoitetaan esimerkkilauseista yksiriviset tiivistelmät
    for sentence in lstSentences:
        oneLineSentence = makeBoldedOneLiner(sentence)
        writeOutput( writeFile, oneLineSentence, "esimerkkilause")
        writeFile.write("\n")
    writeFile.write("\n")

    # 5. Kirjoitetaan esimerkkilauseet,
    #    jokainen sane jäsennyksineen omalle rivilleen
    for sentence in lstSentences:
        writeOutput(writeFile, sentence, "esimerkkilause")
        writeFile.write("\n\n")
    writeFile.write("\n\n")




def findNewFrameFILUs(infix, \
                      maxSize = 100, \
                      startFrame = "", \
                      stopFrame = ""):
    """
    Method for retrieving Frame + FILU -pairs 
    infix: string, which will be included in each output file name retrieved (use unique infixes!)
    maxSize: maximum number of examples in one file;
    a frame won't be divided in multiple frames though
    startFrame: frame + "__" + lemma eg. Ride_vehicle__liftata (included in search)
    stopFrame: frame + "__" + lemma eg. Ride_vehicle__liftata (included in search)
    """
    # 1. Haetaan ihan kaikki FrameLexunitit

    dictTranslations, dictOriginals, dictFees = getAllFrameLUs()
    dictAllFrameFILexunits = {}
    dictAllLemmas = {}

    dictLemmas = getRealLemmasFromFile(lemmaPath)


    runningNumber = 1
    
    outfile = outputPath + pathSep + "output_" + \
              infix + "_" + str(runningNumber) + ".txt"

    # Paniikkitarkistus puuttuvan infiksin varalta.
    if infix == "":
        print("Infix puuttuu")
        print("Toiminta keskeytetään.")
        raise Exception
    # Paniikkitarkistus jo käytettyjen infiksien varalta.
    if [filename for filename in os.listdir(outputPath + pathSep) \
        if filename.startswith("output_" + infix + "_")]:
        print("Tarjoamasi infix (" + infix + ") on jo käytetty")
        print("Toiminta keskeytetään.")
        raise Exception
    
    
    writeFile = open (outfile, "w", encoding="cp1252")
    
    for rid in dictOriginals.keys():
        frameText = dictOriginals[rid][0]
        frame = getValue(frameText, "frame")
        lexunit = getValue(frameText, "lexunit_name")

        finnishFee = " ".join(dictFees[rid])
        if finnishFee == "":
            finnishLemma = ""
        else:
            try:
                finnishLemma = dictLemmas[frame + "_" + lexunit + "_" + finnishFee]
            except:
            
                print(frame)
                print(lexunit)
                print(finnishFee)
                for key in dictLemmas.keys():
                    print(key)
                    print(dictLemmas[key])
                    
                    raise Exception
            
        

        if (((frame + "_" + finnishLemma) in dictAllFrameFILexunits.keys()) == False):
            # Skipataan ne käännökset, joista FEE puuttuu.
            # Niitä oli kaikkiaan 487
            if finnishFee != "":
                addToDict(dictAllFrameFILexunits, \
                          frame + "__" + finnishLemma, \
                          rid, \
                          addCount = False, \
                          appendToList=True)
                dictAllLemmas[rid] = finnishLemma

    # 2. Haetaan ne FrameLexunitit, jotka on toimitettu
    annotatedRids = getRidsFromFile(binPath + pathSep + "annotatedRids_FrameFILU.txt")

    # 3. Ykköskohdan FrameLexunitit - Kakkoskohdan FrameLexunitit = Toimittamattomat

   

    
    # Tämä poisti vain yksittäisen rid:n lausejoukosta
    #
    for rid in annotatedRids:
        dictAllFrameFILexunits = removeFromDict(dictAllFrameFILexunits, rid)

    # Tämä poistaa koko frame+FILU -parin
    #for rid in annotatedRids:
    #    dictAllFrameFILexunits = removeKeyFromDict(dictAllFrameFILexunits, rid)

    # 4. Otetaan kaikki oleellinen tieto Kolmoskohdan FrameLexuniteista

    dictFrameFILexunitContents = {}
    written = 0
    closing = False
    frame = ""
    prevFrame = ""
    
    for key, rids in sorted(dictAllFrameFILexunits.items()):
        
        br = False


        frame = key.split("__")[0]
        if frame != prevFrame:
            print("\tViimeksi selailtu kehys: " + prevFrame)
            print("\tNyt menossa: " + frame)

            if (closing):
                written = 0
                writeFile.close()
                runningNumber += 1
                outfile = outputPath + pathSep + "output_" + \
                          infix + "_" + str(runningNumber) + ".txt"
                writeFile = open(outfile, "w", encoding="cp1252")                
                closing = False
            
        prevFrame = key.split("__")[0]
        

        if written >= maxSize:
            closing = True

        
            
        
        # Jos ajo on kaatunut, voidaan aloittaa viimeisimmästä kehyksestä
        # itse startFrame sisältyy ajoon
        if (startFrame > key) and (startFrame != ""):
            continue

        # Jos halutaan jostain syystä käydä vain osa kehyksistä läpi,
        # voidaan määrittää sekä startFrame että stopFrame
        if (stopFrame < key) and (stopFrame != ""):
            break

        for rid in rids:
            searchWords, info = getSearchWordsAndDeprels(dictOriginals[rid], \
                                                        dictTranslations[rid])

            # searchWords ja info alkavat yhdellä tabilla
            ridContents = searchWords.split("\t")[1:], \
                          info[1:].split("\t")[1:], \
                          rid

            # Content = corewords + deprels + rid within lexunit
            addToDict(dictFrameFILexunitContents, \
                      key, \
                      ridContents, \
                      addCount = False, \
                      appendToList = True)
        
    # 5. Iteroidaan FrameLexuniteittain, ja etsitään mahdollisimman tarkoilla matcheilla
        for sentence in dictFrameFILexunitContents[key]:
            
            lstWords = sentence[0]
            lstDeprels = sentence[1]
            rid = sentence[2]
            feeLemmas = dictAllLemmas[rid]

            cqpList = extractAllWordsAllDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences = getSentencesFewDecadesAtATime(20,20,cqpList)

            if writeResults(writeFile, \
                            lstSentences, \
                            "1", \
                            cqpList, \
                            rid, \
                            dictOriginals[rid], \
                            dictTranslations[rid]):
                br = True
                written += 1
                break
            

        # 6. Seuraavaan Frame+LU-pariin, jos jotain löytyi
        if br:
            continue

        # 7. Löysennetään hakuehtoja
        for sentence in dictFrameFILexunitContents[key]:

            lstWords = sentence[0]
            lstDeprels = sentence[1]
            rid = sentence[2]
            feeLemmas = dictAllLemmas[rid]
            
            cqpList = extractAllWordsFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences = getSentencesFewDecadesAtATime(20,20,cqpList)

            if writeResults(writeFile, \
                            lstSentences, \
                            "2", \
                            cqpList, \
                            rid, \
                            dictOriginals[rid], \
                            dictTranslations[rid]):
                br = True
                written += 1
                break
    
        # 8. Seuraavaan Frame+LU-pariin, jos jotain löytyi
        if br:
            continue

        # 9. Löysennetään hakuehtoja, tästedes sama kaava toistuu
        for sentence in dictFrameFILexunitContents[key]:

            lstWords = sentence[0]
            lstDeprels = sentence[1]
            rid = sentence[2]
            feeLemmas = dictAllLemmas[rid]
            
            cqpList = extractCoreWordsFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences = getSentencesFewDecadesAtATime(20,20,cqpList)

            if writeResults(writeFile, \
                            lstSentences, \
                            "3", \
                            cqpList, \
                            rid, \
                            dictOriginals[rid], \
                            dictTranslations[rid]):
                br = True
                written += 1
                break

        if br:
            continue

            
        for sentence in dictFrameFILexunitContents[key]:
            
            lstWords = sentence[0]
            lstDeprels = sentence[1]
            rid = sentence[2]
            feeLemmas = dictAllLemmas[rid]
            
            cqpList = extractLeftWordsAllDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences = getSentencesFewDecadesAtATime(15,15,cqpList)
            cqpList2 = extractRightWordsAllDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences2 = getSentencesFewDecadesAtATime(15,15,cqpList2)

            if (len(lstSentences) != 0) and (len(lstSentences2) != 0):
                lstSentences.extend(lstSentences2)
            elif (len(lstSentences) == 0) and (len(lstSentences2) != 0):
                lstSentences = lstSentences2

            if writeResults(writeFile, \
                            lstSentences, \
                            ["4left", "4right"], \
                            [cqpList, cqpList2], \
                            rid, \
                            dictOriginals[rid], \
                            dictTranslations[rid]):
                br = True
                written += 1
                break

        if br:
            continue

        for sentence in dictFrameFILexunitContents[key]:

            lstWords = sentence[0]
            lstDeprels = sentence[1]
            rid = sentence[2]
            feeLemmas = dictAllLemmas[rid]
            
            cqpList = extractLeftWordsFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences = getSentencesFewDecadesAtATime(15,15,cqpList)
            cqpList2 = extractRightWordsFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences2 = getSentencesFewDecadesAtATime(15,15,cqpList2)

            if (len(lstSentences) != 0) and (len(lstSentences2) != 0):
                lstSentences.extend(lstSentences2)
            elif (len(lstSentences) == 0) and (len(lstSentences2) != 0):
                lstSentences = lstSentences2

            if writeResults(writeFile, \
                            lstSentences, \
                            ["5left", "5right"], \
                            [cqpList, cqpList2], \
                            rid, \
                            dictOriginals[rid], \
                            dictTranslations[rid]):
                br = True
                written += 1
                break
    
        if br:
            continue

        for sentence in dictFrameFILexunitContents[key]:

            lstWords = sentence[0]
            lstDeprels = sentence[1]
            rid = sentence[2]
            feeLemmas = dictAllLemmas[rid]
            
            cqpList = extractLeftCoreWordsFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences = getSentencesFewDecadesAtATime(15,15,cqpList)
            cqpList2 = extractRightCoreWordsFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences2 = getSentencesFewDecadesAtATime(15,15,cqpList2)
            
            if (len(lstSentences) != 0) and (len(lstSentences2) != 0):
                lstSentences.extend(lstSentences2)
            elif (len(lstSentences) == 0) and (len(lstSentences2) != 0):
                lstSentences = lstSentences2
                
            if writeResults(writeFile, \
                            lstSentences, \
                            ["6left","6right"], \
                            [cqpList, cqpList2], \
                            rid, \
                            dictOriginals[rid], \
                            dictTranslations[rid]):
                br = True
                written += 1
                break
            
        if br:
            continue


        for sentence in dictFrameFILexunitContents[key]:

            lstWords = sentence[0]
            lstDeprels = sentence[1]
            rid = sentence[2]
            feeLemmas = dictAllLemmas[rid]
            
            cqpList = extractFeeWordsAllDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences = getSentencesFewDecadesAtATime(15,15,cqpList)

            if writeResults(writeFile, \
                            lstSentences, \
                            "7", \
                            cqpList, \
                            rid, \
                            dictOriginals[rid], \
                            dictTranslations[rid]):
                br = True
                written += 1
                break

        if br:
            continue


        for sentence in dictFrameFILexunitContents[key]:

            lstWords = sentence[0]
            lstDeprels = sentence[1]
            rid = sentence[2]
            feeLemmas = dictAllLemmas[rid]
            
            cqpList = extractFeeWordsLeftDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences = getSentencesFewDecadesAtATime(15,15,cqpList)
            cqpList2 = extractFeeWordsRightDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences2 = getSentencesFewDecadesAtATime(15,15,cqpList2)

            if (len(lstSentences) != 0) and (len(lstSentences2) != 0):
                lstSentences.extend(lstSentences2)
            elif (len(lstSentences) == 0) and (len(lstSentences2) != 0):
                lstSentences = lstSentences2

            if writeResults(writeFile, \
                            lstSentences, \
                            ["8left", "8right"], \
                            [cqpList, cqpList2], \
                            rid, \
                            dictOriginals[rid], \
                            dictTranslations[rid]):
                br = True
                written += 1
                break

        if br:
            continue

        for sentence in dictFrameFILexunitContents[key]:

            lstWords = sentence[0]
            lstDeprels = sentence[1]
            rid = sentence[2]
            feeLemmas = dictAllLemmas[rid]
            
            cqpList = extractFeeWordsFeeDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences = getSentencesFewDecadesAtATime(15,15,cqpList)

            if writeResults(writeFile, \
                            lstSentences, \
                            "9", \
                            cqpList, \
                            rid, \
                            dictOriginals[rid], \
                            dictTranslations[rid]):
                br = True
                written += 1
                break
            
        if br:
            continue


        for sentence in dictFrameFILexunitContents[key]:

            lstWords = sentence[0]
            lstDeprels = sentence[1]
            rid = sentence[2]
            feeLemmas = dictAllLemmas[rid]
            
            cqpList = extractFeeWordsFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences = getSentencesFewDecadesAtATime(15,15,cqpList)

            if writeResults(writeFile, \
                            lstSentences, \
                            "10", \
                            cqpList, \
                            rid, \
                            dictOriginals[rid], \
                            dictTranslations[rid]):
                br = True
                written += 1
                break

        if br:
            continue


        for sentence in dictFrameFILexunitContents[key]:

            lstWords = sentence[0]
            lstDeprels = sentence[1]
            rid = sentence[2]
            feeLemmas = dictAllLemmas[rid]
            
            cqpList = extractFeeLemmas(lstWords, lstDeprels, feeLemmas)
            lstSentences = getSentencesFewDecadesAtATime(15,15,cqpList)

            if writeResults(writeFile, \
                            lstSentences, \
                            "11", \
                            cqpList, \
                            rid, \
                            dictOriginals[rid], \
                            dictTranslations[rid]):
                br = True
                written += 1
                break

        if br:
            continue
            
        
    writeFile.close()


def writeResults(writeFile, lstSentences, searchMethod, cqpList, rid, original, translation):
    """
    Helper function to reduce redundancy
    Writes written sentences on display and into file
    writeFile: opened file to write into
    lstSentences: list of sentences from Korp
    searchMethod: the means to identify the search method
    cqpList: the CQP clause which was used to retrieve the sentences
    rid: rid of the example
    original: the metadata from the original file
    translation: the translated text
    Returns True if something was written, otherwise False
    """
    if len(lstSentences) != 0:
        if type(searchMethod) == str:
            print("** " + searchMethod + " **")
            try:
                print(cqpList)
            except:
                print("Ei saatu näytettyä hakulausetta")
        else:
            # tuple or list
            for i in range(0, len(searchMethod)):
                method = searchMethod[i]
                cqpList = cqpList[i]
                print("** " + method + " **")
                try:
                    print(cqpList)
                except:
                    print("Ei saatu näytettyä hakulausetta")

        writeSentences(writeFile, \
                       rid, \
                       original, \
                       lstSentences, \
                       translation)
        return True
    else:
        return False
                                     
        

def removeKeyFromDict(dictionary, valueToRemove):
    """
    Helper function to remove the whole key from the dictionary,
    if dict[key] contains the value
    dictionary: dict[key] = [val1, val2, ... valn]
    valueToRemove =  the trigger for removal of the whole key
    Returns the modified dictionary
    """
    for key, lstVals in list(dictionary.items()):
        if valueToRemove in lstVals:
            vals = dictionary.pop(key)
            break
    
    return dictionary


def removeFromDict(dictionary, valueToRemove):
    """
    Helper function to remove a value from a dictionary of lists,
    if dict[key] contains the value
    dictionary: dict[key] = [val1, val2, ... valn]
    valueToRemove =  the value to be removed from the dict[key]
    Returns the modified dictionary
    """
    for key, lstVals in list(dictionary.items()):
        if valueToRemove in lstVals:
            vals = dictionary.pop(key)
            vals.remove(valueToRemove)
            if len(vals) != 0:
                dictionary[key] = vals
    
    return dictionary


def getAllFrameLUs():
    """
    Parses all the original and translation files
    Returns a tuple of three dictionaries: 1. dictTranslations, 2. dictOriginals, dictFees
    """

    lstTranslations = []
    dictTranslations = {}
    dictOriginals = {}
    lstFees = []
    dictFees = {}
    
    for j in range(1,103):
        print("***** Skannataan freimiä " + str(j) + " *****")
        jStr = ("000" + str(j))[-3:]
        
        tmpList = parseTranslations(translationsPath + pathSep + \
                                            "frames_" + jStr + ".xml")
        lstTranslations += tmpList

        tmpDict = parseOriginals(originalsPath + pathSep + \
                                       "frames_" + jStr + ".xml")
        dictOriginals.update(tmpDict)

        tmpListFees = parseFees(translationsPath + pathSep + \
                            "frames_" + jStr + ".xml")
        lstFees += tmpListFees
        
    for fee in lstFees:
        dictFees[fee[0]] = fee[1]
    
    for translation in lstTranslations:
        dictTranslations[translation[0]] = translation[1]

    return dictTranslations, dictOriginals, dictFees






    

def formatNumbers(text, number):
    """
    Helper function to keep the code cleaner elsewhere
    Returns the text + number -pair neatly formatted
    """
    maxLen = 30
    while True:
        if maxLen > len(text):
            break
        maxLen += 10

    ret = ("{:<" + str(maxLen) + "}{!s}").format(text, number)
    ret += "\n"
    return ret


def addToXml(tag, value):
    """
    Helper function to keep the code cleaner elsewhere
    Returns the tagged value
    """
    ret = "<" + tag + ">" + str(value) + "</" + tag + ">\n"
    return ret

    
def addToDict(dictionary, key, value, addCount=True, appendToList=False):
    """
    Helper function to avoid unnecessary typing in many instances
    dictionary = dict
    key = key
    value = value to add
    addCount = value will be added/concatenated to the existing value
    appendToList = value is a list, and the value will be appended
    Returns the dictionary
    """
    if key in dictionary.keys():
        tmpValue = dictionary.pop(key)
        if appendToList:
            tmpValue.append(value)
            dictionary[key] = tmpValue
        elif addCount:
            try:
                tmpValue = (int(tmpValue) + int(value))
            except:
                tmpValue += value
            dictionary[key] = tmpValue
        else:
            # What else is there?
            pass
    else:
        if appendToList:
            dictionary[key] = [value]
        elif addCount:
            try:
                dictionary[key] = int(value)
            except:
                dictionary[key] = value

    return dictionary

    

    
def collectSentRids():
    """
    Collects all the rids, which have been sent for annotation and
    writes them to files
    Basically obsolete
    """

    allTranslations = []
    for j in range(1,103):
        if j != 96:
            jStr = ("000" + str(j))[-3:]
            transFile = open (translationsPath + pathSep + \
                              "frames_" + jStr + ".xml", \
                              "r", encoding="utf8")
            translationText = transFile.read()
            translations = translationText.split("-------------------- END OF SENTENCE --------------------")
            for translation in translations:
                if ("<sentence" in translation):
                    allTranslations.append(translation)
    
    dictTranslations = getTranslationDict(allTranslations)
    
    sentFiles = ""
    rid_file_pairs = ""
    baseFolder = outputPath + pathSep
                

    lstRids = []
    
    fixed16_50 = 0
    for filename in os.listdir (baseFolder + "16-50"):
        if ("fixed" in filename):
            fil = open(baseFolder + "16-50" + pathSep + filename, "r", encoding = "cp1252")
            wholeText = fil.read()
            fil.close()
            rids = getRids(wholeText)
            lstRids += rids
            for rid in rids:
                rid_file_pairs += str(rid) + "\t" + filename + "\n"
            fixed16_50 += len(rids)
            sentFiles += filename + "\t" + str(len(rids)) + "\n"
            print(len(rids))
    
    print(len(lstRids))
    print()

    preps = 0
    for filename in os.listdir (baseFolder + "preps"):
        if ("preps" in filename):
            fil = open(baseFolder + "preps" + pathSep + filename, "r", encoding = "cp1252")
            wholeText = fil.read()
            fil.close()
            rids = getRids(wholeText)
            lstRids += rids
            for rid in rids:
                rid_file_pairs += str(rid) + "\t" + filename + "\n"
            preps += len(rids)
            sentFiles += filename + "\t" + str(len(rids)) + "\n"
            print(len(rids))
    print(len(lstRids))
    print()
    
    nolla = 0
    for filename in os.listdir (baseFolder + "nolla"):
        if ("nolla_" in filename):
            fil = open(baseFolder + "nolla" + pathSep + filename, "r", encoding = "cp1252")
            wholeText = fil.read()
            fil.close()
            rids = getRids(wholeText)
            lstRids += rids
            for rid in rids:
                rid_file_pairs += str(rid) + "\t" + filename + "\n"
            nolla += len(rids)
            sentFiles += filename + "\t" + str(len(rids)) + "\n"
            print(len(rids))
    print(len(lstRids))
    print()
    
    utf8 = 0
    for filename in os.listdir (baseFolder + "utf8"):
        if ("bolded" in filename):
            fil = open(baseFolder + "utf8" + pathSep + filename, "r", encoding = "utf8")
            wholeText = fil.read()
            fil.close()
            rids = getRids(wholeText)
            lstRids += rids
            for rid in rids:
                rid_file_pairs += str(rid) + "\t" + filename + "\n"
            utf8 += len(rids)
            sentFiles += filename + "\t" + str(len(rids)) + "\n"
            print(len(rids))
    print(len(lstRids))
    print()

    hits05_15 = 0
    for filename in os.listdir (baseFolder + "05-15"):
        if ("_1.txt" not in filename):
            fil = open(baseFolder + "05-15" + pathSep + filename, "r", encoding = "cp1252")
            wholeText = fil.read()
            fil.close()
            rids = getRids(wholeText, dictTranslations)
            lstRids += rids
            for rid in rids:
                rid_file_pairs += str(rid) + "\t" + filename + "\n"
            hits05_15 += len(rids)
            sentFiles += filename + "\t" + str(len(rids)) + "\n"
            print(len(rids))
    print(len(lstRids))

    comp = 0
    for filename in os.listdir (baseFolder + "comp"):
        fil = open(baseFolder + "comp" + pathSep + filename, "r", encoding = "cp1252")
        wholeText = fil.read()
        fil.close()
        rids = getRids(wholeText, dictTranslations)
        lstRids += rids
        for rid in rids:
            rid_file_pairs += str(rid) + "\t" + filename + "\n"
        comp += len(rids)
        sentFiles += filename + "\t" + str(len(rids)) + "\n"
        print(len(rids))
    print(len(lstRids))

    nsubj_dobj = 0
    for filename in os.listdir (baseFolder + "nsubj_dobj"):
        fil = open(baseFolder + "nsubj_dobj" + pathSep + filename, "r", encoding = "cp1252")
        wholeText = fil.read()
        fil.close()
        rids = getRids(wholeText, dictTranslations)
        lstRids += rids
        for rid in rids:
            rid_file_pairs += str(rid) + "\t" + filename + "\n"
        nsubj_dobj += len(rids)
        sentFiles += filename + "\t" + str(len(rids)) + "\n"
        print(len(rids))
    print(len(lstRids))  

    poss = 0
    for filename in os.listdir (baseFolder + "poss"):
        fil = open(baseFolder + "poss" + pathSep + filename, "r", encoding = "cp1252")
        wholeText = fil.read()
        fil.close()
        rids = getRids(wholeText, dictTranslations)
        lstRids += rids
        for rid in rids:
            rid_file_pairs += str(rid) + "\t" + filename + "\n"
        poss += len(rids)
        sentFiles += filename + "\t" + str(len(rids)) + "\n"
        print(len(rids))
    print(len(lstRids))

    

    sillsallad1 = 0
    for filename in os.listdir (baseFolder + "sillsallad1"):
        fil = open(baseFolder + "sillsallad1" + pathSep + filename, "r", encoding = "cp1252")
        wholeText = fil.read()
        fil.close()
        rids = getRids(wholeText, dictTranslations)
        lstRids += rids
        for rid in rids:
            rid_file_pairs += str(rid) + "\t" + filename + "\n"
        sillsallad1 += len(rids)
        sentFiles += filename + "\t" + str(len(rids)) + "\n"
        print(len(rids))
    print(len(lstRids))

    sillsallad2 = 0
    for filename in os.listdir (baseFolder + "sillsallad2"):
        fil = open(baseFolder + "sillsallad2" + pathSep + filename, "r", encoding = "cp1252")
        wholeText = fil.read()
        fil.close()
        rids = getRids(wholeText, dictTranslations)
        lstRids += rids
        for rid in rids:
            rid_file_pairs += str(rid) + "\t" + filename + "\n"
        sillsallad2 += len(rids)
        sentFiles += filename + "\t" + str(len(rids)) + "\n"
        print(len(rids))
    print(len(lstRids))

    varia = 0
    for filename in os.listdir (baseFolder + "varia"):
        if "varia" in filename:
            fil = open(baseFolder + "varia" + pathSep + filename, "r", encoding = "cp1252")
            wholeText = fil.read()
            fil.close()
            rids = getRids(wholeText, dictTranslations)
            lstRids += rids
            for rid in rids:
                rid_file_pairs += str(rid) + "\t" + filename + "\n"
            varia += len(rids)
            sentFiles += filename + "\t" + str(len(rids)) + "\n"
            print(len(rids))
    print(len(lstRids))

    varia2plus = 0
    for filename in os.listdir (baseFolder + "varia2plus"):
        fil = open(baseFolder + "varia2plus" + pathSep + filename, "r", encoding = "cp1252")
        wholeText = fil.read()
        fil.close()
        rids = getRids(wholeText, dictTranslations)
        lstRids += rids
        for rid in rids:
            rid_file_pairs += str(rid) + "\t" + filename + "\n"
        varia2plus += len(rids)
        sentFiles += filename + "\t" + str(len(rids)) + "\n"
        print(len(rids))
    print(len(lstRids))
    
    print("\t16-50 :: " + str(fixed16_50))
    print("\tnolla :: " + str(nolla))
    print("\tpreps :: " + str(preps))
    print("\tutf8 :: " + str(utf8))
    print("\t05-15 :: " + str(hits05_15))
    print("\tcomp :: " + str(comp))
    print("\tnsubj_dobj :: " + str(nsubj_dobj))
    print("\tposs :: " + str(poss))
    print("\tpreps :: " + str(preps))
    print("\tsillsallad1 :: " + str(sillsallad1))
    print("\tsillsallad2 :: " + str(sillsallad2))
    print("\tvaria :: " + str(varia))
    print("\tvaria2plus :: " + str(varia2plus))

    f = open(binPath + pathSep + "sentFiles.txt" , "w", encoding="utf8")
    f.write(sentFiles)
    f.close()


    f = open(binPath + pathSep + "sentRids.txt" , "w", encoding="utf8")
    for rid in lstRids:
        f.write(rid)
        f.write("\n")
    f.close()

    f = open(binPath + pathSep + "rid_file_pairs.txt" , "w", encoding="utf8")
    f.write(rid_file_pairs)
    f.close()

    return lstRids
            

def getTranslationDict(translations):
    """
    Helper function to parse the metadata from the translation files
    translations = list of example texts (between the --- END OF SENTENCE --- notation)
    Returns a dict of format:
    dict[frame::lexunit::fes::fes_rel::fes_pos_fn] = rid
    """
    retDict = {}
    for translation in translations:
        frameText = getValue(translation, "frame")
        lexunit_name = getValue(translation, "lexunit_name")
        fes = getValue(translation, "fes")
        fes_rel = getValue(translation, "fes_rel")
        fes_pos_fn = getValue(translation, "fes_pos_fn")
        rid = getValue(translation, "rid")

        # Hieman nurinkurista, eikö vain?
        retDict[frameText + "::" + \
                lexunit_name + "::" + \
                fes +"::" + \
                fes_rel + "::" + \
                fes_pos_fn] = rid

    return retDict



def organizeLemmas(feePhrase, lemmaPhrase):
    """
    Gets a space-separated FEE and the corresponding space-separated lemmas
    Returns space-separated lemmas in the same order as the FEEs
    """
    fees = feePhrase.split(" ")
    lemmas = lemmaPhrase.split(" ")

    # Palautetaan alkuarvo, ellei arvo muutu myöhemmin
    ret = lemmaPhrase

    if (len(fees) != len(lemmas)) or \
       (lemmaPhrase == "EMPTY"):
        return ""

    if len(fees) == 2:
        if fees[0][0] == lemmas[0][0]:
            if fees[1][0] == lemmas[1][0]:
                ret = " ".join(lemmas)
        elif fees[0][0] == lemmas[1][0]:
            if fees[1][0] == lemmas [0][0]:
                ret = lemmas[1] + " " + lemmas[0]

    elif len(fees) == 3:
        if (fees[0][0] == lemmas[0][0]) and \
           (fees[1][0] == lemmas[1][0]) and \
           (fees[2][0] == lemmas[2][0]):
            ret = " ".join(lemmas)
        elif (fees[0][0] == lemmas[0][0]) and \
             (fees[1][0] == lemmas[2][0]) and \
             (fees[2][0] == lemmas[1][0]):
             ret = lemmas[0] + " " + lemmas[2] + " " + lemmas[1]
        elif (fees[0][0] == lemmas[1][0]) and \
             (fees[1][0] == lemmas[0][0]) and \
             (fees[2][0] == lemmas[2][0]):
             ret = lemmas[1] + " " + lemmas[0] + " " + lemmas[2]
        elif (fees[0][0] == lemmas[1][0]) and \
             (fees[1][0] == lemmas[2][0]) and \
             (fees[2][0] == lemmas[0][0]):
             ret = lemmas[1] + " " + lemmas[2] + " " + lemmas[0]
        elif (fees[0][0] == lemmas[2][0]) and \
             (fees[1][0] == lemmas[0][0]) and \
             (fees[2][0] == lemmas[1][0]):
             ret = lemmas[2] + " " + lemmas[0] + " " + lemmas[1]
        elif (fees[0][0] == lemmas[2][0]) and \
             (fees[1][0] == lemmas[1][0]) and \
             (fees[2][0] == lemmas[0][0]):
             ret = lemmas[2] + " " + lemmas[1] + " " + lemmas[0]
    
        if ret == "":
            ret = " ".join(lemmas)
                   
    return ret                       





def extractFeeWordsRightDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 8right
    Creates a CQP list:
    FEE: search words, (deprels), lemmas
    right context: deprels
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """
    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []
    pos = 0

    lstFeeWords = None
    
    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            #lemmas = organizeLemmas(lstWords[i], feeLemmas)
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")
                pos = i
            if (i == (len(lstDeprels)-1)):
                return ""
            #break

    
    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""
    
    lemmas = lemmas.split(" ")

    # Varotoimenpide
    if lstFeeWords is None:
        return ""

    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""

    k = 0
    for i in range(pos, len(lstWords)):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            if lstDeprels[i] == "FEE":
                # aineistosta puuttuu FEE:n jäsennystiedot
                # deprel ei siis ole tiedossa,
                # eikä sitä voi lisätä haun tarkennukseksi
                # lemmat sen sijaan lisätään
                words.append(singleWord)
                crits.append("word")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(True)
            
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            elif lstDeprels[i].startswith("FEE|"):
                words.append(singleWord)
                crits.append("word")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(True)
                
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")

                if len(lemmas) == 1:
                    continues.append(True)

                    words.append(lstDeprels[i][4:])
                    crits.append("deprel")
                    equals.append("==")
                    partials.append("")
                    labels.append("")
                    depheads.append("")

                #if i == (len(lemmas) -1):
                continues.append(False)
                #else:
                #continues.append(False)
                    
            else:
                words.append(lstDeprels[i])
                crits.append("deprel")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)
        
    return cqpList


def extractFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 11
    Creates a CQP list:
    FEE: lemmas
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """
    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []
    pos = 0

    lstFeeWords = None
    
    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            lemmas = organizeLemmas(lstWords[i], feeLemmas)
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")
            #if (lemmas == ""):
            #    return ""
            #break

    
    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""
    
    lemmas = lemmas.split(" ")

    # Varotoimenpide
    if lstFeeWords is None:
        return ""

    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""

    k = 0
    for i in range(0, len(lstWords)):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            if lstDeprels[i].startswith("FEE"):
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)

    return cqpList


def extractFeeWordsFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 10
    Creates a CQP list:
    FEE: search words, lemmas
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """
    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []
    pos = 0

    lstFeeWords = None
    
    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            #lemmas = organizeLemmas(lstWords[i], feeLemmas)
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")
            #if (lemmas == ""):
            #    return ""
            #break

    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""     
    lemmas = lemmas.split(" ")

    # Varotoimenpide
    if lstFeeWords is None:
        return ""

    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""

    k = 0
    for i in range(0, len(lstWords)):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            if lstDeprels[i].startswith("FEE"):
                # aineistosta puuttuu FEE:n jäsennystiedot
                # deprel ei siis ole tiedossa,
                # eikä sitä voi lisätä haun tarkennukseksi
                # lemmat sen sijaan lisätään
                words.append(singleWord)
                crits.append("word")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(True)
            
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)

    return cqpList


def extractFeeWordsFeeDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 9
    Creates a CQP list:
    FEE: search words, (deprels), lemmas
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """
    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []
    pos = 0

    lstFeeWords = None
    
    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            #lemmas = organizeLemmas(lstWords[i], feeLemmas)
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")


    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""     
    lemmas = lemmas.split(" ")

    # Varotoimenpide
    if lstFeeWords is None:
        return ""

    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""

    k = 0
    for i in range(0, len(lstWords)):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            if lstDeprels[i] == "FEE":
                # aineistosta puuttuu FEE:n jäsennystiedot
                # deprel ei siis ole tiedossa,
                # eikä sitä voi lisätä haun tarkennukseksi
                # lemmat sen sijaan lisätään
                words.append(singleWord)
                crits.append("word")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(True)
            
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            elif lstDeprels[i].startswith("FEE|"):
                words.append(singleWord)
                crits.append("word")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(True)
                
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")

                if len(lemmas) == 1:
                    continues.append(True)

                    words.append(lstDeprels[i][4:])
                    crits.append("deprel")
                    equals.append("==")
                    partials.append("")
                    labels.append("")
                    depheads.append("")

                #if i == (len(lemmas) -1):
                continues.append(False)

                #else:
                #    continues.append(True)
                    
            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)

    return cqpList
    

def extractFeeWordsLeftDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 8left
    Creates a CQP list:
    left context: deprels
    FEE: search words, (deprels), lemmas
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """
    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []
    pos = 0

    lstFeeWords = None
    
    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            #lemmas = organizeLemmas(lstWords[i], feeLemmas)
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")
            pos = i
            if (i == 0):
                return ""
            #break

    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""
    lemmas = lemmas.split(" ")

    # Varotoimenpide
    if lstFeeWords is None:
        return ""

    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""

    k = 0
    for i in range(0, (pos + 1)):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            if lstDeprels[i] == "FEE":
                # aineistosta puuttuu FEE:n jäsennystiedot
                # deprel ei siis ole tiedossa,
                # eikä sitä voi lisätä haun tarkennukseksi
                # lemmat sen sijaan lisätään
                words.append(singleWord)
                crits.append("word")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(True)
            
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            elif lstDeprels[i].startswith("FEE|"):
                words.append(singleWord)
                crits.append("word")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(True)
                
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")

                if len(lemmas) == 1:
                    continues.append(True)

                    words.append(lstDeprels[i][4:])
                    crits.append("deprel")
                    equals.append("==")
                    partials.append("")
                    labels.append("")
                    depheads.append("")

                    #if i == (len(lemmas) -1):
                    #continues.append(False)
                    #else:
                continues.append(False)
                    
            else:
                words.append(lstDeprels[i])
                crits.append("deprel")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)
        
    return cqpList


def extractFeeWordsAllDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 7
    Creates a CQP list:
    left context: deprels
    FEE: search words, (deprels), lemmas
    right context: deprels
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """
    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []
    pos = 0

    lstFeeWords = None
    
    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            #lemmas = organizeLemmas(lstWords[i], feeLemmas)
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")
            #if (lemmas == ""):
            #    return ""
            #break

          
    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""
    
    lemmas = lemmas.split(" ")

    # Varotoimenpide
    if lstFeeWords is None:
        return ""

    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""

    k = 0
    for i in range(0, len(lstWords)):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            if lstDeprels[i] == "FEE":
                # aineistosta puuttuu FEE:n jäsennystiedot
                # deprel ei siis ole tiedossa,
                # eikä sitä voi lisätä haun tarkennukseksi
                # lemmat sen sijaan lisätään
                words.append(singleWord)
                crits.append("word")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(True)
            
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            elif lstDeprels[i].startswith("FEE|"):
                words.append(singleWord)
                crits.append("word")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(True)
                
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")

                if len(lemmas) == 1:
                    continues.append(True)

                    words.append(lstDeprels[i][4:])
                    crits.append("deprel")
                    equals.append("==")
                    partials.append("")
                    labels.append("")
                    depheads.append("")

                #if i == (len(lemmas) -1):
                continues.append(False)
                #else:
                #    continues.append(True)
                    
            else:
                words.append(lstDeprels[i])
                crits.append("deprel")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)
        
    return cqpList


def extractRightWordsAllDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 4right
    Creates a CQP list:
    FEE: search words, (deprels), lemmas
    right context: search words, (deprels)
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """
    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []
    pos = 0

    lstFeeWords = None
    
    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            #lemmas = organizeLemmas(lstWords[i], feeLemmas)
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")
                pos = i
            if (i == (len(lstDeprels)-1)):
                return ""
            #break

    

    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""
    
    lemmas = lemmas.split(" ")

    # Varotoimenpide
    if lstFeeWords is None:
        return ""

    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""


    k = 0
    for i in range(pos, len(lstWords)):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            words.append(singleWord)
            crits.append("word")
            equals.append("==")
            partials.append("")
            labels.append("")
            depheads.append("")
            continues.append(True)

            if lstDeprels[i] == "FEE":
                # aineistosta puuttuu FEE:n jäsennystiedot
                # deprel ei siis ole tiedossa,
                # eikä sitä voi lisätä haun tarkennukseksi
                # lemmat sen sijaan lisätään
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            elif lstDeprels[i].startswith("FEE|"):
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")

                if len(lemmas) == 1:
                    continues.append(True)

                    words.append(lstDeprels[i][4:])
                    crits.append("deprel")
                    equals.append("==")
                    partials.append("")
                    labels.append("")
                    depheads.append("")

                #if i == (len(lemmas) -1):
                continues.append(False)
                #else:
                #continues.append(True)
                    
            else:
                words.append(lstDeprels[i])
                crits.append("deprel")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)
        
    return cqpList


def extractLeftWordsAllDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 4left
    Creates a CQP list:
    left context: search words, (deprels)
    FEE: search words, (deprels), lemmas
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """
    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []
    pos = 0

    lstFeeWords = None
    
    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            #lemmas = organizeLemmas(lstWords[i], feeLemmas)
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")
            pos = i
            if (i == 0):
                return ""
            #break

            

    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""
          
    lemmas = lemmas.split(" ")

    # Varotoimenpide
    if lstFeeWords is None:
        return ""
    
    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""

    k = 0
    for i in range(0, (pos + 1)):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            words.append(singleWord)
            crits.append("word")
            equals.append("==")
            partials.append("")
            labels.append("")
            depheads.append("")
            continues.append(True)

            if lstDeprels[i] == "FEE":
                # aineistosta puuttuu FEE:n jäsennystiedot
                # deprel ei siis ole tiedossa,
                # eikä sitä voi lisätä haun tarkennukseksi
                # lemmat sen sijaan lisätään
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            elif lstDeprels[i].startswith("FEE|"):
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")

                if len(lemmas) == 1:
                    continues.append(True)

                    words.append(lstDeprels[i][4:])
                    crits.append("deprel")
                    equals.append("==")
                    partials.append("")
                    labels.append("")
                    depheads.append("")

                #if i == (len(lemmas) -1):
                continues.append(False)
                #else:
                #continues.append(True)
                    
            else:
                words.append(lstDeprels[i])
                crits.append("deprel")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)
        
    return cqpList


def extractAllWordsAllDeprelsFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 1
    Creates a CQP list:
    left context: search words, (deprels)
    FEE: search words, (deprels), lemmas
    right context: search words, (deprels)
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """
    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []

    lstFeeWords = None

    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")
            #lemmas = organizeLemmas(lstWords[i], feeLemmas)
            #if lemmas == "":
            #    return ""
            #break

    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""
    
    lemmas = lemmas.split(" ")

    try:
        a = len(lstFeeWords)
    except:
        print(lstWords)
        print(lstDeprels)
        print(feeLemmas)
        
    # Varotoimenpide
    if lstFeeWords is None:
        return ""

    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""
   

    k = 0
    for i in range(0, len(lstWords) ):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            words.append(singleWord)
            crits.append("word")
            equals.append("==")
            partials.append("")
            labels.append("")
            depheads.append("")
            continues.append(True)

            if lstDeprels[i] == "FEE":
                # aineistosta puuttuu FEE:n jäsennystiedot
                # deprel ei siis ole tiedossa,
                # eikä sitä voi lisätä haun tarkennukseksi
                # lemmat sen sijaan lisätään
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            elif lstDeprels[i].startswith("FEE|"):
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")

                if len(lemmas) == 1:
                    continues.append(True)

                    words.append(lstDeprels[i][4:])
                    crits.append("deprel")
                    equals.append("==")
                    partials.append("")
                    labels.append("")
                    depheads.append("")

                    #if k == (len(lemmas) -1):
                continues.append(False)
                #else:
                #continues.append(True)
                    
            else:
                words.append(lstDeprels[i])
                crits.append("deprel")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)
        
    return cqpList


def extractRightWordsFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 5right
    Creates a CQP list:
    FEE: search words, lemmas
    right context: search words
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """
    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []

    lstFeeWords = None
    
    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            #lemmas = organizeLemmas(lstWords[i], feeLemmas)
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")
                pos = i
            if (i == (len(lstDeprels)-1)):
                return ""
            #break

    
    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""
    lemmas = lemmas.split(" ")

    # Varotoimenpide
    if lstFeeWords is None:
        return ""

    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""

    k = 0
    for i in range(pos, len(lstWords)):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            words.append(singleWord)
            crits.append("word")
            equals.append("==")
            partials.append("")
            labels.append("")
            depheads.append("")
            

            if lstDeprels[i].startswith("FEE"):
                # Lisätään lemmat
                continues.append(True)
                
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            else:
                continues.append(False)

            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)
        
    return cqpList


def extractLeftWordsFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 5left
    Creates a CQP list:
    left context: search words
    FEE: search words, lemmas
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """
    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []

    lstFeeWords = None
    
    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            lemmas = organizeLemmas(lstWords[i], feeLemmas)
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")
            pos = i
            if (i == 0):
                return ""
            #break

    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""
    lemmas = lemmas.split(" ")

    # Varotoimenpide
    if lstFeeWords is None:
        return ""

    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""

    k = 0
    for i in range(0, (pos + 1)):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            words.append(singleWord)
            crits.append("word")
            equals.append("==")
            partials.append("")
            labels.append("")
            depheads.append("")
            

            if lstDeprels[i].startswith("FEE"):
                # Lisätään lemmat
                continues.append(True)
                
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            else:
                continues.append(False)

            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)
        
    return cqpList


def extractAllWordsFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 2
    Creates a CQP list:
    left context: search words
    FEE: search words, lemmas
    right context: search words
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """
    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []

    lstFeeWords = None
    
    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")
            #lemmas = organizeLemmas(lstWords[i], feeLemmas)
            #if lemmas == "":
            #    return ""
            #break

    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""
    lemmas = lemmas.split(" ")

    # Varotoimenpide
    if lstFeeWords is None:
        return ""

    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""


    k = 0
    for i in range(0, len(lstWords) ):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            words.append(singleWord)
            crits.append("word")
            equals.append("==")
            partials.append("")
            labels.append("")
            depheads.append("")
            

            if lstDeprels[i].startswith("FEE"):
                # Lisätään lemmat
                continues.append(True)
                
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            else:
                continues.append(False)

            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)
        
    return cqpList


def extractRightCoreWordsFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 6right
    Creates a CQP list:
    FEE: lemmas
    right context: search words
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """
    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []

    lstFeeWords = None
    
    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            #lemmas = organizeLemmas(lstWords[i], feeLemmas)
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")
                pos = i
            if (i == (len(lstDeprels)-1)):
                return ""
            #break

    
    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""
    lemmas = lemmas.split(" ")

    # Varotoimenpide
    if lstFeeWords is None:
        return ""

    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""


    k = 0
    for i in range(pos, len(lstWords)):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            if lstDeprels[i].startswith("FEE"):
                # Pelkät lemmat
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            else:
                words.append(singleWord)
                crits.append("word")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)
        
    return cqpList


def extractLeftCoreWordsFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 6left
    Creates a CQP list:
    left context: search words
    FEE: lemmas
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """

    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []

    lstFeeWords = None
    
    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            #lemmas = organizeLemmas(lstWords[i], feeLemmas)
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")
            pos = i
            if (i == 0):
                return ""
            #break

    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""
    lemmas = lemmas.split(" ")

    # Varotoimenpide
    if lstFeeWords is None:
        return ""

    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""


    k = 0
    for i in range(0, (pos + 1)):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            if lstDeprels[i].startswith("FEE"):
                # Pelkät lemmat
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            else:
                words.append(singleWord)
                crits.append("word")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)
        
    return cqpList


def extractCoreWordsFeeLemmas(lstWords, lstDeprels, feeLemmas):
    """
    Search method: 3
    Creates a CQP list:
    left context: search words
    FEE: lemmas
    right context: search words
    
    lstWords = list of space-separated search words/phrases
    lstDeprels = list of deprels corresponding to lstWords (FEE is marked by "FEE" or "FEE|deprel"))
    feeLemmas = space-separated lemmas corresponding to FEE(s)
    Returns a CQP list
    """

    lstCriteria = []

    words = []
    crits = []
    equals = []
    continues = []
    partials = []
    labels = []
    depheads = []

    lstFeeWords = None
    
    # Tarkistetaan, että FEE ja lemmat täsmäävät
    for i in range(0,len(lstDeprels)):
        if lstDeprels[i].startswith("FEE"):
            if lstFeeWords != None:
                lstFeeWords.extend(lstWords[i].split(" "))
            else:
                lstFeeWords = lstWords[i].split(" ")

    lemmas = organizeLemmas(" ".join(lstFeeWords), feeLemmas)
    if lemmas == "":
        return ""
    lemmas = lemmas.split(" ")

    # Varotoimenpide
    if lstFeeWords is None:
        return ""

    if (len(lstWords) != len(lstDeprels)) or \
       (len(lstFeeWords) != len(lemmas)):
        return ""


    k = 0
    for i in range(0, len(lstWords) ):

        lstSingleWords = lstWords[i].split(" ")
        
        for singleWord in lstSingleWords:

            if lstDeprels[i].startswith("FEE"):
                # Pelkät lemmat
                words.append(lemmas[k])
                crits.append("lemma")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            else:
                words.append(singleWord)
                crits.append("word")
                equals.append("==")
                partials.append("")
                labels.append("")
                depheads.append("")
                continues.append(False)

            k += 1

    cqpList = createCqp(words, \
                        crits, \
                        partials, \
                        equals, \
                        continues, \
                        labels, \
                        depheads)
        
    return cqpList




    
def getRids(text, dictFrameText = {}):
    """
    Gets a file that has been sent for the annotation
    Returns a list of rids
    """

    retRids = []
    frames = re.split("\n\nrid\=", text)

    
    if re.search("rid=[0-9]+", text):
        print("MIKSEI JO NATSAISI")
        
    # Neljä variaatiota:
    # 1. rid=
    # 2. rid=12345
    # 3. frame="diibadaaba"
    # 4. 12345frame=diibadaaba
    if len(frames) >= 2:
        
        # Tässä käsitellään tapaukset 1 ja 2
        for frame in frames:
            rid = ""
            match = re.search("rid=([0-9]+)", frame)
            if match != None:
                rid = match.groups()[0]
                #print(rid)
            else:
                try:
                    frameText = getFrameText(frame)
                    #for key in dictOriginals.keys():
                    #    if frameText in dictOriginals[key]:
                    #        rid = key
                    #        break
                    #if rid == "":
                    #    raise Exception
                    rid = dictFrameText[frameText]
                except:
                    print("*****")
                    print(frame)
                    raise Exception
                
            if rid != "":
                retRids.append(rid)
    else:

        # Tässä käsitellään tapaukset 3 ja 4
        frames = re.split("\n\n\n+", text)
        newFrames = ['']
        for frame in frames:
            try:
                if re.search("rid=[0-9]+", frame):
                    print(re.search("rid=[0-9]+"), frame)
                    
                if (("frame=" in frame) == False):
                    newFrames[(len(newFrames)-1)] += frame
                #elif ((frame.count("frame=") > 1)):
                #elif re.search(".*KLK_FI.*frame=", frame):   
                #    frs = frame.split("frame=")
                #    print("LEN(FRS)=" + str(len(frs)))
                #    j = 0
                #    for fr in frs:
                #        if j != 0:
                #            # add back the 'frame=', which was lost in the split
                #            fr = "frame=" + fr
                #
                #        if re.search("\n[0-9]+$", fr):
                #            # move rid to next fr, because it belongs there
                #            # format was:
                #            # 12345frame"diibadaaba"
                #            rid = re.search("([0-9]+)$", fr).group()
                #            fr = re.match("(.*?)[0-9]+$", fr).groups()
                #        elif rid != "":
                #            fr = rid + "\n" + fr
                #            rid = ""
                #
                #        if (("frame=" in fr) == False):
                #            newFrames[(len(newFrames)-1)] += fr
                #        else:
                #            newFrames.append(fr)
                #        
                #        j += 1
                else:
                    newFrames.append(frame)
            except:
                print(len(newFrames)-1)
                print(newFrames[(len(newFrames)-1)])
                print(frame[0:100])
                raise Exception

        for frame in newFrames:
            if (frame == "") or (frame is None) or (len(frame) < 50):
                continue
            elif frame.startswith(" KLK_FI_"):
                continue
                      
            rid = ""
            match = re.search("^([0-9]+)", frame)
            
            if match != None:
                rid = re.search("[0-9]+", frame).group()
            else:
                match = re.search("rid=([0-9]+)", frame)
                if match != None:
                    rid = match.group()
                else:
                    try:
                        
                        frameText = getFrameText(frame)
                        #for key in dictOriginals.keys():
                        #    if frameText in dictOriginals[key]:
                        #        rid = key
                        #        break
                        if frameText == None:
                            print("")
                            print("??????????????????????????????")
                            print(frame)
                            raise Exception
                        rid = dictFrameText[frameText]
                        retRids.append(rid)
                        
                    except:
                        
                        print(type(frame))
                        print(len(frame))
                        print(frame)
                        if rid == "":
                            print("*^*^*^*^")
                            print(frameText)
                            print("*****^^^^^^^^^********")
                            for key in dictFrameText.keys():
                                print(key)
                                print(dictFrameText[key])
                                break
                            raise Exception
                        #rid = dictTranslations[frameText]
                    #except:
                        if (frame.startswith(" KLK_FI_")) or (frame.lstrip() == ""):
                            raise Exception
                            pass
                        else:
                            print("*****")
                            print(frame)
                            print(frameText)
                            print(rid)
                            raise Exception

                        #rid = dictTranslations[frameText]
                    #except:
                    #    if (frame.startswith(" KLK_FI_")) or (frame.lstrip() == ""):
                    #        raise Exception
                    #        pass
                    #    else:
                    #        print("***")
                    #        print(frame)
                    #        print(frameText)
                    #        print(rid)
                    #        raise Exception
                            

            if rid != "":
                retRids.append(rid)
            else:
                print(frameText)
                raise Exception
    return retRids            
            
        
def getFrameText(example):
    """
    Helper function to get relevant information from the original files
    example = example from the original file
    Returns a string containing the necessary elements to find the unique rid
    """
    frame = getValue(example, "frame")
    lexunit_name = getValue(example, "lexunit_name")

    fes = getValue(example, "fes")
    fes = " ".join(fes.split(","))
    
    fes_rel = getValue(example, "fes_rel")
    fes_rel = " ".join(fes_rel.split(","))
                       
    fes_pos_fn = getValue(example, "fes_pos_fn")
    fes_pos_fn = " ".join(fes_pos_fn.split(","))

    
    retVal = frame + "::" + \
             lexunit_name + "::" + \
             fes +"::" + \
             fes_rel + "::" + \
             fes_pos_fn
    
    return retVal


def getRidsFromFile(filename):
    """
    Helper function to read rids from a file
    Returns a list of rids
    """
    if os.path.isfile(filename):
        f = open (filename, "r", encoding="cp1252")
        ridText = f.read()
        f.close()
        rids = ridText.split("\n")
        return rids
    else:
        return []
                                    

def getSearchWordsAndDeprels(original, translatedWords):
    """
    Gets metadata from the original file, and a list of translated words
    original[0] = example
    original[1] = [elems]
    translatedWords = list of translated elems, (each elem might contain 0-n words)
    Returns a tuple of:
    A) a tab-separated list of core words (even starts with a tab, just in case)
    B) a tab-separated list of deprels (even starts with a tab, just in case)
    """
    sentence = original[0]
    elems = original[1]

    frame = getValue(sentence, "frame")
    lexunit_name = getValue(sentence, "lexunit_name")
    fes = getValue(sentence, "fes")
    dictFes_rels = getFesRels(sentence)
    fes_pos_fn = getValue(sentence, "fes_pos_fn")

    #print(frame + "\t" + lexunit_name + "\t" + "; ".join(translatedWords))


    
    i = 0
    elemtypes = []
    elemTexts = []
    elTypes =[]
    fe_core_types = []
    fe_rels = []

    feeText = ""

    coreWords = ""
    
    #if len(elems) != len(translatedWords):
    #    print(elems)
    #    print(translatedWords)
    #    return "", ""
    
    for elem in elems:
        elemOneLiner = " ".join(elem)
        elemtype = getValue(elemOneLiner, "elemtype")
        elType = getValue(elemOneLiner, "type")
        fe_core_type = getValue(elemOneLiner, "fe_core_type")

        # Must be matched as a dictionary
        if elType == "FEE":
            fe_rel = "FEE"
        elif elType == "Verb_chain":
            fe_rel = "verb_chain"
        else:
            try:
                if elType.startswith("FEE|"):
                    feType = elType[4:]
                else:
                    feType = elType
                    
                # Ei järin eleganttia
                # otetaan mukaan POS-tagiinkin
                if feType in dictFes_rels:
                    if elType.startswith("FEE|"):
                        fe_rel = "FEE|" + dictFes_rels[feType]
                    else:
                        fe_rel = dictFes_rels[feType]
                else:
                    # These actually exist: faulty data
                    fe_rel = ""
                    #fe_rel = dictFes_rels[elType]
            except:
                print(sentence)
                print(elem[-1])
                raise

        #if "kidneypapuja ja" in translatedWords:
        #    print(elemOneLiner)
        #    print(fe_core_type)
        #    print(elemtype)
        #    print(elType)
        #    print(elem[-1])
        #    print(fe_rel)
        
        
        elemText = elem[-1]

        elemtypes.append(elemtype)
        elTypes.append(elType)
        elemTexts.append(elemText)
        fe_core_types.append(fe_core_type)
        fe_rels.append(fe_rel)

        if (elType == "Verb_chain") and \
           (("empty" in translatedWords[i]) == False):
            feeText += translatedWords[i] + " "
        elif elemtype.startswith("fee"):
            feeText += translatedWords[i]
            feePos = i

        i += 1

    words = ""
    
    
    
    # Start checking

    words = ""
    core_fe_rels = ""
    if (len(elemtypes) == len(translatedWords)):
        for i in range(len(translatedWords)):
            if fe_core_types[i].startswith("Core"):
                coreWords += "\t" + translatedWords[i]
                core_fe_rels += "\t" + fe_rels[i]
            elif (elemtypes[i].startswith("fee")) or \
                 ((elTypes[i] == "Verb_chain") and (("empty" in translatedWords[i]) == False)):
                coreWords += "\t" + translatedWords[i]
                core_fe_rels += "\t" + fe_rels[i]
    else:
        try:
            #print("####")
            #print(translatedWords)
            #print(elemtypes)
            #print(fe_core_types)
            #print(feePos)
            #print(feeText)
            #print("##")
            if translatedWords[feePos] == feeText:
                #offset = 0
                
                for i in range(len(translatedWords)):
                    if fe_core_types[i] == "Core":
                        coreWords += "\t" + translatedWords[i]
                        core_fe_rels += "\t" + fe_rels[i]
                    elif (elemtypes[i].startswith("fee")) or \
                         ((elTypes[i] == "Verb_chain") and (("empty" in translatedWords[i]) == False)):
                        coreWords += "\t" + translatedWords[i]
                        core_fe_rels += "\t" + fe_rels[i]
            else:
                for i in reversed(range(len(translatedWords))):
                    if fe_core_types[i] == "Core":
                        coreWords = translatedWords[i] + "\t" + coreWords
                        core_fe_rels = fe_rels[i] + "\t" + core_fe_rels
                    elif (elemtypes[i].startswith("fee")) or \
                         ((elTypes[i] == "Verb_chain") and (("empty" in translatedWords[i]) == False)):
                        coreWords = translatedWords[i] + "\t" + coreWords
                        core_fe_rels = fe_rels[i] + "\t" + core_fe_rels
                core_fe_rels = "\t" + core_fe_rels[:-1]
                coreWords = "\t" + coreWords[:-1]
        except:
            pass
    # lexunit_namen viimeinen merkki kertoo sanaluokan
    core_fe_rels = lexunit_name[-1] + core_fe_rels
    #if 'kirjoittaa aviollinen nimeni kirjekuoreen' in coreWords:
    #    print(coreWords)
    #    print(translatedWords)
    #    print(core_fe_rels)
    #    print(core_fe_rels.replace("\t", "#"))
    #    print(fe_rels)
    #    raise Exception
    
    #if "kidneypapuja" in coreWords:
    #    print(coreWords)
    #    print(core_fe_rels)
    #    print(translatedWords)
    #    print(feeText)
    #    print(feePos)
    #    raise Exception
    
    return coreWords, core_fe_rels




def getFesRels(sentence):
    """
    Gets a sentence, and extracts the fes_rels from it
    Returns a dict in format:
    dict["Agent"] = "nsubj"
    """
    retFesRels = {}
    fesRels = getValue(sentence, "fes_rel")
    lstFesRels = fesRels.split(",")

    for fesRel in lstFesRels:
        # Älä korjaa, ellei se ole rikki
        match = re.search("^([^\[]+)\[([^\]]*)\]",fesRel)
        if match == None:
            return ""
        
        try:
            retFesRels[match.groups()[0]] = match.groups()[1]
        except:
            print(sentence)
            raise
        

    
    return retFesRels

              
def getValue(sentence, attributeName):
    """
    Helper function, retrieves the attribute value from a text excerpt
    Special handling for FEEs
    sentence = a sentence from the original file, must contain syntax:
    attributeName="value"
    Return the value
    """

    start = "(\W|^)"
    if attributeName == "FEE":
        try:
            # Ensin englanninkielinen versio
            match = re.search(start + 'elemtype="fee' + '(.*)\n', sentence)
            feeRow = match.groups()[1]
            match = re.search("(,,)(.*)(,)", feeRow)
            if match is not None:
                englishFEE = match.groups()[1]
            else:
                match = re.search('fe_core_type=".*",(.*),', feeRow)
                if match is not None:
                    englishFEE = match.groups()[0]
                else:
                    match = re.search('(>)(.*)(</)', feeRow)
                    if match is not None:
                        englishFEE = match.groups()[1]
            match = re.search(start + "(,," + englishFEE + ",,)([^\n]+)", sentence)
            finnishFEE = match.groups()[2]
        except:
            print(sentence)
            raise Exception
        return finnishFEE

    if attributeName == "korpId":
        yearMatch = re.search("[0-9]+", sentence).group()
        year = re.search("[0-9]+", yearMatch).group()
        runningIdMatch = re.search(" sentence [0-9]+", sentence).group()
        runningId = re.search("[0-9]+", runningIdMatch).group()
        #positionMatch = re.search("position [0-9]+", sentence).group()
        #positionId = re.search("[0-9]+", positionMatch).group()
        return year + "_" + runningId #+ "_" + positionMatch
    
    match = re.search(start + attributeName + "\=\"[^\"]+", sentence)
    if match == None:
        return ""

    match = re.search("(" + attributeName + "\=\")([^\"]+)", match.group())
    if match == None:
        return ""

    
    return match.groups()[1]
    




def getSentencesFewDecadesAtATime(maxSentencesPerDecade, \
                                  maxHitsTotal, \
                                  cqpList, \
                                  corpora=[], \
                                  verbose=False):
    """
    Helper function to group decades together, so that
    A) several decades can be searched together and
    B) it's possible to continue searching if it's still necessary using other decades
    maxSentencesPerDecade: makes it possible to distribute hits into different decades
    maxHitsTotal: limits the total number of sentences
    cqpList: the search clause to make requests from Korp
    corpora: list of comma-separated corpora lists in ucnn -format (eg. u193 = 1930-1939)
    verbose: for troubleshooting purposes only, if the Korp requests take really long
    Returns a list of sentences 
    """
    lstSentences = []
    commaSepCorpora = ""
    if corpora == []:
        # Todettiin, että 1930-lukua vanhempia ei kannata ottaa mukaan huonon OCR-tuloksen vuoksi
        corpora.append("u199,u198,u197,u196,u195,u194,u193")
        #corpora.append("u200,u193,u192,u191,u190")
        #corpora.append("u189,u188,u187,u186,u185,u184,u183,u182")
    
    for corpus in corpora:
        t0 = time.clock()
        lstSents = wget_normal(cqpList, corpus, maxSentencesPerDecade)
        t = time.clock() - t0

        if verbose:
            print (t)

        lstSentences.extend(lstSents)
        if len(lstSentences) >= maxHitsTotal:
            break

    if verbose:
        print(" ".join(cqpList) + " :: " + str(len(lstSentences)))
        
    return lstSentences




def writeOutput(writeFile, text, textType, prefix="", suffix="", verbose=False):
    """
    Helper function to write text
    writeFile = avoin tiedosto
    text = kirjoitettava tieto
    textType = kirjoitettavan tiedon yläkäsite (vain virheilmoituksia varten)
    prefix = tekstin eteen kirjoitettava erotinmerkki tms.
    suffix = tekstin perään kirjoitettava erotinmerkki tms.
    verbose = True -> virheilmoitukset näytetään ruudulla
    """
                                    
    try:
        writeFile.write(prefix + text + suffix)
    except:
        try:
            fixedText = fixString(text)
            writeFile.write(prefix + fixedText + suffix)
            
        except:
            if verbose:
                print("\nJäi kirjoittamatta " + textType)
            writeFile.write("*** Tästä puuttuu " + textType + "***")
            if verbose:
                print(text)
                            




def makeBoldedOneLiner(sentence):
    """
    Gets a sentence, which is retrieves from Korp,
    parses it, and "highlights" the found words with asterisks
    """
    words = sentence.split("\n")
    retWords = []
    asterisksHandled = False
    prevAsterisk = False
    start = False
    end = False
    for word in words[1:]:
        if (word.startswith('"*"')) and (prevAsterisk == False):
            start = True
            end = False
            prevAsterisk = True
        elif word.startswith('"*"') and (prevAsterisk == True):
            start = False
        elif (word.startswith('"*"') == False):
            start = False
            if (prevAsterisk == True):
                end = True
                prevAsterisk = False
            else:
                end = False
                
        match = re.search(",\"([^\"])+\"",word)
        if match == None:
            word = ""
        else:
            word = match.group()[2:-1]
            word = word.strip(" ")
            if len(word) != 0:
                if start == True:
                    retWords.append("*****")
                    retWords.append(word)
                elif end == True:
                    # Tässä kirjoitetaan siis ensimmäinen sana
                    # viimeisen asteriskisanan jälkeen
                    retWords.append("*****")
                    retWords.append(word)
                else:
                    retWords.append(word)

    if prevAsterisk == True:
        retWords.append("*****")

    joinedSentence = " ".join(retWords)
    joinedSentence = "\"" + joinedSentence + "\""
    return joinedSentence


def selectRandomSentences(lstSentences, maxSentences):
    """
    Gets a list of found sentences and the maximum amount of sentences to return
    Returns a list of maximum number of sentences in a random order
    """
    retSentences = []
    for sentence in lstSentences:
        if isValidSentence(sentence):
            retSentences.append(sentence)
    if len(retSentences) > maxSentences:
        shuffle(retSentences)

    retSentences = retSentences[:maxSentences]
    return retSentences


def isValidSentence(sentence):
    """
    Helper function to use with selectRandomSentences
    Checks for a certain amount of consecutive short or long words within a sentence
    The idea was to discard sentences with mostly empty words (OCR faults)
    Obsolete, if using good OCR results (=modern corpora) or Korp sentences are tagged
    """
    words = sentence.split("\n")
    if len(words) <= 3:
        return False
    else:
        consecutiveOne = 0
        consecutiveTwo = 0
        stringi = ""
        for word in words:
            if len(word) == 8:
                consecutiveTwo += 1
                consecutiveOne += 1
                stringi += word
            elif len(word) <= 7:
                consecutiveOne += 1
                consecutiveTwo = 0
                stringi += word
            else:
                if consecutiveOne >= 4 or consecutiveTwo >= 6:
                    return False
                else:
                    consecutiveOne = 0
                    consecutiveTwo = 0
                    stringi = ""

        # check for consecutive non-vowels & non-nouns?
        
    return True
                                      
def fixString(string):
    """
    Helper function to reduce write errors when writing in Win format
    """
    retString = b''
    for i in range(0,len(string)):
        if string[i].encode("cp1252", "ignore") == b'':
            retString += b"0"
        else:
            retString += string[i].encode("cp1252")
    return retString

            
def parseFees(filename):
    """
    Gets a translation file and parses it retrieving the FEE:s
    Return a list of sentences:
    [rid, wordList], where wordList is a list of actual FEE:s
    """
    f = open(filename, "r", encoding = "utf8")
    fullText = f.read()
    f.close()
    sentences = str.split(fullText, "-------------------- END OF SENTENCE --------------------\n</sentence>\n")
    
    sentenceList = []
    for sentence in sentences[:-1]:
        wordList = []
        
        rid = re.search('rid=\"([^\"])*\"', sentence).group()
        rid = rid[5:-1]
        #elements = re.split("((type=\"fee\")([^>])*>)|((type=\"fe\")([^>])*>)", sentence)
        #elements = re.split("(<elem elemtype=\"([^>])*>)", sentence)
        elements = re.split("(<elem elemtype=\"fee([^>])*>)", sentence)
        for element in elements:
            if element != None:
                if element != "" \
                   and (element.startswith("type=") == False) \
                   and (element != "\"") \
                   and (element.startswith("<") == False) :
                    textPart = re.split("</", element)[0]
                    if (("empty" in textPart) == False):
                        wordList.append (textPart)

        sentenceList.append([rid, wordList])
                
    return sentenceList


def parseTranslations(filename):
    """
    Gets a translation file and parses it retrieving the translations
    Returns a list of sentences:
    [rid, wordList], where wordList is a list of actual element texts
    """
    f = open(filename, "r", encoding = "utf8")
    fullText = f.read()
    f.close()
    sentences = str.split(fullText, "-------------------- END OF SENTENCE --------------------\n</sentence>\n")
    
    sentenceList = []
    for sentence in sentences[:-1]:
        wordList = []
        
        rid = re.search('rid=\"([^\"])*\"', sentence).group()
        rid = rid[5:-1]
        # Muista varoa kauttamerkkejä itse lauseessa!
        #elements = re.split("(<elem [^\/]*\/elem>\n)", sentence)
        elements = re.split("(<elem .*[\/]elem>)\n", sentence)
        i = 0
        for element in elements:
            if element != None:
                if element.startswith("<elem elemtype=\""):

                    i += 1
                    elemText = re.search('>([^<])*</elem>', element).group()
                    # Start from the second char
                    elemText = re.search('([^<])*', elemText[1:]).group()
                    wordList.append (elemText)
        sentenceList.append([rid, wordList])
                
    return sentenceList


def parseOriginals(filename):
    """
    Gets an original file and parses it retrieving the relevant information
    Returns a dict:
    dictOriginals[rid] = [meta, elems, elemTexts]
    meta = lausetason metatiedot alkuperäistiedostossa
    elems = lista elementeistä: elemtype, type, fe_core_type, elemText
    elemTexts = lista elementtien teksteistä
    """
    f = open(filename, "r", encoding="utf8")
    fullText = f.read()
    f.close()
    sentences = str.split(fullText, "-------------------- END OF SENTENCE --------------------\n</sentence>\n")
    sentenceList = []
    dictOriginals = {}
    for sentence in sentences[:-1]:
        wordList = []
        rid = re.search('rid=\"([^\"])*\"', sentence).group()
        rid = rid[5:-1]
        frame = re.search('frame=\"([^\"])*\"', sentence).group()
        lexunit_name = re.search('lexunit_name=\"([^\"])*\"', sentence).group()
        fes = re.search('fes=\"([^\"])*\"', sentence).group()
        fes = ",".join(str.split(fes, " "))
        
        fes_rel = re.search('fes_rel=\"([^\"])*\"', sentence).group()
        fes_rel = "],".join(str.split(fes_rel, "] "))
        
        fes_pos_fn = re.search('fes_pos_fn=\"([^\"])*\"', sentence).group()
        fes_pos_fn = "],".join(str.split(fes_pos_fn, "] "))

#        context1 = re.search('>([^<])*<', sentence).group()

        # Muutettu 2014-12-01:
        # Kauttamerkit itse lauseessa sekoittivat koko kuvion
        #elements = re.split("(<elem [^\/]*\/elem>\n)", sentence)
        elements = re.split("(<elem .*[\/]elem>)\n", sentence)
        i = 0
        context1 = re.search('[^>].*$', elements[0]).group()
        context2 = re.search('[^\n].*$', sentence).group()

        elems = []
        elemTexts = []        
        for element in elements[1:-1]:

            if (element != None):
            
                if len(element) > 2:
                    # Panic reaction applied to the context found in the middle
                    if element.startswith("<elem") != True:
                        context1 += " " + element
                    else:
                        elemtype = re.search('elemtype="([^\"])*\"', element).group()
                        elType = re.search(' type="([^\"])*\"', element).group()
                        fe_core_type = re.search('fe_core_type="([^\"])*\"', element)
                        if fe_core_type != None:
                            fe_core_type = fe_core_type.group()
                        else:
                            fe_core_type = ""
                        elemText = re.search('>([^<])*</elem>', element).group()
                        # Start from the second char
                        elemText = re.search('([^<])*', elemText[1:]).group()
                        #print (elemtype + " :: " + elType + " :: " + fe_core_type + \
                        #        " :: " + elemText)
                        elems.append([elemtype, elType, fe_core_type, elemText])
                        elemTexts.append(elemText)
                    
        #context2 = re.search('<\/elem>.*', sentence).group()
        
        meta = frame + "\r\n" + lexunit_name + "\r\n" + fes + "\r\n" + \
               fes_rel + "\r\n" + fes_pos_fn + "\r\n\t" + \
               context1 + " " + " ".join(elemTexts) + " " + context2            
                        
        dictOriginals[rid] = [meta, elems, elemTexts]
    return dictOriginals
        







def createCqp(words, crits, partials, equals, continues, labels, depheads):
    """
    Gets 7 equally long lists of elements: eg.
    words = ["Hege", "on", "tyhmin", "tyhmä"]
    crits = ["word", "word", "word", "lemma"]
    partials = ["", "", "", ""] (<- mahdollistaa esim. "Hege on .*tyhmä" -tyyppiset haut)
      mahdolliset arvot: START_PLUS, START_ASTERISK, END_PLUS, END_ASTERISK,
      BOTH_ASTERISK, BOTH_PLUS (Ei testattu)
    equals = ["==", "==", "==", "=="] (<- vaihtoehtona myös != -hakuun) (Ei testattu)
    continues = [False, False, True, False] <- (True tarkoittaa, että seuraava kriteeri liittyy samaan sanaan)
    labels = ["", "", "", ""] (Ei testattu)
    depheads = ["", "", "", ""] (Ei testattu)
    Returns a CQP sentence for a Korp request
    """
    
    i = 0
    cqpList = []
    searchWord = ""

    continuationBegun = False

    for word in words:
        # Tätä ehkä vielä joudun katumaan
        # Ei hakuehtona voi olla tyhjää sanaa, eihän?
        if word == "":
            continue
        
        if partials[i] == "START_ASTERISK":
            start = ".*"
            end = ""
        elif partials[i] == "END_ASTERISK":
            start = ""
            end = ".*"
        elif partials[i] == "BOTH_ASTERISK":
            start = ".*"
            end = ".*"
        elif partials[i] == "START_PLUS":
            start = ".+"
            end = ""
        elif partials[i] == "END_PLUS":
            start = ""
            end = ".+"
        elif partials[i] == "BOTH_PLUS":
            start = ".+"
            end = ".+"
        else:
            start = ""
            end = ""

        if (equals[i] == True) or (equals[i] == "=="):
            eq = "+=+"
        else:
            eq = "+!=+"

        if labels[i] != "":
            label = labels[i] + ":"
        else:
            label = ""

        
        # Isolla alkukirjaimella alkavista hakusanoista
        # hyväksytään myös pienellä alkukirjaimella alkava versio
        # cqp-syntaksiin sisäänrakennettu %c on auttamattoman hidas
        if (word[0].isupper()) and (crits[i] == "word"):
            searchWord += "("
            searchWord += crits[i] + eq + "\"" + start + word.lower() + end + "\""
            searchWord += "+|+"
            searchWord += crits[i] + eq + "\"" + start + word.capitalize() + end + "\""
            searchWord += ")"
        else:
            if (continues == "OR") and (continuationBegun == False):
                searchWord += "("
                continuationBegun = True
            searchWord += crits[i] + eq + "\"" + start + word + end + "\""
        
        if continues[i] == False:
            searchWord = label + "[" + searchWord
            if continuationBegun:
                searchWord += ")"
                continuationBegun = False
            searchWord += "]"
            cqpList.append(searchWord)
            searchWord = ""
        elif continues == "OR":
            searchWord += "+|+"
        else:
            if continuationBegun:
                searchWord += ")"
                continuationBegun = False
            searchWord += "+&+"

        i += 1

    # Tätä osiota ei ole lainkaan testattu
    # Tästä voisi kehittää mahdollisuuden linkittää sanoja pääsanoihinsa
    globalRestriction = ""
    for k in range(0,len(depheads)):
        dephead = depheads[k]
        if (dephead != "") and (labels[k] != ""):
            if dephead in labels:
                if globalRestriction != "":
                    globalRestriction + "+&+"
                globalRestriction += labels[k] + ".dephead+=+" + dephead + ".ref"
            else:
                print("Not matching label & dephead: ")
                print("dephead = " + dephead)
                raise Exception

    if globalRestriction != "":
        cqpList[-1] += "::" + globalRestriction
            

    return cqpList



def wget_normal(cqpList, corpora, maxHits = 25):
    """
    Makes a request to Korp using all the possible corpora
    Returns a list of sentences
    """

    lstRetValues = []
    
    try:
        corpus = getCorpora(corpora)

        if type(cqpList) == list:
            cqpList = constructCQP(cqpList)
            
        show = "sentence,lemma,pos,msd,dephead,deprel,ref,lex"
        show_struct = 'subcorpus_name,sentence_id'

        structs = urllib.parse.quote( "+" )
        attrs = urllib.parse.quote("+,-lex")

        end = str(maxHits)
        
        values = []
        values.append(constructValues("command", "query"))
        values.append(constructValues("corpus", corpus))
        values.append("cqp=" + cqpList)
        values.append(constructValues("start", "0"))
        values.append(constructValues("end", end))
        values.append(constructValues("defaultcontext", "1+sentence", "+"))
        values.append(constructValues("defaultwithin", "sentence"))
        values.append(constructValues("show",show))
        values.append(constructValues("show_struct", show_struct))
        values.append(constructValues("incremental", "true"))
        values.append(constructValues("format", "tokens,csv"))
        values.append(constructValues("structs", "+"))
        values.append(constructValues("attrs", "+,-lex"))
        
        vals = "&".join(values)
        vals = vals.encode("utf8")

        url = 'http://nyklait-09-01.hum.helsinki.fi/cgi-bin/korp/korp_download.cgi'
        
        req = urllib2.Request(url, vals)
        response = urllib2.urlopen(req, vals)
    
        the_page = response.read()
        ret = the_page.decode('utf8')
        
        lstRet = splitToSentences(ret)
        
        if len(lstRet) > 0:
            lstRetValues += lstRet
    except urllib2.HTTPError as err:
        if err.code == 504:
            print("A gateway timeout. Sleep for 6 seconds")
            time.sleep(6)
        else:
            print("ERROR :: " + str(err.code) + "\t" + str(err.reason))
            print(err.read())
            raise
        
        

    return lstRetValues

def wget_dispersed(cqpList, corpora, maxHits = 25):
    """
    Makes a request to Korp targetting one decade at a time
    Returns a list of sentences
    """
    

    lstRetValues = []
    corp = corpora.split(",")
    for c in corp:
        try:
            corpus = getCorpora(c)
            
            cqp = constructCQP(cqpList)
            show = "sentence,lemma,pos,msd,dephead,deprel,ref,lex"
            show_struct = 'subcorpus_name,sentence_id'

            structs = urllib.parse.quote( "+" )
            attrs = urllib.parse.quote("+,-lex")

            end = str(maxHits)
            
            values = []
            values.append(constructValues("command", "query"))
            values.append(constructValues("corpus", corpus))
            values.append("cqp=" + cqp)
            values.append(constructValues("start", "0"))
            values.append(constructValues("end", end))
            values.append(constructValues("defaultcontext", "1+sentence", "+"))
            values.append(constructValues("defaultwithin", "sentence"))
            values.append(constructValues("show",show))
            values.append(constructValues("show_struct", show_struct))
            values.append(constructValues("incremental", "true"))
            values.append(constructValues("format", "tokens,csv"))
            values.append(constructValues("structs", "+"))
            values.append(constructValues("attrs", "+,-lex"))
            
            vals = "&".join(values)
            vals = vals.encode("utf8")

            url = 'http://nyklait-09-01.hum.helsinki.fi/cgi-bin/korp/korp_download.cgi'
            
            req = urllib2.Request(url, vals)
            response = urllib2.urlopen(req, vals)
        
            the_page = response.read()
            ret = the_page.decode('utf8')
            
            lstRet = splitToSentences(ret)
            
            if len(lstRet) > 0:
                lstRetValues += lstRet
        except urllib2.HTTPError as err:
            if err.code == 504:
                print("A gateway timeout. Sleep for 6 seconds")
                time.sleep(6)
            else:
                print("ERROR :: " + str(err.code) + "\t" + str(err.reason))
                raise
            
            continue

    
    return lstRetValues


def splitToSentences(texts):
    """
    Splits the response text from Korp into a list of sentences
    """

    ret = []
    
    if type(texts) == list:
        
        for text in texts:

            sentences = text.split("\r\n\"#")[3:]
            # remove metadata
            for sentence in sentences:
                #ret.append(str.split(sentences, "\r\n"))
                if sentence.startswith("#") != True:
                    ret.append(sentence)
    elif type(texts) == str:
        sentences = texts.split("\r\n\"#")[3:]
        for sentence in sentences:
            #ret.append(str.split(sentences, "\r\n"))
            if sentence.startswith("#") != True:
                ret.append(sentence)
    return ret

    
def constructValues(attrName, attrValue, ignore = ""):
    """
    Helper function to construct a attribute value + name -pair
    """
    attr = urllib.parse.quote(attrValue, ignore)
    ret = attrName + "=" + attr
    return ret

    
def constructCQP(cqpList):
    """
    Helper function to construct a valid CQP sentence for urllib retrieval
    Gets a list of CQP sentences and joins them in appropriate format
    """
    ret = ""
    for cqp in cqpList:
        ret += "+" + urllib.parse.quote( cqp, "[]+!*")
    ret = ret[1:]
    return ret







def getCorpora(decades):
    """
    decades = comma-separated list of decades in format 'u'cnn (eg. u193 = 1930-1939)
    returns a comma-separated list of valid years to retrieve from Korp
    """
    lstDecades = decades.split(",")
    years = []
    
    for decade in lstDecades:
        
        minYear = 10 * int(decade[-3:])

        if minYear == 2000:
            years.append("KLK_FI_" + str(minYear))
        elif minYear == 1900:
            for year in range(minYear, minYear + 6):
                years.append("KLK_FI_" + str(year))
        else:
            for year in range(minYear, minYear + 10):
                if (year != 1828) and (year != 1843):
                    years.append("KLK_FI_" + str(year))

    strYears = ",".join(years)
    
    return  strYears


def combineIntel(folder=binPath):

    bad_allDictExtra = {}
    bad_allDict = {}
    good_allDict = {}
    good_allDictExtra = {}
    fileSpecificDicts = []

    newDict = {}
    newDictExtra = {}
    
    for file in os.listdir(folder):
        if (os.path.isdir(folder + pathSep + file) == False):
            if (file.startswith("goodSearches")) or \
               (file.startswith("badSearches")):
                splitFile = file.split("_")
                #fileGroup = splitFile[-2]
                searchSuccess = (splitFile[0] == "goodSearches")
                annotatedFile = splitFile[1:]
                
                if file.startswith("goodSearches"):
                    getSearchTypesFromFile(folder + pathSep + file, \
                                           good_allDict, \
                                           good_allDictExtra)
                elif file.startswith("badSearches"):
                    getSearchTypesFromFile(folder + pathSep + file, \
                                           bad_allDict, \
                                           bad_allDictExtra)

                    
                #fileSpecificDicts.append(searchSuccess + "_" + fileGroup + "_" + file, (newDict, newDictExtra))
                #groupSpecificDicts.append(searchSuccess + "_" + fileGroup, (groupSpecificDict, groupSpecificDictExtra))

    return good_allDict, good_allDictExtra, bad_allDict, bad_allDictExtra
    
    for filename, twoDicts in fileSpecificDicts.items():
        fileSpecificDict = twoDicts[0]
        fileSpecificDictExtra = twoDicts[1]
        f = open (outputPath + pathSep + filename, "w", encoding="cp1252")
        for key, value in fileSpecificDict.items():
            f.write(key + "\t" + value)
            
            
def finalCountdown():

    good_allDict, good_allDictExtra, bad_allDict, bad_allDictExtra = combineIntel()

    #filtered_dict = {key:value for (key:value) in good_allDictExtra.items() \
    #                 if key.startswith("1")}


    ret = printFinalSums("1_", good_allDictExtra, bad_allDictExtra, printExistingDeprels=True)
    ret += printFinalSums("2_", good_allDictExtra, bad_allDictExtra, printExistingDeprels=True)
    ret += printFinalSums("3_", good_allDictExtra, bad_allDictExtra)
    ret += printFinalSums("4left_", good_allDictExtra, bad_allDictExtra, printExistingDeprels=True)
    ret += printFinalSums("4right_", good_allDictExtra, bad_allDictExtra, printExistingDeprels=True)
    ret += printFinalSums("5left_", good_allDictExtra, bad_allDictExtra, printExistingDeprels=True)
    ret += printFinalSums("5right_", good_allDictExtra, bad_allDictExtra, printExistingDeprels=True)
    ret += printFinalSums("6left_", good_allDictExtra, bad_allDictExtra,)
    ret += printFinalSums("6right_", good_allDictExtra, bad_allDictExtra)
    ret += printFinalSums("7_", good_allDictExtra, bad_allDictExtra, printExistingDeprels=True)
    ret += printFinalSums("8left_", good_allDictExtra, bad_allDictExtra, printExistingDeprels=True)
    ret += printFinalSums("8right_", good_allDictExtra, bad_allDictExtra, printExistingDeprels=True)
    ret += printFinalSums("9_", good_allDictExtra, bad_allDictExtra, printExistingDeprels=True)
    ret += printFinalSums("10_", good_allDictExtra, bad_allDictExtra)
    ret += printFinalSums("11_", good_allDictExtra, bad_allDictExtra)

    ret += printFinalSums("", good_allDictExtra, bad_allDictExtra, printExistingDeprels=True)
    
    good_sum = getFinalSums("", good_allDictExtra)
    bad_sum = getFinalSums("", bad_allDictExtra)
    good_sums_method1 = getFinalSums("1_", good_allDictExtra)
    good_sums_method2 = getFinalSums("2_", good_allDictExtra)
    good_sums_method3 = getFinalSums("3_", good_allDictExtra)
    good_sums_method4left = getFinalSums("4left_", good_allDictExtra)
    good_sums_method4right = getFinalSums("4right_", good_allDictExtra)
    good_sums_method5left = getFinalSums("5left_", good_allDictExtra)
    good_sums_method5right = getFinalSums("5right_", good_allDictExtra)
    good_sums_method6left = getFinalSums("6left_", good_allDictExtra)
    good_sums_method6right = getFinalSums("6right_", good_allDictExtra)
    good_sums_method7 = getFinalSums("7_", good_allDictExtra)
    good_sums_method8left = getFinalSums("8left", good_allDictExtra)
    good_sums_method8right = getFinalSums("8right_", good_allDictExtra)
    good_sums_method9 = getFinalSums("9_", good_allDictExtra)
    good_sums_method10 = getFinalSums("10_", good_allDictExtra)
    good_sums_method11 = getFinalSums("11_", good_allDictExtra)
    good_sums_FAIL = getFinalSums("FAIL_", good_allDictExtra)
    good_sums_WTF = (good_sum - \
                    (good_sums_method1 + good_sums_method2 + good_sums_method3 + \
                     good_sums_method4left + good_sums_method4right + \
                     good_sums_method5left + good_sums_method5right + \
                     good_sums_method6left + good_sums_method6right + \
                     good_sums_method7 + good_sums_method8left + good_sums_method8right + \
                     good_sums_method9 + good_sums_method10 + \
                     good_sums_method11 + good_sums_FAIL))

    bad_sums_method1 = getFinalSums("1_", bad_allDictExtra)
    bad_sums_method2 = getFinalSums("2_", bad_allDictExtra)
    bad_sums_method3 = getFinalSums("3_", bad_allDictExtra)
    bad_sums_method4left = getFinalSums("4left_", bad_allDictExtra)
    bad_sums_method4right = getFinalSums("4right_", bad_allDictExtra)
    bad_sums_method5left = getFinalSums("5left_", bad_allDictExtra)
    bad_sums_method5right = getFinalSums("5right_", bad_allDictExtra)
    bad_sums_method6left = getFinalSums("6left_", bad_allDictExtra)
    bad_sums_method6right = getFinalSums("6right_", bad_allDictExtra)
    bad_sums_method7 = getFinalSums("7_", bad_allDictExtra)
    bad_sums_method8left = getFinalSums("8left", bad_allDictExtra)
    bad_sums_method8right = getFinalSums("8right_", bad_allDictExtra)
    bad_sums_method9 = getFinalSums("9_", bad_allDictExtra)
    bad_sums_method10 = getFinalSums("10_", bad_allDictExtra)
    bad_sums_method11 = getFinalSums("11_", bad_allDictExtra)
    bad_sums_FAIL = getFinalSums("FAIL_", bad_allDictExtra)
    bad_sums_WTF = (bad_sum - \
                    (bad_sums_method1 + bad_sums_method2 + bad_sums_method3 + \
                     bad_sums_method4left + bad_sums_method4right + \
                     bad_sums_method5left + bad_sums_method5right + \
                     bad_sums_method6left + bad_sums_method6right + \
                     bad_sums_method7 + bad_sums_method8left + bad_sums_method8right + \
                     bad_sums_method9 + bad_sums_method10 + \
                     bad_sums_method11 + bad_sums_FAIL))
    
    
    ret += "\n".rjust(68, "-")
    ret += "Method % of grand total\n".rjust(50)
    ret += "{0:40s}{1:6s}{2:6s}{3:6s}{4:6s}\n".format("", "  GOOD", "   BAD", "  Good%", "   Bad%")        

    ret += formatFinalText("Method 1", good_sums_method1, bad_sums_method1, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Method 2", good_sums_method2, bad_sums_method2, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Method 3", good_sums_method3, bad_sums_method3, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Method 4left", good_sums_method4left, bad_sums_method4left, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Method 4right", good_sums_method4right, bad_sums_method4right, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Method 5left", good_sums_method5left, bad_sums_method5left, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Method 5right", good_sums_method5right, bad_sums_method5right, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Method 6left", good_sums_method6left, bad_sums_method6left, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Method 6right", good_sums_method6right, bad_sums_method6right, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Method 7", good_sums_method7, bad_sums_method7, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Method 8left", good_sums_method8left, bad_sums_method8left, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Method 8right", good_sums_method8right, bad_sums_method8right, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Method 9", good_sums_method9, bad_sums_method9, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Method 10", good_sums_method10, bad_sums_method10, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Method 11", good_sums_method11, bad_sums_method11, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("FAIL", good_sums_FAIL, bad_sums_FAIL, \
                           int3=good_sum, int4=bad_sum)
    ret += formatFinalText("Something else", good_sums_WTF, bad_sums_WTF, \
                           int3=good_sum, int4=bad_sum)

    print(ret)
    
def printFinalSums(startFilter, \
                   good_allDictExtra, \
                   bad_allDictExtra, \
                   printExistingDeprels=False, \
                   grandTotal=False):

    good_figures = getFinalSums(startFilter, good_allDictExtra)
    bad_figures = getFinalSums(startFilter, bad_allDictExtra)

    if startFilter == "":
        # calculating grand total, let's keep irrelevant numbers afar
        tupleDeprelsNeeded = ("1_", "2_", "4left", "4right", \
                             "5left", "5right", "7_", "8left", "8right", "9_")
        tupleDeprelsNotNeeded = ("3_", "6left", "6right", "10_", "11_")
        good_existingDeprels_False, good_existingDeprels_True = getExistingDeprels(tupleDeprelsNeeded, good_allDictExtra)
        bad_existingDeprels_False, bad_existingDeprels_True = getExistingDeprels(tupleDeprelsNeeded, bad_allDictExtra)
        good_existingDeprels_NA = getFinalSums(tupleDeprelsNotNeeded, good_allDictExtra)
        bad_existingDeprels_NA = getFinalSums(tupleDeprelsNotNeeded, bad_allDictExtra)
    else:
        good_existingDeprels_False, good_existingDeprels_True = getExistingDeprels(startFilter, good_allDictExtra)
        bad_existingDeprels_False, bad_existingDeprels_True = getExistingDeprels(startFilter, bad_allDictExtra)
        
    good_noLemmas = getLooseningMethods(startFilter, "no_lemmas", good_allDictExtra, "fee_deprels_no_lemmas")
    bad_noLemmas = getLooseningMethods(startFilter, "no_lemmas", bad_allDictExtra, "fee_deprels_no_lemmas")
    good_deprelsPartial= getLooseningMethods(startFilter, "deprels_partial", good_allDictExtra, "lc_deprels_partial", "rc_deprels_partial", "plus_deprels_partial")
    bad_deprelsPartial = getLooseningMethods(startFilter, "deprels_partial", bad_allDictExtra, "lc_deprels_partial", "rc_deprels_partial", "plus_deprels_partial")
    good_switchedOrder= getLooseningMethods(startFilter, "switched_order", good_allDictExtra)
    bad_switchedOrder = getLooseningMethods(startFilter, "switched_order", bad_allDictExtra)
    good_partialWords= getLooseningMethods(startFilter, "partial_words", good_allDictExtra)
    bad_partialWords = getLooseningMethods(startFilter, "partial_words", bad_allDictExtra)
    good_partialLemmas = getLooseningMethods(startFilter, "partial", good_allDictExtra, "deprels_partial", "partial_words")
    bad_partialLemmas = getLooseningMethods(startFilter, "partial", bad_allDictExtra, "deprels_partial", "partial_words")
    
    good_lcDeprelsPartial = getLooseningMethods(startFilter, "lc_deprels_partial", good_allDictExtra)
    bad_lcDeprelsPartial = getLooseningMethods(startFilter, "lc_deprels_partial", bad_allDictExtra)
    good_rcDeprelsPartial = getLooseningMethods(startFilter, "rc_deprels_partial", good_allDictExtra)
    bad_rcDeprelsPartial = getLooseningMethods(startFilter, "rc_deprels_partial", bad_allDictExtra)

    good_noFeeDeprels = getLooseningMethods(startFilter, "no_fee_deprels", good_allDictExtra)
    bad_noFeeDeprels = getLooseningMethods(startFilter, "no_fee_deprels", bad_allDictExtra)    
    good_feeDeprelsNoLemmas = getLooseningMethods(startFilter, "fee_deprels_no_lemmas", good_allDictExtra)
    bad_feeDeprelsNoLemmas = getLooseningMethods(startFilter, "fee_deprels_no_lemmas", bad_allDictExtra)
    good_plusDeprels = getLooseningMethods(startFilter, "plus_deprels", good_allDictExtra, "plus_deprels_partial")
    bad_plusDeprels = getLooseningMethods(startFilter, "plus_deprels", bad_allDictExtra, "plus_deprels_partial")
    good_plusDeprelsPartial = getLooseningMethods(startFilter, "plus_deprels_partial", good_allDictExtra)
    bad_plusDeprelsPartial = getLooseningMethods(startFilter, "plus_deprels_partial", bad_allDictExtra)

    # plus_deprels & plus_deprels_partial aren't loosened, but tightened methods
    good_pure = getFinalSums(startFilter + "False", good_allDictExtra)
    good_pure += getFinalSums(startFilter + "True", good_allDictExtra)
    good_pure += getFinalSums(startFilter + "plus_deprels_False", good_allDictExtra)
    good_pure += getFinalSums(startFilter + "plus_deprels_True", good_allDictExtra)
    good_pure += getFinalSums(startFilter + "plus_deprels_partial_False", good_allDictExtra)
    good_pure += getFinalSums(startFilter + "plus_deprels_partial_True", good_allDictExtra)
    
    bad_pure = getFinalSums(startFilter + "False", bad_allDictExtra)
    bad_pure += getFinalSums(startFilter + "True", bad_allDictExtra)
    bad_pure += getFinalSums(startFilter + "plus_deprels_False", bad_allDictExtra)
    bad_pure += getFinalSums(startFilter + "plus_deprels_True", bad_allDictExtra)
    bad_pure += getFinalSums(startFilter + "plus_deprels_partial_False", bad_allDictExtra)
    bad_pure += getFinalSums(startFilter + "plus_deprels_partial_True", bad_allDictExtra)
    
    good_impure = (good_figures - good_pure)
    bad_impure = (bad_figures - bad_pure)

    ret = "\n".rjust(68, "-")

    if startFilter == "":
        ret += "GRAND TOTAL\n".rjust(40)
    else:
        ret += "Method {0}\n".rjust(40).format(startFilter.split("_")[0])

    ret += "{0:40s}{1:6s}{2:6s}{3:6s}{4:6s}\n".format("", "  GOOD", "   BAD", "  Good%", "   Bad%")
    ret += formatFinalText("Total", good_figures, bad_figures, printAlways=True)
    ret += formatFinalText("Total (unloosened)", good_pure, bad_pure, \
                           printAlways=True, int3=good_figures, int4=bad_figures)
    ret += formatFinalText("Total (loosened)", good_impure, bad_impure, \
                           printAlways=True, int3=good_figures, int4=bad_figures)

    if printExistingDeprels:
        ret += formatFinalText("Existing fee deprels: True", \
            good_existingDeprels_True, bad_existingDeprels_True, \
            int3=good_figures, int4=bad_figures)
        ret += formatFinalText("Existing fee deprels: False", \
            good_existingDeprels_False, bad_existingDeprels_False, \
            int3=good_figures, int4=bad_figures)
        if startFilter == "":
            ret += formatFinalText("Existing FEE deprels: N/A", \
                good_existingDeprels_NA, bad_existingDeprels_NA, \
                int3=good_figures, int4=bad_figures)

    
    ret += formatFinalText("No lemmas", good_noLemmas, bad_noLemmas, \
                           int3=good_figures, int4=bad_figures)
    ret += formatFinalText("Partial deprels (FEE)", good_deprelsPartial, bad_deprelsPartial, \
                           int3=good_figures, int4=bad_figures)
    ret += formatFinalText("Switched word order", good_switchedOrder, bad_switchedOrder, \
                           int3=good_figures, int4=bad_figures)
    ret += formatFinalText("Partial words", good_partialWords, bad_partialWords, \
                           int3=good_figures, int4=bad_figures)
    ret += formatFinalText("Partial lemmas", good_partialLemmas, bad_partialLemmas, \
                           int3=good_figures, int4=bad_figures)
    ret += formatFinalText("Partial deprels (left)", good_lcDeprelsPartial, bad_lcDeprelsPartial, \
                           int3=good_figures, int4=bad_figures)
    ret += formatFinalText("Partial deprels (right)", good_rcDeprelsPartial, bad_rcDeprelsPartial, \
                           int3=good_figures, int4=bad_figures)
    ret += formatFinalText("No deprels (FEE)", good_noFeeDeprels, bad_noFeeDeprels, \
                           int3=good_figures, int4=bad_figures)
    ret += formatFinalText("No lemmas, but deprels (FEE)", good_feeDeprelsNoLemmas, bad_feeDeprelsNoLemmas, \
                           int3=good_figures, int4=bad_figures)
    ret += formatFinalText("Additional deprels (context)", good_plusDeprels, bad_plusDeprels, \
                           int3=good_figures, int4=bad_figures)
    ret += formatFinalText("Additional partial deprels (context)", good_plusDeprelsPartial, bad_plusDeprelsPartial, \
                           int3=good_figures, int4=bad_figures)
    
    return ret

def formatFinalText(header, int1, int2, printAlways=False, int3=0, int4=0):

    if (int1 > 0) or (int2 > 0) or (printAlways):
        if (int3 > 0) and (int4 > 0):
            percentage1 = (int1 / int3) * 100
            percentage2 = (int2 / int4) * 100
            
            ret = "{0:40s}{1:6n}{2:6n} {3:6.1f} {4:6.1f}\n".format(\
                header, int1, int2, percentage1, percentage2)
        else:
            ret = "{0:40s}{1:6n}{2:6n}\n".format(header, int1, int2)
    else:
        ret = ""
    return ret


    
def getLooseningMethods(startfilter, containFilter, dct, exclude1="", exclude2="", exclude3=""):

    if (exclude1 != "") and (exclude2 != "") and (exclude3 != ""):
        methodCount = sum(value for (key,value) in dct.items() \
                     if ((key.startswith(startfilter)) \
                         and (containFilter in key) \
                         and (exclude1 not in key) \
                         and (exclude2 not in key) \
                         and (exclude3 not in key)))
    if (exclude1 != "") and (exclude2 != ""):
        methodCount = sum(value for (key,value) in dct.items() \
                     if ((key.startswith(startfilter)) \
                         and (containFilter in key) \
                         and (exclude1 not in key) \
                         and (exclude2 not in key)))
    elif (exclude1 != ""):
        methodCount = sum(value for (key,value) in dct.items() \
                     if ((key.startswith(startfilter)) \
                         and (containFilter in key) \
                         and (exclude1 not in key)))
    else:
         methodCount = sum(value for (key,value) in dct.items() \
                           if ((key.startswith(startfilter)) \
                               and (containFilter in key)))

    return methodCount


def getExistingDeprels(startfilter, dct):

    existingDeprels_False = sum(value for (key,value) in dct.items() \
                     if (key.startswith(startfilter) and key.endswith("False")))

    existingDeprels_True = sum(value for (key,value) in dct.items() \
                     if (key.startswith(startfilter) and key.endswith("True")))
    
    return existingDeprels_False, existingDeprels_True


def getFinalSums(startfilter, dct):

    finalSum = sum(value for (key,value) in dct.items() \
                     if key.startswith(startfilter))
   
    return finalSum


def getSearchTypesFromFile(filepath, dictionary, dictExtra):

    f = open(filepath, "r", encoding="cp1252")
    filename = filepath.split(pathSep)[-1]
    text = f.read()
    f.close()
    lines = text.split("\n")
    try:
        for line in lines:
            if line != "":
                cols = line.split("\t")
                rid = cols[0]
                sentenceID = cols[1]
                searchMethod = cols[2]
                extraContentExists = (cols[3] == "Exists")
                addToDict(dictionary, searchMethod, 1)
                addToDict(dictExtra, searchMethod + "_" + str(extraContentExists), 1)

                #addToDict(dictionary, searchMethod + "_" + filename, 1)
                #addToDict(dictExtra, searchMethod + "_" + str(extraContentExists) + "_" + filename, 1)

                #addToDict(dictionary, filename, 1)
                #addToDict(dictExtra, filename, 1)
                #addToDict(allDict, searchMethod, + 1)
                #addToDict(allDictExtra, searchMethod + "_" + extraContent, 1)
    except:
        print(line)
        raise
    
            
#getFigures()
#makeRidExcel()
#getOkRidsFromFile()
#getAnnotatedRidsFromFile(True)
#findNewFrameFILUs("varia12",maxSize=100,startFrame="Change_of_leadership__äänestää")
#findNewFrameFILUs("varia13",maxSize=100,startFrame="Place_weight_on__painottaa")
#getSentenceIDs()
